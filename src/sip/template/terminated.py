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

__all__ = ["SIP_TERMINATE"]

# 21.4.25 487 Request Terminated
#
# The request was terminated by a BYE or CANCEL request.  This response
# is never returned for a CANCEL request itself.
#
# https://tools.ietf.org/html/rfc3261#section-21.4.25
SIP_TERMINATE = {
    "status_line": "SIP/%(sip_version)s 487 Request Terminated",
    "sip": [
        "Call-ID",
        "Contact",
        "From",
        "To",
        "Via",
    ],
}

SIP_TERMINATE_SAMPLE = """\
"""
