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

__all__ = ["SIP_OPTIONS"]

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
SIP_OPTIONS = {
    "status_line": "OPTIONS sip:%(dest_ip)s:%(dest_port)s SIP/2.0",
    "sip": [
        "Allow",
        "Call_Id",
        "From",
        "Max-Forwards",
        "Supported",
        "To",
        "Via",
    ],
}

SIP_OPTIONS_SAMPLE = """
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
"""
