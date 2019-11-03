[![Build Status](https://travis-ci.org/initbar/sipping.svg?branch=master)](https://travis-ci.org/initbar/sipping)

![](./.docs/assets/cover.png)

<div align="center">
  <p><strong>A high-performance Session Initiation Protocol daemon.</strong></p>
</div>

## About

**sipping** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) server daemon, which was developed to decode raw SIP messages directly with [Genesys](https://www.genesys.com) [Resource Managers](https://docs.genesys.com/Documentation/GVP/85/GDG/GCRM) ("signal servers"), respond with dynamically crafted SIP/SDP packets, interface with an [external RTP protocol decoding software](), and send serialized datagrams to database handlers.

## What makes **sipping** different from others?

Some key features are:

- **High performance** using [reactor pattern](https://en.wikipedia.org/wiki/Reactor_pattern) to [efficiently handle incredible loads](#case-study).
- **Resilient and self-recoverable**. No program is perfect and all software developers will end up writing bugs. **sipping** accounts for those possibilities and tries to automatically recover through self health checks.
- **Maximum portability** implemented in Python and minimal dependencies. Just install, configure some settings, and run while you take a sip of your favorite coffee.

## Usage

When using **sipping**, everything must be configured through [settings.yaml](./settings.yaml) configuration.

```bash
~$ # wget 'https://raw.githubusercontent.com/initbar/sipping/master/settings.yaml'
~$ pip install sipping
```

## Build

If you want to build and run locally (or remotely), you *must* have Python 3+ and the [requiremented packages](./requirements.txt) installed.

```bash
~$ pip install -r requirements.txt
~$ make
```

## Tests

To run tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

## Documentations

See [documentations]().

## License

**sipping** is licensed under [MIT License](./LICENSE.md).
