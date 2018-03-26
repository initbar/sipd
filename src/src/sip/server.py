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
import logging
import random
import sys
import threading
import time

try:
    from src.debug import create_random_uuid
    from src.debug import dissect_packet
    from src.parser import convert_to_sip_packet
    from src.parser import parse_sip_packet
    from src.parser import validate_sip_signature
    from src.rtp.server import SynchronousRTPRouter
    from src.sip.gc import SynchronousSIPGarbageCollector
    from src.sip.static.busy import SIP_BUSY
    from src.sip.static.bye import SIP_BYE
    from src.sip.static.ok import SIP_OK
    from src.sip.static.options import SIP_OPTIONS
    from src.sip.static.ringing import SIP_RINGING
    from src.sip.static.terminated import SIP_TERMINATE
    from src.sip.static.trying import SIP_TRYING
    from src.sockets import unsafe_allocate_random_udp_socket
    from src.sockets import unsafe_allocate_udp_socket
except ImportError: raise

logger = logging.getLogger(__name__)

_SETTINGS = {} # `sipd.json`

# each worker should not instantiate a new garbage collector since a subsequent
# related requests can not guarantee to hit the same worker. Therefore, the
# workers should all use the same garbage collector and just register a new
# collection tasks to the collector queue.
_GC = SynchronousSIPGarbageCollector()

# SIP socket
#-------------------------------------------------------------------------------

def unsafe_allocate_sip_socket(port=5060, timeout=1.0):
    ''' allocate listening SIP socket that must be manually cleaned up.
    '''
    logger.debug('attempting to create SIP socket on port: %i.' % port)
    return unsafe_allocate_udp_socket(host='0.0.0.0', port=port, timeout=timeout, is_reused=True)

class safe_allocate_sip_socket(object):
    ''' allocate exception-safe listening SIP socket.
    '''
    def __init__(self, port=5060, timeout=1.0):
        self.port = port
        self.timeout = timeout
        self._socket = None

    def __enter__(self):
        self._socket = unsafe_allocate_sip_socket(self.port, self.timeout)
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
            global _SETTINGS
            _SETTINGS = setting
        logger.info('[sip] server initialized.')

class AsynchronousSIPServer(SIPServerPrototype):
    ''' Asynchronous SIP server implementation.
    '''
    def serve(self):
        # assign asynchronous handler to the receiving SIP port. Currently,
        # `asyncore` module was chosen in order to provide backward
        # compatibility with Python 2 (where there's no `asyncio`). All
        # incoming traffic is routed and initially handled by the router.
        try: sip_port = _SETTINGS['sip']['router']['port']
        except: sip_port = 5060 # udp
        with safe_allocate_sip_socket(port=sip_port) as sip_socket:
            sip_router = AsynchronousSIPRouter(sip_socket)
            asyncore.loop() # push events to the event loop.

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
            worker_size = _SETTINGS['sip']['worker']['count']
            assert worker_size > 0 # check for dynamic allocation.
            # if worker size is given, then normalize the count to not
            # exceed the available resources. After all, GIL only
            # permits only one active thread at a given time.
            self._worker_size = min(max(worker_size, 1), cpu_count())
        except:
            self._worker_size = 1 + int(cpu_count() * 0.32)
        logger.debug('[sip] router workers: %i.', self._worker_size)

        self._random = random.random # cache random number generator.

        # workers should never cause conflict with main server thread.
        # For that reason, each worker must exist as their own thread.
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
                work_delegated = True
                worker.event.clear()
                worker.assign(sip_endpoint, sip_message)
                break

# SIP worker
#-------------------------------------------------------------------------------

