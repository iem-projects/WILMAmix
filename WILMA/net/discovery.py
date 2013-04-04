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

## dictionary:
## name ->
##        iface -> {ip, port}

import discoveryAvahi


def discoverer(service = '_wilma-sm._udp', domain='local'):
    return discoveryAvahi.discoverer(service=service, domain=domain)


##############

def publisher(service='_wilma-sm._udp', port=7777, name=None):
    return discoveryAvahi.publisher(service=service, port=port, name=name)


######################################################################

def test_doloop():
    import gobject
    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass


def test_discover():
    discover = discoverer()
    test_doloop()


def test_publish():
    tcp = publisher('_wilma-sm._tcp')
    udp = publisher('_wilma-sm._udp')
    test_doloop()

if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        typ=sys.argv[1]
        if typ == "publish":
            test_publish()
        elif typ == "discover":
            test_discover()
        else:
            print "%s publish|discover" % (sys.argv[0])
    else:
        print "defaulting to 'discover'"
        test_discover()
