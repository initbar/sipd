# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

"""
sipd.__main__
----------------
"""

from __future__ import absolute_import

import sys
import yaml

from app import Application
from app import parse_arguments
from logger import initialize_logger
from version import BRANCH, VERSION


if __name__ == "__main__":

    # enforce minimum Python 3 version.
    if not ((3, 0) <= sys.version_info):
        raise RuntimeError("minimum Python version 3.0 required")

    # parse `-h` and `-v`.
    args = parse_arguments()
    if args.version:
        sys.stderr.write(Application.version)
        sys.exit()

    try:  # parse configuration file and merge with command line arguments.
        with open(args.config) as configuration:
            settings = yaml.safe_load(configuration.read())
            settings["server"]["host"] = args.address
            settings["server"]["port"] = args.port
            settings["server"]["worker"] = args.worker_count
            if args.print_debug_logs:
                settings["log"]["level"] = "DEBUG"
    except FileNotFoundError:
        logger.error("configuration file does not exist: '%s'.", args.config)

    # parse environment.
    if args.print_environment:
        sys.stderr.write(str(settings))
        sys.exit()

    logger = initialize_logger(
        level=settings["log"]["level"],
        log_to_disk=settings["log"]["disk"]["enabled"],
        log_path=settings["log"]["disk"]["path"],
        log_name=settings["log"]["disk"]["name"],
        log_days=settings["log"]["disk"]["total_days_preserved"]
    )
    logger.debug("successfully initialized logger.")

    try:
        app = Application(param=settings)
        result, benchmark = app.run()
    except KeyboardInterrupt:
        pass
    finally:
        if args.print_benchmark:
            # TODO: benchmark is not always accurate since it also adds
            # `sys.stdout.write` time. I need to either change the start
            # and end or subtract print time from the overall benchmark.
            logger.info("app performance: %s seconds.", benchmark)
