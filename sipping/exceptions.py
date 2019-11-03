# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

"""
sipping.exceptions
------------------
"""


class BaseError(Exception):
    pass


#
# SIP
#


class SIPInvalidProtocol(BaseError):
    """ Invalid SIP protocol """
    # throw this exception when validating incoming SIP packets (e.g. invalid or
    # non-existent SIP signature, mismatched SIP version, non-RFC methods, ..


class SIPEncodingError(BaseError):
    """ Unable to encode/serialize SIP """
    # throw this exception when compiling python SIP datagram back into
    # text-based SIP message and an error occurs.


class SIPDecodingError(BaseError):
    """ Unable to decode/deserialize SIP """
    # throw this exception when parsing text-based SIP message into SIP datagram
    # and an error occurs.
