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

#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------

SIP_BYE = {
    'status_line': 'SIP/2.0 BYE',
    'sip': []
}


SIP_BYE_SAMPLE = '''\
'''
