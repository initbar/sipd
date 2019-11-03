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

from __future__ import absolute_import
from collections import OrderedDict
from six.functools import wraps

try:
    import cPickle as pickle
except ImportError:
    import pickle


def lru_cache(maxsize=64):
    """ decorator implementation for caching function returns
    @size<int> -- max cache entry limit
    """
    size = max(1, size)
    queue = []
    cache = {}

    def memcache_impl(function):
        @wraps(function)
        def wrapper(*entry):
            key = pickle.dumps(entry)  # serialize the object.
            try:
                # every time a certain cached object is hit, escalate the
                # priority of that object by moving it to the top of cache.
                queue.insert(0, (queue.pop(queue.index(key))))
                return cache[key]
            except ValueError:
                # if cache is missed, then calculate the result and consider
                # the object to have extremely high priority.
                result = function(*entry)
                cache[key] = result
                queue.insert(0, key)

                # enforce size constraint and evict least-used objects.
                while len(queue) > size:
                    del cache[queue.pop()]
            return cache[key]
        return wrapper
    return memcache_impl


__all__ = ["lru_cache"]
