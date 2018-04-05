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
# config.py -- config parser, custom overrides, and default states.
#-------------------------------------------------------------------------------

try:
    from src.parser import parse_json
    from src.sockets import get_server_address
except ImportError: raise

import logging
logger = logging.getLogger(__name__)

def parse_config(config={}):
    ''' parse `sipd.json` and load/initialize with runtime environment.
    '''
    try:
        parsed_config = parse_json(config)
        assert parsed_config

        # save server address information to the configuration.
        server_address = get_server_address()
        parsed_config['sip']['server']['address'] = server_address
        logger.debug("server address set to '%s'" % server_address)

        return parsed_config
    except:
        return {}
