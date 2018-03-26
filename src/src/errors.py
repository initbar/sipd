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
# errors.py -- custom error suite.
#-------------------------------------------------------------------------------

# SIP
#-------------------------------------------------------------------------------

class SIPError(Exception):
    ''' default SIP error.
    '''
    def __init__(self, *args):
        super(SIPError, self).__init__(*args)
        self.args = args

class SIPBrokenProtocol(SIPError):
    ''' invalid SIP message format.
    '''
    pass

class SIPPackError(SIPError):
    ''' SIP message to Python object parsing error.
    '''
    pass

class SIPUnpackError(SIPError):
    ''' Python object to SIP message conversion error.
    '''
    pass
