#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2013, IOhannes m zmölnig, IEM

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

import osc
import socket, gobject
from Discovery import Publisher

class NetServer:
    """ OSC-server running on SMi.
    publishes connection information (via zeroconf),
    receives OSC-messages (and emits signals with the data),
    sends back OSC-messages
    """

    def __init__(self, host='', port=0):
        """creates a listener on any (or specified) port"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.keepListening=True
        
        gobject.io_add_watch(self.socket, gobject.IO_IN, self._callback)
        
        self.remote = None

        ip, port = self.socket.getsockname()

        self.addressManager = osc.CallbackManager()
        self.publisher = Publisher(port=port)

    def __del__(self):
        self.shutdown()

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


    def _callback(self, socket, *args):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        # sock == self.socket
        data, address = socket.recvfrom(8192)
        if self.keepListening and (self.addressManager is not None):
            #self.socket = socket
            self.remote = address
            self.addressManager.handle(data)

        return self.keepListening

    def add(self, callback, oscAddress):
        """add a callback for oscAddress"""
        if self.addressManager is not None:
            self.addressManager.add(callback, oscAddress)

    def sendMsg(self, oscAddress, dataArray=[]):
        """send an OSC-message to connected client(s)"""
        if self.socket is not None and self.remote is not None:
            self.socket.sendto( osc.createBinaryMsg(oscAddress, dataArray),  self.remote)

    def sendBundle(self, bundle):
        """send an OSC-bundle to connected client(s)"""
        if self.socket is not None and self.remote is not None:
            self.socket.sendto(bundle.message, self.remote)


class NetClient:
    """ OSC-client running on GOD.
    sends OSC-messages to SMi.
    receives OSC-messages from SMi (and emits signals with the data)
    """
    def __init__(self, host, port):
        print "NetClient"
        self.addressManager = osc.CallbackManager()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote = (host, port) ## FIXXME: 'host' is not canonicalized
        self.keepListening=True
        gobject.io_add_watch(self.socket, gobject.IO_IN, self._callback)
      

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        self.keepListening=False
        if self.socket is not None:
            try:
                self.socket.shutdown()
                self.socket.close()
            except:
                pass
        if self.addressManager is not None:
            del self.addressManager
            self.addressManager = None
        self.remote = None
        self.socket = None

    def _callback(self, socket, *args):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        # sock == self.socket
        data, client = socket.recvfrom(8192)
        #print "DATA: ", data
        if self.keepListening and (self.addressManager is not None):
            #self.socket = socket
            #self.remote = client
            self.addressManager.handle(data)
        return self.keepListening

    def add(self, callback, oscAddress):
        """add a callback for oscAddress"""
        if self.addressManager is not None:
            self.addressManager.add(callback, oscAddress)

    def sendMsg(self, oscAddress, dataArray=[]):
        """send an OSC-message to the server"""
        if self.socket is not None and self.remote is not None:
            self.socket.sendto( osc.createBinaryMsg(oscAddress, dataArray),  self.remote)

    def sendBundle(self, bundle):
        """send an OSC-bundle to the server"""
        if self.socket is not None and self.remote is not None:
            self.socket.sendto(bundle.message, self.remote)

def _callback(message, source):
    print "callback (no class): ", message

class _TestServer:
    def __init__(self, port=0):
        self.serv = NetServer(port=port)
        self.serv.add(self.callback, '/test')

    def __del__(self):
        if self.serv is not None:
            self.serv.shutdown()
            del self.serv
            self.serv = None

    def callback(self, message, source):
        print "callback: ",message
        self.serv.sendMsg(message[0], message[2:])

    def shutdown(self):
        self.serv.shutdown()

n = None
def _test_server():
    global n
    n = _TestServer(port=7777)

def _test_client():
    import time
    global n
    n = NetClient('localhost', 7777)
    n.add(_callback, '/foo')
    n.sendMsg('/foo');

if __name__ == '__main__':
    if 1 is 0:
        _test_server()
    else:
        _test_client()

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    print n
    if n is not None:
        n.shutdown()
        del n
    print "bye"
        


