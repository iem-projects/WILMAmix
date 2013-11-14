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
import logging as logging_
logging = logging_.getLogger('WILMA.net.server.UDP')
import socket, gobject

import serverAbstract
from discovery import publisher

class serverUDP(serverAbstract.serverAbstract):
    """ OSC-server running on SMi.
    publishes connection information (via zeroconf),
    receives OSC-messages (and emits signals with the data),
    sends back OSC-messages
    """

    def __init__(self, host='', port=0, oscprefix=None, service=None, verbose=False):
        """creates a listener on any (or specified) port"""
        super(serverUDP, self).__init__(port=port, oscprefix=oscprefix, verbose=verbose)
        self.verbose=verbose
        self.keepListening=True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        ip, port = self.socket.getsockname()
        gobject.io_add_watch(self.socket, gobject.IO_IN, self._callback)
        self.port=port

        if service is not None:
            self.publisher = publisher(port=port, name=self.publishname, service=service+'._udp')

    def __del__(self):
        self.shutdown()

    def _callback(self, socket, *args):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        # sock == self.socket
        data, address = socket.recvfrom(8192)
        if self.keepListening and (self.addressManager is not None):
            #self.socket = socket
            self.remote = address
            self.addressManager.handle(data, address)

        return self.keepListening

    def shutdown(self):
        self.keepListening=False
        if self.socket is not None:
            try:
                self.socket.shutdown()
                self.socket.close()
            except:
                pass
        if self.publisher is not None:
            self.publisher.shutdown()
            del self.publisher
            self.publisher = None
        if self.addressManager is not None:
            del self.addressManager
            self.addressManager = None
        self.remote = None
        self.socket = None


    def _send(self, data):
        if self.socket is not None and self.remote is not None:
            logging.log(1, "serverUDP.sending '%s' to %s" % (str(data), str(self.remote)))
            self.socket.sendto( data,  self.remote)

######################################################################

def _callback(addr, typetags, message, source):
    print "callback (no class): ", (addr, typetags, message, source)

class _TestServer:
    def __init__(self, port=0):
        self.serv = serverUDP(port=port)
        self.bundle = None
        self.serv.add(self.callback, '/test')
        self.serv.add(self.bundles , '#bundle')

    def __del__(self):
        if self.serv is not None:
            self.serv.shutdown()
            del self.serv
            self.serv = None

    def bundles(self, timestamp, state, depth, source):
        # we inflate all bundles to a single one
        if 0==depth:
            if state:
                from osc import Bundle
                self.bundle = Bundle(timestamp=timestamp)
            else:
                self.serv.sendBundle(self.bundle)

    def callback(self, addr, typetags, data, source):
        print "callback: ",(addr, typetags, data, source)
        if self.bundle is None:
            self.serv.sendMsg(addr[1], data)
        else:
            self.bundle.append((addr[1], data))

    def shutdown(self):
        self.serv.shutdown()

if __name__ == '__main__':
    n = _TestServer(port=8777)
    gobject.threads_init()

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    print n
    if n is not None:
        n.shutdown()
        del n
    print "bye"
