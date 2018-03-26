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

from copy import deepcopy

try:
    from src.parser import parse_json
    from src.parser import safe_encode
    from src.sockets import get_server_address
except ImportError: raise

def parse_config(config={}):
    ''' parse `sipd.json` and load/initialize with runtime environment.
    '''
    parsed_config = parse_json(config)
    if not parsed_config: return {}

    # save server address information to the configuration.
    server_address = str(get_server_address())
    parsed_config['sip']['server']['address'] = server_address

    # initialize SIP.
    try:
        sip_allow   = parsed_config['sip']['defaults']['Allow']
        sip_contact = parsed_config['sip']['defaults']['Contact']
        parsed_config['sip']['defaults']['Allow']   = ', '.join(sip_allow)
        parsed_config['sip']['defaults']['Contact'] = sip_contact % server_address
    except:
        parsed_config['sip']['defaults'] = {
            'Allow': 'ACK, BYE, CANCEL, INVITE, OPTIONS, REFER, UPDATE',
            'Contact': '<sip:%s:5060;transport=udp>' % server_address,
            'Max-Forwards': '70',
            'Min-SE': '1800',
            'Require': 'timer',
            'Server': 'sipd',
            'Session-Expires': '1800;refresher=uac',
            'Supported': 'timer'
        }

    return parsed_config
