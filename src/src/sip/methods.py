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
# -------------------------------------------------------------------------------

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