class SIPWorkerPrototype(object):
    ''' Asynchronous SIP worker component prototype.
    '''
    def __init__(self, worker_id, gc=None, verbose=False):
        self.verbose = verbose # display dissected packets.

        # each worker has its own designated identifier to distinguish one
        # from the another. The order in which a worker was assigned to its
        # thread is considered as an identifier.
        self.name = 'worker-' + str(worker_id)

        # each worker is managed by thead events. A worker is considered
        # "working" if its event is 'true' and "free" if 'false'.
        self.event = threading.Event()
        self.is_ready = lambda: not self.event.isSet()

        # each worker has its own socket to send data and a RTP router
        # to yield RTP server information to include inside SDP headers.
        self._socket = unsafe_allocate_random_udp_socket(is_reused=True)
        self._rtp_handler = SynchronousRTPRouter(_SETTINGS)

        # default SIP headers to override parsed requests and respond with.
        try: self._sip_defaults = _SETTINGS['sip']['defaults']
        except: self._sip_defaults = {}

        # if SIP server did not receive CANCEL/BYE due to unforseen error(s),
        # then we need absolute maximum time-to-live (ttl) value to force-expire
        # a call from RTP decoder. By default, all calls expire after one hour.
        try: self.lifetime = _SETTINGS['gc']['call_lifetime'] # seconds
        except: self.lifetime = 60 * 60

        # tag the current call to contextualize worker. A tag is in UUID format.
        self.tag = None

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

    def handle(self):
        ''' worker logic implementation.
        '''
        self.tag = create_random_uuid() # session tag.
        try:

            # error check.
            assert self.sip_endpoint and self.sip_message
            logger.debug("--->> [sip] [%s] <<%s>> received %s Bytes from [%s]." % (
                self.name, self.tag, hex(len(self.sip_message)), self.sip_endpoint))

            try: # check and parse message.
                assert validate_sip_signature(self.sip_message)
                sip_datagram = parse_sip_packet(self.sip_message)
            except:
                logger.error("----- [sip] [%s] <<%s>> UNABLE TO PARSE: '%s'." % (
                    self.name, self.tag, self.sip_message))
                return

            # override parsed values with pre-defined fields.
            call_id = sip_datagram['sip'].get('Call-ID')
            method  = sip_datagram['sip'].get('Method')
            for (x, y) in self._sip_defaults.items():
                sip_datagram['sip'][x] = y

            # INVITE
            #-------------------------------------------------------------------
            logger.debug('--->> [sip] [%s] <<%s>> <%s>' % (self.name, self.tag, method))
            if method == 'INVITE':
                self.__send_sip_trying(sip_datagram)

                # prepare proxy to RTP handler. RTP handler should send back port
                # information to begin receiving RTP traffic.
                try: chances = SERVER_SETTINGS['sip']['worker']['retry']
                except: chances = 1
                while chances:
                    if not self._rtp_handler: break

                    # contact RTP handler.
                    self.__send_sip_ringing(sip_datagram)
                    _sip_datagram = self._rtp_handler.handle(self.tag, sip_datagram)
                    if not _sip_datagram:
                        chances -= 1
                    else:
                        sip_datagram = _sip_datagram
                        break

                # create a deferred task and register to the garbage collection queue.
                # All task context is explained in SynchronousSIPGarbageCollector.
                def task_deferred(method, call_id):
                    if not _GC.membership.get(call_id):
                        # register new session to history.
                        _GC.calls_history[call_id] = None
                        _GC.calls_stats += (call_id in _GC.calls_history)
                        # register new session to membership.
                        _GC.membership[call_id] = {
                            'state': method,
                            'tags': [self.tag],
                            'tags_cnt': 1
                        }
                    else: # add session to existing membership.
                        _GC.membership[call_id]['tags'].append(self.tag)
                        _GC.membership[call_id]['tags_cnt'] += 1
                        _GC._garbage.append({
                            'Call-ID': call_id,
                            'ttl': self.lifetime + int(time.time()),
                            'tag': self.tag
                        })
                _GC.register_new_task(lambda:task_deferred(method, call_id))
                self.__send_sip_ok(sip_datagram)

            # BYE, CANCEL
            #-------------------------------------------------------------------
            elif method in ['BYE', 'CANCEL']:
                self.__send_sip_ok(sip_datagram)
                if not self._rtp_handler: pass
                else: # clean up existing sessions.
                    if method == 'CANCEL':
                        self._rtp_handler.handle(
                            sip_tag=self.tag,
                            sip_datagram=sip_datagram,
                            rtp_state='stop')
                    else:
                        _GC.gc_consume_membership(
                            call_tag=self.tag,
                            call_id=sip_datagram['sip']['Call-ID'],
                            forced=True)
                self.__send_sip_term(sip_datagram)

            # Default
            #-------------------------------------------------------------------
            else: self.__send_sip_ok(sip_datagram)

        # if anything goes wrong, relinquish work from worker for availability.
        except AssertionError: pass
        finally:
            self.sip_endpoint = self.sip_message = None
            self.event.clear()

    #
    # worker responses
    #

    def __send_sip_cancel(self, sip_datagram):
        ''' send SIP CANCEL to endpoint.
        '''
        logger.debug('<<--- [sip] [%s] <<%s>> <CANCEL>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_CANCEL, sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_ok(self, sip_datagram):
        ''' send SIP OK to endpoint.
        '''
        logger.debug('<<--- [sip] [%s] <<%s>> <OK>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_OK, sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_options(self, sip_datagram):
        ''' send SIP OPTIONS to endpoint.
        '''
        logger.debug('<<--- [sip] [%s] <<%s>> <OPTIONS>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_OPTIONS, sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_ringing(self, sip_datagram):
        ''' send SIP RINGING to endpoint.
        '''
        logger.debug('<<--- [sip] [%s] <<%s>> <RINGING>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_RINGING, sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_term(self, sip_datagram):
        ''' send SIP TERMINATE to endpoint.
        '''
        logger.debug('<<--- [sip] [%s] <<%s>> <TERM>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_TERMINATE, sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)

    def __send_sip_trying(self, sip_datagram):
        ''' send SIP TRYING to endpoint.
        '''
        logger.debug('<<--- [sip] [%s] <<%s>> <TRYING>' % (self.name, self.tag))
        sip_packet = convert_to_sip_packet(SIP_TRYING, sip_datagram)
        self._socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.tag)
