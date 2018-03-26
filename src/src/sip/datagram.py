# Active recording Session Initiation Protocol daemon (SIPd).
# Copyright (C) 2018  Herbert Shin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# https://github.com/initbar/SIPd

#-------------------------------------------------------------------------------
# 1.5.3 Text-Based
#
# SIP is text-based, using ISO 10646 in UTF-8 encoding throughout. This
# allows easy implementation in languages such as Java, Tcl and Perl,
# allows easy debugging, and most importantly, makes SIP flexible and
# extensible. As SIP is used for initiating multimedia conferences
# rather than delivering media data, it is believed that the additional
# overhead of using a text-based protocol is not significant.
#
# https://tools.ietf.org/html/rfc2543#section-1.5.3
#-------------------------------------------------------------------------------

class SIPDynamicDatagram(object):
    ''' empty datagram for dynamic insertion.
    '''
    def __init__(self):
        self.__data__ = {}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__data__.__str__()

    def __eq__(self, data):
        return isinstance(data, dict) and\
            self.__data__.__eq__(data)

    def __getitem__(self, key):
        return self.__data__.get(key)

    def __setitem__(self, key, value):
        key = key.replace('-', '_').lower()
        self.__data__[key] = value

    def setdefault(self, key, value):
        key = key.replace('-', '_').lower()
        self.__data__.setdefault(key, value)

    def items(self):
        return self.__data__.items()

    def get(self, key):
        return self.__getitem__(key)

    def set(self, key, value):
        return self.__setitem__(key, value)

class SIPDatagram(object):
    ''' datagram for generic SIP message.
    '''
    __slots__ = [ # memory optimization.
        '_from',
        '_to',
        'accept',
        'accept_encoding',
        'accept_language',
        'call_id',
        'contact',
        'content_encoding',
        'content_length',
        'content_type',
        'cseq',
        'date',
        'encryption',
        'expires',
        'record_route',
        'timestamp',
        'via'
    ]
    def __init__(self,
                 call_id=None,
                 _from=None,
                 _to=None):
        # general headers
        self.accept =\
        self.accept_encoding =\
        self.accept_language =\
        self.call_id =\
        self.contact =\
        self.cseq =\
        self.date =\
        self.encryption =\
        self.expires =\
        self.record_route =\
        self.timestamp =\
        self.via = None
        self._from = _from
        self._to = _to

        # entity headers
        self.content_encoding = None
        self.content_length = 0
        self.content_type = None

        # Genesys headers
        pass

#-------------------------------------------------------------------------------
# 4.1 Request-Line
#
# The Request-Line begins with a method token, followed by the
# Request-URI and the protocol version, and ending with CRLF. The
# elements are separated by SP characters.  No CR or LF are allowed
# except in the final CRLF sequence.
#
# https://tools.ietf.org/html/rfc2543#section-4.1
#-------------------------------------------------------------------------------

class SIPRequest(SIPDatagram):
    ''' extension to SIPDatagram with request headers.
    '''
    __slots__ = [ # memory optimization.
        'authorization',
        'contact',
        'hide',
        'max_forwards',
        'organization',
        'priority',
        'proxy_authorization',
        'proxy_require',
        'require',
        'response_key',
        'route',
        'subject',
        'user_agent'
    ]
    def __init__(self):
        super(SIPRequest, self).__init__(*args, **kw)
        self.authorization =\
        self.contact =\
        self.hide = None
        self.max_forwards = 70
        self.organization =\
        self.priority =\
        self.proxy_authorization =\
        self.proxy_require =\
        self.route =\
        self.require =\
        self.response_key =\
        self.subject =\
        self.user_agent = None

#-------------------------------------------------------------------------------
# 5 Response
#
# After receiving and interpreting a request message, the recipient
# responds with a SIP response message. The response message format is
# shown below:
#
#     Response  =  Status-Line        ;  Section 5.1
#                  *( general-header
#                  | response-header
#                  | entity-header )
#                  CRLF
#                  [ message-body ]   ;  Section 8
#
# SIP's structure of responses is similar to [H6], but is defined
# explicitly here.
#
# https://tools.ietf.org/html/rfc2543#section-5
#-------------------------------------------------------------------------------

class SIPResponse(SIPDatagram):
    ''' extension to SIPDatagram with response headers.
    '''
    __slots__ = [ # memory optimization.
        'allow',
        'proxy_authenticate',
        'retry_after',
        'server',
        'unsupported',
        'warning',
        'www_authenticate'
    ]
    def __init__(self):
        super(SIPResponse, self).__init__(*args, **kw)
        self.allow =\
        self.proxy_authenticate =\
        self.retry_after =\
        self.server =\
        self.unsupported =\
        self.warning =\
        self.www_authenticate = None
