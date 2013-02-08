#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2013, IOhannes m zmölnig, IEM

# publish a service on ZeroConf
#

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

import dbus
import avahi
from dbus.mainloop.glib import DBusGMainLoop

class Publish:
    def __init__(self,  service='_mint-sm._udp', port=7777, name=None):
        DBusGMainLoop( set_as_default=True )
        self.group       = None #our entry group
        self.domain      = "" # Domain to publish on, default to .local
        self.host        = "" # Host to publish records for, default to localhost

        if name is None:
            import socket
            name = socket.gethostname()

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
        if not self.group is None:
            self.group.Free()


    def add_service(self):
        if self.group is None:
            self.group = dbus.Interface(
                self.bus.get_object( avahi.DBUS_NAME, self.server.EntryGroupNew()),
                avahi.DBUS_INTERFACE_ENTRY_GROUP)
            self.group.connect_to_signal('StateChanged', self.entry_group_state_changed)

        #print "Adding service '%s' of type '%s' ..." % (self.serviceName, self.serviceType)

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
            #print "WARNING: Server name collision"
            self.remove_service()
        elif state == avahi.SERVER_RUNNING:
            self.add_service()

    def entry_group_state_changed(self, state, error):
        #print "state change: %i" % state

        if state == avahi.ENTRY_GROUP_ESTABLISHED:
            #print "Service established."
            pass
        elif state == avahi.ENTRY_GROUP_COLLISION:
            self.serviceName = self.server.GetAlternativeServiceName(self.serviceName)
            #print "WARNING: Service name collision, changing name to '%s' ..." % self.serviceName
            self.remove_service()
            self.add_service()
        elif state == avahi.ENTRY_GROUP_FAILURE:
            print "Error in group state changed", error
            #main_loop.quit()
            return




if __name__ == '__main__':
    import gobject

    tcp = Publish('_mint-sm._tcp')
    udp = Publish('_mint-sm._udp')
    
    main_loop = gobject.MainLoop()
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass
