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

import MySQLdb as mysql
import logging

logger = logging.getLogger(__name__)

# MySQL client allocator
#-------------------------------------------------------------------------------

def unsafe_allocate_mysql_client(host, port, username, password, database, table):
    ''' unsafely allocate a MySQL client.
    '''
    try:
        mysql_client = MySQLClientPrototype(host, port,
                                            username, password,
                                            database, table)
        assert mysql_client.connect() # connect to database.
        logger.info("[mysql] successfully allocated MySQL client.")
    except Exception as message:
        logger.error("[mysql] unable to allocate client: '%s'." % message)
    return locals().get('mysql_client')

class safe_allocate_mysql_client(object):
    ''' allocate exception-safe MySQL client.
    '''
    def __init__(self, host, port,
                 username, password,
                 database, table=None):
        # configuration.
        self.host     = host
        self.port     = port
        self.username = username
        self.password = password
        self.database = database
        self.table    = table
        # database session.
        self._session = None

    def __enter__(self):
        self._session = unsafe_allocate_mysql_client(self.host,
                                                     self.port,
                                                     self.username,
                                                     self.password,
                                                     self.database,
                                                     self.table)
        return self._session # assumed that client is connected.

    def __exit__(self, type, value, traceback):
        try: self._session.close()
        except: del self._session

# MySQL clients
#-------------------------------------------------------------------------------

class MySQLClientPrototype(object):
    ''' MySQL client wrapper implementation.
    '''
    def __init__(self, host, port,
                 username, password,
                 database, table=''):
        # configuration.
        self.host =     str(host)
        self.port =     int(port)
        self.username = str(username)
        self.password = str(password)
        self.database = str(database)
        self.table =    str(table)
        # session cursor.
        self._session = None

    def connect(self):
        ''' connect to MySQL database.
        '''
        try: self._session = mysql.connect(host=self.host,
                                           port=self.port,
                                           user=self.username,
                                           passwd=self.password,
                                           db=self.database)
        except: raise # catch failures later.
        return (self._session and self._session.open)

    def run(self, query):
        ''' run SQL statement.
        '''
        if not statement: yield
        yield []
