# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

"""
sipping.sip.server
------------------
"""

from __future__ import absolute_import
from abc import abstractmethod

import asyncore
import attr
import logging

from net.lib import safe_allocate_udp_socket
from sip.router import AsynchronousUDPRouter

logger = logging.getLogger()


@attr.s(slots=True)
class AsynchronousServer(object):
    """ Asynchronous server """

    settings = attr.ib()

    def __repr__(self):
        return "AsynchronousServer(settings=%s)" % self.settings

    def __str__(self):
        return self.__repr__().__str__()

    @abstractmethod
    def serve(self):
        raise NotImplementedError


class AsynchronousUDPServer(AsynchronousServer):
    """ Asynchronous UDP server """

    def __repr__(self):
        return "AsynchronousUDPServer(settings=%s)" % self.settings

    def serve(self):
        host = self.settings["server"]["host"]
        port = self.settings["server"]["port"]
        with safe_allocate_udp_socket(host=host, port=port, is_reused=True) as socket:
            router = AsynchronousUDPRouter(settings=self.settings, socket=socket)
            router.standby()
            logger.info("successfully created router.")
            logger.debug("router: %s", router)
            logger.info("successfully created server.")
            logger.debug("server: %s", self)
            asyncore.loop()


__all__ = ["AsynchronousServer", "AsynchronousUDPServer"]
