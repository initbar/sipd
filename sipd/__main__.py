# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

import sys
import yaml

from app import Application
from app import parse_arguments
from logger import initialize_logger
from version import BRANCH, VERSION


# enforce minimum Python 3 version.
if not ((3, 0) <= sys.version_info):
    raise RuntimeError("minimum Python version 3.0 required")


if __name__ == "__main__":

    # parse CLI arguments.
    args = parse_arguments()
    if args.version:
        sys.stderr.write(Application.version)
        sys.exit()

    #
    try:
        with open(args.config) as configuration:
            settings = yaml.safe_load(configuration.read())
        settings["server"]["host"] = args.address
        settings["server"]["port"] = args.port
        settings["server"]["worker"] = args.worker_count
        if args.print_debug_logs:
            settings["log"]["level"] = "DEBUG"
    except FileNotFoundError:
        logger.error("configuration file does not exist: '%s'.", args.config)

    logger = initialize_logger(
        level=settings["log"]["level"],
        log_to_disk=settings["log"]["disk"]["enabled"],
        log_path=settings["log"]["disk"]["path"],
        log_name=settings["log"]["disk"]["name"],
        log_days=settings["log"]["disk"]["total_days_preserved"]
    )

    try:
        app = Application(param=settings)
        result = app.run()
    except KeyboardInterrupt:
        pass
