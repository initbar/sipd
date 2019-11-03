    [![Build Status](https://travis-ci.org/initbar/sipping.svg?branch=master)](https://travis-ci.org/initbar/sipping)

![](./.docs/assets/cover.png)

<div align="center">
  <p><strong>A high-performance Session Initiation Protocol daemon.</strong></p>
</div>

## About

**sipping** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) server daemon designed to do the followings:

- **High performance** using [reactor pattern](https://en.wikipedia.org/wiki/Reactor_pattern) to [efficiently handle incredible loads](#case-study).
- **Resilient and self-recoverable**. No program is perfect and all software developers will end up writing bugs. **sipping** accounts for those possibilities and tries to automatically recover through self health checks.
- **Maximum portability** implemented in Python and minimal dependencies. Just install, configure some settings, and run while you take a sip of your favorite coffee.
- Decode raw SIP messages against [Genesys](https://www.genesys.com) [Resource Managers](https://docs.genesys.com/Documentation/GVP/85/GDG/GCRM) ("signal servers").
- Respond with dynamically crafted SIP/SDP packets.
- Extensible with an [RTP protocol decoder]()
- Send serialized datagrams to databases.

## License

**sipping** is licensed under [MIT License](./LICENSE).
