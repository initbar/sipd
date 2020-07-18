# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

import asyncore
import logging

# from net.lib import safe_allocate_udp_socket
# from sip.router import AsynchronousUDPRouter

logger = logging.getLogger()


# class AsynchronousUDPServer(object):
#     """Asynchronous UDP server."""

#     def serve(self):
#         host = self.settings["server"]["host"]
#         port = self.settings["server"]["port"]
#         with safe_allocate_udp_socket(host=host, port=port, is_reused=True) as socket:
#             router = AsynchronousUDPRouter(settings=self.settings, socket=socket)
#             router.standby()
#             logger.info("successfully created router.")
#             logger.debug("router: %s", router)
#             logger.info("successfully created server.")
#             logger.debug("server: %s", self)
#             asyncore.loop()


class AsynchronousUDPServer(object):
    ...
