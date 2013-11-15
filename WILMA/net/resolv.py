#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2013, IOhannes m zmölnig, IEM

# This file is part of WILMix
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WILMix.  If not, see <http://www.gnu.org/licenses/>.

from PySide.QtNetwork import QHostInfo, QHostAddress

def getAddress(hostname, preferIPv6=None):
# IPv6=true: prefer IPv6 addresses (if there are none, the function might still return IPv4)
# IPv6=false: prefer IPv4 addresses (if there are none, the function might still return IPv6)
# IPv6=None: first available address returned
    info=QHostInfo()
    adr=info.fromName(hostname).addresses()
    if not adr: return None
    if preferIPv6 is None:
        return adr[0].toString()
    for a_ in adr:
        a=QHostAddress(a_)
        if preferIPv6:
            if a.toIPv6Address():
                return a.toString()
        else:
            if a.toIPv4Address():
                return a.toString()
    return adr[0].toString()

if __name__ == '__main__':
    def testfun(name, ipv6):
        addr=getAddress(name, ipv6)
        print("%s -> %s" % (name, addr))

    import sys
    progname=sys.argv[0]
    ipv6=None
    args=[]
    if len(sys.argv)>1:
        s=sys.argv[1]
        if s.startswith('-'):
            args=sys.argv[2:]
            if "-ipv4" == s:
                ipv6=False
            elif "-ipv6" == s:
                ipv6=True
            else:
                print("Usage: resolv.py [-ipv4|-ipv6] <host1> [<host2> ...]")
                sys.exit(1)
        else:
            args=sys.argv[1:]
    if not args:
        args=['localhost', 'umlautq', 'example.com']
    for h in args:
        testfun(h,ipv6)
        

