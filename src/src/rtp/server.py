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
# server.py
#-------------------------------------------------------------------------------

import logging
import random

from src.parser import dump_json
from src.parser import parse_json
from src.rtp.start import RTPD_START
from src.rtp.stop import RTPD_STOP
from src.sockets import safe_allocate_random_udp_socket

logger = logging.getLogger()

class RTPRouter(object):
    ''' RTP router prototype.
    '''
    def __init__(self, setting={}):
        self.setting = setting
        self.handlers = filter(lambda handler: handler['enabled'], setting['rtp']['handler'])
        self.handler_port_mapping = {}
        logger.debug('<rtp>: successfully loaded RTP configuration.')
        logger.debug('<rtp>: successfully initialized RTP handler.')

    def get_random_handler_endpoint(self):
        ''' return random handler.
        '''
        return random.choice(self.handlers)

    def get_random_handler_address(self):
        ''' return random handler address.
        '''
        try:
            handler = self.get_random_handler_endpoint()
            server = (address, port) = handler['host'], int(handler['port'])
            logger.info('<rtp>: balancing packets to %s', server)
            return address
        except AttributeError:
            logger.error('<rtp>: no handler loaded from configuration.')
        except KeyError:
            logger.error('<rtp>: failed to balance to a handler.')
        return

class SynchronousRTPRouter(RTPRouter):
    ''' RTP router implementation.
    '''
    def handle(self, datagram, action='start'):
        '''
        @datagram<dict> -- SIP response datagram.
        @action<str> -- RTP handler action.
        '''
        if not datagram:
            return
        if action == 'start': # request external handler to open RX/TX ports.
            return self.send_start_signal(datagram=datagram)
        else: # request external handler to close RX/TX ports.
            call_id = datagram['sip'].get('Call-ID')
            return self.send_stop_signal(call_id=call_id)

    def send_start_signal(self, datagram):
        ''' request external handler to open RX/TX ports.
        @datagram<dict> -- SIP response datagram.
        '''
        if not datagram:
            return

        # populate RTP template with existing datagram data.
        template = RTPD_START
        params = ['Call-ID', 'X-Genesys-GVP-Session-ID']
        for param in params:
            template[param] = datagram['sip'].get(param, '')

        # request to receive RX/TX port information.
        with safe_allocate_random_udp_socket() as udp_socket:
            handler = self.get_random_handler_endpoint()
            endpoint = (handler.get('host'), int(handler.get('port')))
            if not all(endpoint):
                return

            udp_socket.sendto(dump_json(template), endpoint)
            logger.debug("<<< <rtp>: requesting ports from %s", endpoint)
            logger.debug("<rtp>: waiting response from %s", endpoint)
            try:
                data = udp_socket.recvfrom(0xff)
                logger.debug("<rtp>: %s is up.", endpoint)
                logger.debug(">>> <rtp>: received %s from %s", data, endpoint)
            except Exception as message:
                logger.error("<rtp>: %s is down: %s", endpoint, message)
                return

            # parse RX/TX ports.
            data = str(data[0])
            rxtx_ports = parse_json(data)

            # generate static SDP data.
            server_address = self.setting['sip']['server']['address']
            tx_port, rx_port = rxtx_ports.get('TxPort'), rxtx_ports.get('RxPort')
            logger.info('<rtp>: RxPort = %s', rx_port)
            logger.info('<rtp>: TxPort = %s', tx_port)
            static_sdp = [
                'v=0',
                's=phone-call',
                'c=IN IP4 %s' % endpoint[0], # address
                't=0 0',

                # [caller]
                'm=audio %s RTP/AVP 0 8 18 96' % tx_port,
                'a=rtpmap:0 PCMU/8000',
                'a=rtpmap:8 PCMA/8000',
                'a=rtpmap:18 G729/8000', # G729/8000
                'a=rtpmap:96 telephone-event/8000',
                'a=fmtp:96 0-15',
                'a=recvonly',
                'a=ptime:20',
                'a=maxptime:1000',

                # [agent]
                'm=audio %s RTP/AVP 0 8 18 96' % rx_port,
                'a=rtpmap:0 PCMU/8000',
                'a=rtpmap:8 PCMA/8000',
                'a=rtpmap:18 G729/8000', # G729/8000
                'a=rtpmap:96 telephone-event/8000',
                'a=fmtp:96 0-15',
                'a=recvonly',
                'a=ptime:20',
                'a=maxptime:1000'
            ]
            for sdp in static_sdp:
                datagram['sdp'].append(sdp)

        # store RX/TX ports to correctly close at 'stop' event.
        # TODO

        # return original/updated sip datagram.
        return datagram

    def send_stop_signal(self, call_id):
        ''' request external handler to close RX/TX ports.
        @call_id<str> -- SIP Call-ID.
        '''
        if not call_id:
            return

        # populate RTP template with existing datagram data.
        template = RTPD_STOP
        template['Call-ID'] = call_id

        # allocate a temporary socket to send the information.
        with safe_allocate_random_udp_socket() as udp_socket:
            handler = self.get_random_handler_endpoint()
            endpoint = (handler.get('host'), int(handler.get('port')))
            if not all(endpoint):
                return

            udp_socket.sendto(dump_json(template), endpoint)
            logger.debug("<<< <rtp>: requesting ports from %s", endpoint)
            logger.debug("<rtp>: waiting response from %s", endpoint)
            try:
                data = udp_socket.recvfrom(0xff)
                logger.debug("<rtp>: %s is up.", endpoint)
                logger.debug(">>> <rtp>: received %s from %s", data, endpoint)
            except Exception as message:
                logger.error("<rtp>: %s is down: %s", endpoint, message)
                return

            # parse response message.
            data = str(data[0])
            status_message = parse_json(data)
            status_code = status_message.get('ResultCode')
            status_message = status_message.get('Message')
            logger.info('<rtp>: ResultCode: %s', status_code)
            logger.info('<rtp>: Message: %s', status_message)
            return call_id
