# Active recording Session Initiation Protocol daemon (SIPd).
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
# https://github.com/initbar/SIPd

from src.parser import *
from src.sip.sip_options import *

from string import printable as ASCII
import re
import unittest

class TestParser(unittest.TestCase):

    #
    # static regex
    #

    def test_parser_ipv4_regex_ip_min(self):
        sample = answer = '0.0.0.0'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_ip_max(self):
        sample = answer = '255.255.255.255'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_min(self):
        sample = answer = '0.0.0.0:0'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_max(self):
        sample = answer = '255.255.255.255:65535'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_missing(self):
        sample = '0.0.0.0:'
        answer = '0.0.0.0'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_wrong_format_1(self):
        sample = '0.0.0.0::'
        answer = '0.0.0.0'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_wrong_format_2(self):
        sample = '0.0.0.0::0'
        answer = '0.0.0.0'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertEqual(answer, attempt[0])

    def test_parser_ipv4_regex_port_wrong_format_3(self):
        sample = '0.0.0.0:00000000'
        answer = '0.0.0.0'
        attempt = re.findall(REGX_IPV4, sample)
        self.assertNotEqual(answer, attempt[0])

    #
    # encoder/decoder
    #

    def test_parser_safe_encode_empty_string(self):
        sample = answer = ''
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_encode_short_repeated(self):
        sample = answer = 'A'
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_encode_medium_repeated(self):
        sample = answer = 'A' * 0xff
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_encode_long_repeated(self):
        sample = answer = 'A' * 0xffff
        self.assertEqual(safe_encode(sample), answer)

    def test_parser_safe_decode_short_repeated(self):
        sample = answer = 'A'
        self.assertEqual(safe_decode(sample), answer)

    def test_parser_safe_decode_medium_repeated(self):
        sample = answer = 'A' * 0xff
        self.assertEqual(safe_decode(sample), answer)

    def test_parser_safe_decode_long_repeated(self):
        sample = answer = 'A' * 0xffff
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
        for datatype in [None, '', 0, [], (), {}]:
            self.assertFalse(validate_sip_signature(datatype))

    def test_parser_sip_signature_validation_no_version_uppercase(self):
        sample = 'SIP'
        self.assertTrue(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_no_version_capitalize(self):
        sample = 'Sip'
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_no_version_lowercase(self):
        sample = 'sip'
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_legacy_version_uppercase(self):
        sample = 'SIP/1.0'
        self.assertTrue(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_legacy_version_capitalize(self):
        sample = 'Sip/1.0'
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_legacy_version_lowercase(self):
        sample = 'sip/1.0'
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_modern_version_uppercase(self):
        sample = 'SIP/2.0'
        self.assertTrue(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_modern_version_capitalize(self):
        sample = 'Sip/2.0'
        self.assertFalse(validate_sip_signature(sample))

    def test_parser_sip_signature_validation_modern_version_lowercase(self):
        sample = 'sip/2.0'
        self.assertFalse(validate_sip_signature(sample))

    #
    # SIP packet unpack
    #

    def test_parser_parse_sip_packet_single_header(self):
        packet = SIP_OPTIONS_SAMPLE
        self.assertEqual(
            parse_sip_packet(packet),
            {'sip': {
                'Content-Length': '0',
                'Via': 'SIP/2.0/UDP 105.20.3.41:15064;branch=z9hG4bK0x2473c35084b6b1',
                'From': '<sip:GVP@105.20.3.41:15064>;tag=9E565000-FB73-C996-4E01-0810C8DE0CF4',
                'Supported': 'timer, uui',
                'To': 'sip:105.20.3.66:5060',
                'Contact': '<sip:GVP@105.20.3.41:15064>',
                'CSeq': '307103 OPTIONS',
                'Allow': 'INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO',
                'Call-ID': '9E565000-FB73-F13E-6076-D8822FB9A4E4-15064@105.20.3.41',
                'Max-Forwards': '70',
                'Method': 'OPTIONS'},
             'sdp': []})

    def test_parser_parse_sip_packet_multiple_headers(self):
        packet = SIP_OPTIONS_SAMPLE
        packet += 'Supported: X\r\n'
        self.assertEqual(
            parse_sip_packet(packet),
            {'sip': {
                'Content-Length': '0',
                'Via': 'SIP/2.0/UDP 105.20.3.41:15064;branch=z9hG4bK0x2473c35084b6b1',
                'From': '<sip:GVP@105.20.3.41:15064>;tag=9E565000-FB73-C996-4E01-0810C8DE0CF4',
                'Supported': 'timer, uui,X',
                'To': 'sip:105.20.3.66:5060',
                'Contact': '<sip:GVP@105.20.3.41:15064>',
                'CSeq': '307103 OPTIONS',
                'Allow': 'INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO',
                'Call-ID': '9E565000-FB73-F13E-6076-D8822FB9A4E4-15064@105.20.3.41',
                'Max-Forwards': '70',
                'Method': 'OPTIONS'},
             'sdp': []})

    def test_parser_parse_sip_packet_genesys_headers(self):
        packet = SIP_OPTIONS_SAMPLE
        packet += 'X-Genesys-GVP-Session-ID: 9E565000-457B-6487-67D5-BA32B23886C4;gvp.rm.datanodes=2|1;gvp.rm.tenant-id=1.102_MSML_PROFILE\r\n'
        packet += 'X-Genesys-GVP-Session-Data: callsession=9E565000-457B-6487-67D5-BA32B23886C4;2;1;;;;Environment/USA_NAHQ_SEA;MSML_PROFILE\r\n'
        packet += 'X-Genesys-RM-Application-dbid: 105\r\n'
        self.assertEqual(
            parse_sip_packet(packet),
            {'sip': {
                'X-Genesys-GVP-Session-Data': 'callsession=9E565000-457B-6487-67D5-BA32B23886C4;2;1;;;;Environment/USA_NAHQ_SEA;MSML_PROFILE',
                'Content-Length': '0',
                'Via': 'SIP/2.0/UDP 105.20.3.41:15064;branch=z9hG4bK0x2473c35084b6b1',
                'From': '<sip:GVP@105.20.3.41:15064>;tag=9E565000-FB73-C996-4E01-0810C8DE0CF4',
                'Supported': 'timer, uui',
                'X-Genesys-RM-Application-dbid': '105',
                'To': 'sip:105.20.3.66:5060',
                'X-Genesys-GVP-Session-ID': '9E565000-457B-6487-67D5-BA32B23886C4;gvp.rm.datanodes=2|1;gvp.rm.tenant-id=1.102_MSML_PROFILE',
                'Contact': '<sip:GVP@105.20.3.41:15064>',
                'CSeq': '307103 OPTIONS',
                'Allow': 'INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO',
                'Call-ID': '9E565000-FB73-F13E-6076-D8822FB9A4E4-15064@105.20.3.41',
                'Max-Forwards': '70',
                'Method': 'OPTIONS'},
             'sdp': []})
