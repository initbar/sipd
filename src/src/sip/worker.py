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

# from src.errors import SIPBrokenProtocol
# from src.sip.static.busy import SIP_BUSY
# from src.sip.static.bye import SIP_BYE
from src.debug import create_random_uuid
from src.optimizer import memcache
from src.parser import convert_to_sip_packet
from src.parser import parse_sip_packet
from src.parser import validate_sip_signature
from src.rtp.server import SynchronousRTPRouter
from src.sip.static.ok import SIP_OK
from src.sip.static.ok import SIP_OK_NO_SDP
from src.sip.static.options import SIP_OPTIONS
from src.sip.static.ringing import SIP_RINGING
from src.sip.static.terminated import SIP_TERMINATE
from src.sip.static.trying import SIP_TRYING
from src.sockets import unsafe_allocate_random_udp_socket

logger = logging.getLogger()

SIPTemplates = {
    'OK +SDP': SIP_OK,
    'OK -SDP': SIP_OK_NO_SDP,
    'OPTIONS': SIP_OPTIONS,
    'RINGING': SIP_RINGING,
    'TERMINATE': SIP_TERMINATE,
    'TRYING': SIP_TRYING
}

@memcache(size=1024)
def generate_sip_response(sip_datagram, sip_method):
    ''' generate SIP message payload.
    @sip_datagram<dict> -- SIP payload.
    @sip_method<str> -- SIP method.
    '''
    try:
        template = SIPTemplates[sip_method]
    except KeyError:
        template = SIPTemplates['OK -SDP'] # default
    return convert_to_sip_packet(template, sip_datagram)

