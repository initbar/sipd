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

import logging

try:
    from src.debug import *
    from src.parser import *
    from src.rtp.start import RTPD_START
    from src.rtp.stop import RTPD_STOP
    from src.sockets import *
    import socket
except ImportError: raise

logger = logging.getLogger(__name__)

# RTP router
#-------------------------------------------------------------------------------

class RTPRouterPrototype(object):
    ''' RTP router prototype.
    '''
    def __init__(self, setting={}):
        self.setting = setting

        self.tag = None # session tag from worker.

        try: # configure handler.
            handler = self.setting['rtp']['handler']
            assert handler.get('enabled', False)
            self.host    = handler['host']
            self.port    = handler['port']
            self._server = tuple((self.host, self.port))
        except: pass
        logger.debug('[rtp] successfully initialized.')

    def handle(self, *args, **kwargs):
        return self._external_handler(*args, **kwargs)

    def _external_handler(self, sip_tag, sip_datagram, rtp_state='start'):
        raise NotImplementedError

class SynchronousRTPRouter(RTPRouterPrototype):
    ''' RTP router implementation.
    '''
    def _external_handler(self, sip_tag, sip_datagram, rtp_state='start'):
        ''' `rttd` implementation.
        '''
        if not sip_datagram: return
        self.tag = sip_tag

        # signal the external RTP decoder to open new ports.
        if rtp_state == 'start':
            return self.send_start_signal(sip_datagram)

        # signal the external RTP decoder to close existing ports.
        else:
            call_id = sip_datagram['sip'].get('Call-ID')
            return self.send_stop_signal(call_id)

    def send_start_signal(self, sip_datagram):
        ''' request external RTP decoder to open new RTP proxy ports.
        '''
        if not sip_datagram: return

        template = RTPD_START

        # replace payload to send to external RTP decoder.
        rtpd_param = ['Call-ID', 'X-Genesys-GVP-Session-ID']
        for key in rtpd_param:
            template[key] = sip_datagram['sip'].get(key, '')

        # allocate a temporary socket to send the payload.
        with safe_allocate_random_udp_socket() as udp_socket:
            udp_socket.sendto(dump_json(template), self._server)
            logger.info("<<--- [rtp] <<%s>> sent 'start' to external rtpd." % self.tag)
            logger.info("[rtp] <<%s>> waiting response from external rtpd." % self.tag)
            try: buffer = udp_socket.recvfrom(0xff)
            except Exception as message:
                logger.error('[rtp] <<%s>> external rtpd is DOWN: %s.' % (self.tag, str(message)))
                return

            logger.info('[rtp] <<%s>> external rtpd is UP.' % self.tag)
            rtpd_server, rtpd_payload = tuple(buffer[1]), str(buffer[0])
            logger.debug("--->> [rtp] <<%s>> [%s] received %s Bytes from external rtpd." % (
                self.tag, self._server, hex(len(rtpd_payload))))

            # receive RTP ports.
            rtpd_json = parse_json(rtpd_payload)
            logger.info("[rtp] <<%s>> parsed responses from external rtpd." % self.tag)

            # generate static SDP data.
            tx_port, rx_port = rtpd_json.get('TxPort'), rtpd_json.get('RxPort')
            logger.debug('[rtp] <<%s>> RxPort = %s' % (self.tag, rx_port))
            logger.debug('[rtp] <<%s>> TxPort = %s' % (self.tag, tx_port))
            host_address = self.setting['sip']['server']['address']

            # currently only delegates: G.711, G.729 encodings.
            static_sdp = [
                'v=0',
                's=phone-call',
                'c=IN IP4 %s' % host_address,
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
                sip_datagram['sdp'].append(sdp)

        # return original/updated sip datagram.
        return sip_datagram

    def send_stop_signal(self, call_id):
        if not call_id: return

        # replace payload to send to external RTP decoder.
        template = RTPD_STOP
        template['Call-ID'] = call_id

        # allocate a temporary socket to send the payload.
        with safe_allocate_random_udp_socket() as udp_socket:
            udp_socket.sendto(dump_json(template), self._server)
            logger.info("<<--- [rtp] <<%s>> sent 'stop' to external rtpd." % self.tag)
            logger.info("[rtp] <<%s>> waiting response from external rtpd." % self.tag)
            try: buffer = udp_socket.recvfrom(0xff)
            except Exception as message:
                logger.error('[rtp] <<%s>> external rtpd is DOWN: %s.' % (self.tag, str(message)))
                return False

            logger.info('[rtp] <<%s>> external rtpd is UP.' % self.tag)
            rtpd_server, rtpd_payload = tuple(buffer[1]), str(buffer[0])
            logger.debug("--->> [rtp] <<%s>> [%s] received %s Bytes from external rtpd." % (
                self.tag, self._server, hex(len(rtpd_payload))))

            rtpd_json = parse_json(rtpd_payload)
            logger.info("[rtp] <<%s>> parsed responses from external rtpd." % self.tag)
            status_code = rtpd_json.get('ResultCode')
            status_message = rtpd_json.get('Message')
            logger.debug('[rtp] <<%s>> ResultCode: %s' % (self.tag, status_code))
            logger.debug('[rtp] <<%s>> Message: %s' % (self.tag, status_message))

        # return original/updated sip datagram.
        return call_id
