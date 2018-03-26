
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

#
# optimizer.py -- common optimization modules.
#

from functools import wraps

# memoization
#-------------------------------------------------------------------------------

def memcache(function):
    ''' cache function return values for faster return.
    note: use as `@memcache` decorator.
    '''
    memcache = {}
    memcache_size = 0
    memcache_max = 64
    @wraps(function)
    def wrapper(*entry):
        # make sure cache has upper memory limit.
        if memcache_size >= memcache_max:
            memcache_size = 0
            memcache.clear()
        if entry in memcache: # hit.
            return memcache.get(entry)
        else: # miss.
            _ = function(*entry)
            memcache[entry] = _
            memcache_size += 1
            return _
    return wrapper
