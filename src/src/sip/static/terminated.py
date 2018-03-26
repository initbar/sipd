# Active recording Session Initiation Protocol daemon (SIPd).
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
# https://github.com/initbar/SIPd

#-------------------------------------------------------------------------------
# 21.4.25 487 Request Terminated
#
# The request was terminated by a BYE or CANCEL request.  This response
# is never returned for a CANCEL request itself.
#
# https://tools.ietf.org/html/rfc3261#section-21.4.25
#-------------------------------------------------------------------------------

SIP_TERMINATE = {
    'status_line': 'SIP/2.0 487 Request Terminated',
    'sip': [
        'From',
        'To',
        'Via',
        'Call-ID',
        'Contact'
    ]
}

SIP_TERMINATE_SAMPLE = ''
