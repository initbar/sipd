[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)

# sipd

**sipd** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) server daemon, which was developed to decode raw SIP signals directly from [Genesys](https://www.genesys.com) [Resource Managers](https://docs.genesys.com/Documentation/GVP/85/GDG/GCRM) ("signal servers"), dynamically respond with crafted SIP/SDP packets, interface with external RTP protocol softwares, and send parsed datagrams to custom database handlers.

## Usage

When using **sipd**, everything must be configured through [settings.json](./settings.json).

```bash
~$ make
~$ ./sipd --config settings.json
```

## Tests

To run unit tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ make test
```

## Notes

- Currently being used by Samsung Electronics of America.

## License

**sipd** is licensed under [MIT License](./LICENSE.md).
