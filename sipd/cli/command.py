# MIT License
#
# Copyright (c) 2018 Herbert Shin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# https://github.com/initbar/sipd

"""
loader.py
---------
"""

from __future__ import absolute_import
from abc import abstractmethod
from multiprocessing import cpu_count

import argparse
import attr
import logging
import os

from logger import initialize_logger
from sip.server import AsynchronousUDPServer
from version import BRANCH, VERSION


def parse_arguments():
    """ parse and return command-line arguments """

    formatter = argparse.HelpFormatter
    argsparser = argparse.ArgumentParser(
        formatter_class=lambda prog: formatter(prog, max_help_position=30)
    )

    argsparser.add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="print program version and exit",
    )

    #
    # server
    #

    server = argsparser.add_argument_group("server arguments")

    server.add_argument(
        "--address",
        metavar="str",
        type=str,
        default="127.0.0.1",
        help="server listening address (default: '127.0.0.1')",
    )

    server.add_argument(
        "--port",
        metavar="int",
        type=int,
        default="5060",
        help="server listening port (default: 5060)",
    )

    server.add_argument(
        "--worker-count",
        metavar="int",
        type=int,
        default=1,
        help="number of workers available upto %s (default: 1)" % cpu_count(),
    )

    #
    # configuration
    #

    config = argsparser.add_argument_group("config arguments")

    default_settings = os.path.abspath(os.path.curdir) + "/settings.yaml"
    config.add_argument(
        "--config",
        metavar="str",
        type=str,
        default=default_settings,
        help="configuration path (default: '%s')" % default_settings,
    )

    args = argsparser.parse_args()
    return args


@attr.s(frozen=True, slots=True)
class Application(object):
    """ Application
    """

    version = "branch:%s-version:%s" % (BRANCH, VERSION)
    param = attr.ib()

    def run(self, *a, **kw):
        server = AsynchronousUDPServer(settings=self.param)
        return server.serve()

    @abstractmethod
    def test(self):
        import unittest
        raise NotImplementedError


__all__ = ["parse_arguments", "Application"]
