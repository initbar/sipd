# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

"""
sipd.net.udp
---------------
"""

from __future__ import absolute_import
from contextlib import contextmanager

import logging
import socket

# from net.lib import get_random_privileged_port
from net.lib import get_random_unprivileged_port
from net.lib import unsafe_allocate_udp_socket

logger = logging.getLogger()


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


__all__ = [
    "safe_allocate_random_udp_socket",
    "safe_allocate_udp_client",
    "unsafe_allocate_random_udp_socket",
    "unsafe_allocate_udp_socket",
]
