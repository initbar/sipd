# Active recording Session Initiation Protocol daemon (sipd).
# Copyright (C) 2018  Herbert Shin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# https://github.com/initbar/sipd

#-------------------------------------------------------------------------------
# server.py -- asynchronous SIP server module.
#-------------------------------------------------------------------------------

# ARCHITECTURE
#-------------------------------------------------------------------------------
#
#                                            | | | receive SIP
#                                            | | | messages.
#                                            V V V
# +--------+  create asynchronous router   +--------+  dispatch to workers
# | server | ----------------------------> | router | --+----------+-------
# +--------+                               +--------+   |          |
#                                                       |          |
#                                                       V          V
#                                                  +--------+  +--------+
#                                              ..  | worker |  | worker |  ..
#                                                  +--------+  +--------+
#                                                       ^          ^
#                       +-------------+                 |          |
#                       | RTP decoder | <---------------+----------+-------
#                       +-------------+   delegate RTP to RTP decoder
#                                         using SDP headers.
#-------------------------------------------------------------------------------

from multiprocessing import cpu_count

import asyncore
import random
import sys
import threading
import time

try:
    from src.debug import create_random_uuid
    from src.errors import SIPBrokenProtocol
    from src.parser import convert_to_sip_packet
    from src.parser import parse_sip_packet
    from src.parser import validate_sip_signature
    from src.rtp.server import SynchronousRTPRouter
    from src.sip.garbage import SynchronousSIPGarbageCollector
    from src.sip.static.busy import SIP_BUSY
    from src.sip.static.bye import SIP_BYE
    from src.sip.static.ok import SIP_OK
    from src.sip.static.ok import SIP_OK_NO_SDP
    from src.sip.static.options import SIP_OPTIONS
    from src.sip.static.ringing import SIP_RINGING
    from src.sip.static.terminated import SIP_TERMINATE
    from src.sip.static.trying import SIP_TRYING
    from src.sockets import unsafe_allocate_random_udp_socket
    from src.sockets import unsafe_allocate_udp_socket
except ImportError: raise

import logging
logger = logging.getLogger(__name__)

# each worker should not instantiate a new garbage collector since a subsequent
# related requests can not guarantee to hit the same worker. Therefore, the
# workers should all use the same garbage collector and just register a new
# collection tasks to the collector queue.
GC = None

SERVER_SETTINGS = {} # `sipd.json`

# SIP socket
#-------------------------------------------------------------------------------

def unsafe_allocate_sip_socket(host='0.0.0.0', port=5060, timeout=1.0):
    ''' allocate listening SIP socket that must be manually cleaned up.
    '''
    logger.debug('attempting to create SIP socket on port: %i.' % port)
    return unsafe_allocate_udp_socket(host, port, timeout, is_reused=True)

class safe_allocate_sip_socket(object):
    ''' allocate exception-safe listening SIP socket.
    '''
    def __init__(self, port=5060, timeout=1.0):
        self.port = port
        self.timeout = timeout
        self._socket = None

    def __enter__(self):
        self._socket = unsafe_allocate_sip_socket(port=self.port, timeout=self.timeout)
        return self._socket

    def __exit__(self, type, value, traceback):
        try: self._socket.close()
        except:
            self._socket.shutdown()
            self._socket.close()
            del self._socket

# SIP server
#-------------------------------------------------------------------------------

class SIPServerPrototype(object):
    ''' Asynchronous SIP server prototype.
    '''
    def __init__(self, setting):
        if isinstance(setting, dict):
            # globalize settings and garbage collector.
            global SERVER_SETTINGS; SERVER_SETTINGS = setting
            global GC; GC = SynchronousSIPGarbageCollector(setting)
            logger.debug('[sip] globalized settings.')
        logger.info('[sip] server initialized.')

