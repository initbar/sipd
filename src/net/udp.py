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
udp.py
------
"""

from __future__ import absolute_import
from contextlib import contextmanager

import logging
import socket

# from net.lib import get_random_privileged_port
from net.lib import get_random_unprivileged_port
from net.lib import unsafe_allocate_udp_socket

logger = logging.getLogger()

__all__ = [
    "safe_allocate_random_udp_socket",
    "safe_allocate_udp_client",
    "unsafe_allocate_random_udp_socket",
    "unsafe_allocate_udp_socket",
]


#
# SERVER
#


def unsafe_allocate_random_udp_socket(host: str = "127.0.0.1", is_reused: bool = False) -> socket:
    """
    @is_reused<bool> -- enable socket reuse.
    """
    while not locals().get("udp_socket"):
        port = get_random_unprivileged_port()
        udp_socket = unsafe_allocate_udp_socket(host=host, port=port, is_reused=is_reused)
    logger.info("successfully created a random UDP socket.")
    return udp_socket


@contextmanager
def safe_allocate_random_udp_socket(host: str = "127.0.0.1", is_reused: bool = False) -> socket:
    """
    @is_reused<bool> -- enable socket reuse.
    """
    udp_socket = unsafe_allocate_random_udp_socket(host=host, is_reused=is_reused)
    try: yield udp_socket
    finally:
        try: udp_socket.close()
        except AttributeError:
            pass


#
# CLIENT
#


def unsafe_allocate_udp_client(timeout: float = 1.0) -> socket:
    """
    @timeout<float> -- UDP socket timeout in seconds.
    """
    while not locals().get("client"):
        client = unsafe_allocate_udp_socket(timeout=timeout, is_client=True)
    logger.info("successfully created an UDP client.")
    return client


@contextmanager
def safe_allocate_udp_client(timeout: float = 1.0) -> socket:
    """
    @timeout<float> -- UDP socket timeout in seconds.
    """
    udp_socket = unsafe_allocate_udp_client(timeout=timeout)
    try: yield udp_socket
    finally:
        try: udp_socket.close()
        except AttributeError:
            pass
