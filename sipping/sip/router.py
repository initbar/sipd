# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipping
#
# This source code is licensed under the MIT license.

"""
sipping.sip.router
------------------
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
