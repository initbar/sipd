# MIT License
#
# Copyright (c) 2018 Herbert Shin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://github.com/initbar/sipd

# -------------------------------------------------------------------------------
# optimizer.py -- common optimization modules.
# -------------------------------------------------------------------------------

try:
    import cPickle as pickle
except ImportError:
    import pickle

from collections import OrderedDict
from functools import wraps

# memoization technique
# -------------------------------------------------------------------------------


def memcache(size=64):
    """ decorator implementation for caching function returns.
    @size<int> -- max cache entry limit.
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


# limited dictionary
# -------------------------------------------------------------------------------


class limited_dict(OrderedDict):

    def __init__(self, *a, **kw):
        self.limit = kw.pop("maxsize", None)
        OrderedDict.__init__(self, *a, **kw)

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self.__check()

    def __check(self):
        if self.limit is not None:
            while len(self) > self.limit:
                self.popitem(last=False)
