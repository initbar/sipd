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

# MySQL allocator
#-------------------------------------------------------------------------------

def unsafe_allocate_mysql_client(host, port, username, password, database, table=None):
    ''' allocate a MySQL client.
    '''
    if not all(host, port, username, password, database): return
    try:
        mysql_client = MySQLClient(host, port, username, password, database, table)
        assert mysql_client.connect()
        logger.info("[mysql] successfully allocated MySQL client.")
    except Exception as message:
        logger.error("[mysql] unable to allocate client: '%s'" % message)
    return locals().get(mysql_client)

def safe_allocate_mysql_client(host, port, username, password, database, table):
    ''' allocate exception-safe MySQL client.
    '''
    def __init__(self, host, port, username, password, database, table):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.table = table

    def __enter__(self):
        self._cursor = unsafe_allocate_mysql_client(self.host, self.port,
                                                    self.username, self.password,
                                                    self.database, self.table)
        return self._cursor # connected client.

    def __exit__(self):
        try: self._cursor.close()
        except:
            self._cursor.close() # try again
            del self._cursor

# MySQL client
#-------------------------------------------------------------------------------

class MySQLClient(object):
    ''' MySQL client template.
    '''

    def __init__(self, host, port,
                 username, password,
                 database, table=None):
        # MySQL configuration.
        self.host = host
        self.port = port
        self.username = usernmae
        self.password = password
        self.database = database
        self.table = table
        # MySQL cursor.
        self.session = None

    def connect(self):
        mysql.connect(host=self.host, port=self.port,
                      user=self.username, passwd=self.password,
                      db=self.database)
        return self.session.open()

    def query(self, statement):
        if not statement: yield
        yield []
