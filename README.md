[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Finitbar%2Fsipd.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Finitbar%2Fsipd?ref=badge_shield)
<p align="center">
  <img src="./docs/logo.png">
</p>

**sipd** is an [active recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) daemon. A daemon is a background process that handles incoming requests and logically responds - and a minute customization ranging from custom SIP method handling to internal/external RTP routing is possible.

Some key features are:

- **Universal support** from Python 2.7 to Python 3+.

- **Maximum portability** implemented in pure Python and [non-mandatory dependencies](./requirements.txt). You can either run it by cloning the git repository or [building a single binary](#deploy).

- **High performance** using [reactor asynchronous design pattern](https://en.wikipedia.org/wiki/Reactor_pattern).

- **SIP load balance** to other SIP daemons.

- **Fast RTP routing** using dynamic [Session Description Protocol](https://en.wikipedia.org/wiki/Session_Description_Protocol) generation. For the optimal performance, using an external [Real-time Transport Protocol](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol) decoder is highly recommended.

- **Production ready** and currently running in a production environment against [Genesys](http://www.genesys.com) devices and handling [Samsung Electronics of America](http://www.samsung.com) call traffic.

## Dependencies

```bash
~$ sudo apt install libmysqlclient-dev
~$ sudo pip install -r requirements.txt
```

## Usage

[sipd.json](./sipd.json) is a non-mandatory configuration file that allows customization to the runtime environment. Although default settings is fine, it can also be tuned for higher performance.

```bash
~$ git clone https://github.com/initbar/sipd
~$ cd ~/sipd
~$ # vi sipd.json
~$ make run
```

## Tests

To run unit tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ make test
```

## Deploy

You can either use `make` to build and deploy to a remote server or `pip` to download straight from Python package manager.

```bash
~$ make clean
~$ make
```

## Database

By default, **sipd** only supports MySQL database. For more, please feel free to fork the project and PR.

## License
**sipd** is licensed under [GNU GPLv3](./LICENSE.md).

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Finitbar%2Fsipd.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Finitbar%2Fsipd?ref=badge_large)
