# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

"""
sipping.sip.parser
------------------
"""

from __future__ import absolute_import
from collections import deque
from functools import lru_cache

import logging
import re
import six

from src.sip.methods import SIP_METHODS

logger = logging.getLogger()

__all__ = [
    "convert_to_sip_message",
    "parse_sip_message",
    "validate_sip_signature",
]

#
# entities
#

COLON = ":"
COMMA = ","
CRLF = "\r\n"

#
# SIP
#

SDP_PATTERN = re.compile("^[a-z]{1}=.+$")

# check if SIP signature exists inside SIP message.
validate_sip_signature = lambda string: "SIP" in string


@lru_cache(maxsize=128, typed=True)
def parse_sip_message(message: str) -> dict:
    """ convert SIP message into SIP datagram.
    @message<str> -- SIP message.
    """
    if not message:
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
        # TODO: throw exception.
        return
    datagram["sip"]["Method"] = [method]

    # for the remaining headers, split by the first occurance of header and
    # definition CRLF and insert into the dynamic datagram. Since it's possible
    # to have multiple values for a given key (e.g. Via), temporarily store
    # the values as list.
    while queue:
        header = queue.popleft()
        try:
            assert not SDP_PATTERN.match(header)
            k, v = header.split(COLON, 1)
            datagram["sip"].setdefault(k, [])
            datagram["sip"][k].append(v.strip())
        except:
            # TODO: print error.
            pass

    # compress multiple SIP keys into single key.
    try:
        for (k, v) in list(datagram["sip"].items()):
            datagram_compressed["sip"].setdefault(k, [])
            datagram_compressed["sip"][k] = COMMA.join(v)
    except:
        # TODO: print error.
        pass

    # compress multiple SDP keys into single key.
    try:
        for (k, v) in list(datagram["sdp"].items()):
            datagram_compressed["sdp"].setdefault(k, [])
            datagram_compressed["sdp"][k] = CRLF.join([sdp for sdp in set(v)])
    except:
        # TODO: print error.
        pass

    return datagram_compressed


@lru_cache(maxsize=128, typed=True)
def convert_to_sip_message(template: str, datagram: dict) -> str:
    """ convert SIP datagram into SIP message.
    @template<str> -- SIP response template.
    @datagram<dict> -- SIP datagram.
    """
    if not template:
        return CRLF

    # reconstruct SIP message from datagram.
    message = "%s%s" % (template["status_line"], CRLF)
    try:
        message += CRLF.join([
            "%s: %s" % (sip_field, datagram["sip"].get(sip_field))
            for sip_field in template["sip"]
            if datagram["sip"].get(sip_field)
        ])
    except TypeError:
        logger.error("failed to parse using %s", datagram)
        return CRLF

    # reconstruct SDP message from datagram.
    if template.get("sdp"):
        message += "%s%s" % (CRLF, "Content-Type: application/sdp")
        sdp = CRLF.join(datagram.get("sdp"))
        sdp_length = str(len(sdp))
        message += "%s%s" % (CRLF, "Content-Length: " + sdp_length)
    else:
        message += "%s%s" % (CRLF, "Content-Length: 0")
    message += 2 * CRLF  # double CRLF to end section.

    # merge reconstructed SDP message with SIP message.
    if locals().get("sdp"):
        message += sdp

    # correct errors if exists.
    if not message.endswith(CRLF):
        message += CRLF

    return message
