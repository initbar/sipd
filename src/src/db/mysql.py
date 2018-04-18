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
# mysql.py -- MySQL client.
#-------------------------------------------------------------------------------

import MySQLdb as mysql
from src.optimizer import memcache
from src.db.errors import (
    DBConnectionError,
    DBError,
    DBExecutionError,
    DBParameterError
)

import datetime
import logging

logger = logging.getLogger()

# MySQL client
#-------------------------------------------------------------------------------

class MySQLClient(object):
    ''' MySQL client wrapper implementation.
    '''
    def __init__(self,
                 host=None,
                 port=None,
                 username=None,
                 password=None,
                 database=None):
        ''' MySQL client prototype.
        @host<str> -- MySQL database address.
        @port<int> -- MySQL database port.
        @username<str> -- MySQL database username.
        @password<str> -- MySQL database password.
        @database<str> -- MySQL database name.

        : lazy-loaded:
        @_session<mysql> -- authenticated database session.
        @_cursor<mysql> -- authenticated database cursor.
        '''
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    def db_connect(self,
                   host='127.0.0.1',
                   port=3306,
                   username='root',
                   password='',
                   database=None):
        ''' connect to database.
        @host<str> -- MySQL database address.
        @port<int> -- MySQL database port.
        @username<str> -- MySQL database username.
        @password<str> -- MySQL database password.
        @database<str> -- MySQL database name.
        '''
        if not all([ host, port, username, database ]):
            raise DBParameterError
        else:
            self.host = host
            self.port = port
            self.username = username
            self.password = password
            self.database = database

        self.__session = self.__cursor = None
        try: # connecting to database.
            self.__session = mysql.connect(host=host,
                                          port=port,
                                          user=username,
                                          passwd=password,
                                          db=database)
        except Exception as message:
            raise DBConnectionError(message)

        try: # cache database cursor.
            assert self.__session and self.__session.open
            self.__cursor = self.__session.cursor()
            assert self.__cursor
        except Exception as message:
            raise DBConnectionError(message)
        return bool(self.__cursor)

    @memcache(size=128)
    def db_execute(self, statement):
        ''' execute SQL statement.
        @statement<str> -- SQL statement.
        '''
        if not statement:
            return []
        elif not self.__cursor: # retry
            self.db_connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database)
        result = self._blind_sql_execute(sanitize_sql(statement))
        return result

    def _blind_sql_execute(self, statement):
        ''' blind execute SQL statement.
        @statement<str> -- SQL statement.
        '''
        try:
            self.__cursor.execute(statement)
        except Exception as message:
            raise DBExecutionError(message)
        yield self.__cursor.fetchall()