class AsynchronousSIPServer(SIPServerPrototype):
    ''' Asynchronous SIP server implementation.
    '''
    def serve(self):
        # assign asynchronous handler to the receiving SIP port. Currently,
        # `asyncore` module was chosen in order to provide backward
        # compatibility with Python 2 (where there's no `asyncio`). All
        # incoming traffic is routed and initially handled by the router.
        try: sip_port = SERVER_SETTINGS['sip']['router']['port']
        except: sip_port = 5060 # udp
        with safe_allocate_sip_socket(port=sip_port) as sip_socket:
            sip_router = AsynchronousSIPRouter(sip_socket)
            asyncore.loop() # push new events to the event loop.

# SIP router
#-------------------------------------------------------------------------------

class SIPRouterPrototype(asyncore.dispatcher):
    ''' Asynchronous SIP routing component prototype.
    '''
    def __init__(self, sip_socket):

        # in order to prevent double creation of a router socket, inherit
        # SIP port from SIP server. A router should only be used to receive
        # traffic. For that reason (and also to not cause 100% CPU
        # utilization by infinite loop checks), override polling states.
        asyncore.dispatcher.__init__(self, sip_socket)
        self.is_readable = True
        self.is_writable = False

        # since it's possible that SIP server is running on a server with
        # multiple cores/threads, workers are dynamically allocated based
        # on server specification. Unless given, the following formula is
        # used for dynamic allocation of workers:
        #
        #   total_workers = [ 1 + floor(total_cores * 0.32) ]
        #
        # Which has the following distribution:
        #
        #  6 |                                                    x
        #  5 |                                        x   x   x   x
        #  4 |                            x   x   x   x   x   x   x
        #  3 |                   x  x  x  x   x   x   x   x   x   x
        #  2 |          x  x  x  x  x  x  x   x   x   x   x   x   x
        #  1 | x  x  x  x  x  x  x  x  x  x   x   x   x   x   x   x
        #    +-----------------------------------------------------------
        #      1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16
        try:
            worker_size = SERVER_SETTINGS['sip']['worker']['count']
            assert worker_size > 0 # check for dynamic allocation.
            # if worker size is given, then normalize the count to not
            # exceed the available resources. After all, GIL only
            # permits only one active thread at a given time.
            self._worker_size = min(max(worker_size, 1), cpu_count())
        except:
            self._worker_size = 1 + int(cpu_count() * 0.32)
        logger.debug('[sip] total router workers: %i.', self._worker_size)

        self._random = random.random # cache random number generator.

        # workers should never cause conflict with main server thread.
        # For that reason, each worker must exist in their own thread.
        self._workers = [ SynchronousSIPWorker(i) for i in range(self._worker_size) ]
        self._handlers = []
        for worker in self._workers:
            handler_name = worker.name
            handler = threading.Thread(name=worker.name, target=worker.handle)
            handler.daemon = True
            self._handlers.append(handler)
        map(lambda thread:thread.start(), self._handlers) # start threads.
        random.shuffle(self._workers) # shuffle workers for selection.
        logger.info('[sip] router initialized.')

    def readable(self):
        ''' return current readable state.
        '''
        return self.is_readable

    def writable(self):
        ''' return current writable state.
        '''
        return self.is_writable

    def handle_write(self):
        return

class AsynchronousSIPRouter(SIPRouterPrototype):
    ''' Asynchronous SIP routing component implementation.
    '''
    def handle_read(self):
        # the purpose of router is to only receive data ("work") and delegate
        # them to its' workers. A worker holds the logic implementation.
        try:
            message = self.recvfrom(0xffff) # max receive bytes.
            sip_endpoint = tuple(message[1])
            sip_message  = str(message[0])
        except: return
        # we want a balanced distribution to our workers. For example, we want
        # to reflect round robin distribution closely as possible - yet have
        # enough chance to delegate two short tasks to the same worker.
        while not locals().get('work_delegated', False): # temporary.
            p_index = int(self._random() * self._worker_size)
            worker = self._workers[p_index]
            if worker.is_ready():
                worker.assign(sip_endpoint, sip_message)
                work_delegated = True # break loop.

# SIP worker
#-------------------------------------------------------------------------------

