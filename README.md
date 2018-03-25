<p align="center">
  <img src="./docs/logo.png">
</p>

# SIPd

**SIPd** is an active recording [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) daemon. A daemon is a customizable background process that handles incoming requests and outputs respective responses. **SIPd** provides a daemon that allows full customization ranging from SIP method requests (e.g. *INVITE*) to internal/external RTP handling.

The key features of **SIPd** are:

* **Maximum Portability**: **SIPd** is implemented in pure Python with only [one non-mandatory dependency](#dependencies). You can either run it by porting the git repository or [building a single binary](./Makefile). Currently, Windows native is not supported.

* **Python Standardization**: **SIPd** fully supports Python 2 and Python 3.

* **Asynchronous Design**: **SIPd** fully and asynchronously runs on bottom-up customizations and designs.

* **Production Ready**: **SIPd** was written and tested with [Genesys](http://www.genesys.com) devices for high-volume Samsung Electronics of America traffic.

## Dependencies

```bash
~$ sudo -H pip install unittest # not required
```

## Usage

`sipd.json` is a configuration file that customizes runtime environment of **SIPd**.

```bash
~$ # emacs sipd.json
~$ make run
```

To run tests, type `make test`. If the test exists with exit status 0, then it's ready to be run!

```bash
~$ make test
```

Use `make` to build and deploy to a remote server:

```bash
~$ make clean
~$ make
```

## License
**SIPd** is licensed under [GNU GPLv3](./LICENSE.md).
