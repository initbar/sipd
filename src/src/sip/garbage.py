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
from src.optimizer import restricted_dict
from src.rtp.server import SynchronousRTPRouter

logger = logging.getLogger()

#-------------------------------------------------------------------------------
# gc.py -- synchronous garbage collection module.
#-------------------------------------------------------------------------------

class SynchronousGarbageCollector(object):
    ''' Asynchronous garbage collection component implementation.
    '''
    def __init__(self, settings={}):
        self.settings = settings

        self.garbage = deque(maxlen=8192) # temporary call queue for eviction.
        self._tasks = Queue() # deferred function queue for execution.

        # statistics
        self.rtp = SynchronousRTPRouter(settings)
        self.statistic = 0

        # garbage is collected under self._garbage. In order to reduce thread
        # conflict with the main thread, garbage collector uses its own
        # thread. By default, garbage collector runs once every minute.
        try:
            self.check_interval = float(settings['gc']['check_interval'])
        except:
            self.check_interval = 60.0 # seconds

        self.locked = False # thread management.
        self.initialize_garbage_collector()
        logger.info('<gc>:successfully initialized garbage collector.')

    def initialize_garbage_collector(self):
        ''' initialize a new thread for garbage collector.
        '''
        def maintain():
            while True:
                time.sleep(self.check_interval)
                self.consume_garbage()
        gc = threading.Thread(
            name='maintenance',
            target=maintain)
        self.gc = gc
        self.gc.daemon = True
        self.gc.start()

    def register_new_task(self, deferred_task):
        ''' register a new collection task.
        '''
        # instead of directly manipulating garbage, demultiplex garbage tasks
        # into a single thread-safe queue and consume in order later.
        if deferred_task is None:
            return
        self._tasks.put(item=deferred_task)

    def consume_garbage(self):
        ''' consume garbage.
        '''
        if self.locked or self._tasks.empty():
            return
        else:
            self.locked = True # lock thread.

        # catch up on delinquent deferred tasks inside polled queue.
        while not self._tasks.empty():
            run_task = self._tasks.get()
            try:
                run_task() # deferred execute.
                logger.debug('<gc>:executed deferred task: %s', run_task)
            except TypeError:
                logger.error("<gc>:expected task: received nothing.")

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
            self.locked = False # release thread.

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
