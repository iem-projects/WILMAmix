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
import logging as logging_
logging = logging_.getLogger('WILMA.net.discovery.Avahi')

import dbus, avahi
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop


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

class discoverer:
    def getKey(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        key = "["+str(arg_interface)+'/'+str(arg_protocol)+'/'+str(arg_name)+'/'+str(arg_stype)+'/'+str(arg_domain)+"]"
        return key

    def newHandler(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        try:
            interface, protocol, name, stype, domain, host, aprotocol, address, port, txt, flags = self.server.ResolveService(
                arg_interface, arg_protocol, arg_name, arg_stype, arg_domain,
                avahi.PROTO_UNSPEC, dbus.UInt32(0))
            key=self.getKey(arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags)
            self.dict[key]={'name': str(name), 'address': str(address), 'port': int(port), 'iface': if_indextoname(interface)}
        except DBusException:
            logging.exception("caught exception")
	#logging.debug( "added...%s" % self.dict)
        
    def delHandler(self, arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags):
        key=self.getKey(arg_interface, arg_protocol, arg_name, arg_stype, arg_domain, arg_flags)
        try:
            del self.dict[key]
        except:
            logging.info("removed element '%s' not in dict" % key)
	#logging.debug( "deleted...%s" % self.dict)

    def __init__(self, service = '_wilma-sm._udp', domain='local'):
        self.dict=dict()
        loop = DBusGMainLoop()
        bus = dbus.SystemBus(mainloop=loop)
        self.server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'),
                                      avahi.DBUS_INTERFACE_SERVER)
        sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
                                                 self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                                                               avahi.PROTO_INET,
                                                                               service,
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

            if not name in ret:
                ret[name]=dict()
            (ret[name])[d['iface']]={'address':d['address'], 'port':d['port']}
        return ret


##############

class publisher:
    def __init__(self,  service='_wilma-sm._udp', port=7777, name=None):
        DBusGMainLoop( set_as_default=True )
        self.group       = None #our entry group
        self.domain      = "" # Domain to publish on, default to .local
        self.host        = "" # Host to publish records for, default to localhost

        if type(name) is not str:
            name = str(name)

        self.serviceName = name
        self.serviceType = service
        self.servicePort = port
        self.serviceTXT  = ["linux = rulez", "protocol = OSC"] #TXT record for the service


        self.bus = dbus.SystemBus()

        self.server = dbus.Interface(
            self.bus.get_object( avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER ),
            avahi.DBUS_INTERFACE_SERVER )

        self.server.connect_to_signal( "StateChanged", self.server_state_changed )
        self.server_state_changed( self.server.GetState() )

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.remove_service()
        if not self.group is None:
            self.group.Free()

    def add_service(self):
        if self.group is None:
            self.group = dbus.Interface(
                self.bus.get_object( avahi.DBUS_NAME, self.server.EntryGroupNew()),
                avahi.DBUS_INTERFACE_ENTRY_GROUP)
            self.group.connect_to_signal('StateChanged', self.entry_group_state_changed)

        #logging.debug( "Adding service '%s' of type '%s' ..." % (self.serviceName, self.serviceType))

        self.group.AddService(
            avahi.IF_UNSPEC,  #interface
            avahi.PROTO_INET, #protocol (IPv4)
            dbus.UInt32(0),   #flags
            self.serviceName, self.serviceType,
            self.domain, self.host,
            dbus.UInt16(self.servicePort),
            avahi.string_array_to_txt_array(self.serviceTXT))
        self.group.Commit()

    def remove_service(self):
        if not self.group is None:
            self.group.Reset()

    def server_state_changed(self, state):
        if state == avahi.SERVER_COLLISION:
            #logging.debug( "WARNING: Server name collision")
            self.remove_service()
        elif state == avahi.SERVER_RUNNING:
            self.add_service()

    def entry_group_state_changed(self, state, error):
        #logging.debug( "state change: %i" % state)

        if state == avahi.ENTRY_GROUP_ESTABLISHED:
            #logging.debug( "Service established.")
            pass
        elif state == avahi.ENTRY_GROUP_COLLISION:
            self.serviceName = self.server.GetAlternativeServiceName(self.serviceName)
            #logging.debug( "WARNING: Service name collision, changing name to '%s' ..." % self.serviceName)
            self.remove_service()
            self.add_service()
        elif state == avahi.ENTRY_GROUP_FAILURE:
            logging.debug( "Error in group state changed: %s" % str( error))
            #main_loop.quit()
            return


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

