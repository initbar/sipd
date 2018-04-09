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
# worker.py -- asynchronous SIP worker module.
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

from src.debug import create_random_uuid
from src.errors import SIPBrokenProtocol
from src.parser import convert_to_sip_packet
from src.parser import parse_sip_packet
from src.parser import validate_sip_signature
from src.rtp.server import SynchronousRTPRouter
from src.sip.static.busy import SIP_BUSY
from src.sip.static.bye import SIP_BYE
from src.sip.static.ok import SIP_OK
from src.sip.static.ok import SIP_OK_NO_SDP
from src.sip.static.options import SIP_OPTIONS
from src.sip.static.ringing import SIP_RINGING
from src.sip.static.terminated import SIP_TERMINATE
from src.sip.static.trying import SIP_TRYING
from src.sockets import unsafe_allocate_random_udp_socket

import threading
import time

import logging
logger = logging.getLogger(__name__)

# SIP worker prototype
#-------------------------------------------------------------------------------

class SIPWorkerPrototype(object):
    ''' Asynchronous SIP worker component prototype.
    '''
    def __init__(self,
                 worker_id,
                 settings={},
                 gc=None,
                 verbose=False):
        self.name = 'worker-' + worker_id
        self.verbose = verbose

        self.__settings = settings
        self.__garbage  = gc

        # a worker is considered to be "working" if its' threading event is set.
        self.__event = threading.Event()
        self.is_ready = lambda: not self.__event.isSet()
        self.is_busy  = lambda: not self.is_ready()

        # a worker has its own handling socket and a RTP handler.
        self.__socket = unsafe_allocate_random_udp_socket(is_reused=True)
        self.__rtp_handler = SynchronousRTPRouter(settings)

        try: # load any SIP headers from setting.
            self.sip_headers = settings['sip']['worker']['headers']
        except:
            logger.warning('[sip] failed to parse sip headers setting.')
            self.sip_headers = {}
        logger.info('[sip] sip defaults: %s' % self.sip_headers)

        try: # load call lifetime from setting.
            self.lifetime = settings['gc']['call_lifetime'] # seconds
        except:
            logger.warning('[sip] failed to parse sip lifetime setting.')
            self.lifetime = 60 * 60
        logger.info('[sip] call lifetime: %s' % self.lifetime)

        self.__sip_endpoint = self.__sip_message = None # "work"

        # handler configuration.
        self.handlers = {
            'ACK':     self.handler_ack,
            'BYE':     self.handler_cancel,
            'CANCEL':  self.handler_bye,
            'DEFAULT': self.handler_default,
            'INVITE':  self.handler_invite
        }

# SIP worker implementation
#-------------------------------------------------------------------------------

