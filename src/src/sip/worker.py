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

# -------------------------------------------------------------------------------
# worker.py
# -------------------------------------------------------------------------------

import copy
import logging
import socket
import time

from src.debug import create_random_uuid
from src.debug import md5sum
from src.optimizer import memcache
from src.parser import convert_to_sip_packet
from src.parser import dump_json
from src.parser import parse_address
from src.parser import parse_sip_packet
from src.parser import validate_sip_signature
from src.rtp.server import SynchronousRTPRouter
from src.sip.static.ok import SIP_OK
from src.sip.static.ok import SIP_OK_NO_SDP
from src.sip.static.options import SIP_OPTIONS
from src.sip.static.ringing import SIP_RINGING
from src.sip.static.terminated import SIP_TERMINATE
from src.sip.static.trying import SIP_TRYING
from src.sockets import safe_allocate_tcp_client
from src.sockets import safe_allocate_udp_client
from src.sockets import unsafe_allocate_random_udp_socket

# custom logger
# -------------------------------------------------------------------------------


class ContextLogger(object):
    """ custom logger with call context.
    """

    def __init__(self, logger):
        self.log = logger
        self.fmt = "%s %s"
        self.context = "none"

    def refresh(self):
        """ generate random context string.
        """
        self.context = md5sum(create_random_uuid())[:8]  # first 8 Bytes only.

    def critical(self, *a, **kw):
        try:
            string = a[0] % a[1:]
        except:
            string = a
        fmt = "%s \033[91m%s\033[0m"
        self.log.critical(fmt % (self.context, string))

    def debug(self, *a, **kw):
        try:
            string = a[0] % a[1:]
        except:
            string = a
        self.log.debug(self.fmt % (self.context, string))

    def error(self, *a, **kw):
        try:
            string = a[0] % a[1:]
        except:
            string = a
        fmt = "%s \033[91m%s\033[0m"
        self.log.error(fmt % (self.context, string))

    def info(self, *a, **kw):
        try:
            string = a[0] % a[1:]
        except:
            string = a
        self.log.info(self.fmt % (self.context, string))

    def warning(self, *a, **kw):
        try:
            string = a[0] % a[1:]
        except:
            string = a
        fmt = "%s \033[91m%s\033[0m"
        self.log.warning(fmt % (self.context, string))


logger = ContextLogger(logging.getLogger())

# SIP responses
# -------------------------------------------------------------------------------

SIPTemplates = {
    "DEFAULT": SIP_OK_NO_SDP,
    "OK +SDP": SIP_OK,
    "OK -SDP": SIP_OK_NO_SDP,
    "OPTIONS": SIP_OPTIONS,
    "RINGING": SIP_RINGING,
    "TERMINATE": SIP_TERMINATE,
    "TRYING": SIP_TRYING,
}

SIPColors = {
    "+++": "\033[01m\033[35m+++\033[0m",  # bold, purple, reset
    ">>>": "\033[01m\033[32m>>>\033[0m",  # bold, green, reset
    "<<<": "\033[01m\033[91m<<<\033[0m",  # bold, yellow, reset
}


@memcache(size=32)
def generate_response(method, datagram):
    """ memcached SIP message generator.
    @datagram<dict> -- SIP response datagram.
    @method<str> -- SIP response method.
    """
    return convert_to_sip_packet(
        template=SIPTemplates.get(method, SIPTemplates["DEFAULT"]), datagram=datagram
    )


def send_response(shared_socket, endpoint, datagram, method):
    """ SIP message response sender.
    @shared_socket<socket> -- shared UDP socket.
    @endpoint<tuple> -- server endpoint address.
    @datagram<dict> -- parsed SIP datagram.
    @method<str> -- SIP method.
    """
    if not endpoint:
        logger.error("<worker>: unable to send response due to empty endpoint.")
        return
    # generate response and send to the endpoint.
    response = generate_response(method, datagram)
    logger.info("%s <worker>: [\033[01m\033[91m%s\033[0m]", SIPColors["<<<"], method)
    logger.debug("%s <worker>: sent to %s\n%s", SIPColors["<<<"], endpoint, response)
    try:
        shared_socket.sendto(response, endpoint)
    except Exception as message:
        logging.error("<worker>: failed to send using shared socket: %s", message)
        try:  # close shared socket and re-create another one later.
            shared_socket.close()
            shared_socket = None  # unset to re-initialize at next iteration.
        except AttributeError:
            pass
        # temporarily allocate an udp client to send data.
        logging.info("<worker>: using backup client-socket to send response.")
        with safe_allocate_udp_client() as client:
            client.sendto(response, endpoint)


# SIP worker
# -------------------------------------------------------------------------------


