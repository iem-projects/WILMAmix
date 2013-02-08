#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013, IOhannes m zmölnig, IEM

# This file is part of MINTmix
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
# along with MINTmix.  If not, see <http://www.gnu.org/licenses/>.

## dictionary:
## name ->
##        {ip, port, iface}

import dbus, avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop

TYPE = '_mint-sm._udp'

if_index2name=[]
try:
    import netifaces
    if_index2name = netifaces.interfaces()
except: pass

def if_indextoname(index):
    try:
        ifname=if_index2name[index-1]
    except:
        ifname="net:%02d" % (index)
    return ifname

class DiscoverSM:

    def getKey(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        key = "["+str(arg_interface)+'/'+str(arg_protocol)+'/'+str(arg_name)+'/'+str(arg_stype)+'/'+str(arg_domain)+"]"
        return key

    def newHandler(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags = self.server.ResolveService(
            arg_interface, arg_protocol, arg_name, arg_stype, arg_domain,
            avahi.PROTO_UNSPEC, dbus.UInt32(0))
        key=self.getKey(arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags)
        self.dict[key]={'name': str(name), 'address': str(address), 'port': int(port), 'iface': if_indextoname(interface)}
        
    def delHandler(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        key=self.getKey(arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags)
        try:
            del self.dict[key]
        except:
            print "removed element not in dict: ", key

    def __init__(self, domain='local'):
        self.dict=dict()
        loop = DBusGMainLoop()
        bus = dbus.SystemBus(mainloop=loop)
        self.server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
                                      avahi.DBUS_INTERFACE_SERVER)
        sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
                                                 self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                                                               avahi.PROTO_INET,
                                                                               TYPE,
                                                                               domain,
                                                                               dbus.UInt32(0))),
                                  avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        sbrowser.connect_to_signal("ItemNew", self.newHandler)
        sbrowser.connect_to_signal("ItemRemove", self.delHandler)

    def getDict(self):
        ## FIXXME: this will return a shallow copy, use deepcopy instead!
        ret=dict()
        for d0 in self.dict:
            d=self.dict[d0]
            name=d['name']
            if name in ret:
                ret[name]+=[{'address':d['address'], 'port':d['port'], 'iface':d['iface']}]
            else:
                ret[name] =[{'address':d['address'], 'port':d['port'], 'iface':d['iface']}]
        return ret


if __name__ == '__main__':
    discover = DiscoverSM()
    import gobject
    gobject.MainLoop().run()
