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
# server.py -- asynchronous SIP server module.
#-------------------------------------------------------------------------------

# ARCHITECTURE
#-------------------------------------------------------------------------------
#
#                                            | | | receive SIP
#                                            | | | messages.
#                                            V V V
# +--------+  create asynchronous router   +--------+  dispatch to workers
# | server | ----------------------------> | router | --+----------+-------
# +--------+                               +--------+   |          |
#                                                       |          |
#                                                       V          V
#                                                  +--------+  +--------+
#                                              ..  | worker |  | worker |  ..
#                                                  +--------+  +--------+
#                                                       ^          ^
#                       +-------------+                 |          |
#                       | RTP decoder | <---------------+----------+-------
#                       +-------------+   delegate RTP to RTP decoder
#                                         using SDP headers.
#-------------------------------------------------------------------------------

from multiprocessing import cpu_count
from src.sip.garbage import SynchronousSIPGarbageCollector
from src.sockets     import unsafe_allocate_udp_socket

import asyncore
import random
import threading

import logging
logger = logging.getLogger(__name__)

# each worker should not instantiate a new garbage collector since a subsequent
# related requests can not guarantee to hit the same worker. Therefore, the
# workers should all use the same garbage collector and just register a new
# collection tasks to the collector queue.
GC = None

SERVER_SETTINGS = {} # `sipd.json`

# SIP socket
#-------------------------------------------------------------------------------

class safe_allocate_sip_socket(object):
    ''' allocate exception-safe listening SIP socket.
    '''
    def __init__(self, port=5060):
        self.__port = port

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, number):
        try: assert 1025 < port < 65535
        except: raise ValueError(port)
        self.__port = number

    def __enter__(self):
        self.__socket = unsafe_allocate_udp_socket(
            host='0.0.0.0', port=self.__port, is_reused=True)
        return self.__socket

    def __exit__(self, type, value, traceback):
        try: self.__socket.close()
        except:
            self.__socket.shutdown()
            self.__socket.close()
            del self.__socket

# SIP server
#-------------------------------------------------------------------------------

class SIPServerPrototype(object):
    ''' Asynchronous SIP server prototype.
    '''
    def __init__(self, setting={}):
        if setting and isinstance(setting, dict):
            global SERVER_SETTINGS; SERVER_SETTINGS = setting
        global GC; GC = SynchronousSIPGarbageCollector(setting)
        logger.info('[sip] server initialized.')

class AsynchronousSIPServer(SIPServerPrototype):
    ''' Asynchronous SIP server implementation.
    '''
    def serve(self):
        # assign asynchronous handler to the receiving SIP port. Currently,
        # `asyncore` module was chosen in order to provide backward
        # compatibility with Python 2 (where there's no `asyncio`). All
        # incoming traffic is routed and initially handled by the router.
        try: sip_port = SERVER_SETTINGS['sip']['router']['port']
        except: sip_port = 5060 # udp
        with safe_allocate_sip_socket(port=sip_port) as sip_socket:
            sip_router = AsynchronousSIPRouter(sip_socket)
            asyncore.loop() # push new events to the event loop.

# SIP router
#-------------------------------------------------------------------------------

class SIPRouterPrototype(asyncore.dispatcher):
    ''' Asynchronous SIP routing component prototype.
    '''
    def __init__(self, sip_socket):
        asyncore.dispatcher.__init__(self, sip_socket)

        # in order to prevent double creation of a router socket, inherit
        # SIP port from SIP server. A router should only be used to receive
        # traffic. For that reason (and also to not cause 100% CPU
        # utilization by infinite loop checks), override polling states.
        self.is_readable = True
        self.readable    = lambda: self.is_readable

        # override socket to disable writes.
        self.is_writable  = False
        self.writable     = lambda: self.is_writable
        self.handle_write = lambda: None

        self._random = random.random # cache random number generator.

        # since it's possible that SIP server is running on a server with
        # multiple cores/threads, workers are dynamically allocated based
        # on server specification. Unless given, the following formula is
        # used for dynamic allocation of workers:
        #
        #   total_workers = [ 1 + floor(total_cores * 0.32) ]
        #
        # Which has the following distribution:
        #
        #  6 |                                                    x
        #  5 |                                        x   x   x   x
        #  4 |                            x   x   x   x   x   x   x
        #  3 |                   x  x  x  x   x   x   x   x   x   x
        #  2 |          x  x  x  x  x  x  x   x   x   x   x   x   x
        #  1 | x  x  x  x  x  x  x  x  x  x   x   x   x   x   x   x
        #    +-----------------------------------------------------------
        #      1  2  3  4  5  6  7  8  9  10  11  12  13  14  15  16
        try:
            # if worker size is given, then normalize the count to not
            # exceed the available resources. After all, GIL only
            # permits only one active thread at a given time.
            worker_size = SERVER_SETTINGS['sip']['worker']['count']
            assert worker_size > 0 # check for dynamic allocation.
            self.__worker_size = min(max(worker_size, 1), cpu_count())
        except:
            self.__worker_size = 1 + int(cpu_count() * 0.32)
        logger.info('[sip] total router workers: %i.', self.__worker_size)

        # workers should never cause conflict with main server thread.
        # For that reason, each worker must exist in their own thread.
        self.__workers = [ SynchronousSIPWorker(i) for i in range(self.__worker_size) ]
        self._handlers = []
        for worker in self.__workers:
            handler = threading.Thread(name=worker.name, target=worker.handle)
            handler.daemon = True
            self._handlers.append(handler)
        map(lambda thread:thread.start(), self._handlers) # start threads.
        random.shuffle(self.__workers) # shuffle workers for selection.
        logger.info('[sip] router initialized.')

class AsynchronousSIPRouter(SIPRouterPrototype):
    ''' Asynchronous SIP routing component implementation.
    '''
    def handle_read(self):
        # the purpose of router is to only receive data ("work") and delegate
        # them to its' workers. A worker holds the logic implementation.
        try:
            message = self.recvfrom(0xffff) # max receive bytes.
            sip_endpoint = tuple(message[1])
            sip_message  = str(message[0])
        except: return
        # we want a balanced distribution to our workers. For example, we want
        # to reflect round robin distribution closely as possible - yet have
        # enough chance to delegate two short tasks to the same worker.
        while not locals().get('work_delegated', False): # temporary.
            p_index = int(self._random() * self.__worker_size)
            worker = self.__workers[p_index]
            if worker.is_ready():
                worker.assign(sip_endpoint, sip_message)
                work_delegated = True # break loop.
