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
import sys
import threading
import time

from multiprocessing import Process
from multiprocessing import cpu_count
from src.sip.garbage import SynchronousSIPGarbageCollector
from src.sip.worker import LazySIPWorker
from src.sockets import unsafe_allocate_udp_socket

logger = logging.getLogger('__main__')

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
        self.__port = int(port)
        self.__socket = None

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, number):
        number = int(number)
        if not 1024 < number < 65535:
            logger.critical("<sip>:cannot use privileged ports: '%i'", number)
            sys.exit(errno.EPERM)
        self.__port = number

    def __enter__(self):
        self.__socket = unsafe_allocate_udp_socket('0.0.0.0', self.port, is_reused=True)
        return self.__socket

    def __exit__(self, *a, **kw):
        self.__socket.close()
        del self.__socket

# server
#-------------------------------------------------------------------------------

class AsynchronousSIPServer(object):
    ''' Asynchronous SIP server that initializes SIP router and SIP workers.
    '''
    def __init__(self, setting):
        if setting:
            global SERVER_SETTINGS
            global GARBAGE_COLLECTOR
            SERVER_SETTINGS = setting
            GARBAGE_COLLECTOR = SynchronousSIPGarbageCollector(setting)
        else:
            logger.critical('<sip>:failed to initialize SIP server.')
            sys.exit(errno.EINVAL)
        logger.info('<sip>:successfully initialized SIP server.')

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
            cls.router.initialize_collector()
            logger.info('<sip>:successfully initialized SIP router.')
            asyncore.loop() # push new events to the event loop.

# router
#-------------------------------------------------------------------------------

def async_worker_function(endpoint, message):
    worker = LazySIPWorker(SERVER_SETTINGS, GARBAGE_COLLECTOR)
    worker.handle(sip_endpoint=endpoint, sip_message=message)

class AsynchronousSIPRouter(asyncore.dispatcher):
    ''' Asynchronous SIP routing component prototype.
    '''
    def __init__(self, sip_socket):
        # in order to prevent double creation of a router socket, inherit
        # SIP port from SIP server. A router should only be used to receive
        # traffic from the remote endpoint.
        asyncore.dispatcher.__init__(self, sip_socket)

        # override socket read state to read-only.
        self.is_readable = True
        self.readable = lambda: self.is_readable

        # override socket read state to disable writes.
        self.is_writable = False
        self.writable = lambda: self.is_writable
        self.handle_write = lambda: None

        # demultiplxer and collector.
        self.__demux = None # must be a FIFO queue
        self.collector = None

        try:
            pool_size = SERVER_SETTINGS['sip']['worker']['count']
        except KeyError:
            pool_size = cpu_count()

        # workers
        self.__pool_size = min(pool_size, cpu_count())
        self.worker_pool = [
            LazySIPWorker(SERVER_SETTINGS, GARBAGE_COLLECTOR)
            for i in range(self.__pool_size)
        ]

    def initialize_demultiplexer(self):
        '''
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

    def initialize_collector(self):
        '''
        '''
        if not self.__demux:
            logger.critical("failed to initialize router properties.")
            sys.exit(errno.EAGAIN)

        def collect():
            while True:
                if self.__demux.empty():
                    time.sleep(0.1)

                session = []
                for worker in range(self.__pool_size):
                    endpoint, message = self.__demux.get()
                    process = Process(target=async_worker_function,
                                      args=(endpoint, message))
                    session.append(process)
                for process in session:
                    process.start()
                    process.join()

        self.collector = threading.Thread(name='collector', target=collect)
        self.collector.daemon = True
        self.collector.start()

    def handle_read(self):
        # the purpose of router is to only receive data ("work") and delegate
        # them to its' workers. A worker holds the logic implementation.
        payload = self.recvfrom(0xffff) # max receive bytes.
        endpoint, message = tuple(payload[1]), str(payload[0])
        self.__demux.put((endpoint, message)) # push new jobs.
