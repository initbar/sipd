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
# -------------------------------------------------------------------------------

SIP_BUSY = {"status_line": "SIP/2.0 486 Busy Here", "sip": ["Contact"]}

SIP_BUSY_SAMPLE = """\
SIP/2.0 486 Busy Here
"""
