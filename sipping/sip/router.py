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
# https://github.com/initbar/sipping

"""
router.py
---------
"""

from __future__ import absolute_import
from abc import abstractmethod
from abc import abstractproperty
from multiprocessing import Process
from multiprocessing import cpu_count

import asyncore
import attr
import logging
import random

from lib.coroutine import coroutine
from sip.worker import SipWorker

logger = logging.getLogger()


class PacketRouter(asyncore.dispatcher):
    """ Base packet router """

    def __repr__(self):
        return "PacketRouter(settings=%s, socket=%s, workers=%s)" % (
            self.settings,
            self.socket,
            self.workers,
        )

    def __str__(self):
        return self.__repr__().__str__()

    @abstractmethod
    def route(self):
        raise NotImplementedError


class AsynchronousUDPRouter(PacketRouter):
    """ Asynchronous UDP packet router """

    def __init__(self, settings=None, socket=None):
        asyncore.dispatcher.__init__(self, socket)
        self.settings = settings
        self.socket = socket

    def __repr__(self):
        return "AsynchronousUDPRouter(settings=%s, socket=%s, workers=%s)" % (
            self.settings,
            self.socket,
            self.workers,
        )

    def handle_read(self):
        try:
            packet = self.recvfrom(0xffff)  # max bytes
            endpoint, message = tuple(packet[1]), str(packet[0])
            self.demultiplexer.send((endpoint, message))
        except EOFError:
            pass

    @property
    @coroutine
    def demultiplexer(self, *a, **kw):
        while True:
            message = yield
            random.choice(self.workers).enqueue(message)

    def standby(self, *a, **kw):
        # initialize and limit workers to the total number of CPU cores.
        # If worker processes exceed the total core count, then performance
        # benefits are minimal or even detrimental.
        worker_count = min(max(1, self.settings["server"]["worker"]), cpu_count())
        if worker_count != self.settings["server"]["worker"]:
            logger.warning("throttled worker count to '%s'.", worker_count)

        # wrap each workers in its own sub-process.
        self.workers = [SipWorker(name="worker-%s" %i) for i in range(worker_count)]
        self._workers = []
        for worker in self.workers:
            process = Process(name=worker.name, target=worker.standby)
            process.daemon = True
            process.start()
            self._workers.append(process)
            logger.info("successfully created '%s'.", worker.name)
            logger.debug("worker: %s", worker)


__all__ = ["AsynchronousUDPRouter", "PacketRouter"]
