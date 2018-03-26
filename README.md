[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)
<p align="center">
  <img src="./docs/logo.png">
</p>

**sipd** is an [active recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) daemon. A daemon is a background process that handles incoming requests and logically responds - and a minute customization ranging from custom SIP method handling to internal/external RTP routing is possible.

Some key features are:

- **Maximum portability** implemented in pure Python and [only one non-mandatory dependency](#tests). You can either run it by porting the git repository or [building a single binary](./Makefile).

- **Ubiquitous support** from Python 2.7 to Python 3+.

- **High performance** using [customized asynchronous designs]().

- **RTP routing** using dynamic [Session Description Protocol](https://en.wikipedia.org/wiki/Session_Description_Protocol) population. For performance, using an external [Real-time Transport Protocol](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol) decoder is recommended.

- **Production ready** and currently running in a production environment against [Genesys](http://www.genesys.com) devices and handling [Samsung Electronics of America](http://www.samsung.com) call traffic.

## Usage

[sipd.json](./sipd.json) is a configuration file that customizes runtime environment. Although default setting will run fine, it can also be tuned for higher performance.

```bash
~$ git clone https://github.com/initbar/sipd.git
~$ cd ~/sipd
~$ emacs sipd.json # optional
~$ make run
```

## Tests

To run tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ sudo -H pip install unittest # testing framework
~$ make test
```

## Deploy

You can either use `make` to build and deploy to a remote server or `pip` to download straight from Python package manager.

```bash
~$ make clean
~$ make
```

## License
**sipd** is licensed under [GNU GPLv3](./LICENSE.md).
