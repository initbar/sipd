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

#-------------------------------------------------------------------------------
# server.py
#-------------------------------------------------------------------------------

import asyncore
import errno
import logging
import random
import sys
import time

from collections import deque
from multiprocessing import Process
from multiprocessing import cpu_count
from src.sip.garbage import SynchronousSIPGarbageCollector
from src.sip.worker import LazySIPWorker
from src.sockets import unsafe_allocate_udp_socket
from threading import Thread

logger = logging.getLogger()

SERVER_SETTINGS = None # `sipd.json`

# each worker should not instantiate a new garbage collector since a subsequent
# related requests can not guarantee to hit the same worker. Therefore, the
# workers should all use the same garbage collector and just register a new
# collection tasks to the collector queue.
GARBAGE_COLLECTOR = None

class safe_allocate_sip_socket(object):
    ''' allocate exception-safe listening SIP socket.
    '''
    def __init__(self, port=5060):
        ''' SIP socket allocator implementation.
        @port<int> -- SIP receiving port number.
        '''
        self.__port = port
        self.__socket = None

    @property
    def port(self):
        ''' port getter.
        '''
        return self.__port

    @port.setter
    def port(self, number):
        ''' port setter.
        @number<int> -- SIP receiving port number.
        '''
        number = int(number)
        if not 1024 < number < 65535:
            logger.critical("<sip>:cannot use privileged ports: '%i'", number)
            sys.exit(errno.EPERM)
        self.__port = number

    def __enter__(self):
        self.__socket = unsafe_allocate_udp_socket('0.0.0.0', self.port, is_reused=True)
        return self.__socket

    def __exit__(self, *a, **kw):
        try: self.__socket.close()
        except AttributeError:
            pass # already closed
        del self.__socket

# server
#-------------------------------------------------------------------------------

class AsynchronousSIPServer(object):
    ''' Asynchronous SIP server to initialize router and globalize settings.
    '''
    def __init__(self, setting):
        if not setting:
            logger.critical('<server>:failed to initialize SIP server.')
            sys.exit(errno.EINVAL)
        global SERVER_SETTINGS
        global GARBAGE_COLLECTOR
        SERVER_SETTINGS = setting
        GARBAGE_COLLECTOR = SynchronousSIPGarbageCollector(setting)
        logger.info('<server>:successfully initialized SIP server.')

    @classmethod
    def serve(cls):
        try:
            sip_port = SERVER_SETTINGS['sip']['router']['port']
        except KeyError:
            sip_port = 5060 # udp
        # assign asynchronous handler to the receiving SIP port. Currently,
        # `asyncore` module was chosen in order to provide backward
        # compatibility with Python 2 (where there's no `asyncio`). All
        # incoming traffic is routed and initially handled by the router.
        with safe_allocate_sip_socket(sip_port) as sip_socket:
            cls.router = AsynchronousSIPRouter(sip_socket)
            cls.router.initialize_demultiplexer()
            cls.router.initialize_consumer()
            logger.info('<server>:successfully initialized SIP router.')
            asyncore.loop() # push new events to the event loop.

# router
#-------------------------------------------------------------------------------

def deploy_worker_thread(worker_pool, endpoint, message):
    ''' deploy a worker thread to handle work.
    @worker_pool<list> -- a pool of worker instances.
    @endpoint<tuple> -- SIP endpoint.
    @message<str> -- SIP message.
    '''
    worker = random.choice(worker_pool)
    if worker.is_ready:
        worker_thread = Thread(
            name=worker.name,
            target=worker.handle,
            args=(endpoint, message)
        )
    else: # if no workers are ready, create a temporary worker.
        worker = LazySIPWorker(
            settings=SERVER_SETTINGS,
            gc=GARBAGE_COLLECTOR)
        worker_thread = Thread(
            name=worker.name,
            target=worker.handle,
            args=(endpoint, message)
        )
    worker_thread.daemon = True
    worker_thread.start()
    return worker_thread

class AsynchronousSIPRouter(asyncore.dispatcher):
    ''' Asynchronous SIP router to demultiplex and delegate work to workers.
    '''
    def __init__(self, sip_socket):
        # in order to prevent double creation of a router socket, inherit
        # SIP port from SIP server. A router should only be used to receive
        # traffic from the remote endpoint.
        asyncore.dispatcher.__init__(self, sip_socket)

        # override to read-only.
        self.is_readable = True
        self.readable = lambda: self.is_readable
        # self.handle_read = lambda: None

        # override to disable write.
        self.is_writable = False
        self.writable = lambda: self.is_writable
        self.handle_write = lambda: None

        try: # calculate worker pool size.
            self.__pool_size = SERVER_SETTINGS['sip']['worker']['count']
            if self.__pool_size <= 0:
                self.__pool_size = cpu_count()
        except KeyError:
            self.__pool_size = 1

    def handle_read(self):
        try: # router only receives data ("work") and delegate to worker(s).
            packet = self.recvfrom(0xffff) # max receive bytes.
            endpoint, message = tuple(packet[1]), str(packet[0])
            self.__demux.put((endpoint, message)) # demultiplex.
        except EOFError:
            pass

    def initialize_consumer(self):
        ''' initialize consumer thread.
        '''
        if not self.__demux:
            logger.critical("<router>:failed to initialize router demultiplexer.")
            sys.exit(errno.EAGAIN)

        worker_queue = deque(maxlen=(self.__pool_size * 2))
        worker_pool = [ # pre-generated workers.
            LazySIPWorker(worker_name, SERVER_SETTINGS, GARBAGE_COLLECTOR)
            for worker_name in range(self.__pool_size)
        ]
        logger.info("<router>:pre-generated worker pool: %s", worker_pool)

        # function closure to initialize workers and take demultiplexed "work".
        def consume():
            while True:
                # if queue is overflowing with processes, then wait until we
                # escape the pool size limitation set by the configuration.
                if self.__demux.empty() or len(worker_queue) >= self.__pool_size:
                    time.sleep(1e-2)
                    continue
                # ensure no workers are generated more than available work.
                worker_size = min(self.__demux.qsize(), self.__pool_size)
                for _ in range(worker_size):
                    endpoint, message = self.__demux.get()
                    worker_queue.append( # remember generated threads.
                        deploy_worker_thread(worker_pool, endpoint, message)
                    )
                # throttle if the worker processes are leaking over limit.
                while len(worker_queue) >= self.__pool_size:
                    thread = worker_queue.popleft()
                    if thread.is_alive():
                        worker_queue.append(thread)
        self.__consumer = Thread(name='consumer', target=consume)
        self.__consumer.daemon = True
        self.__consumer.start()

    def initialize_demultiplexer(self):
        ''' initialize demultiplexer.
        '''
        try:
            from multiprocessing import Queue # best
        except ImportError:
            try:
                from Queue import Queue
            except ImportError:
                from queue import Queue as Queue
        self.__demux = Queue()
        return bool(self.__demux)
