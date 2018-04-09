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

from src.config import parse_config
from src.sip.server import AsynchronousSIPServer

import argparse
import os

__program__ = 'sipd -- Active recording Session Initiation Protocol Daemon'
__version__ = '1.2.9'
__license__ = 'GNU GPLv3'

# Logging
#-------------------------------------------------------------------------------

import logging

from logging import StreamHandler
from logging.handlers import RotatingFileHandler

logging_file = os.path.abspath(os.path.curdir) + '/sipd.log'
logging_size = 10 * 0x100000 # MB
logging_format = ' '.join(
    [
        '[%(asctime)-15s]',
        '<%(filename)s:%(lineno)s>',
        '[%(levelname)s]',
        '%(message)s'
    ]
)

handler_console = StreamHandler(sys.stdout)
handler_file    = RotatingFileHandler(logging_file,
                                      maxBytes=logging_size,
                                      backupCount=30)

logging.basicConfig(level=logging.DEBUG,
                    format=logging_format,
                    handlers=[
                        handler_console,
                        handler_file
                    ])

logger = logging.getLogger(__name__)
# logger.addHandler(handler_console)
# logger.addHandler(handler_file)

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
    n_exec = argsparser.add_argument_group('execution arguments')
    n_exec.add_argument('-c', '--config',
                        nargs='?',
                        metavar='str',
                        default='sipd.json',
                        help='configuration file path (default: None)')

    # -t, --test: run test suite and exit.
    n_test = argsparser.add_argument_group('testing arguments')
    n_test.add_argument('-t', '--test',
                        action='store_true',
                        default=False,
                        help="run tests (default: no)")

    try:
        args = argsparser.parse_args()

        # run unit tests.
        if args.test: sys.exit(test())

        # parse configuration.
        config_file = str(args.config)
        try:
            assert os.path.exists(config_file) and os.path.isfile(config_file)
            with open(config_file) as f:
                content = f.read()
                config = parse_config(content)
            logger.info('successfully loaded configurations:')
            logger.info(str(config))
        except AssertionError:
            logger.error('unable to load configurations: ' + config_file)

        # deploy server.
        server = AsynchronousSIPServer(locals().get('config'))
        sys.exit(server.serve())
    except KeyboardInterrupt: pass
    finally:
        logger.info('%s (v%s)' % (__program__, __version__))
