#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus, gobject, avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop

TYPE = '_mintOSC._udp'

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

class ZeroConf:

    def getKey(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        key = "["+str(arg_interface)+'/'+str(arg_protocol)+'/'+str(arg_name)+'/'+str(arg_stype)+'/'+str(arg_domain)+"]"
        return key

    def newHandler(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags = self.server.ResolveService(
            arg_interface, arg_protocol, arg_name, arg_stype, arg_domain,
            avahi.PROTO_UNSPEC, dbus.UInt32(0))
        key=self.getKey(arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags)
        self.dict[key]={'name': name, 'address': address, 'port': port, 'iface': if_indextoname(interface)}
        
        
    def delHandler(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        key=self.getKey(arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags)
        try:
            del self.dict[key]
        except:
            print "removed element not in dict: ", key

        ## FIXXME: print
        print self.dict

    def __init__(self, domain='local'):
        self.dict=dict()
        loop = DBusGMainLoop()
        bus = dbus.SystemBus(mainloop=loop)
        self.server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
                                      avahi.DBUS_INTERFACE_SERVER)
        sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
                                                 self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                                                               avahi.PROTO_UNSPEC,
                                                                               TYPE,
                                                                               domain,
                                                                               dbus.UInt32(0))),
                                  avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        sbrowser.connect_to_signal("ItemNew", self.newHandler)
        sbrowser.connect_to_signal("ItemRemove", self.delHandler)

    def getDict(self):
        ## FIXXME: this will return a shallow copy, use deepcopy instead!
        return self.dict


if __name__ == '__main__':
    zc = ZeroConf()
    gobject.MainLoop().run()
