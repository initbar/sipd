[![Build Status](https://travis-ci.org/initbar/sipd.svg?branch=master)](https://travis-ci.org/initbar/sipd)

<div align="center">
  <p><strong>A high-performance <a href="https://tools.ietf.org/html/rfc2543">Session Initiation Protocol</a> daemon.</strong></p>
</div>

## About

**sipd** is an [active-recording](https://en.wikipedia.org/wiki/VoIP_recording) [Session Initiation Protocol](https://www.ietf.org/rfc/rfc3261.txt) server daemon designed to handle complex SIP packets. For example, it decodes raw SIP messages against [Genesys](https://www.genesys.com) [Resource Managers](https://docs.genesys.com/Documentation/GVP/85/GDG/GCRM) ("signal servers"), generates and responds dynamically crafted SIP/SDP packets, and optionally extensible with an [RTP protocol](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol) decoder.

## Design

![](./docs/design.png)

## License

**sipd** is licensed under [MIT License](./LICENSE).
