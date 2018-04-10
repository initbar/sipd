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
# logger.py -- logging component.
#-------------------------------------------------------------------------------

import logger

def initialize_logger(configuration):

    logging_format = ' '.join(
        [
            u'\u001b[0m[%(asctime)-15s]',
            u'<<\u001b[32;1m%(threadName)s\u001b[0m>>',
            '%(levelname)s',
            u'<\u001b[36m%(filename)s\u001b[0m:\u001b[31;1m%(lineno)s\u001b[0m>',
            '%(message)s',
        ]
    ); logging_formatter = logging.Formatter(logging_format)

    # initialize filesystem logging.
    log_fs = configuration['log']['filesystem']
    if log_fs.get('enabled'):

        # adjust log path.
        log_file = str(log_fs.get('name'))
        log_path = str(log_fs.get('path'))
        if not log_path.endswith('/'):
            log_path += '/'
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_path += log_file

        # set handler for old logs.
        log_days = int(log_fs.get('total_days'))
        handler_fs = logging.handlers.TimedRotatingFileHandler(log_path, 'midnight', 1, log_days)
        handler_fs.suffix = '%Y%m%d'
        handler_fs.setFormatter(logging_formatter)
    else:
        handler_fs = None

    # initialize console logging.
    log_cli = configuration['log']['console']
    if log_cli.get('enabled'):
        logging.basicConfig(
            level=configuration['log']['level'],
            format=logging_format,
            handlers=[handler_fs]
        )

    logger = logging.getLogger(__name__)
    if config['log']['coloredlogs']:
        try:
            import coloredlogs
        except ImportError:
            logger.critical("module `coloredlogs` does not exist.")
            sys.exit()
        coloredlogs.install(level=config['log']['level'],
                            logger=logger,
                            fmt=logging_format,
                            milliseconds=True)
        logger.addHandler(handler_fs)
    logger.info("<main>:successfully initialized logging.")
    return logger
