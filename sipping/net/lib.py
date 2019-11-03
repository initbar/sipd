# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

from __future__ import absolute_import
from contextlib import contextmanager
from functools import lru_cache

import logging
import random
import re
import socket

logger = logging.getLogger()


#
# IPV4
#


REGX_IPV4 = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:\:\d{1,5})*")

@lru_cache(maxsize=128, typed=True)
def parse_ipv4_address(string: str) -> list:
    """ find all IPv4 addresses in a string.
    """
    return REGX_IPV4.findall(string)


#
# PORT
#


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
        logger.debug("attempting to bind to udp port: '%s'.", port)
        udp_socket.settimeout(timeout)
        udp_socket.bind((host, port))
    except socket.error:
        logger.error("failed to bind to udp port: '%s'.", port)
        return

    # reuse the server socket.
    if is_reused:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)

    logger.info("successfully created udp socket port '%s'.", port)
    return udp_socket


@contextmanager
def safe_allocate_udp_socket(*a, **kw) -> socket:
    """ create an UDP socket that automatically closes.
    """
    _socket = unsafe_allocate_udp_socket(*a, **kw)
    try: yield _socket
    finally:
        try: _socket.close()
        except AttributeError:
            pass


__all__ = [
    "get_random_privileged_port",
    "get_random_unprivileged_port",
    "parse_ipv4_address",
    "safe_allocate_udp_socket",
    "unsafe_allocate_udp_socket",
]
