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

import unittest

from src.errors import *

class TestErrors(unittest.TestCase):

    def test_errors_inheritance_sip_error(self):
        exception = SIPError()
        self.assertTrue(isinstance(exception, Exception))

    def test_errors_inheritance_brok_proto(self):
        exception = SIPBrokenProtocol()
        self.assertTrue(isinstance(exception, SIPError))

    def test_errors_inheritance_pack_error(self):
        exception = SIPPackError()
        self.assertTrue(isinstance(exception, SIPError))

    def test_errors_inheritance_unpack_error(self):
        exception = SIPUnpackError()
        self.assertTrue(isinstance(exception, SIPError))
