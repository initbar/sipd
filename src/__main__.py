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

# -------------------------------------------------------------------------------
# __main__.py
# -------------------------------------------------------------------------------

# check supported version.
try:
    import sys
    assert (2, 7) <= sys.version_info <= (3, 7)
except AssertionError:
    raise

import argparse
import errno
import os

from src.config import parse_config
from src.logger import initialize_logger
from src.sip.server import AsynchronousSIPServer
from src.tester import run_test_suite

__program__ = 'sipd -- Active recording Session Initiation Protocol Daemon'
__version__ = '1.3.7'
__license__ = 'GNU GPLv3'


def main():
    '''
    '''
    argsparser = argparse.ArgumentParser(prog=__program__)
    n_exec = argsparser.add_argument_group('execution arguments')
    n_test = argsparser.add_argument_group('testing arguments')

    default_configuration = os.path.abspath(os.path.curdir) + '/sipd.json'

    # version: show program's version number and exit.
    argsparser.add_argument('-v', '--version',
                            action='version',
                            version=__version__)

    # config: configuration file path.
    n_exec.add_argument('-c', '--config',
                        nargs='?',
                        metavar='str',
                        default=default_configuration,
                        help='configuration file path (default: None)')

    # test: run test suite and exit.
    n_test.add_argument('-t', '--test',
                        action='store_true',
                        default=False,
                        help="run tests (default: no)")

    args = argsparser.parse_args()
    config_file = str(args.config)

    # load configuration file and initialize logging platform.
    if os.path.exists(config_file) and os.path.isfile(config_file):
        with open(config_file) as config_buffer:
            config = parse_config(config_buffer.read())
        logger = initialize_logger(config)
        logger.debug("<main>:successfully loaded: '%s'.", config_file)
        logger.debug(config)
    else:
        sys.stderr.write("<main>:file does not exist: '%s'.\n", config_file)
        return errno.ENOENT

    if args.test:
        return run_test_suite()

    server = AsynchronousSIPServer(config)
    return server.serve()


if __name__ == '__main__':

    # adjust path if this main class is packed executable.
    if __package__ is None and not hasattr(sys, 'frozen'):
        sys.path.insert(0, os.path.dirname(os.path.dirname(
            os.path.realpath(os.path.abspath(__file__)))))

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
