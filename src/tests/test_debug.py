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

from src.debug import *


class TestDebug(unittest.TestCase):

    #
    # UUID
    #

    def test_debug_uuid_collision(self):
        _test = set()
        for uuid in range(int(1e6)):
            _test.add(uuid)
        self.assertEqual(len(_test), 1e6)

    #
    # MD5
    #

    def test_debug_md5sum_string_empty(self):
        sample = ""
        attempt = md5sum(sample)
        answer = "d41d8cd98f00b204e9800998ecf8427e"
        self.assertEqual(attempt, answer)

    def test_debug_md5sum_string_small(self):
        sample = "a"
        attempt = md5sum(sample)
        answer = "0cc175b9c0f1b6a831c399e269772661"
        self.assertEqual(attempt, answer)

    def test_debug_md5sum_string_medium(self):
        sample = "hello"
        attempt = md5sum(sample)
        answer = "5d41402abc4b2a76b9719d911017c592"
        self.assertEqual(attempt, answer)

    def test_debug_md5sum_string_long(self):
        sample = "A" * 0xfff
        attempt = md5sum(sample)
        answer = "4ea84bed94e81f1fa0fc360e3cf857b7"
        self.assertEqual(attempt, answer)

    #
    # SHA1
    #

    def test_debug_sha1sum_string_empty(self):
        sample = ""
        attempt = sha1sum(sample)
        answer = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        self.assertEqual(attempt, answer)

    def test_debug_sha1sum_string_small(self):
        sample = "a"
        attempt = sha1sum(sample)
        answer = "86f7e437faa5a7fce15d1ddcb9eaeaea377667b8"
        self.assertEqual(attempt, answer)

    def test_debug_sha1sum_string_medium(self):
        sample = "hello"
        attempt = sha1sum(sample)
        answer = "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d"
        self.assertEqual(attempt, answer)

    def test_debug_sha1sum_string_long(self):
        sample = "A" * 0xfff
        attempt = sha1sum(sample)
        answer = "24c314d3c0b06dc0ff17a96ad44f648520dbc5a6"
        self.assertEqual(attempt, answer)

    #
    # SHA256
    #

    def test_debug_sha256sum_string_empty(self):
        sample = ""
        attempt = sha256sum(sample)
        answer = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(attempt, answer)

    def test_debug_sha256sum_string_small(self):
        sample = "a"
        attempt = sha256sum(sample)
        answer = "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"
        self.assertEqual(attempt, answer)

    def test_debug_sha256sum_string_medium(self):
        sample = "hello"
        attempt = sha256sum(sample)
        answer = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        self.assertEqual(attempt, answer)

    def test_debug_sha256sum_string_long(self):
        sample = "A" * 0xfff
        attempt = sha256sum(sample)
        answer = "ec3a61bfe4f74b1db3d423f57c491060dd0e57a2392591f82c44323b0fd3410c"
        self.assertEqual(attempt, answer)

    #
    # SHA512
    #

    def test_debug_sha512sum_string_empty(self):
        sample = ""
        attempt = sha512sum(sample)
        answer = (
            "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        )
        self.assertEqual(attempt, answer)

    def test_debug_sha512sum_string_small(self):
        sample = "a"
        attempt = sha512sum(sample)
        answer = (
            "1f40fc92da241694750979ee6cf582f2d5d7d28e18335de05abc54d0560e0f5302860c652bf08d560252aa5e74210546f369fbbbce8c12cfc7957b2652fe9a75"
        )
        self.assertEqual(attempt, answer)

    def test_debug_sha512sum_string_medium(self):
        sample = "hello"
        attempt = sha512sum(sample)
        answer = (
            "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043"
        )
        self.assertEqual(attempt, answer)

    def test_debug_sha512sum_string_long(self):
        sample = "A" * 0xfff
        attempt = sha512sum(sample)
        answer = (
            "34e60053d4330246808246aa78cdbff2302361f25fea9f34a153cf33ed99604985a253031aa137f0c072fd8d71c9c411fda3be3b3ab33a18cdd61386ba75107c"
        )
        self.assertEqual(attempt, answer)
