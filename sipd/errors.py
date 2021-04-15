# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.


class SipError(Exception): ...


class SipInvalidProtocol(SipError):
   """Invalid SIP protocol.

   Throw this exception when validating incoming SIP packets (e.g.
   invalid or non-existent SIP signature, mismatched SIP version,
   non-RFC methods, ..).
   """


class SipEncodingError(SipError):
    """Unable to encode/serialize SIP.

    Throw this exception when compiling python SIP datagram back into
    text-based SIP message and an error occurs.
    """


class SipDecodingError(SipError):
    """Unable to decode/deserialize SIP.

    Throw this exception when parsing text-based SIP message into SIP
    datagram and an error occurs.
    """