class SIPWorkerPrototype(object):
    ''' Asynchronous SIP worker component prototype.
    '''
    def __init__(self, worker_id, gc=None, verbose=False):
        self.verbose = verbose # display dissected packets.
        self.name = 'worker-' + str(worker_id)

        # each worker is managed by thead events. A worker is considered
        # "working" if its event is 'true' and "free" if 'false'.
        self.event = threading.Event()
        self.is_ready = lambda: not self.event.isSet()

        # each worker has its own socket to send data and a RTP router
        # to yield RTP server information to dynamically generate SDP headers.
        self._socket = unsafe_allocate_random_udp_socket(is_reused=True)
        self._rtp_handler = SynchronousRTPRouter(SERVER_SETTINGS)

        # default SIP headers to override parsed requests and respond with.
        try: self._sip_defaults = SERVER_SETTINGS['sip']['worker']['headers']
        except: self._sip_defaults = {}
        logger.debug('[env] sip defaults: %s' % self._sip_defaults)

        # if SIP server did not receive CANCEL/BYE due to unforseen error(s),
        # then we need absolute maximum time-to-live (ttl) value to force-expire
        # a call from RTP decoder. By default, all calls expire after one hour.
        try: self.lifetime = SERVER_SETTINGS['gc']['call_lifetime'] # seconds
        except: self.lifetime = 60 * 60
        logger.debug('[env] call lifetime: %s' % self.lifetime)

        # shared objects.
        [
            self.sip_datagram,
            self.call_id,
            self.method,
            self.tag
        ] = [None] * 4

        # custom handlers.
        self.handlers = {
            'ACK':     self.handler_ack,
            'BYE':     self.handler_cancel,
            'CANCEL':  self.handler_bye,
            'DEFAULT': self.handler_default,
            'INVITE':  self.handler_invite
        }

