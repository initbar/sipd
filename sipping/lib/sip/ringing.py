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
# https://github.com/initbar/sipping

__all__ = ["SIP_RINGING"]

# 21.1.2 180 Ringing
#
# The UA receiving the INVITE is trying to alert the user.  This
# response MAY be used to initiate local ringback.
#
# https://tools.ietf.org/html/rfc3261#section-21.1.2
SIP_RINGING = {
    "status_line": "SIP/%(sip_version)s 180 Ringing",
    "sip": [
        "Allow",
        "CSeq",
        "Call-ID",
        "Contact",
        "From",
        "Record-Route",
        "To",
        "Via",
    ],
}

SIP_RINGING_SAMPLE = """\
SIP/2.0 180 Ringing
CSeq: 1 INVITE
Call-ID: 9E565000-C50B-B39A-61A3-33FB67415050-7090@192.168.1.4
From: <sip:Genesys@192.168.1.4:7090>;tag=9E565000-C50B-45BE-9F69-DCFCE02B493D
To: <sip:record=2018-02-21:20-14-192.168.1.8:15060>
Via: SIP/2.0/UDP 192.168.1.8:15060;branch=z9hG4bK0x25b1a5408dd30fabcdef09,SIP/2.0/TCP 192.168.1.4:7090;branch=z9hG4bK0x194bd1008dd30f
Record-Route: <sip:0x196e3b00@192.168.1.8:15060;lr;gvp.rm.datanodes=1;confinstid=2018-02-21-192.168.1.8:15060;idtag=0000000C>
Contact: <sip:ImpactRecorder@192.168.1.9:5060;transport=udp>
Allow: INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO
Content-Length: 0
"""
