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
# worker.py
#-------------------------------------------------------------------------------

import logging
import time

from src.db.mysql import MySQLClient
from src.debug import create_random_uuid
# from src.errors import SIPBrokenProtocol
from src.optimizer import memcache
from src.parser import convert_to_sip_packet
from src.parser import parse_sip_packet
from src.parser import validate_sip_signature
from src.rtp.server import SynchronousRTPRouter
# from src.sip.static.busy import SIP_BUSY
# from src.sip.static.bye import SIP_BYE
from src.sip.static.ok import SIP_OK
from src.sip.static.ok import SIP_OK_NO_SDP
from src.sip.static.options import SIP_OPTIONS
from src.sip.static.ringing import SIP_RINGING
from src.sip.static.terminated import SIP_TERMINATE
from src.sip.static.trying import SIP_TRYING
from src.sockets import safe_allocate_udp_client

logger = logging.getLogger()

SIPTemplates = {
    'OK -SDP': SIP_OK_NO_SDP,
    'OK +SDP': SIP_OK,
    'OPTIONS': SIP_OPTIONS,
    'RINGING': SIP_RINGING,
    'TERMINATE': SIP_TERMINATE,
    'TRYING': SIP_TRYING
}

@memcache(size=1024)
def generate_sip_response(sip_datagram, sip_method):
    ''' generate SIP message.
    @sip_datagram<dict> -- SIP payload.
    @sip_method<str> -- SIP method.
    '''
    try:
        template = SIPTemplates[sip_method]
    except KeyError:
        template = SIPTemplates['OK -SDP'] # default
    sip_packet = convert_to_sip_packet(template, sip_datagram)
    return sip_packet

def send_sip_response(endpoint, sip_datagram, sip_method, tag=''):
    ''' generate SIP message.
    @endpoint<tuple> -- SIP server endpoint address.
    @sip_datagram<dict> -- SIP payload.
    @sip_method<str> -- SIP method.
    @tag<str> -- call context tag.
    '''
    logger.debug(' '.join([
        '\033[93m\033[01m<<<\033[00m',
        '<worker>:<<%s>>',
        '<\033[1m\033[31m%s\033[00m>'
    ]), tag, sip_method)

    # generate response and send to the SIP server.
    sip_packet = generate_sip_response(sip_datagram, sip_method)
    with safe_allocate_udp_client() as client:
        client.sendto(sip_packet, endpoint)