class SynchronousSIPWorker(SIPWorkerPrototype):
    ''' Asynchronous SIP worker component implementation.
    '''
    def __init__(self, *args, **kwargs):
        super(SynchronousSIPWorker, self).__init__(*args, **kwargs)
        self.sip_endpoint = self.sip_message = None # "work"
        logger.debug('[sip] %s initialized.' % self.name)

    #
    # worker interface
    #

    def assign(self, sip_endpoint, sip_message=None):
        ''' assign a worker with "work".
        '''
        if not (sip_endpoint and sip_message): return
        self.sip_endpoint = sip_endpoint
        self.sip_message  = sip_message
        self.event.set() # worker is now assigned.
        self.handle() # worker hook to force work.

    def relinquish_work(self):
        ''' relinquish a worker from "work".
        '''
        self.sip_endpoint = self.sip_message = None
        self.event.clear()

    def handle(self):
        ''' worker logic implementation.
        '''
        self.tag = create_random_uuid() # session tag.

        try: # error check if worker has work.
            assert self.sip_endpoint and self.sip_message
            if not validate_sip_signature(self.sip_message):
                raise SIPBrokenProtocol
            self.sip_datagram = parse_sip_packet(self.sip_message)
        except SIPBrokenProtocol:
            # instead of error correction, relinquish the work from worker
            # so that it can move on to the next future task.
            logger.error("---- [sip] [%s] <<%s>> PARSE FAILED: '%s'" % (
                self.name, self.tag, self.sip_message))
            return self.relinquish_work()
        except Exception as message:
            logger.error("----- [sip] %s" % message)
            return self.relinquish_work()

        # override parsed values with pre-defined fields.
        try:
            self.call_id = self.sip_datagram['sip'].get('Call-ID')
            self.method  = self.sip_datagram['sip'].get('Method')
        except:
            logger.error('---- [sip] malformed packet: %s' % self.sip_datagram)
        for (field, value) in self._sip_defaults.items():
            self.sip_datagram['sip'][field] = value

        # handler mapping.
        logger.debug('-->> [sip] [%s] <<%s>> <%s>' % (self.name, self.tag, self.method))
        self.handlers.get(self.method, 'DEFAULT')()
        self.relinquish_work()

    #
    # worker handlers
    #

    def handler_default(self):
        ''' default event handler.
        '''
        self.__send_sip_ok()

    def handler_ack(self):
        pass # ignore ACK.

    def handler_bye(self):
        ''' BYE event handler.
        '''
        self.__send_sip_ok_no_sdp()
        deferred_revoke_host = lambda: GC.consume_membership(
            call_tag=self.tag, call_id=self.call_id, forced=True)
        GC.register_new_task(lambda: deferred_revoke_host())
        self.__send_sip_term()

    def handler_cancel(self):
        ''' CANCEL event handler.
        '''
        self.__send_sip_ok()
        if self._rtp_handler:
            self._rtp_handler.handle(
                sip_tag=self.tag,
                sip_datagram=self.sip_datagram,
                rtp_state='stop')
        self.__send_sip_term()

    def handler_invite(self):
        ''' INVITE event handler.
        '''
        # TODO: decide to delegate to another server.
        logger.debug('---- [sip] deciding to load balance to another server..')
        self.sip_datagram['sip']['Contact'] = '<sip:%s:5060>' % SERVER_SETTINGS['sip']['server']['address']
        logger.debug('---- [sip] balancing to node: %s' % self.sip_datagram['sip']['Contact'])

        # if duplicate INVITE message was received with same Call-ID, then it's
        # necessary to ignore the future duplicates.
        if self.call_id in GC.calls_history:
            logger.warning('---- [sip] received duplicate Call-ID: %s' % self.call_id)
            self.__send_sip_ok_no_sdp()
            return
        elif not self._rtp_handler:
            logger.error('---- [sip] external RTP handler is not configured.')
            self.__send_sip_ok_no_sdp()
            return
        else:
            self.__send_sip_trying()

        # prepare RTP delegation. An external RTP handler must reply with two
        # ports to receive TX/RX RTP traffic.
        try: chances = max(1, SERVER_SETTINGS['rtp']['max_retry'])
        except: chances = 1
        while chances:
            self.__send_sip_ringing()
            chances -= 1

            # if external RTP handler replies with one or more ports, rewrite
            # and update the SIP datagram with new SDP information.
            sip_datagram = self._rtp_handler.handle(self.tag, self.sip_datagram)
            if sip_datagram:
                self.sip_datagram = sip_datagram
                break

        # create a deferred task and register to the garbage collection
        # queue. All task context is explained in gc implementation.
        def deferred_register_new_host():
            # register new session to history and membership.
            if not GC.membership.get(self.call_id):
                GC.calls_history[self.call_id] = None
                GC.calls_stats += (self.call_id in GC.calls_history)
                GC.membership[self.call_id] = {
                    'state': self.method,
                    'tags': [self.tag],
                    'tags_cnt': 1}
            else: # add current session to existing membership.
                GC.membership[self.call_id]['tags'].append(self.tag)
                GC.membership[self.call_id]['tags_cnt'] += 1
            GC._garbage.append({
                'Call-ID': self.call_id,
                'tag': self.tag,
                'ttl': self.lifetime + int(time.time())})

        # add deferred to GC queue to linearly task demultiplexed jobs.
        GC.register_new_task(lambda: deferred_register_new_host())
        self.__send_sip_ok()

    #
    # worker responses
    #

    def __send_sip_cancel(self):
        ''' send SIP CANCEL to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <CANCEL>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_CANCEL, self.sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_ok(self):
        ''' send SIP OK to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <OK +SDP>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_OK, self.sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_ok_no_sdp(self):
        logger.debug('<<-- [sip] [%s] <<%s>> <OK -SDP>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_OK_NO_SDP, self.sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_options(self):
        ''' send SIP OPTIONS to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <OPTIONS>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_OPTIONS, self.sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_ringing(self):
        ''' send SIP RINGING to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <RINGING>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_RINGING, self.sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_term(self):
        ''' send SIP TERMINATE to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <TERM>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_TERMINATE, self.sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_trying(self):
        ''' send SIP TRYING to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <TRYING>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_TRYING, self.sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)
