<p align="center">
  <img src="./docs/logo.png">
</p>

# SIPd

**SIPd** is an active recording [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) daemon. A daemon is a background process that handles incoming requests and logical responses - and a full customization ranging from custom SIP method handlers (e.g. *INVITE*) to internal/external RTP handlers are possible.

Some key features are:

- **Maximum portability** implemented in pure Python and [only one non-mandatory dependency](#dependencies). You can either run it by porting the git repository or [building a single binary](./Makefile).

- **Ubiquitous support** for Python 2 and Python 3.

- **High performance** using customized asynchronous patterns and designs.

- **Production ready** and currently running in a production environment against [Genesys](http://www.genesys.com) devices and [Samsung Electronics of America](http://www.samsung.com) call traffic.

## Dependencies

```bash
~$ sudo -H pip install unittest # not required
```

## Usage

[sipd.json](./sipd.json) is a configuration file that customizes runtime environment. Although default setting will run fine in a staging environment, it can also be tuned for higher performance.

```bash
~$ # emacs sipd.json
~$ make run
```

## Tests

To run tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ make test
```

## Deploy

Use `make` to build and deploy to a remote server:

```bash
~$ make clean
~$ make
```

## License
**SIPd** is licensed under [GNU GPLv3](./LICENSE.md).
