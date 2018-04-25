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
        @history<deque> -- limited record of most recently seen Call-ID.
        @meta<dict> -- dynamically-allocated metadata for `self.history`.
        @count<int> -- general statistics of total received calls.
        '''
        self.history = deque(maxlen=4096)
        self.meta = limited_dict(maxsize=len(self.history))
        self.count = 0 # only increment.

    def increment(self):
        self.count += 1

class AsynchronousGarbageCollector(object):
    ''' asynchronous garbage collector implementation.
    '''
    def __init__(self, settings={}):
        '''
        @settings<dict> -- `sipd.json`
        '''
        self.settings = settings

        try: # load garbage collector run-interval.
            self.check_interval = float(settings['gc']['check_interval'])
        except:
            self.check_interval = 1e-2 # seconds
        finally:
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
        gc = threading.Thread(
            name='garbage-collector',
            target=create_thread)
        self.__thread = gc
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

        # since the garbage is a FIFO, technically, the oldest call is pushed
        # first (top) and the youngest call is pushed last (bottom).
        try:
            now = int(time.time())
            while now >= self.garbage[0]['ttl']:
                # `get` method in Queue is destructive. Unlike a general lookup,
                # `get` pops the first element and returns that element. If the
                # conditions for garbage consumption is not satisfied, the popped
                # element must be placed back inside the garbage.
                peek = self.garbage.popleft()
                call_id = self.membership[peek['Call-ID']]
                self.consume_membership(call_id=peek['Call-ID'], call_tag=peek['tag'])
        except Exception as message:
            self.garbage.append(peek)
            logger.error('<gc>:unable to cleanly collect garbage: %s.' % str(message))
        finally:
            self.is_ready = True # release thread.

    def consume_membership(self, call_id, call_tag, forced=False):
        ''' consume a call from membership.
        '''
        # since it is possible that there are multiple sessions ("tag") with
        # same Call-ID, consume membership by tags first and then by Call-ID.
        try:
            if call_id not in self.membership: return
            self.membership[call_id]['tags_cnt'] -= 1
            if any([ self.membership[call_id]['tags_cnt'] <= 0,
                     self.membership[call_id]['state'] == 'BYE',
                     forced ]): # consumption conditions.
                self.rtp.send_stop_signal(call_id)
                del self.membership[call_id]
                logger.info('<gc>:safe revoke member: %s' % call_id)
        except Exception as message:
            logger.error('<gc>:failed consumption: %s' % str(message))
