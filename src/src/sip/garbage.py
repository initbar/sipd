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
from src.rtp.server import SynchronousRTPRouter

# from multiprocessing import Queue
try:
    from Queue import Queue
except ImportError:
    from queue import Queue

logger = logging.getLogger()

#-------------------------------------------------------------------------------
# gc.py
#-------------------------------------------------------------------------------

class CallContainer(object):
    ''' call information container.
    '''
    def __init__(self):
        '''
        @history<deque> -- record of managed Call-ID by garbage collector.
        @metadata<dict> -- CallMetadata objects index by Call-ID in history.
        @count<int> -- general statistics of total received calls.
        '''
        self.history = deque(maxlen=(0xffff - 6000) / 2)
        self.metadata = {}
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
        if function:
            self.__tasks.put(item=function)

    def consume_tasks(self):
        ''' consume demultiplexed garbage collector tasks.
        '''
        if not self.is_ready or self.__tasks.empty():
            return
        self.is_ready = False # garbage collector is busy.

        if self.rtp is None:
            self.rtp = SynchronousRTPRouter(self.settings)

        # consume deferred tasks.
        while not self.__tasks.empty():
            try:
                task = self.__tasks.get()
                task() # deferred execution.
                logger.debug('<gc>:executed deferred task: %s', task)
            except TypeError:
                logger.error("<gc>:expected task: received %s", task)

        now = int(time.time())
        try: # remove calls from management.
            for _ in self.calls.history:
                # since call queue is FIFO, the oldest call is placed on top
                # (left) and the youngest call is placed on the bottom (right).
                call_id = self.calls.history.popleft()
                # if there is no metadata aligned with Call-ID or the current
                # Call-ID has already expired, then force the RTP handler to
                # relieve ports allocated for Call-ID.
                metadata = self.calls.metadata.get(call_id)
                if not metadata:
                    self.rtp.send_stop_signal(call_id=call_id)
                    continue
                if now > metadata.expiration:
                    self.revoke(call_id=call_id)
                # since the oldest call is yet to expire, that means remaining
                # calls also don't need to be checked.
                else:
                    self.calls.history.appendleft(call_id)
                    break
        except AttributeError:
            self.rtp = None # unset to re-initialize at next iteration.
        finally:
            self.is_ready = True # garbage collector is available.

    def register(self, call_id):
        ''' register Call-ID and its' metadata.
        '''
        if call_id is None or call_id in self.calls.history:
            return
        metadata = CallMetadata(expiration=time.time() + self.call_lifetime)
        self.calls.history.append(call_id)
        self.calls.metadata[call_id] = metadata

    def revoke(self, call_id):
        ''' force remove Call-ID and its' metadata.
        '''
        if call_id is None:
            return
        if self.calls.metadata.get(call_id):
            logger.debug("<gc>:removing Call-ID '%s'", call_id)
            self.rtp.send_stop_signal(call_id=call_id)
            del self.calls.metadata[call_id]