class SynchronousSIPWorker(SIPWorkerPrototype):
    ''' Asynchronous SIP worker component implementation.
    '''
    def __init__(self, *args, **kwargs):
        super(SynchronousSIPWorker, self).__init__(*args, **kwargs)
        logger.debug("[sip] '%s' initialized." % self.name)

    @property
    def sip_endpoint(self):
        return self.__sip_endpoint

    @sip_endpoint.setter
    def sip_endpoint(self, endpoint):
        self.__sip_endpoint = endpoint

    @property
    def sip_message(self):
        return self.__sip_message

    @sip_message.setter
    def sip_message(self, message):
        self.__sip_message = message

    def assign(self, sip_endpoint, sip_message=None):
        ''' assign a worker with "work".
        '''
        if sip_endpoint and sip_message:
            self.sip_endpoint = sip_endpoint
            self.sip_message  = sip_message
            self.__event.set() # worker is now assigned.
            self.handle() # worker hook to force work.

    def cleanup(self):
        ''' relinquish a worker from "work".
        '''
        self.sip_endpoint = self.sip_message = None
        self.__event.clear()

    #
    # handler interface
    #

    def handle(self):
        self.__tag = create_random_uuid() # call context.

        try: # check that worker has valid work assignment.
            assert self.sip_endpoint and self.sip_message
            if not validate_sip_signature(self.sip_message):
                raise SIPBrokenProtocol
            self.__sip_datagram = parse_sip_packet(self.sip_message)

        # instead of error correction, relinquish the work from worker so that
        # it can move on to the next future task.
        except SIPBrokenProtocol:
            logger.error("---- [sip] [%s] <<%s>> PARSE FAILED: '%s'" % (self.name,
                                                                        self.__tag,
                                                                        self.sip_message))
            logger.warning('---- [sip] [%s] prematurely relinquishing work.' % self.name)
            return self.cleanup()
        except:
            logger.warning('---- [sip] [%s] prematurely relinquishing work.' % self.name)
            return self.cleanup()

        try: # override parsed SIP headers with default headers.
            self.__call_id = self.__sip_datagram['sip'].get('Call-ID')
            self.__method  = self.__sip_datagram['sip'].get('Method')
        except:
            logger.error('---- [sip] malformed packet: %s' % self.__sip_datagram)
            logger.warning('---- [sip] [%s] prematurely relinquishing work.' % self.name)
            return self.cleanup()

        for (field, value) in self.sip_headers.items():
            self.__sip_datagram['sip'][field] = value

        logger.debug('-->> [sip] [%s] <<%s>> <%s>' % (self.name, self.__tag, self.__method))
        self.handlers.get(self.__method, 'DEFAULT')()
        self.cleanup()

    #
    # handler implementation
    #

    def handler_default(self):
        self.__send_sip_ok_no_sdp()

    def handler_ack(self):
        pass

    def handler_bye(self):
        self.__send_sip_ok_no_sdp()
        if self.__rtp_handler:
            self.__garbage.register_new_task(
                lambda: self.__garbage.consume_membership(
                    call_tag=self.__tag,
                    call_id=self.__call_id,
                    forced=True))
        self.__send_sip_term()

    def handler_cancel(self):
        self.__send_sip_ok_no_sdp()
        if self.__rtp_handler:
            self.__rtp_handler.handle(
                sip_tag=self.__tag,
                sip_datagram=self.__sip_datagram,
                rtp_state='stop')
        self.__send_sip_term()

    def handler_invite(self):
        # TODO: decide to delegate to another server.
        logger.debug('---- [sip] deciding to load balance to another server..')
        self.__sip_datagram['sip']['Contact'] = '<sip:%s:5060>' % self.__settings['sip']['server']['address']
        logger.debug('---- [sip] balancing to node: %s' % self.__sip_datagram['sip']['Contact'])

        # if duplicate INVITE message was received with same Call-ID, then it's
        # necessary to ignore the future duplicates.
        if self.__call_id in self.__garbage.calls_history:
            logger.warning('---- [sip] received duplicate Call-ID: %s' % self.__call_id)
            # TODO: consider this as HOLD.
            self.__send_sip_ok_no_sdp()
            return
        elif not self.__rtp_handler:
            logger.error('---- [sip] external RTP handler is not configured.')
            self.__send_sip_ok_no_sdp()
            return
        else:
            self.__send_sip_trying()

        # prepare RTP delegation. An external RTP handler must reply with two
        # ports to receive TX/RX RTP traffic.
        try: chances = max(1, self.__settings['rtp']['max_retry'])
        except: chances = 1
        while chances:
            self.__send_sip_ringing()
            chances -= 1

            # if external RTP handler replies with one or more ports, rewrite
            # and update the SIP datagram with new SDP information.
            sip_datagram = self.__rtp_handler.handle(self.__tag, self.__sip_datagram)
            if sip_datagram:
                self.__sip_datagram = sip_datagram
                break

        # add deferred to self.__garbage queue to linearly task demultiplexed jobs.
        self.__index_callid()
        self.__send_sip_ok()

    #
    # deferred tasks
    #

    def __index_callid(self):
        ''' index new/existing Call-ID to garbage collector.
        '''
        def deferred_index_callid():
            # register session to the garbage collection queue.
            self.__garbage._garbage.append({
                'Call-ID': self.__call_id,
                'tag': self.__tag,
                'ttl': self.lifetime + int(time.time())
            })
            # register the first unique Call-ID membership.
            if self.__garbage.membership.get(self.__call_id) == None:
                self.__garbage.calls_history[self.__call_id] = None
                self.__garbage.calls_stats += (self.__call_id in self.__garbage.calls_history)
                self.__garbage.membership[self.__call_id] = {
                    'state': self.__method,
                    'tags': [self.__tag],
                    'tags_cnt': 1
                }
            # register session only for existing Call-ID membership.
            else:
                self.__garbage.membership[self.__call_id]['tags'].append(self.__tag)
                self.__garbage.membership[self.__call_id]['tags_cnt'] += 1
        self.__garbage.register_new_task(lambda: deferred_index_callid())

    #
    # worker responses
    #

    def __send_sip_cancel(self):
        ''' send SIP CANCEL to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <CANCEL>' % (self.name, self.__tag))
        sip_packet = convert_to_sip_packet(SIP_CANCEL, self.__sip_datagram)
        self.__socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.__tag)

    def __send_sip_ok(self):
        ''' send SIP OK to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <OK +SDP>' % (self.name, self.__tag))
        sip_packet = convert_to_sip_packet(SIP_OK, self.__sip_datagram)
        self.__socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.__tag)

    def __send_sip_ok_no_sdp(self):
        logger.debug('<<-- [sip] [%s] <<%s>> <OK -SDP>' % (self.name, self.__tag))
        sip_packet = convert_to_sip_packet(SIP_OK_NO_SDP, self.__sip_datagram)
        self.__socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.__tag)

    def __send_sip_options(self):
        ''' send SIP OPTIONS to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <OPTIONS>' % (self.name, self.__tag))
        sip_packet = convert_to_sip_packet(SIP_OPTIONS, self.__sip_datagram)
        self.__socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.__tag)

    def __send_sip_ringing(self):
        ''' send SIP RINGING to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <RINGING>' % (self.name, self.__tag))
        sip_packet = convert_to_sip_packet(SIP_RINGING, self.__sip_datagram)
        self.__socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.__tag)

    def __send_sip_term(self):
        ''' send SIP TERMINATE to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <TERM>' % (self.name, self.__tag))
        sip_packet = convert_to_sip_packet(SIP_TERMINATE, self.__sip_datagram)
        self.__socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.__tag)

    def __send_sip_trying(self):
        ''' send SIP TRYING to endpoint.
        '''
        logger.debug('<<-- [sip] [%s] <<%s>> <TRYING>' % (self.name, self.__tag))
        sip_packet = convert_to_sip_packet(SIP_TRYING, self.__sip_datagram)
        self.__socket.sendto(sip_packet, self.sip_endpoint)
        if self.verbose: dissect_packet(sip_packet, self.__tag)
