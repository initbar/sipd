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
# tester.py
#-------------------------------------------------------------------------------

import logging
import unittest

from tests.test_debug import TestDebug
from tests.test_errors import TestErrors
from tests.test_parser import TestParser
from tests.test_sockets import TestSockets

LOGGER = logging.getLogger('__main__')

def run_test_suite():
    LOGGER.info('initializing self-tests..')
    test_suites, test_cases = [], [
        TestDebug,
        TestErrors,
        TestParser,
        TestSockets
    ]
    for test_case in test_cases:
        LOGGER.info("adding test suite: '%s'.", test_case)
        test_suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        test_suites.append(test_suite)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(test_suites))
    return not result.wasSuccessful()
