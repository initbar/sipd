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
# server.py -- synchronous RTP routing module.
#-------------------------------------------------------------------------------

import logging
logger = logging.getLogger(__name__)

# RTP router
#-------------------------------------------------------------------------------

class RTPRouterPrototype(object):
    ''' RTP router prototype.
    '''
    def __init__(self, setting={}):
        self.setting = setting
        self.internal = self.external = False

        try: # configure internal handler.
            handler = self.setting['rtp']['handler']['internal']
            assert handler.get('enabled')
            self.host     = handler['host']
            self.port     = handler['port']
            self.protocol = handler['protocol']
            self._server  = tuple((self.host, self.port))
            self.internal = True
        except: pass

        try: # configure external handler.
            handler = self.setting['rtp']['handler']['external']
            assert handler.get('enabled')
            self.host     = handler['host']
            self.port     = handler['port']
            self.protocol = handler['protocol']
            self._server  = tuple((self.host, self.port))
            self.external = True
        except: pass

        self.tag = None # no active sessions yet.
        logger.debug('[rtp] successfully initialized.')

    def _internal_handler(self, *args, **kwargs):
        return

    def _external_handler(self, *args, **kwargs):
        return

    def handle(self, *args, **kwargs):
        # there can only one handler active at once. For that reason,
        # external handler takes precedence over internal handler.
        if self.external:   return self._external_handler(*args, **kwargs)
        elif self.internal: return self._internal_handler(*args, **kwargs)
        else: return
