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

from string import printable as ASCII

import re
import unittest

from src.parser import *
from src.sip.static.options import SIP_OPTIONS_SAMPLE


class TestParser(unittest.TestCase):

    #
    # static regex
    #

    def test_parser_ipv4_regex_ip_min(self):
        sample = answer = "0.0.0.0"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_ip_max(self):
        sample = answer = "255.255.255.255"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_min(self):
        sample = answer = "0.0.0.0:0"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_max(self):
        sample = answer = "255.255.255.255:65535"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_missing(self):
        sample = "0.0.0.0:"
        answer = "0.0.0.0"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_wrong_format_1(self):
        sample = "0.0.0.0::"
        answer = "0.0.0.0"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_wrong_format_2(self):
        sample = "0.0.0.0::0"
        answer = "0.0.0.0"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_wrong_format_3(self):
        sample = "0.0.0.0:00000000"
        answer = "0.0.0.0"
        attempt = re.findall(REGX_IPV4, sample)
        self.assertNotEqual(answer, attempt[0])

    #
    # encoder/decoder
    #

    def test_parser_safe_encode_empty_string(self):
        sample = answer = ""
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_encode_short_repeated(self):
        sample = answer = "A"
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_encode_medium_repeated(self):
        sample = answer = "A" * 0xff
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_encode_long_repeated(self):
        sample = answer = "A" * 0xffff
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_decode_short_repeated(self):
        sample = answer = "A"
        self.assertEqual(safe_decode(sample), answer)

    def test_parser_safe_decode_medium_repeated(self):
        sample = answer = "A" * 0xff
        self.assertEqual(safe_decode(sample), answer)

    def test_parser_safe_decode_long_repeated(self):
        sample = answer = "A" * 0xffff
        self.assertEqual(safe_decode(sample), answer)

    def test_parser_safe_encode_ascii(self):
        sample = answer = ASCII
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_decode_ascii(self):
        sample = answer = ASCII
        self.assertEqual(safe_decode(sample), answer)

    def test_parser_safe_encode_decode_ascii(self):
        sample = answer = ASCII
        self.assertEqual(safe_encode(safe_decode(sample)), answer)

    def test_parser_safe_decode_encode_ascii(self):
        sample = answer = ASCII
        self.assertEqual(safe_decode(safe_encode(sample)), answer)

    #
    # SIP signature validation
    #

    def test_parser_sip_signature_validation_empty_datatypes(self):
        for datatype in [None, "", 0, [], (), {}]:
            self.assertFalse(validate_sip_signature(datatype))

    def test_parser_sip_signature_validation_no_version_uppercase(self):
        sample = "SIP"
        self.assertTrue(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_no_version_capitalize(self):
        sample = "Sip"
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_no_version_lowercase(self):
        sample = "sip"
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_legacy_version_uppercase(self):
        sample = "SIP/1.0"
        self.assertTrue(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_legacy_version_capitalize(self):
        sample = "Sip/1.0"
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_legacy_version_lowercase(self):
        sample = "sip/1.0"
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_modern_version_uppercase(self):
        sample = "SIP/2.0"
        self.assertTrue(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_modern_version_capitalize(self):
        sample = "Sip/2.0"
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_modern_version_lowercase(self):
        sample = "sip/2.0"
        self.assertFalse(validate_sip_signature(sample))

    #
    # SIP packet unpack
    #

    def test_parser_parse_sip_packet_single_header(self):
        packet = SIP_OPTIONS_SAMPLE
        self.assertEqual(
            parse_sip_packet(packet),
            {
                "sip": {
                    "Content-Length": "0",
                    "Via": "SIP/2.0/UDP 192.168.1.3:15064;branch=z9hG4bK0x2473c35084b6b1",
                    "From": "<sip:GVP@192.168.1.3:15064>;tag=9E565000-FB73-C996-4E01-0810C8DE0CF4",
                    "Supported": "timer, uui",
                    "To": "sip:192.168.1.6:5060",
                    "Contact": "<sip:GVP@192.168.1.3:15064>",
                    "CSeq": "307103 OPTIONS",
                    "Allow": "INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO",
                    "Call-ID": "9E565000-FB73-F13E-6076-D8822FB9A4E4-15064@192.168.1.3",
                    "Max-Forwards": "70",
                    "Method": "OPTIONS",
                },
                "sdp": [],
            },
        )

    def test_parser_parse_sip_packet_multiple_headers(self):
        packet = SIP_OPTIONS_SAMPLE
        packet += "Supported: X\r\n"
        self.assertEqual(
            parse_sip_packet(packet),
            {
                "sip": {
                    "Content-Length": "0",
                    "Via": "SIP/2.0/UDP 192.168.1.3:15064;branch=z9hG4bK0x2473c35084b6b1",
                    "From": "<sip:GVP@192.168.1.3:15064>;tag=9E565000-FB73-C996-4E01-0810C8DE0CF4",
                    "Supported": "timer, uui,X",
                    "To": "sip:192.168.1.6:5060",
                    "Contact": "<sip:GVP@192.168.1.3:15064>",
                    "CSeq": "307103 OPTIONS",
                    "Allow": "INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO",
                    "Call-ID": "9E565000-FB73-F13E-6076-D8822FB9A4E4-15064@192.168.1.3",
                    "Max-Forwards": "70",
                    "Method": "OPTIONS",
                },
                "sdp": [],
            },
        )

    def test_parser_parse_sip_packet_genesys_headers(self):
        packet = SIP_OPTIONS_SAMPLE
        packet += (
            "X-Genesys-GVP-Session-ID: 9E565000-457B-6487-67D5-BA32B23886C4;gvp.rm.datanodes=2|1;gvp.rm.tenant-id=1.102_MSML_PROFILE\r\n"
        )
        packet += (
            "X-Genesys-GVP-Session-Data: callsession=9E565000-457B-6487-67D5-BA32B23886C4;2;1;;;;Environment/USA_NAHQ_SEA;MSML_PROFILE\r\n"
        )
        packet += "X-Genesys-RM-Application-dbid: 105\r\n"
        self.assertEqual(
            parse_sip_packet(packet),
            {
                "sip": {
                    "X-Genesys-GVP-Session-Data": "callsession=9E565000-457B-6487-67D5-BA32B23886C4;2;1;;;;Environment/USA_NAHQ_SEA;MSML_PROFILE",
                    "Content-Length": "0",
                    "Via": "SIP/2.0/UDP 192.168.1.3:15064;branch=z9hG4bK0x2473c35084b6b1",
                    "From": "<sip:GVP@192.168.1.3:15064>;tag=9E565000-FB73-C996-4E01-0810C8DE0CF4",
                    "Supported": "timer, uui",
                    "X-Genesys-RM-Application-dbid": "105",
                    "To": "sip:192.168.1.6:5060",
                    "X-Genesys-GVP-Session-ID": "9E565000-457B-6487-67D5-BA32B23886C4;gvp.rm.datanodes=2|1;gvp.rm.tenant-id=1.102_MSML_PROFILE",
                    "Contact": "<sip:GVP@192.168.1.3:15064>",
                    "CSeq": "307103 OPTIONS",
                    "Allow": "INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO",
                    "Call-ID": "9E565000-FB73-F13E-6076-D8822FB9A4E4-15064@192.168.1.3",
                    "Max-Forwards": "70",
                    "Method": "OPTIONS",
                },
                "sdp": [],
            },
        )
