[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)

<p align="center">
  <img src="./docs/logo.png">
</p>

**sipd** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) server daemon.

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

## License

**sipd** is licensed under [MIT Licesne](./LICENSE.md).