class LazyWorker(object):
    """ worker implementation.
    """

    def __init__(self, name=None, settings=None, gc=None):
        """
        @name<str> -- worker name.
        @settings<dict> -- `sipd.json`
        @gc<SynchronousGarbageCollector> -- shared garbage collector.
        """
        if name is None:
            self.name = "temp-%s" % create_random_uuid()[:4]
        else:
            self.name = "worker-" + str(name)

        self.settings = settings
        self.gc = gc

        self.socket = None  # lazy initialize.
        self.rtp = None  # lazy initialize.
        self.handlers = {
            "DEFAULT": self.handle_default,
            "ACK": self.handle_ack,
            "BYE": self.handle_bye,
            "CANCEL": self.handle_cancel,
            "INVITE": self.handle_invite,
        }

        self.is_ready = True  # recyclable state.
        logger.debug("<worker>: successfully initialized %s.", self.name)

    def reset(self):
        """ reset worker.
        """
        self.call_id = self.datagram = self.endpoint = self.method = None
        self.is_ready = True

    def handle(self, message, endpoint):
        """ worker logic.
        @message<str> -- worker "work".
        @endpoint<tuple> -- worker response endpoint.
        """
        self.is_ready = False  # woker is busy.
        logger.refresh()  # create new context.

        if not message or not endpoint:
            logger.warning("<worker>: reset from incomplete work assignment.")
            self.reset()
            return
        else:  # prepare worker.
            self.endpoint = endpoint
            # self.message = message
            if self.socket is None:
                self.socket = unsafe_allocate_random_udp_socket(is_reused=True)
            if self.rtp is None:
                self.rtp = SynchronousRTPRouter(self.settings)
        self.rtp.context = logger.context

        # validate work.
        if not validate_sip_signature(message):
            logger.warning("<worker>: reset from invalid signature: '%s'", message)
            self.reset()
            return
        self.datagram = parse_sip_packet(message)
        try:  # override parsed headers with loaded headers.
            self.call_id = self.datagram["sip"]["Call-ID"]
            self.method = self.datagram["sip"]["Method"]
            logger.info("%s <worker>: reference %s", SIPColors[">>>"], self.call_id)
        except KeyError:
            logger.warning("<worker>: reset from invalid format: '%s'", message)
            self.reset()
            return

        # load eligible SIP headers from the configuration.
        sip_headers = self.settings["sip"]["worker"]["headers"]
        for (field, value) in sip_headers.items():
            try:
                self.datagram["sip"][field] = value
            except TypeError:
                logger.error("<worker>: unable to use header: %s %s", field, value)

        # set 'Contact' response header to delegate future messages.
        server_address = self.settings["sip"]["server"]["address"]  # server address.
        self.datagram["sip"]["Contact"] = (
            "<sip:SIPd@%s:5060;transport=udp>" % server_address
        )

        logger.info(
            "%s <worker>: [\033[01m\033[91m%s\033[0m]", SIPColors[">>>"], self.method
        )
        logger.debug(
            "%s <worker>: received from %s\n%s", SIPColors[">>>"], endpoint, message
        )
        self.handlers.get(self.method, self.handlers["DEFAULT"])()
        self.reset()

    #
    # custom handlers
    #

    def handle_default(self):
        send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")

    def handle_ack(self):
        pass

    def handle_bye(self):
        send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
        send_response(self.socket, self.endpoint, self.datagram, "TERMINATE")
        self.gc.revoke(call_id=self.call_id)

    def handle_cancel(self):
        send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
        try:
            self.rtp.handle(datagram=self.datagram, action="stop")
        except AttributeError as error:
            logger.error("<rtp>:RTP handler is down: %s", error)
            self.rtp = None  # unset to re-initialize at next iteration.
        send_response(self.socket, self.endpoint, self.datagram, "TERMINATE")

    def handle_invite(self):
        if self.call_id in self.gc.calls.history:
            logger.warning("<worker>: detected duplicate Call-ID: %s", self.call_id)
            send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
            return
        # receive TX/RX ports to delegate RTP packets.
        send_response(self.socket, self.endpoint, self.datagram, "TRYING")
        max_retry = max(1, self.settings["rtp"].get("max_retry", 1))
        for _ in range(max_retry, 0, -1):
            send_response(self.socket, self.endpoint, self.datagram, "RINGING")
            # if external RTP handler replies with one or more ports, rewrite
            # and update the existing datagram with new information and respond.
            datagram = None
            try:
                datagram = self.rtp.handle(datagram=self.datagram)
            except AttributeError as error:
                logger.error("<rtp>:RTP handler is down: %s", error)
                self.rtp = None  # unset to re-initialize at next iteration.
            if datagram:
                self.datagram = datagram
                send_response(self.socket, self.endpoint, self.datagram, "OK +SDP")
                break
            else:
                logger.warning("<worker>: RTP handler did not send RX/TX ports.")
                send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
        try:
            self.gc.register(call_id=self.call_id)
            self.send_to_db_interface()
        except:
            pass

    def send_to_db_interface(self):
        """ send datagram to db interface.
        """
        db = self.settings["db"]
        if not db.get("enabled"):
            return
        db_host, db_port = db["host"], int(db["port"])
        db_username = db["username"]
        db_password = db["password"]
        with safe_allocate_tcp_client(host=db_host, port=db_port) as client:
            datagram = copy.deepcopy(self.datagram)
            datagram["user"] = db_username
            datagram["pass"] = db_password
            client.sendall(dump_json(datagram))
            logger.info("<worker>: sent metadata to remote database.")
