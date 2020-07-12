# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

class lazyproperty(object):
    """ lazy-initialize and cache a property """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        value = self.func(instance)
        setattr(instance, self.func.__name__, value)
        return value
