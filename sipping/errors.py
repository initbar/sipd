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

"""
errors.py
---------
"""


class BaseError(Exception):
    pass


#
# SIP
#


class SIPInvalidProtocol(BaseError):
    # throw this exception when validating incoming SIP packets (e.g. invalid or
    # non-existent SIP signature, mismatched SIP version, non-RFC methods, ..
    pass


class SIPEncodingError(BaseError):
    # throw this exception when compiling python SIP datagram back into
    # text-based SIP message and an error occurs.
    pass


class SIPDecodingError(BaseError):
    # throw this exception when parsing text-based SIP message into SIP datagram
    # and an error occurs.
    pass


__all__ = [
    "SIPDecodingError",
    "SIPEncodingError",
    "SIPInvalidProtocol",
]
