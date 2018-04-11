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
# logger.py
#-------------------------------------------------------------------------------

import errno
import logging
import os
import sys

from logging.handlers import TimedRotatingFileHandler

def initialize_logger(configuration):
    '''
    '''
    logging_format = ' '.join(
        [
            u'\u001b[0m[%(asctime)-15s]',
            u'<<\u001b[32;1m%(threadName)s\u001b[0m>>',
            '%(levelname)s',
            u'<\u001b[36m%(filename)s\u001b[0m:\u001b[31;1m%(lineno)s\u001b[0m>',
            '%(message)s',
        ]
    ); logging_formatter = logging.Formatter(logging_format)

    log_cli = configuration['log']['console']
    log_clr = configuration['log']['coloredlogs']
    log_fs = configuration['log']['filesystem']

    # filesystem
    if log_fs.get('enabled'):
        log_days = log_fs['total_days']
        log_file = log_fs['name']
        log_path = log_fs['path']
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        if not log_path.endswith('/'):
            log_path += '/'
        log_path += log_file
        fs_handler = TimedRotatingFileHandler(
            log_path,   # log path
            'midnight', # log rotation time
            1,          # interval
            log_days)   # total logs
        fs_handler.setFormatter(logging_formatter)
        fs_handler.suffix = '%Y%m%d'
    else:
        fs_handler = None

    # console
    if log_cli.get('enabled'):
        logging.basicConfig(level=configuration['log']['level'], format=logging_format)

    logger = logging.getLogger()

    # coloredlogs
    if log_clr:
        try:
            import coloredlogs
        except ImportError:
            logger.critical("module `coloredlogs` does not exist.")
            sys.exit(errno.ENOENT)
        coloredlogs.install(level=configuration['log']['level'],
                            logger=logger,
                            fmt=logging_format,
                            milliseconds=True)

    logger.addHandler(fs_handler)
    logger.info("<main>:successfully initialized logging.")
    return logger
