[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)

# sipd

**sipd** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) server daemon, which was developed to decode raw SIP messages directly with [Genesys](https://www.genesys.com) [Resource Managers](https://docs.genesys.com/Documentation/GVP/85/GDG/GCRM) ("signal servers"), respond with dynamically crafted SIP/SDP packets, interface with an [external RTP protocol decoding software](), and send serialized datagrams to database handlers.

## Usage

When using **sipd**, everything must be first configured through [settings.json](./settings.json). Any `null` values in [settings.json](./settings.json) means that particular feature has yet to be implemented. Otherwise, please refer to the [documentations](#documentations) for configuration explanations.

```bash
~$ # vi settings.json
~$ make
~$ pip install -r requirements.txt
~$ ./sipd --config settings.json
```

## Installation

If you do not want to locally build, simply install the stable versions of **sipd** and copy the [settings.json](./settings.json).

```bash
~$ wget 'https://raw.githubusercontent.com/initbar/sipd/master/settings.json'
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
