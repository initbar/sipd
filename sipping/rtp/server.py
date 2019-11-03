# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

import logging
import random
import time

from src.parser import dump_json
from src.parser import parse_json
from src.rtp.start import RTPD_START
from src.rtp.stop import RTPD_STOP
from src.sockets import safe_allocate_random_udp_socket
from src.sockets import safe_allocate_udp_client

logger = logging.getLogger()


class RTPRouter(object):
    """ RTP router prototype.
    """

    def __init__(self, setting={}):
        self.setting = setting
        self.handlers = filter(  # filter by enabled routers.
            lambda handler: handler["enabled"], setting["rtp"]["handlers"]
        )

        # logging context
        self.context = ""
        logger.debug("<rtp>: successfully loaded RTP configuration.")
        logger.debug("<rtp>: successfully initialized RTP handler.")

    def get_random_handler(self):
        """ return random handler.
        """
        try:
            handler = random.choice(self.handlers)
        except IndexError:
            handler = None
        return handler

    def get_random_handler_address(self):
        """ return random handler address.
        """
        try:
            handler = self.get_random_handler()
            logger.info("%s <rtp>: balancing to %s", self.context, server)
            server = (address, port) = handler["host"], int(handler["port"])
            return address
        except AttributeError as error:
            logger.error("%s <rtp>: no handler enabled: %s", self.context, error)
        except KeyError as error:
            logger.error("%s <rtp>: no handler enabled: %s", self.context, error)


class SynchronousRTPRouter(RTPRouter):
    """ RTP router implementation.
    """

    def handle(self, datagram, action="start"):
        """
        @datagram<dict> -- SIP response datagram.
        @action<str> -- RTP handler action.
        """
        if not datagram:
            return
        if action == "start":  # request external handler to open RX/TX ports.
            return self.send_start_signal(datagram=datagram)
        else:  # request external handler to close RX/TX ports.
            call_id = datagram["sip"].get("Call-ID")
            return self.send_stop_signal(call_id=call_id)

    def send_start_signal(self, datagram):
        """ request external handler to open RX/TX ports.
        @datagram<dict> -- SIP response datagram.
        """
        if not datagram:
            return

        handler = self.get_random_handler()
        if not handler:
            logger.warning("<rtp>: all handlers are currently disabled.")
            return

        handler_endpoint = [handler.get("host"), int(handler.get("port"))]
        if not all(handler_endpoint):  # check for None.
            return
        elif handler_endpoint[0] == "127.0.0.1":  # resolve localhost.
            server_address = self.setting["sip"]["server"]["address"]
            handler_endpoint[0] = server_address
        handler_address = handler_endpoint[0]

        # populate RTP template with existing datagram data.
        template = RTPD_START
        params = ["Call-ID", "X-Genesys-GVP-Session-ID"]
        for param in params:
            template[param] = datagram["sip"].get(param, "")

        # request to receive RX/TX port information.
        json_template = dump_json(template)
        with safe_allocate_random_udp_socket() as udp_socket:
            udp_socket.sendto(json_template, tuple(handler_endpoint))
            logger.debug(
                "%s <<< <rtp>: requesting ports from %s", self.context, handler_endpoint
            )
            logger.debug(
                "%s <rtp>: waiting response from %s", self.context, handler_endpoint
            )
            try:
                socket_data = udp_socket.recvfrom(0xff)
                logger.debug("%s <rtp>: %s is up.", self.context, handler_endpoint)
                logger.debug(
                    "%s >>> <rtp>: received %s from %s",
                    self.context,
                    socket_data,
                    handler_endpoint,
                )
            except Exception as message:
                logger.error(
                    "%s <rtp>: %s is down: %s", self.context, handler_endpoint, message
                )
                return

        # parse RX/TX ports.
        rxtx_ports = str(socket_data[0])
        rxtx_ports = parse_json(rxtx_ports)

        # generate static SDP data.
        tx_port, rx_port = rxtx_ports.get("TxPort"), rxtx_ports.get("RxPort")
        logger.info("%s <rtp>: RxPort = %s", self.context, rx_port)
        logger.info("%s <rtp>: TxPort = %s", self.context, tx_port)
        static_sdp = [
            "o=- 0 0 IN IP4 %s" % handler_address,
            "v=0",
            "s=phone-call",
            "c=IN IP4 %s" % handler_address,
            "t=0 0",
            # [caller]
            "m=audio %s RTP/AVP 0 8 18 96" % tx_port,
            "a=rtpmap:0 PCMU/8000",
            "a=rtpmap:8 PCMA/8000",
            "a=rtpmap:18 G729/8000",  # G729/8000
            "a=rtpmap:96 telephone-event/8000",
            "a=fmtp:96 0-15",
            "a=recvonly",
            "a=ptime:20",
            "a=maxptime:1000",
            # [agent]
            "m=audio %s RTP/AVP 0 8 18 96" % rx_port,
            "a=rtpmap:0 PCMU/8000",
            "a=rtpmap:8 PCMA/8000",
            "a=rtpmap:18 G729/8000",  # G729/8000
            "a=rtpmap:96 telephone-event/8000",
            "a=fmtp:96 0-15",
            "a=recvonly",
            "a=ptime:20",
            "a=maxptime:1000",
        ]
        for sdp in static_sdp:
            datagram["sdp"].append(sdp)

        return datagram  # updated datagram.

    def send_stop_signal(self, call_id):
        """ request external handler to close RX/TX ports.
        @call_id<str> -- SIP Call-ID.
        """
        if not call_id:
            return
        # signal all handlers to remove Call-ID.
        template = RTPD_STOP
        template["Call-ID"] = call_id
        with safe_allocate_udp_client() as client:
            for handler in self.handlers:
                handler_endpoint = (handler["host"], int(handler["port"]))
                client.sendto(dump_json(template), handler_endpoint)
