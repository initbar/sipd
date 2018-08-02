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

# -------------------------------------------------------------------------------
# config.py -- config parser, custom overrides, and default states.
# -------------------------------------------------------------------------------

from src.parser import parse_json
from src.sockets import get_server_address

import sys  # no logger setup yet


def parse_config(config={}):
    """ parse `config.json` and load/initialize with runtime environment.
    """
    try:
        parsed_config = parse_json(config)
        assert parsed_config

        # save server address information to the configuration.
        if not parsed_config["sip"]["server"]["address"]:
            public_address = get_server_address()
            parsed_config["sip"]["server"]["address"] = public_address

        return parsed_config
    except AssertionError:
        return {}
