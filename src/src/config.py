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
# config.py -- config parser, custom overrides, and default states.
#-------------------------------------------------------------------------------

from copy import deepcopy

try:
    from src.parser import parse_json
    from src.parser import safe_encode
    from src.sockets import get_server_address
except ImportError: raise

def parse_config(config={}):
    _config = parse_json(config)
    if not config: return {}

    server_address = str(get_server_address())
    try:
        # set server host ip address.
        _config['sip']['server']['address'] = server_address

        # merge Allow headers.
        try:
            _config['sip']['defaults']['Allow'] = ', '.join(_config['sip']['defaults']['Allow'])
        except:
            _config['sip']['defaults'] = {
                'Allow': ', '.join([
                    'ACK',
                    'BYE',
                    'CANCEL',
                    'INVITE',
                    'OPTIONS',
                    'REFER',
                    'UPDATE'
                ]),
                'Contact': '<sip:%s:5060;transport=udp>' % server_address,
                'Max-Forwards': '70',
                'Min-SE': '1800',
                'Require': 'timer',
                'Server': 'SIPd',
                'Session-Expires': '1800;refresher=uac',
                'Supported': 'timer'
            }
    except: raise
    return _config
