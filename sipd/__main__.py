# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

from sipd.cli.command import Sipd
from sipd.cli.config import Config
from sipd.cli.config import parse_arguments

if __name__ == "__main__":
    app = Sipd(config=Config(**parse_arguments()))
    app.run()