class LazySIPWorker(object):
    ''' SIP worker implementation.
    '''
    def __init__(self,
                 settings=None,
                 gc=None):
        '''
        @settings<dict> -- `sipd.json`
        @gc<SynchronousSIPGarbageCollector> -- shared garbage collector.
        '''
        self.settings = settings
        self.__garbage = gc

        self.handlers = {
            'ACK': self.handle_ack,
            'BYE': self.handle_cancel,
            'CANCEL': self.handle_bye,
            'DEFAULT': self.handle_default,
            'INVITE': self.handle_invite
        }

        self.rtp_handler = None # initialize only when handle is called.

        # worker state
        self.is_ready = True
        logger.info("<worker>:successfully initialized worker.")

    def reset(self):
        ''' reset worker back to its initial state.
        '''
        self.__sip_endpoint =\
        self.__sip_datagram =\
        self.__call_id =\
        self.__method =\
        self.__tag = None
        self.is_ready = True

    def handle(self, sip_endpoint, sip_message):
        ''' worker handler.
        @sip_endpoint<tuple> -- SIP server endpoint address.
        @sip_message<str> -- SIP server socket buffer.
        '''
        if sip_endpoint and sip_message:
            self.__sip_endpoint = sip_endpoint
            # self.sip_message = sip_message
            self.is_ready = False
        else:
            self.reset()
            return

        self.__tag = create_random_uuid() # call context.
        if not validate_sip_signature(sip_message):
            logger.error("<worker>:<<%s>> INVALID SIP: '%s'", self.__tag, sip_message)
            logger.warning('<worker>:<<%s>> unassigning worker.', self.__tag)
            self.reset()
            return

        self.__sip_datagram = parse_sip_packet(sip_message)
        try: # override parsed SIP headers with default headers.
            self.__call_id = self.__sip_datagram['sip']['Call-ID']
            self.__method = self.__sip_datagram['sip']['Method']
        except KeyError:
            logger.error('<worker>:<<%s>> MALFORMED SIP: %s', self.__tag, sip_message)
            logger.warning('<worker>:<<%s>> unassigning worker.', self.__tag)
            self.reset()
            return

        # add eligible SIP headers from `sipd.json`.
        sip_headers = self.settings['sip']['worker']['headers']
        for (field, value) in sip_headers.items():
            self.__sip_datagram['sip'][field] = value

        logger.debug(' '.join([ # print incoming SIP method.
            '\033[1m\33[35m>>>\033[00m',
            '<worker>:<<%s>>',
            '<\033[1m\033[31m%s\033[00m>'
        ]), self.__tag, self.__method)

        # set 'Contact' header for future SIP requests.
        server_address = self.settings['sip']['server']['address']
        self.__sip_datagram['sip']['Contact'] = '<sip:%s:5060>' % server_address

        if not self.rtp_handler: # lazy initialize RTP handler.
            self.rtp_handler = SynchronousRTPRouter(self.settings)
        try:
            self.handlers[self.__method]()
        except KeyError:
            self.handlers['DEFAULT']()
        finally:
            self.reset()

    #
    # custom handlers
    #

    def handle_default(self):
        send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'OK -SDP', self.__tag)

    def handle_ack(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.2
        '''
        pass

    def handle_bye(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.4
        '''
        send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'OK -SDP', self.__tag)
        if self.rtp_handler:
            self.__garbage.register_new_task(
                lambda: self.__garbage.consume_membership(
                    call_tag=self.__tag,
                    call_id=self.__call_id,
                    forced=True))
        send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'TERMINATE', self.__tag)

    def handle_cancel(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.5
        '''
        send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'OK -SDP', self.__tag)
        if self.rtp_handler:
            self.rtp_handler.handle(
                sip_tag=self.__tag,
                sip_datagram=self.__sip_datagram,
                rtp_state='stop')
        send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'TERMINATE', self.__tag)

    def handle_invite(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.1
        '''
        # duplicate SIP INVITE is considered as HOLD.
        if self.__call_id in self.__garbage.calls_history:
            logger.warning('<worker>:<<%s>> received duplicate Call-ID: %s', self.__tag, self.__call_id)
            return send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'OK -SDP', self.__tag)

        elif not self.rtp_handler:
            logger.error('<worker>:<<%s>> RTP handler is not configured.', self.__tag)
            return send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'OK -SDP', self.__tag)

        send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'TRYING', self.__tag)

        # RTP handler must reply with two ports to receive TX/RX RTP traffic.
        chances = max(1, self.settings['rtp'].get('max_retry', 1))
        while chances:
            send_sip_response(self.__sip_endpoint, self.__sip_datagram, 'RINGING', self.__tag)
            chances -= 1
            # if external RTP handler replies with one or more ports, rewrite
            # and update the SIP datagram with new SDP information to respond.
            sip_datagram = self.rtp_handler.handle(self.__tag, self.__sip_datagram)
            if sip_datagram:
                send_sip_response(self.__sip_endpoint, sip_datagram, 'OK +SDP', self.__tag)
                self.__sip_datagram = sip_datagram
                self.__index_callid()
                break
            else:
                logger.warning('<worker>:RTP handler did not send RX/TX information.')
                send_sip_response(self.__sip_endpoint, sip_datagram, 'OK -SDP', self.__tag)

    #
    # deferred tasks
    #

    def __index_callid(self):
        ''' index new/existing Call-ID to garbage collector.
        '''
        try:
            lifetime = self.settings['gc']['call_lifetime']
            assert lifetime > 0
        except AssertionError:
            lifetime = 60 * 60 # seconds
        def deferred_index_callid():
            # register session to the garbage collection queue.
            self.__garbage._garbage.append({
                'Call-ID': self.__call_id,
                'tag': self.__tag,
                'ttl': lifetime + int(time.time())
            })
            # register the first unique Call-ID membership.
            if not self.__garbage.membership.get(self.__call_id):
                self.__garbage.calls_history[self.__call_id] = None
                self.__garbage.calls_stats += (self.__call_id in self.__garbage.calls_history)
                self.__garbage.membership[self.__call_id] = {
                    'state': self.__method,
                    'tags': [self.__tag],
                    'tags_cnt': 1
                }
            else: # register session only for existing Call-ID membership.
                self.__garbage.membership[self.__call_id]['tags'].append(self.__tag)
                self.__garbage.membership[self.__call_id]['tags_cnt'] += 1
        self.__garbage.register_new_task(deferred_index_callid())
