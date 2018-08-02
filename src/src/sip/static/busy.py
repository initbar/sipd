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

__all__ = ["SIP_BUSY"]

# 7.4.23 486 Busy Here
#
# The callee's end system was contacted successfully but the callee is
# currently not willing or able to take additional calls. The response
# MAY indicate a better time to call in the Retry-After header. The
# user could also be available elsewhere, such as through a voice mail
# service, thus, this response does not terminate any searches.  Status
# 600 (Busy Everywhere) SHOULD be used if the client knows that no
# other end system will be able to accept this call.
#
# https://tools.ietf.org/html/rfc2543#section-7.4.23
SIP_BUSY = {
    "status_line": "SIP/2.0 486 Busy Here",
    "sip": ["Contact"],
}

SIP_BUSY_SAMPLE = """
SIP/2.0 486 Busy Here
"""
