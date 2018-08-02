[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)

# sipd

**sipd** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) server daemon, which was developed to decode raw SIP signals directly from [Genesys](https://www.genesys.com) [Resource Managers](https://docs.genesys.com/Documentation/GVP/85/GDG/GCRM) ("signal servers"), dynamically respond with crafted SIP/SDP packets, interface with external RTP protocol softwares, and send parsed datagrams to custom database handlers.

Although the optimized and specialized version of **sipd** is currently running in production for [Samsung Electronics of America](https://www.samsung.com/us) to process their call center calls, this [GitHub branch](https://github.com/initbar/sipd) is for bugfixes, performance enhancements, and design updates.

## Usage

When using **sipd**, everything must be first configured through [settings.json](./settings.json). Any `null` values in [settings.json](./settings.json) means that particular feature has yet to be implemented. Otherwise, please refer to the [documentations](#documentations) for configuration explanations.

```bash
~$ # vi settings.json
~$ make
~$ ./sipd --config settings.json
```

## Installation

If you do not want to build the **sipd** locally, simply download the packaged version in **sipd** along with a copy of [settings.json](./settings.json) from GitHub.

```bash
~$ pip install sipd
```

## Tests

To run tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ make test
```

## Documentations

See [documentations]().

## License

**sipd** is licensed under [MIT License](./LICENSE.md).