def send_sip_response(socket, endpoint, sip_datagram, sip_method, tag=''):
    ''' generate and send SIP message payload.
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
    socket.sendto(sip_packet, endpoint)

class LazySIPWorker(object):
    ''' SIP worker implementation.
    '''
    def __init__(self,
                 name='',
                 settings=None,
                 gc=None):
        '''
        @settings<dict> -- `sipd.json`
        @gc<SynchronousSIPGarbageCollector> -- shared garbage collector.
        '''
        self.name = 'worker-' + str(name)
        self.settings = settings
        self.gc = gc
        self.socket = unsafe_allocate_random_udp_socket(is_reused=True)
        self.rtp = SynchronousRTPRouter(self.settings)
        if settings['db']['mysql']['enabled']:
            db_config = settings['db']['mysql']
            from src.db.mysql import MySQLClient
            self.db = MySQLClient(
                host=db_config['host'],
                port=db_config['port'],
                username=db_config['username'],
                password=db_config['password'],
                database=db_config['database']
            )
        else:
            self.db = None
        self.handlers = {
            'ACK': self.handle_ack,
            'BYE': self.handle_cancel,
            'CANCEL': self.handle_bye,
            'DEFAULT': self.handle_default,
            'INVITE': self.handle_invite
        }
        self.is_ready = True # recycle worker
        logger.info('<worker>:successfully initialized worker.')

    #
    # deferred garbage collection
    #

    def index_callid(self):
        ''' index new/existing Call-ID to garbage collector.
        '''
        try:
            lifetime = self.settings['gc']['call_lifetime']
            assert lifetime > 0
        except AssertionError:
            lifetime = 60 * 60 # seconds
        def deferred_index_callid():
            # register session to the garbage collection queue.
            self.gc._garbage.append({
                'Call-ID': self.call_id,
                'tag': self.tag,
                'ttl': lifetime + int(time.time())
            })
            # register the first unique Call-ID membership.
            if not self.gc.membership.get(self.call_id):
                self.gc.calls_history[self.call_id] = None
                self.gc.calls_stats += (self.call_id in self.gc.calls_history)
                self.gc.membership[self.call_id] = {
                    'state': self.method,
                    'tags': [self.tag],
                    'tags_cnt': 1
                }
            else: # register session only for existing Call-ID membership.
                self.gc.membership[self.call_id]['tags'].append(self.tag)
                self.gc.membership[self.call_id]['tags_cnt'] += 1
        self.gc.register_new_task(deferred_index_callid())

    #
    # worker state
    #

    def reset(self):
        ''' reset worker back to its initial state.
        '''
        self.__sip_endpoint =\
        self.__sip_datagram =\
        self.__call_id =\
        self.__method =\
        self.__tag = None
        self.is_ready = True

    #
    # custom handlers
    #

    def handle_default(self):
        ''' default response to non-indexed SIP methods.
        '''
        send_sip_response(self.socket,
                          self.sip_endpoint,
                          self.sip_datagram,
                          'OK -SDP', self.tag)

    def handle_ack(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.2
        '''
        pass

    def handle_bye(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.4
        '''
        send_sip_response(self.socket,
                          self.sip_endpoint,
                          self.sip_datagram,
                          'OK -SDP', self.tag)
        try:
            self.gc.register_new_task(
                lambda: self.gc.consume_membership(
                    call_tag=self.tag,
                    call_id=self.call_id,
                    forced=True))
        except AttributeError: # RTP is down.
            logger.error(' '.join([
                '<rtp>:<<%s>>',
                'RTP is down!'
            ]), self.tag)
        send_sip_response(self.socket,
                          self.sip_endpoint,
                          self.sip_datagram,
                          'TERMINATE', self.tag)

    def handle_cancel(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.5
        '''
        send_sip_response(self.socket,
                          self.sip_endpoint,
                          self.sip_datagram,
                          'OK -SDP', self.tag)
        try:
            self.rtp.handle(
                sip_tag=self.tag,
                sip_datagram=self.sip_datagram,
                rtp_state='stop')
        except AttributeError: # RTP is down.
            logger.error(' '.join([
                '<rtp>:<<%s>>',
                'RTP is down!'
            ]), self.tag)
        send_sip_response(self.socket,
                          self.sip_endpoint,
                          self.sip_datagram,
                          'TERMINATE', self.tag)

    def handle_invite(self):
        ''' https://tools.ietf.org/html/rfc2543#section-4.2.1
        '''
        # duplicate SIP INVITE is considered as HOLD.
        if self.call_id in self.gc.calls_history:
            logger.warning(' '.join([
                '<worker>:<<%s>>',
                'received duplicate Call-ID: %s'
            ]), self.tag, self.call_id)
            send_sip_response(self.socket,
                              self.sip_endpoint,
                              self.sip_datagram,
                              'OK -SDP', self.tag)
            return

        if not self.rtp:
            logger.error(' '.join([
                '<rtp>:<<%s>>',
                'RTP is down!'
            ]), self.tag)
            send_sip_response(self.socket,
                              self.sip_endpoint,
                              self.sip_datagram,
                              'OK -SDP', self.tag)
            return

        # try to receive RX/TX ports.
        send_sip_response(self.socket,
                          self.sip_endpoint,
                          self.sip_datagram,
                          'TRYING', self.tag)

        # RTP handler must reply with two ports to receive TX/RX RTP traffic.
        chances = max(1, self.settings['rtp'].get('max_retry', 1))
        while chances:
            send_sip_response(self.socket,
                              self.sip_endpoint,
                              self.sip_datagram,
                              'RINGING', self.tag)
            # if external RTP handler replies with one or more ports, rewrite
            # and update the SIP datagram with new SDP information to respond.
            sip_datagram = self.rtp.handle(self.tag, self.sip_datagram)
            if sip_datagram:
                send_sip_response(self.socket,
                                  self.sip_endpoint,
                                  sip_datagram,
                                  'OK +SDP', self.tag)
                self.sip_datagram = sip_datagram
                self.index_callid()
                break
            else:
                logger.warning('<worker>:RTP handler did not send RX/TX information.')
                send_sip_response(self.socket,
                                  self.sip_endpoint,
                                  sip_datagram,
                                  'OK -SDP', self.tag)
                chances -= 1

    #
    # worker interface
    #

    def handle(self, sip_endpoint, sip_message):
        ''' worker interface entrypoint.
        @sip_endpoint<tuple> -- SIP server endpoint address.
        @sip_message<str> -- SIP server socket buffer.
        '''
        if sip_endpoint and sip_message:
            self.sip_endpoint = sip_endpoint
            # self.sip_message = sip_message
        else:
            self.reset()
            return

        self.tag = create_random_uuid() # call session.
        if not validate_sip_signature(sip_message):
            logger.error(' '.join([
                '<worker>:<<%s>>',
                "INVALID SIP: '%s'"
            ]), self.tag, sip_message)
            self.reset()
            return

        self.sip_datagram = parse_sip_packet(sip_message)
        try: # override parsed SIP headers with default headers.
            self.call_id = self.sip_datagram['sip']['Call-ID']
            self.method = self.sip_datagram['sip']['Method']
        except KeyError:
            logger.error(' '.join([
                '<worker>:<<%s>>',
                'MALFORMED SIP: %s'
            ]), self.tag, sip_message)
            self.reset()
            return

        # load eligible SIP headers from the configuration.
        sip_headers = self.settings['sip']['worker']['headers']
        for (field, value) in sip_headers.items():
            self.sip_datagram['sip'][field] = value

        # set 'Contact' header for future SIP requests.
        server_address = self.settings['sip']['server']['address']
        self.sip_datagram['sip']['Contact'] = '<sip:%s:5060>' % server_address

        logger.debug(' '.join([ # print incoming SIP method.
            '\033[1m\33[35m>>>\033[00m',
            '<worker>:<<%s>>',
            '<\033[1m\033[31m%s\033[00m>'
        ]), self.tag, self.method)
        try: # responding to SIP requests.
            self.handlers[self.method]()
        except KeyError:
            self.handlers['DEFAULT']()
        finally:
            self.reset()
