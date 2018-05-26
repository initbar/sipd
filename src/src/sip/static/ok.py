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

# -------------------------------------------------------------------------------
# 7.2.1 200 OK
#
# The request has succeeded. The information returned with the response
# depends on the method used in the request, for example:
#
# BYE: The call has been terminated. The message body is empty.
#
# CANCEL: The search has been cancelled. The message body is empty.
#
# INVITE: The callee has agreed to participate; the message body
#         indicates the callee's capabilities.
#
# OPTIONS: The callee has agreed to share its capabilities, included in
#          the message body.
#
# REGISTER: The registration has succeeded. The client treats the
#           message body according to its Content-Type.
#
# https://tools.ietf.org/html/rfc2543#section-7.2.1
# -------------------------------------------------------------------------------

SIP_OK = {
    "status_line": "SIP/2.0 200 OK",
    "sdp": True,
    "sip": [
        "Via",
        "From",
        "To",
        "CSeq",
        "Max-Forwards",
        "Call-ID",
        "Contact",
        "Supported",
        "Require",
        "Session-Expires",
        "Server",
        "Allow",
        "Min-SE",
    ],
}

SIP_OK_NO_SDP = {
    "status_line": "SIP/2.0 200 OK",
    "sip": [
        "Via",
        "From",
        "To",
        "CSeq",
        "Max-Forwards",
        "Call-ID",
        "Contact",
        "Supported",
        "Require",
        "Session-Expires",
        "Server",
        "Allow",
        "Min-SE",
    ],
}

SIP_OK_SAMPLE = """\
SIP/2.0 200 OK
Allow: ACK, BYE, CANCEL, INVITE, OPTIONS, UPDATE
Call-ID: 9E565000-C50B-90B0-2119-BE6C9297421D-7090@192.168.1.3
Contact: <sip:192.168.1.2;transport=udp>
CSeq: 1 INVITE
From: <sip:Genesys@192.168.1.3:7090>;tag=9E565000-C50B-88B0-71C6-533AEE26FF83
Supported: timer, uui
To: <sip:record=2018-02-28:16-30-192.168.1.4:15060>;
Via: SIP/2.0/UDP 192.168.1.4:15060;
Content-Type: application/sdp
Content-Length: 381

v=0
o=- 1269036923 0 IN IP4 192.168.1.3
s=phone-call
t=0 0
a=rtpmap:18 g729/8000
a=fmtp:18 annexb=no
a=ptime:20
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=sendonly
a=rtpmap:18 g729/8000
a=fmtp:18 annexb=no
a=ptime:20
a=rtpmap:101 telephone-event/8000
a=fmtp:101 0-15
a=sendonly
c=IN IP4 192.168.1.5
m=audio 6000 RTP/AVP 18 101
m=audio 6001 RTP/AVP 18 101
"""
