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

from __future__ import absolute_import
from contextlib import contextmanager

import logging
import random
import socket

logger = logging.getLogger()

__all__ = [
    "get_random_privileged_port",
    "get_random_unprivileged_port",
    "safe_allocate_udp_socket",
    "unsafe_allocate_udp_socket",
]


# get random port number from privileged port range.
get_random_privileged_port = lambda: random.randint(1, 1024)

# get random port number from unprivileged port range.
get_random_unprivileged_port = lambda: random.randint(1025, 65535)


#
# UDP
#


def unsafe_allocate_udp_socket(
        host: str = "127.0.0.1",
        port: int = None,
        timeout: float = 1.0,
        is_client: bool = False,
        is_reused: bool = False) -> socket:
    """ create an UDP socket that requires manual close.
    @host<str> -- UDP socket host.
    @port<int> -- UDP socket port.
    @timeout<float> -- UDP socket timeout in seconds.
    @is_client<bool> -- enable socket client-mode.
    @is_reused<bool> -- enable socket reuse.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setblocking(False)  # should never block to demux efficiently.

    # client socket.
    if is_client:
        return udp_socket

    # bind the server socket.
    try:
        logger.debug("attempting to bind to udp port: '%s'", port)
        udp_socket.settimeout(timeout)
        udp_socket.bind((host, port))
    except socket.error:
        logger.error("failed to bind to udp port: '%s'", port)
        return

    # reuse the server socket.
    if is_reused:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)

    logger.info("successfully created udp socket port '%s'", port)
    return udp_socket


@contextmanager
def safe_allocate_udp_socket(*a, **kw) -> socket:
    """ create an UDP socket that automatically closes.
    """
    _socket = unsafe_allocate_udp_socket(*a, **kw)
    try:
        yield _socket
    finally:
        try: _socket.close()
        except AttributeError:
            pass  # already closed.


#
# TCP
#
