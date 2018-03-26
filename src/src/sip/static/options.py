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

#-------------------------------------------------------------------------------
# 4.2.3 OPTIONS
#
# The server is being queried as to its capabilities. A server that
# believes it can contact the user, such as a user agent where the user
# is logged in and has been recently active, MAY respond to this
# request with a capability set. A called user agent MAY return a
# status reflecting how it would have responded to an invitation, e.g.,
# 600 (Busy). Such a server SHOULD return an Allow header field
# indicating the methods that it supports. Proxy and redirect servers
# simply forward the request without indicating their capabilities.
#
# This method MUST be supported by SIP proxy, redirect and user agent
# servers, registrars and clients.
#
# https://tools.ietf.org/html/rfc2543#section-4.2.3
#-------------------------------------------------------------------------------

SIP_OPTIONS = {
    'status_line': 'OPTIONS sip:%(dest_ip)s:%(dest_port)s SIP/2.0',
    'sip': [
        'Allow',
        'Call_Id',
        'From',
        'Max-Forwards',
        'Supported'
        'To',
        'Via',
    ]
}

SIP_OPTIONS_SAMPLE = '''\
OPTIONS sip:192.168.1.6:5060 SIP/2.0
Via: SIP/2.0/UDP 192.168.1.3:15064;branch=z9hG4bK0x2473c35084b6b1
From: <sip:GVP@192.168.1.3:15064>;tag=9E565000-FB73-C996-4E01-0810C8DE0CF4
To: sip:192.168.1.6:5060
Max-Forwards: 70
CSeq: 307103 OPTIONS
Call-ID: 9E565000-FB73-F13E-6076-D8822FB9A4E4-15064@192.168.1.3
Contact: <sip:GVP@192.168.1.3:15064>
Content-Length: 0
Allow: INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO
Supported: timer, uui
'''
