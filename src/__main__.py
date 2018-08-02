# MIT License

# Copyright (c) 2018 Herbert Shin

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://github.com/initbar/sipd

# ------------------------------------------------------------------------------
# __main__.py
# ------------------------------------------------------------------------------

import argparse
import errno
import os
import sys

from src.config import parse_config
from src.logger import initialize_logger
from src.sip.server import AsynchronousSIPServer
from src.tester import run_test_suite

__program__ = "sipd -- active-recording Session Initiation Protocol daemon"
__version__ = "1.4.0"
__license__ = "GNU GPLv3"

# check supported version.
try:
    assert (2, 7) <= sys.version_info <= (3, 7)
except AssertionError:
    raise


def main():
    """
    """
    argsparser = argparse.ArgumentParser(prog=__program__)
    n_exec = argsparser.add_argument_group("execution arguments")
    n_test = argsparser.add_argument_group("testing arguments")

    default_configuration = os.path.abspath(os.path.curdir) + "/config.json"

    # version: show program's version number and exit.
    argsparser.add_argument("-v", "--version", action="version", version=__version__)

    # config: configuration file path.
    n_exec.add_argument(
        "-c",
        "--config",
        nargs="?",
        metavar="str",
        default=default_configuration,
        help="configuration file path (default: None)",
    )

    # test: run test suite and exit.
    n_test.add_argument(
        "-t",
        "--test",
        action="store_true",
        default=False,
        help="run tests (default: no)",
    )

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


if __name__ == "__main__":

    # adjust path if this main class is packed executable.
    if __package__ is None and not hasattr(sys, "frozen"):
        sys.path.insert(
            0,
            os.path.dirname(
                os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
            ),
        )

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
