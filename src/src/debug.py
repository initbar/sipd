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
# debug.py -- debugging and helper function module.
#-------------------------------------------------------------------------------

from datetime import datetime
from uuid import uuid4 as UUID

import hashlib
import pprint
import sys

try:
    from src.optimizer import memcache
except ImportError: raise

# namespace
#-------------------------------------------------------------------------------
# https://tools.ietf.org/html/rfc4122.html

# generate a random UUID string.
create_random_uuid = lambda: UUID().__str__()

# hash
#-------------------------------------------------------------------------------
# https://tools.ietf.org/html/rfc4634

md5sum    = lambda plaintext: hashlib.md5(plaintext).hexdigest()
sha1sum   = lambda plaintext: hashlib.sha1(plaintext).hexdigest()
sha256sum = lambda plaintext: hashlib.sha256(plaintext).hexdigest()
sha512sum = lambda plaintext: hashlib.sha512(plaintext).hexdigest()

# timestamps
#-------------------------------------------------------------------------------
# https://tools.ietf.org/html/rfc1305

def time_in_ntp():
    now = datetime.utcnow() - datetime(1900, 1, 1, 0, 0, 0)
    ntp = now.seconds + (now.days * 0x15180) # 24 * 60 ** 2
    return str(ntp)

# packet dissection
#-------------------------------------------------------------------------------

pp      = pprint.PrettyPrinter(indent=2, width=80)
pformat = pp.pformat # localized function cache.

_stderr = sys.stderr.write # localized function cache.

_delim = '+-' * 40 # localized delimiter cache.

@memcache
def dissect_packet(packet):
    ''' pretty-print a text-based network packet.
    '''
    _stderr('\n'.join([ _delim, pformat(packet), _delim ]) + '\n')
