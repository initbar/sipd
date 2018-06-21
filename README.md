[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)

![](./docs/sample.png)

**sipd** is an [active recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) daemon. A daemon is a background process that handles incoming requests and logically responds - and a minute customization ranging from custom SIP method handling to internal/external RTP routing is possible.

Key features are:

- **High performance** using [reactor asynchronous design pattern](https://en.wikipedia.org/wiki/Reactor_pattern) and multi-core handlers.

- **Fast RTP routing** using dynamic [Session Description Protocol](https://en.wikipedia.org/wiki/Session_Description_Protocol) generation. For the optimal performance, use external [Real-time Transport Protocol](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol) decoders.

- **Enterprise-level performance** currently handling production calls for [Samsung Electronics of America](http://www.samsung.com)'s call centers.

- **Maximum portability** implemented in pure Python and [non-mandatory dependencies](./requirements.txt). You can either run it by cloning the latest codes or [from packed packages](https://github.com/initbar/sipd/releases).

## Usage

[config.json](./config.json) is a mandatory configuration file that allows customization of the runtime environment. Although default settings is fine, it can be tuned for better performance.

```bash
~$ make run
```

## Deploy

You can either use `make` to easily build and deploy to a remote server:

```bash
~$ make
~$ ./sipd
```

## Tests

To run unit tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ make test
```

## Design

![](./docs/design.png)

## License

**sipd** is licensed under [GNU GPLv3](./LICENSE.md).
