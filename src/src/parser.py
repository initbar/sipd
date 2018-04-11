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

#-------------------------------------------------------------------------------
# parser.py -- SIP message parser.
#-------------------------------------------------------------------------------

from collections import deque
from src.errors import SIPBrokenProtocol
from src.optimizer import memcache
from src.sip.methods import SIP_METHODS

import json
import re

import logging
logger = logging.getLogger()

# pre-compiled regex
#-------------------------------------------------------------------------------

REGX_IPV4 = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:\:\d{1,5})*')
REGX_SDP  = re.compile('^[a-z]{1}=.+$')

# string entities
#-------------------------------------------------------------------------------

COLON = ':'
COMMA = ','
CRLF = '\r\n'

def safe_encode(plaintext, encoding='utf-8'):
    ''' safely encode a string to `encoding` type.
    '''
    return plaintext.encode(encoding)

def safe_decode(plaintext, encoding='utf-8'):
    ''' safely decode a string to `encoding` type.
    '''
    return plaintext.decode(encoding)

# JSON entities
#-------------------------------------------------------------------------------

def parse_json(_json):
    ''' read JSON and return dictionary.
    '''
    return json.loads(safe_encode(_json))

def dump_json(_json):
    ''' read dictionary and return JSON.
    '''
    return safe_encode(json.dumps(_json))

# SIP entities
#-------------------------------------------------------------------------------

# check if SIP signature exists inside SIP message.
validate_sip_signature = lambda message: 'SIP' in str(message)

@memcache(size=128)
def convert_to_sip_packet(sip_template, sip_datagram):
    ''' convert human-readable text into ready-only SIP packet.
    '''
    if not sip_template:
        return CRLF

    # reconstruct SIP from datagram.
    packet = '%s%s' % (sip_template['status_line'], CRLF)
    packet += CRLF.join([
        '%s: %s' % (sip_field, sip_datagram['sip'].get(sip_field))
        for sip_field in sip_template['sip']
        if sip_datagram['sip'].get(sip_field) ])

    # reconstruct SDP from datagram.
    if sip_template.get('sdp'):
        packet += '%s%s' % (CRLF, 'Content-Type: application/sdp')
        sdp = CRLF.join(sip_datagram.get('sdp'))
        sdp_length = str(len(sdp))
        packet += '%s%s' % (CRLF, 'Content-Length: ' + sdp_length)
    else:
        packet += '%s%s' % (CRLF, 'Content-Length: 0')
    packet += (2 * CRLF) # double \r\n to end header section.

    # add SDP data.
    if locals().get('sdp'):
        packet += sdp

    # error correction.
    if not packet.endswith(CRLF):
        packet += CRLF
    return packet

@memcache(size=128)
def parse_sip_packet(sip_buffer):
    ''' deconstruct a SIP packet to a list of headers.
    '''
    if not (sip_buffer and isinstance(sip_buffer, basestring)):
        logger.warning('sip_buffer format is incorrect: ' + str(sip_buffer))
        return

    # allocate Pythonic object to interface with SIP headers. Originally, the
    # design was to whitelist known SIP headers into a SIP datagram using
    # SIPResponse and SIPRequest datagrams. However, since headers will be
    # unknown (as well as possibly volitile), the design was changed to
    # dynamically insert any keys extracted from single SIP packet.
    queue = deque(filter(None, sip_buffer.replace(CRLF, '\n').split('\n')))
    datagram = {
        'sip': {},
        'sdp': []
    }; datagram_compressed = datagram.copy()

    # rotate and parse each SIP headers. But first, since set intersection
    # operation is more computationally expensive than other search operations
    # - and since we already know that the first header will always indicate
    # SIP method - parse the method first.
    header = queue.popleft()
    try: method = (SIP_METHODS & set(header.split())).pop()
    except:
        logger.error(SIPBrokenProtocol(header))
        raise
    datagram['sip']['Method'] = [method]

    # for the remaining headers, split by the first occurance of header and
    # definition CRLF and insert into the dynamic datagram. Since it's possible
    # to have multiple values for a given key (e.g. Via), temporarily store
    # the values as list.
    while queue:
        header = queue.popleft()
        try:
            assert not REGX_SDP.match(header)
            k, v = header.split(COLON, 1)
            datagram['sip'].setdefault(k, [])
            datagram['sip'][k].append(v.strip())
        except:
            if header.startswith('o='):
                datagram['sdp'].append(header.strip())
            else: # discard rest.
                pass

    try: # compress multiple SIP keys into single key.
        for (k,v) in list(datagram['sip'].items()):
            datagram_compressed['sip'].setdefault(k, [])
            datagram_compressed['sip'][k] = COMMA.join(v)
    except: pass

    try: # compress multiple SDP keys into single key.
        for (k,v) in list(datagram['sdp'].items()):
            datagram_compressed['sdp'].setdefault(k, [])
            datagram_compressed['sdp'][k] = CRLF.join([ sdp for sdp in set(v) ])
    except: pass

    # return compressed datagram.
    return datagram_compressed
