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
# https://github.com/initbar/sipping

import re
import unittest

from src.sockets import *
from src.parser import *


class TestSockets(unittest.TestCase):

    #
    # ip address
    #

    def test_sockets_get_server_address(self):
        ip_address = get_server_address()
        self.assertTrue(ip_address != "no IP found")
        self.assertTrue(REGX_IPV4.match(ip_address))

    #
    # udp sockets
    #

    def test_sockets_unsafe_allocate_udp_socket_empty_both(self):
        self.assertFalse(unsafe_allocate_udp_socket("", ""))

    def test_sockets_unsafe_allocate_udp_socket_empty_host(self):
        self.assertFalse(unsafe_allocate_udp_socket("", 8080))

    def test_sockets_unsafe_allocate_udp_socket_empty_port(self):
        self.assertFalse(unsafe_allocate_udp_socket("127.0.0.1", ""))

    def test_sockets_unsafe_allocate_udp_socket_hostname_1(self):
        self.assertFalse(unsafe_allocate_udp_socket("127.0.1", 8080))

    def test_sockets_unsafe_allocate_udp_socket_hostname_2(self):
        self.assertFalse(unsafe_allocate_udp_socket("localhose", 8080))

    def test_sockets_unsafe_allocate_udp_socket_hostname_3(self):
        self.assertFalse(unsafe_allocate_udp_socket("0.0.0.0.0", 8080))

    def test_sockets_unsafe_allocate_udp_socket(self):
        with safe_allocate_random_udp_socket() as udp_socket:
            socket_port = udp_socket.getsockname()[1]
            with safe_allocate_udp_client() as udp_client:
                udp_client.connect(("127.0.0.1", socket_port))
