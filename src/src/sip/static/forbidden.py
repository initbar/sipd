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
# 21.4.4 403 Forbidden
#
# The server understood the request, but is refusing to fulfill it.
# Authorization will not help, and the request SHOULD NOT be repeated.#
# -------------------------------------------------------------------------------

SIP_RINGING = {"status_line": "SIP/2.0 403 Forbidden", "sip": ["Contact"]}

SIP_RINGING_SAMPLE = """\
SIP/2.0 403 Forbidden
"""
