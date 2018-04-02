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

from src.db.mysql import safe_allocate_mysql_client

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format=' '.join(
        [
            '[%(asctime)-15s]',
            '<%(filename)s:%(lineno)s>',
            '[%(levelname)s]',
            '%(message)s'
        ])
); logger = logging.getLogger(__name__)

if __name__ == '__main__':

    with safe_allocate_mysql_client(
            host='127.0.0.1',
            port='3306',
            username='<username>',
            password='<password>',
            database='<database>'
    ) as sql:
        print sql
