# SIPd

Active recording [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) daemon.

## Dependencies
```bash
~$ sudo -H pip install unittest
```

## Usage
```bash
~$ # vi sipd.json
~$ make test
~$ make run
```

## Portability
**SIPd** is designed to be portable across all UNIX-based platforms with Python installation.

Use `make` to build and deploy to a remote server:
```bash
~$ make clean
~$ make
```

## License
**SIPd** is licensed under [GNU GPLv3](./LICENSE.md).
