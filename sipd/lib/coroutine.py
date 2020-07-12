# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

def coroutine(func):
    """ convert a function into a coroutine """
    def impl(*a, **kw):
        cr = func(*a, **kw)
        next(cr)
        return cr
    return impl
