# MIT License
#
# Copyright (c) 2018 Herbert Shin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://github.com/initbar/sipd

"""
server.py
---------
"""

from __future__ import absolute_import

import asyncore
import attr
import logging

from net.lib import safe_allocate_udp_socket
from sip.router import AsynchronousUDPRouter

logger = logging.getLogger()


@attr.s(slots=True)
class AsynchronousUDPServer(object):
    """ Asynchronous UDP server
    """

    settings = attr.ib()
    router = attr.ib(default=None)

    def __repr__(self):
        return "AsynchronousUDPServer(settings=%s)" % self.settings

    def serve(self):
        host = str(self.settings.address)
        port = int(self.settings.port)
        with safe_allocate_udp_socket(host=host, port=port, is_reused=True) as socket:
            self.router = AsynchronousUDPRouter(settings=self.settings, socket=socket)
            self.router.route()
            logger.info("successfully created router.")
            logger.debug("router => %s", self.router)
            logger.info("successfully created server.")
            logger.debug("server => %s", self)
            asyncore.loop()


__all__ = ["AsynchronousUDPServer"]
