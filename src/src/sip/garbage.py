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

from collections import deque

import threading
import time

try: import Queue             # Python 2
except: import queue as Queue # Python 3

try:
    from src.rtp.server import SynchronousRTPRouter
except ImportError: raise

import logging
logger = logging.getLogger()

#-------------------------------------------------------------------------------
# gc.py -- synchronous SIP garbage collection module.
#-------------------------------------------------------------------------------

class SynchronousSIPGarbageCollector(object):
    ''' Asynchronous SIP garbage collection component implementation.
    '''
    def __init__(self, settings={}):

        # to maintain historical statistics w/o degrading performance, we want
        # to keep hashes of all incoming Call-ID and lookup time at O(1).
        # Since it's expensive to re-calculate the length at each iteration,
        # store call counts separately. A call count should only be incremented
        # by distinct SIP 'INVITE'.
        self.calls_history = {}
        self.calls_stats = 0
        self.membership = {}

        # garbage is collected under self._garbage. In order to reduce thread
        # conflict with the main thread, garbage collector uses its own
        # thread. By default, garbage collector runs once every minute.
        try: self._gc_interval = float(settings['gc']['check_interval'])
        except: self._gc_interval = 60.0 # seconds
        self._gc = self.initialize_garbage_collector()
        self._gc_locked = False # "thread lock"
        self._garbage = deque()

        # since a locked collector should not receive new blocking tasks,
        # any new "tasks" are polled under self._futures object.
        self._futures = Queue.Queue() # thread-safe FIFO.

        # custom RTP handler for garbage clean up.
        self._rtp_handler = SynchronousRTPRouter(settings)
        logger.info('<gc>:successfully initialized garbage collector.')

    def initialize_garbage_collector(self):
        ''' initialize a new thread for garbage collector.
        '''
        if self.__dict__.get('_gc'):
            return self._gc # error check.
        def initialization():
            thread_event = threading.Event()
            while not thread_event.wait(self._gc_interval):
                self.consume_garbage()
        gc = threading.Timer(self._gc_interval, initialization)
        gc.daemon = True
        gc.start()
        return gc

    def register_new_task(self, function):
        ''' register a new collection task.
        '''
        # instead of directly manipulating garbage, demultiplex garbage tasks
        # into a single thread-safe queue and consume in order later.
        try:
            self._futures.put(item=function)
        except:
            raise

    def consume_garbage(self):
        ''' consume garbage.
        '''
        if self.is_locked() or self._futures.empty(): return
        else: self._gc_locked = True # lock thread.

        # catch up on delinquent deferred tasks inside polled queue.
        while not self._futures.empty():
            run_task = self._futures.get()
            run_task() # deferred execute.
            logger.debug('<gc>:executed deferred task: %s', run_task)

        # since the garbage is a FIFO, technically, the oldest call is pushed
        # first (top) and the youngest call is pushed last (bottom).
        try:
            now = int(time.time())
            while now >= self._garbage[0]['ttl']:
                # `get` method in Queue is destructive. Unlike a general lookup,
                # `get` pops the first element and returns that element. If the
                # conditions for garbage consumption is not satisfied, the popped
                # element must be placed back inside the garbage.
                peek    = self._garbage.popleft()
                call_id = self.membership[peek['Call-ID']]
                self.consume_membership(call_id=peek['Call-ID'], call_tag=peek['tag'])
        except Exception as message:
            self._garbage.append(peek)
            logger.error('<gc>:unable to cleanly collect garbage: %s.' % str(message))
        finally:
            self._gc_locked = False # release thread.

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
                self._rtp_handler.send_stop_signal(call_id)
                del self.membership[call_id]
                logger.info('<gc>:safe revoke member: %s' % call_id)
        except Exception as message:
            logger.error('<gc>:failed consumption: %s' % str(message))

    def is_locked(self):
        ''' check if garbage collector is locked.
        '''
        return self._gc_locked

    def is_free(self):
        ''' check if garbage collector is free.
        '''
        return not self.is_locked()
