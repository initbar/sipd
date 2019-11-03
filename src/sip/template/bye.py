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

__all__ = ["SIP_BYE"]

# 4.2.4 BYE
#
# The user agent client uses BYE to indicate to the server that it
# wishes to release the call. A BYE request is forwarded like an INVITE
# request and MAY be issued by either caller or callee. A party to a
# call SHOULD issue a BYE request before releasing a call ("hanging
# up"). A party receiving a BYE request MUST cease transmitting media
# streams specifically directed at the party issuing the BYE request.
#
# If the INVITE request contained a Contact header, the callee SHOULD
# send a BYE request to that address rather than the From address.
#
# This method MUST be supported by proxy servers and SHOULD be
# supported by redirect and user agent SIP servers.
#
# https://tools.ietf.org/html/rfc2543#section-4.2.4
SIP_BYE = {
    "status_line": "SIP/%(sip_version)s BYE",
    "sip": [],
}

SIP_BYE_SAMPLE = """\
"""
