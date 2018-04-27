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
# 7.1.1 100 Trying
#
# Some unspecified action is being taken on behalf of this call (e.g.,
# a database is being consulted), but the user has not yet been
# located.
#
# https://tools.ietf.org/html/rfc2543#section-7.1.1
#-------------------------------------------------------------------------------

SIP_TRYING = {
    'status_line': 'SIP/2.0 100 Trying',
    'sip': [
        'CSeq',
        'From',
        'To',
        'Via',
        'Call-ID',
        'Allow',
        'Contact'
    ]
}

SIP_TRYING_SAMPLE = ''
