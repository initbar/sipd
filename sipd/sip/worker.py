# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from __future__ import absolute_import
from abc import abstractmethod
from abc import abstractproperty

import attr
import copy
import logging
import multiprocessing
import socket
import time

from lib.coroutine import coroutine

# from src.debug import create_random_uuid
# from src.debug import md5sum
# from src.optimizer import memcache
# from src.parser import convert_to_sip_packet
# from src.parser import dump_json
# from src.parser import parse_address
# from src.parser import parse_sip_packet
# from src.parser import validate_sip_signature
# from src.rtp.server import SynchronousRTPRouter
# from src.sip.static.ok import SIP_OK
# from src.sip.static.ok import SIP_OK_NO_SDP
# from src.sip.static.options import SIP_OPTIONS
# from src.sip.static.ringing import SIP_RINGING
# from src.sip.static.terminated import SIP_TERMINATE
# from src.sip.static.trying import SIP_TRYING
# from src.sockets import safe_allocate_tcp_client
# from src.sockets import safe_allocate_udp_client
# from src.sockets import unsafe_allocate_random_udp_socket

logger = logging.getLogger()


@attr.s(frozen=True, slots=True)
class Worker(object):
    """ Unspecialized worker """

    name = attr.ib(default="worker")

    _input = multiprocessing.Queue()
    _output = attr.ib(default=None)

    def __repr__(self):
        return "Worker(name=%s)" % self.name

    def __str__(self):
        return self.__repr__().__str__()

    @abstractproperty
    def size(self):
        return self._input.qsize()

    @abstractmethod
    def enqueue(self, message):
        self._input.put(message)

    @abstractmethod
    def standby(self):
        raise NotImplementedError


class SipWorker(Worker):
    """ """

    def __repr__(self):
        return "SipWorker(name='%s', size=%s)" % (self.name, self.size)

    def standby(self, *a, **kw):
        return



# # SIP responses
# # -------------------------------------------------------------------------------

# SIPTemplates = {
#     "DEFAULT": SIP_OK_NO_SDP,
#     "OK +SDP": SIP_OK,
#     "OK -SDP": SIP_OK_NO_SDP,
#     "OPTIONS": SIP_OPTIONS,
#     "RINGING": SIP_RINGING,
#     "TERMINATE": SIP_TERMINATE,
#     "TRYING": SIP_TRYING,
# }

# SIPColors = {
#     "+++": "\033[01m\033[35m+++\033[0m",  # bold, purple, reset
#     ">>>": "\033[01m\033[32m>>>\033[0m",  # bold, green, reset
#     "<<<": "\033[01m\033[91m<<<\033[0m",  # bold, yellow, reset
# }


# @memcache(size=32)
# def generate_response(method, datagram):
#     """ memcached SIP message generator.
#     @datagram<dict> -- SIP response datagram.
#     @method<str> -- SIP response method.
#     """
#     return convert_to_sip_packet(
#         template=SIPTemplates.get(method, SIPTemplates["DEFAULT"]), datagram=datagram
#     )


# def send_response(shared_socket, endpoint, datagram, method):
#     """ SIP message response sender.
#     @shared_socket<socket> -- shared UDP socket.
#     @endpoint<tuple> -- server endpoint address.
#     @datagram<dict> -- parsed SIP datagram.
#     @method<str> -- SIP method.
#     """
#     if not endpoint:
#         logger.error("<worker>: unable to send response due to empty endpoint.")
#         return
#     # generate response and send to the endpoint.
#     response = generate_response(method, datagram)
#     logger.info("%s <worker>: [\033[01m\033[91m%s\033[0m]", SIPColors["<<<"], method)
#     logger.debug("%s <worker>: sent to %s\n%s", SIPColors["<<<"], endpoint, response)
#     try:
#         shared_socket.sendto(response, endpoint)
#     except Exception as message:
#         logging.error("<worker>: failed to send using shared socket: %s", message)
#         try:  # close shared socket and re-create another one later.
#             shared_socket.close()
#             shared_socket = None  # unset to re-initialize at next iteration.
#         except AttributeError:
#             pass
#         # temporarily allocate an udp client to send data.
#         logging.info("<worker>: using backup client-socket to send response.")
#         with safe_allocate_udp_client() as client:
#             client.sendto(response, endpoint)


# # SIP worker
# # -------------------------------------------------------------------------------


# class LazyWorker(object):
#     """ worker implementation.
#     """

#     def __init__(self, name=None, settings=None, gc=None):
#         """
#         @name<str> -- worker name.
#         @settings<dict> -- `config.json`
#         @gc<SynchronousGarbageCollector> -- shared garbage collector.
#         """
#         if name is None:
#             self.name = "temp-%s" % create_random_uuid()[:4]
#         else:
#             self.name = "worker-" + str(name)

#         self.settings = settings
#         self.gc = gc

#         self.socket = None  # lazy initialize.
#         self.rtp = None  # lazy initialize.
#         self.handlers = {
#             "DEFAULT": self.handle_default,
#             "ACK": self.handle_ack,
#             "BYE": self.handle_bye,
#             "CANCEL": self.handle_cancel,
#             "INVITE": self.handle_invite,
#         }

