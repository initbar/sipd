# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

# 4.2 Methods
#
# The methods are defined below. Methods that are not supported by a
# proxy or redirect server are treated by that server as if they were
# an OPTIONS method and forwarded accordingly. Methods that are not
# supported by a user agent server or registrar cause a 501 (Not
# Implemented) response to be returned (Section 7). As in HTTP, the
# Method token is case-sensitive.
#
#     Method  =  "INVITE" | "ACK" | "OPTIONS" | "BYE"
#                | "CANCEL" | "REGISTER"
#
# https://tools.ietf.org/html/rfc2543#section-4.2
SIP_METHODS = {
    "ACK",
    "BYE",
    "CANCEL",
    "INFO",
    "INVITE",
    "MESSAGE",
    "NOTIFY",
    "OK",
    "OPTIONS",
    "PRACK",
    "PUBLISH",
    "REFER",
    "REGISTER",
    "SUBSCRIBE",
    "UPDATE",
}
