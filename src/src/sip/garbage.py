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

import logging
import threading
import time

from collections import deque
from multiprocessing import Queue
from src.logger import ContextLogger
from src.optimizer import limited_dict
from src.rtp.server import SynchronousRTPRouter

logger = ContextLogger(logging.getLogger())

#-------------------------------------------------------------------------------
# gc.py
#-------------------------------------------------------------------------------

class CallContainer(object):
    ''' call information container.
    '''
    def __init__(self):
        '''
        @history<deque> -- record of managed Call-ID by garbage collector.
        @meta<dict> -- dynamically-allocated metadata for `self.history`.
        @count<int> -- general statistics of total received calls.
        '''
        self.history = deque()
        self.meta = {} # contains CallMetadata objects indexed by Call-ID.
        self.count = 0 # only increment.

    def increment(self):
        self.count += 1

class CallMetadata(object):
    ''' call metadata container.
    '''
    def __init__(self, expiration):
        self.expiration = expiration
        # TODO: add more.

class AsynchronousGarbageCollector(object):
    ''' asynchronous garbage collector implementation.
    '''
    def __init__(self, settings={}):
        '''
        @settings<dict> -- `sipd.json`
        '''
        self.settings = settings
        self.check_interval = float(settings['gc']['check_interval'])
        self.call_lifetime = float(settings['gc']['call_lifetime'])
        self.initialize_garbage_collector()

        # call information and metadata.
        self.calls = CallContainer()
        self.rtp = None

        # instead of directly manipulating garbage using multiple threads,
        # demultiplex tasks into a thread-safe queue and consume later.
        self.__tasks = Queue()

        self.is_ready = True # recyclable state.
        logger.info('<gc>:successfully initialized garbage collector.')

    def initialize_garbage_collector(self):
        ''' create a garbage collector thread.
        '''
        def create_thread():
            while True:
                time.sleep(self.check_interval)
                self.consume_tasks()
        thread = threading.Thread(
            name='garbage-collector',
            target=create_thread)
        self.__thread = thread
        self.__thread.daemon = True
        self.__thread.start()

    def queue_task(self, function):
        ''' demultiplex a new future garbage collector task.
        '''
        if function is None:
            return
        self.__tasks.put(item=function)

    def consume_tasks(self):
        ''' consume garbage.
        '''
        if not self.is_ready or self.__tasks.empty():
            return
        self.is_ready = False # thread is busy.

        # consume deferred tasks.
        while not self.__tasks.empty():
            try:
                task = self.__tasks.get()
                task() # deferred execution.
                logger.debug('<gc>:executed deferred task: %s', task)
            except TypeError:
                logger.error("<gc>:expected task: received %s", task)

        try: # remove expired calls.
            now = int(time.time())
            # since the call history is FIFO, the oldest call is placed on top
            # and the youngest call is placed on the bottom of the queue.
            for call_id in self.calls.history:
                meta = self.calls.meta[call_id]

        except Exception as message:
            self.garbage.append(peek)
            logger.error('<gc>:unable to cleanly collect garbage: %s.' % str(message))
        finally:
            self.is_ready = True # release thread.

    def register(self, call_id):
        pass
