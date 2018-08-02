[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)

<center>
  <img href="./docs/logo.png">
</center>

**sipd** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) daemon.

## Usage

[config.json](./config.json) is a mandatory configuration file that allows minute customization of the runtime environment. Although default settings is fine, it can be tuned for better performance.

```bash
~$ make
~$ ./sipd
```

## Tests

To run unit tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ make test
```

## License

**sipd** is licensed under [GNU GPLv3](./LICENSE.md).
