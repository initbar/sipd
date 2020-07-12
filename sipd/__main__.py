# Copyright 2018 (c) Herbert Shin  https://github.com/initbar/sipd
#
# This source code is licensed under the MIT license.

if __name__ == "__main__":
    from cli.command import Application
    from cli.command import parse_arguments
    from cli.config import Config

    try:
        app = Application(config: Config = parse_arguments())
    else:
        app.run()
