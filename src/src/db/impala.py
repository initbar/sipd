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
# impala.py -- Impala client.
#-------------------------------------------------------------------------------

import logging

try:
    from impala.dbapi import connect
except ImportError: raise

class ImpalaClient(object):

    def __init__(self, host='127.0.0.1', port=21050, db=None):
        self.host = host
        self.port = port

        self.db = db
        self.cursor = self._try_connect()

    def _try_connect(self):
        try:
            connection = connect(host=self.host, port=self.port)
            self.cursor = connection.cursor() # persistant
        except: raise

    def execute(self, query):
        if not query: return
        else: self.cursor.execute(query)

    def execute_batch(self, queries=[]):
        for query in queries:
            self.execute(query)