#         self.is_ready = True  # recyclable state.
#         logger.debug("<worker>: successfully initialized %s.", self.name)

#     def reset(self):
#         """ reset worker.
#         """
#         self.call_id = self.datagram = self.endpoint = self.method = None
#         self.is_ready = True

#     def handle(self, message, endpoint):
#         """ worker logic.
#         @message<str> -- worker "work".
#         @endpoint<tuple> -- worker response endpoint.
#         """
#         self.is_ready = False  # woker is busy.
#         logger.refresh()  # create new context.

#         if not message or not endpoint:
#             logger.warning("<worker>: reset from incomplete work assignment.")
#             self.reset()
#             return
#         else:  # prepare worker.
#             self.endpoint = endpoint
#             # self.message = message
#             if self.socket is None:
#                 self.socket = unsafe_allocate_random_udp_socket(is_reused=True)
#             if self.rtp is None:
#                 self.rtp = SynchronousRTPRouter(self.settings)
#         self.rtp.context = logger.context

#         # validate work.
#         if not validate_sip_signature(message):
#             logger.warning("<worker>: reset from invalid signature: '%s'", message)
#             self.reset()
#             return
#         self.datagram = parse_sip_packet(message)
#         try:  # override parsed headers with loaded headers.
#             self.call_id = self.datagram["sip"]["Call-ID"]
#             self.method = self.datagram["sip"]["Method"]
#             logger.info("%s <worker>: reference %s", SIPColors[">>>"], self.call_id)
#         except KeyError:
#             logger.warning("<worker>: reset from invalid format: '%s'", message)
#             self.reset()
#             return

#         # load eligible SIP headers from the configuration.
#         sip_headers = self.settings["sip"]["worker"]["headers"]
#         for (field, value) in sip_headers.items():
#             try:
#                 self.datagram["sip"][field] = value
#             except TypeError:
#                 logger.error("<worker>: unable to use header: %s %s", field, value)

#         # set 'Contact' response header to delegate future messages.
#         server_address = self.settings["sip"]["server"]["address"]  # server address.
#         self.datagram["sip"]["Contact"] = (
#             "<sip:SIPd@%s:5060;transport=udp>" % server_address
#         )

#         logger.info(
#             "%s <worker>: [\033[01m\033[91m%s\033[0m]", SIPColors[">>>"], self.method
#         )
#         logger.debug(
#             "%s <worker>: received from %s\n%s", SIPColors[">>>"], endpoint, message
#         )
#         self.handlers.get(self.method, self.handlers["DEFAULT"])()
#         self.reset()

#     #
#     # custom handlers
#     #

#     def handle_default(self):
#         send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")

#     def handle_ack(self):
#         pass

#     def handle_bye(self):
#         send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
#         send_response(self.socket, self.endpoint, self.datagram, "TERMINATE")
#         self.gc.revoke(call_id=self.call_id)

#     def handle_cancel(self):
#         send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
#         try:
#             self.rtp.handle(datagram=self.datagram, action="stop")
#         except AttributeError as error:
#             logger.error("<rtp>:RTP handler is down: %s", error)
#             self.rtp = None  # unset to re-initialize at next iteration.
#         send_response(self.socket, self.endpoint, self.datagram, "TERMINATE")

#     def handle_invite(self):
#         if self.call_id in self.gc.calls.history:
#             logger.warning("<worker>: detected duplicate Call-ID: %s", self.call_id)
#             send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
#             return
#         # receive TX/RX ports to delegate RTP packets.
#         send_response(self.socket, self.endpoint, self.datagram, "TRYING")
#         max_retry = max(1, self.settings["rtp"].get("max_retry", 1))
#         for _ in range(max_retry, 0, -1):
#             send_response(self.socket, self.endpoint, self.datagram, "RINGING")
#             # if external RTP handler replies with one or more ports, rewrite
#             # and update the existing datagram with new information and respond.
#             datagram = None
#             try:
#                 datagram = self.rtp.handle(datagram=self.datagram)
#             except AttributeError as error:
#                 logger.error("<rtp>:RTP handler is down: %s", error)
#                 self.rtp = None  # unset to re-initialize at next iteration.
#             if datagram:
#                 self.datagram = datagram
#                 send_response(self.socket, self.endpoint, self.datagram, "OK +SDP")
#                 break
#             else:
#                 logger.warning("<worker>: RTP handler did not send RX/TX ports.")
#                 send_response(self.socket, self.endpoint, self.datagram, "OK -SDP")
#         try:
#             self.gc.register(call_id=self.call_id)
#             self.send_to_db_interface()
#         except:
#             pass

#     def send_to_db_interface(self):
#         """ send datagram to db interface.
#         """
#         db = self.settings["db"]
#         if not db.get("enabled"):
#             return
#         db_host, db_port = db["host"], int(db["port"])
#         db_username = db["username"]
#         db_password = db["password"]
#         with safe_allocate_tcp_client(host=db_host, port=db_port) as client:
#             datagram = copy.deepcopy(self.datagram)
#             datagram["user"] = db_username
#             datagram["pass"] = db_password
#             client.sendall(dump_json(datagram))
#             logger.info("<worker>: sent metadata to remote database.")
