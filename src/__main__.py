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

try: # check supported version.
    import sys
    assert (2,7) <= sys.version_info <= (3,7)
except AssertionError: raise

from logging.handlers import RotatingFileHandler
from src.config import parse_config
from src.sip.server import AsynchronousSIPServer

import argparse
import logging
import os

__program__ = 'sipd -- Active recording Session Initiation Protocol Daemon'
__version__ = '1.2.12'
__license__ = 'GNU GPLv3'

# Test
#-------------------------------------------------------------------------------

def test():
    logger.info('initializing self-tests ..')
    # ignore any `SyntaxWarning` or `SyntaxError` raised from interpreter since
    # lazy loading modules means import pre-optimization will not take place.
    import unittest
    from tests.test_debug import TestDebug
    from tests.test_errors import TestErrors
    from tests.test_parser import TestParser
    from tests.test_sockets import TestSockets
    test_suites, test_cases = [], [
        TestDebug,
        TestErrors,
        TestParser,
        TestSockets
    ]
    for test_case in test_cases:
        logger.info("adding test suite: '%s'." % test_case)
        test_suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suites.append(test_suite)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(test_suites))
    return (not result.wasSuccessful())

# Logging
#-------------------------------------------------------------------------------

logger = None

def initialize_logger(config={}):

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
    log_fs = config['log']['filesystem']
    if log_fs.get('enabled'):
        log_size = int(log_fs.get('size_in_kb')) * 1024
        log_cnt  = int(log_fs.get('total_logs'))

        log_file = str(log_fs.get('name'))
        log_path = str(log_fs.get('path'))
        if not log_path.endswith('/'):
            log_path += '/'
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_path += log_file

        handler_fs = RotatingFileHandler(
            log_path,
            mode='a',
            maxBytes=log_size,
            encoding='utf-8',
            backupCount=log_cnt
        )
        handler_fs.setFormatter(logging_formatter)
    else:
        handler_fs = None

    # initialize console logging.
    log_cli = config['log']['console']
    if log_cli.get('enabled'):
        logging.basicConfig(
            level=config['log']['level'],
            format=logging_format,
            handlers=[handler_fs]
        )

    # globalize logger.
    global logger
    logger = logging.getLogger(__name__)

    try:
        assert config['log']['coloredlogs']
        import coloredlogs
        coloredlogs.install(level=config['log']['level'],
                            logger=logger,
                            fmt=logging_format,
                            milliseconds=True)
        logger.addHandler(handler_fs)
    except Exception as message:
        logger.warning("failed to initialize coloredlogs: '%s'." % message)
        pass
    logger.info("<main>:successfully initialized logging.")

# CLI
#-------------------------------------------------------------------------------

if __name__ == '__main__':

    # adjust path if this main class is packed executable.
    if __package__ is None and not hasattr(sys, 'frozen'):
        path = os.path.realpath(os.path.abspath(__file__))
        sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

    # -v, --version: show program's version number and exit.
    argsparser = argparse.ArgumentParser(prog=__program__)
    argsparser.add_argument('-v', '--version',
                            action='version',
                            version=__version__)

    # -c, --config: configuration file path.
    default_config_file = os.path.abspath(os.path.curdir) + '/sipd.json'
    n_exec = argsparser.add_argument_group('execution arguments')
    n_exec.add_argument('-c', '--config',
                        nargs='?',
                        metavar='str',
                        default=default_config_file,
                        help='configuration file path (default: None)')

    # -t, --test: run test suite and exit.
    n_test = argsparser.add_argument_group('testing arguments')
    n_test.add_argument('-t', '--test',
                        action='store_true',
                        default=False,
                        help="run tests (default: no)")

    try:
        args = argsparser.parse_args()

        # parse configuration.
        config_file = str(args.config)
        try:
            assert os.path.exists(config_file) and os.path.isfile(config_file)
            with open(config_file) as f:
                content = f.read()
                config = parse_config(content)

            # initialize logging.
            initialize_logger(config)
            logger.info("<main>:successfully loaded configuration file: '%s'." % config_file)
            logger.debug(config)
        except AssertionError:
            sys.stderr.write("configuration file does not exist: '%s'.\n" % config_file)
            sys.exit()

        # run unit tests.
        if args.test: sys.exit(test())

        # deploy server.
        server = AsynchronousSIPServer(locals().get('config'))
        sys.exit(server.serve())
    except KeyboardInterrupt: pass
    finally:
        sys.stdout.write('%s (v%s)' % (__program__, __version__))
