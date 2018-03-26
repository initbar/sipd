# Active recording Session Initiation Protocol daemon (SIPd).
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
# https://github.com/initbar/SIPd

__program__ = 'SIPd -- Active recording Session Initiation Protocol Daemon'
__version__ = '1.2.1'
__license__ = 'GNU GPLv3'

try: # check supported version.
    import sys
    assert (2,7) <= sys.version_info <= (3,7)
except AssertionError: raise

import argparse
import os

try:
    from src.config import parse_config
    from src.sip.server import AsynchronousSIPServer
except ImportError: raise

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

def test():
    logger.info('initializing self-tests ..')
    # ignore any `SyntaxWarning` or `SyntaxError` raised from interpreter since
    # lazy loading modules means import pre-optimization will not take place.
    try:
        import unittest
        from tests.test_debug import TestDebug
        from tests.test_errors import TestErrors
        from tests.test_parser import TestParser
        from tests.test_sockets import TestSockets
    except ImportError: raise
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

#
# SIPd
#

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
        if args.test: sys.exit(test()) # unit tests.

        # parse configuration.
        config_file = str(args.config)
        try:
            assert os.path.exists(config_file) and os.path.isfile(config_file)
            with open(config_file) as f:
                content = f.read()
                config = parse_config(content)
        except: config = None
        finally:
            if config:
                logger.info('successfully loaded configurations:')
                logger.debug(str(config))
            else:
                logger.error('unable to load configuration file: ' + config_file)
                logger.warning('falling back to default configurations.')

        # deploy.
        server = AsynchronousSIPServer(config)
        sys.exit(server.serve())
    except KeyboardInterrupt: pass
    finally:
        logger.info('%s (v%s)' % (__program__, __version__))
