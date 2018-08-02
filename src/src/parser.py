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

# -------------------------------------------------------------------------------
# parser.py -- SIP message parser.
# -------------------------------------------------------------------------------

from collections import deque
from src.errors import SIPBrokenProtocol
from src.optimizer import memcache
from src.sip.methods import SIP_METHODS

import json
import re

import logging

logger = logging.getLogger()

# pre-compiled regex
# -------------------------------------------------------------------------------

REGX_IPV4 = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:\:\d{1,5})*")
REGX_SDP = re.compile("^[a-z]{1}=.+$")

# ip entities
# -------------------------------------------------------------------------------


def parse_address(plaintext):
    """ find all ip addresses in a string.
    """
    return REGX_IPV4.findall(safe_encode(plaintext))


# string entities
# -------------------------------------------------------------------------------

COLON = ":"
COMMA = ","
CRLF = "\r\n"


def safe_encode(plaintext, encoding="utf-8"):
    """ safely encode a string to `encoding` type.
    """
    return plaintext.encode(encoding)


def safe_decode(plaintext, encoding="utf-8"):
    """ safely decode a string to `encoding` type.
    """
    return plaintext.decode(encoding)


# JSON entities
# -------------------------------------------------------------------------------


def parse_json(_json):
    """ read JSON and return dictionary.
    """
    return json.loads(safe_encode(_json))


def dump_json(_json):
    """ read dictionary and return JSON.
    """
    return safe_encode(json.dumps(_json))


# SIP entities
# -------------------------------------------------------------------------------

# check if SIP signature exists inside SIP message.
validate_sip_signature = lambda message: "SIP" in str(message)


def convert_to_sip_packet(template, datagram):
    """ convert human-readable text into ready-only SIP packet.
    """
    if not template:
        return CRLF

    # reconstruct SIP from datagram.
    packet = "%s%s" % (template["status_line"], CRLF)
    try:
        packet += CRLF.join(
            [
                "%s: %s" % (sip_field, datagram["sip"].get(sip_field))
                for sip_field in template["sip"]
                if datagram["sip"].get(sip_field)
            ]
        )
    except TypeError:
        logger.error("<parser>:failed to parse using %s", datagram)
        return CRLF

    # reconstruct SDP from datagram.
    if template.get("sdp"):
        packet += "%s%s" % (CRLF, "Content-Type: application/sdp")
        sdp = CRLF.join(datagram.get("sdp"))
        sdp_length = str(len(sdp))
        packet += "%s%s" % (CRLF, "Content-Length: " + sdp_length)
    else:
        packet += "%s%s" % (CRLF, "Content-Length: 0")
    packet += 2 * CRLF  # double \r\n to end header section.

    # add SDP data.
    if locals().get("sdp"):
        packet += sdp

    # error correction.
    if not packet.endswith(CRLF):
        packet += CRLF
    return packet


@memcache(size=128)
def parse_sip_packet(message):
    """ deconstruct a SIP packet to a list of headers.
    """
    if not message:
        logger.warning("message format is incorrect: " + str(message))
        return {}

    # allocate Pythonic object to interface with SIP headers. Originally, the
    # design was to whitelist known SIP headers into a SIP datagram using
    # SIPResponse and SIPRequest datagrams. However, since headers will be
    # unknown (as well as possibly volitile), the design was changed to
    # dynamically insert any keys extracted from single SIP packet.
    queue = deque(filter(None, message.replace(CRLF, "\n").split("\n")))
    datagram = {"sip": {}, "sdp": []}
    datagram_compressed = datagram.copy()

    # rotate and parse each SIP headers. But first, since set intersection
    # operation is more computationally expensive than other search operations
    # - and since we already know that the first header will always indicate
    # SIP method - parse the method first.
    header = queue.popleft()
    try:
        method = (SIP_METHODS & set(header.split())).pop()
    except:
        logger.error(SIPBrokenProtocol(header))
        return
    datagram["sip"]["Method"] = [method]

    # for the remaining headers, split by the first occurance of header and
    # definition CRLF and insert into the dynamic datagram. Since it's possible
    # to have multiple values for a given key (e.g. Via), temporarily store
    # the values as list.
    while queue:
        header = queue.popleft()
        try:
            assert not REGX_SDP.match(header)
            k, v = header.split(COLON, 1)
            datagram["sip"].setdefault(k, [])
            datagram["sip"][k].append(v.strip())
        except:
            pass

    try:  # compress multiple SIP keys into single key.
        for (k, v) in list(datagram["sip"].items()):
            datagram_compressed["sip"].setdefault(k, [])
            datagram_compressed["sip"][k] = COMMA.join(v)
    except:
        pass

    try:  # compress multiple SDP keys into single key.
        for (k, v) in list(datagram["sdp"].items()):
            datagram_compressed["sdp"].setdefault(k, [])
            datagram_compressed["sdp"][k] = CRLF.join([sdp for sdp in set(v)])
    except:
        pass

    # return compressed datagram.
    return datagram_compressed
