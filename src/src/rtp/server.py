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
# server.py -- synchronous external RTP routing module.
#-------------------------------------------------------------------------------

from src.parser import dump_json
from src.parser import parse_json
from src.rtp.start import RTPD_START
from src.rtp.stop import RTPD_STOP
from src.sockets import safe_allocate_random_udp_socket

import random

import logging
logger = logging.getLogger()

# RTP router
#-------------------------------------------------------------------------------

class RTPRouterPrototype(object):
    ''' RTP router prototype.
    '''
    def __init__(self, setting={}):
        self.setting = setting

        try: # load RTP handlers and filter by enabled handlers.
            self.rtp = filter(lambda rtp: rtp['enabled'], setting['rtp']['handler'])
            logger.debug('<rtp>: successfully loaded RTP configuration.')
        except:
            logger.error("<rtp>: failed to load RTP configuration: '%s'")
            self.rtp = None
        logger.debug('<rtp>: successfully initialized RTP handler.')

    def get_random_rtp_handler(self):
        return random.choice(self.rtp)

    def get_random_rtp_handler_address(self):
        handler = self.get_random_rtp_handler()
        try:
            server = (address, port) = str(handler['host']), int(handler['port'])
            logger.info('<rtp>: balancing to %s', server)
            return server
        except AttributeError:
            logger.error('<rtp>: no RTP is set to load from configuration.')
            return
        except KeyError:
            logger.error('<rtp>: failed to balance to a handler.')
            return

class SynchronousRTPRouter(RTPRouterPrototype):
    ''' RTP router implementation.
    '''
    def handle(self, datagram, action='start'):
        ''' `rttd` implementation.
        '''
        if not datagram:
            return
        # signal the external RTP decoder to open new ports.
        if action == 'start':
            return self.send_start_signal(datagram)
        else: # signal the external RTP decoder to close existing ports.
            call_id = datagram['sip']['Call-ID']
            return self.send_stop_signal(call_id)

    def send_start_signal(self, datagram):
        ''' request external RTP decoder to open new RTP proxy ports.
        '''
        if not datagram: return

        # populate external RTP template with existing data.
        template, rtpd_param = RTPD_START, ['Call-ID', 'X-Genesys-GVP-Session-ID']
        for key in rtpd_param: template[key] = datagram['sip'].get(key, '')

        with safe_allocate_random_udp_socket() as udp_socket:
            handler = self.get_random_rtp_handler_address()
            if not handler:
                return

            udp_socket.sendto(dump_json(template), handler)
            logger.debug("<<< <rtp>: requesting ports from '%s'", handler)
            logger.debug("<rtp>: waiting response from '%s'", handler)
            try:
                payload = udp_socket.recvfrom(0xff)
            except:
                logger.error("<rtp>: '%s' is down.", handler)
                return

            logger.debug("<rtp>: '%s' is up.", handler)
            rtpd_server, rtpd_payload = tuple(payload[1]), str(payload[0])
            logger.debug(">>> <rtp>: received %s Bytes from '%s'", hex(len(rtpd_payload)), handler)

            # receive RTP ports.
            rtpd_json = parse_json(rtpd_payload)
            logger.debug("<rtp>: parsed responses from '%s'", handler)

            # generate static SDP data.
            tx_port, rx_port = rtpd_json.get('TxPort'), rtpd_json.get('RxPort')
            logger.info('<rtp>: RxPort = %s', rx_port)
            logger.info('<rtp>: TxPort = %s', tx_port)
            server_address = self.setting['sip']['server']['address']

            # currently only delegates: G.711, G.729 encodings.
            static_sdp = [
                'v=0',
                's=phone-call',
                'c=IN IP4 %s' % handler[0], # host address
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

        # return original/updated sip datagram.
        return datagram

    def send_stop_signal(self, call_id):
        if not call_id:
            return

        # replace payload to send to external RTP decoder.
        template = RTPD_STOP
        template['Call-ID'] = call_id

        # allocate a temporary socket to send the payload.
        with safe_allocate_random_udp_socket() as udp_socket:
            handler = self.get_random_rtp_handler_address()
            if not handler:
                return

            udp_socket.sendto(dump_json(template), handler)
            logger.debug("<<< <rtp>: requesting 'stop' from '%s'", handler)
            logger.debug("<rtp>: waiting response from '%s'", handler)
            try:
                payload = udp_socket.recvfrom(0xff)
            except:
                logger.error("<rtp>: '%s' is down.", handler)
                return False

            logger.debug("<rtp>: '%s' is up.", handler)
            rtpd_server, rtpd_payload = tuple(payload[1]), str(payload[0])
            logger.debug(">>> <rtp>: received %s Bytes from '%s'", hex(len(rtpd_payload)), handler)

            rtpd_json = parse_json(rtpd_payload)
            logger.debug("<rtp>: parsed responses from '%s'", handler)
            status_code = rtpd_json.get('ResultCode')
            status_message = rtpd_json.get('Message')
            logger.info('<rtp>: ResultCode: %s', status_code)
            logger.info('<rtp>: Message: %s', status_message)

        # return original/updated sip datagram.
        return call_id
