# Active recording Session Initiation Protocol daemon (sipd).
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
# https://github.com/initbar/sipd

#-------------------------------------------------------------------------------
# 21.1.2 180 Ringing
#
# The UA receiving the INVITE is trying to alert the user.  This
# response MAY be used to initiate local ringback.
#
# https://tools.ietf.org/html/rfc3261#section-21.1.2
#-------------------------------------------------------------------------------

SIP_RINGING = {
    'status_line': 'SIP/2.0 180 Ringing',
    'sip': [
        'From',
        'To',
        'Via',
        'Call-ID',
        'Contact',
        'CSeq',
        'Allow'
    ]
}

SIP_RINGING_SAMPLE = '''\
SIP/2.0 180 Ringing
CSeq: 1 INVITE
Call-ID: 9E565000-C50B-B39A-61A3-33FB67415050-7090@192.168.1.4
From: <sip:Genesys@192.168.1.4:7090>;tag=9E565000-C50B-45BE-9F69-DCFCE02B493D
To: <sip:record=2018-02-21:20-14-192.168.1.8:15060>
Via: SIP/2.0/UDP 192.168.1.8:15060;branch=z9hG4bK0x25b1a5408dd30fabcdef09,SIP/2.0/TCP 192.168.1.4:7090;branch=z9hG4bK0x194bd1008dd30f
Record-Route: <sip:0x196e3b00@192.168.1.8:15060;lr;gvp.rm.datanodes=1;confinstid=2018-02-21-192.168.1.8:15060;idtag=0000000C>
Contact: <sip:ImpactRecorder@192.168.1.9:5060;transport=udp>
Allow: INVITE, OPTIONS, BYE, CANCEL, ACK, UPDATE, INFO
Content-Length: 0
'''
