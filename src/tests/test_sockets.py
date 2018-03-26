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
        self.assertFalse(unsafe_allocate_udp_socket('', ''))

    def test_sockets_unsafe_allocate_udp_socket_empty_host(self):
        self.assertFalse(unsafe_allocate_udp_socket('', 8080))

    def test_sockets_unsafe_allocate_udp_socket_empty_port(self):
        self.assertFalse(unsafe_allocate_udp_socket('127.0.0.1', ''))

    def test_sockets_unsafe_allocate_udp_socket_hostname_1(self):
        self.assertFalse(unsafe_allocate_udp_socket('127.0.1', 8080))

    def test_sockets_unsafe_allocate_udp_socket_hostname_2(self):
        self.assertFalse(unsafe_allocate_udp_socket('localhose', 8080))

    def test_sockets_unsafe_allocate_udp_socket_hostname_3(self):
        self.assertFalse(unsafe_allocate_udp_socket('0.0.0.0.0', 8080))

    def test_sockets_unsafe_allocate_udp_socket(self):
        with safe_allocate_random_udp_socket() as udp_socket:
            socket_port = udp_socket.getsockname()[1]
            with safe_allocate_udp_client() as udp_client:
                udp_client.connect(('127.0.0.1', socket_port))
