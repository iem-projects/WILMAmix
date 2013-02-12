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
from PySide.QtNetwork import QUdpSocket

class NetClient:
    """ OSC-client running on GOD.
    sends OSC-messages to SMi.
    receives OSC-messages from SMi (and emits signals with the data)
    """

    def __init__(self, host, port, oscprefix=''):
        print "NetClient"
        self.addressManager = osc.CallbackManager()
        self.socket = QUdpSocket()
        self.socket.readyRead.connect(self._callback)
        self.socket.connectToHost(host, port);
        
        self.remote = (host, port) ## FIXXME: 'host' is not canonicalized
        self.keepListening=True
        self.oscPrefix=oscprefix
      

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

    def _callback(self):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        while self.socket.hasPendingDatagrams():
            datagram, sender, senderPort = self.socket.readDatagram(self.socket.pendingDatagramSize())
            self.addressManager.handle(datagram.data(), (sender.toString(), senderPort))

    def add(self, callback, oscAddress):
        """add a callback for oscAddress"""
        if self.addressManager is not None:
            self.addressManager.add(callback,  self.oscPrefix+oscAddress)

    def sendMsg(self, oscAddress, dataArray=[]):
        """send an OSC-message to the server"""
        from PySide.QtNetwork import QHostAddress

        if self.socket is not None and self.remote is not None:
            #self.socket.writeDatagram( osc.createBinaryMsg(self.oscPrefix+oscAddress, dataArray),  QHostAddress(self.remote[0]), self.remote[1])
            self.socket.writeDatagram( osc.createBinaryMsg(self.oscPrefix+oscAddress, dataArray),  QHostAddress(self.remote[0]), self.remote[1])

    def sendBundle(self, bundle):
        """send an OSC-bundle to the server"""
        if self.socket is not None and self.remote is not None:
            self.socket.sendto(bundle.message, self.remote)





def _callback(message, source):
    print "callback (no class): ", message

n = None

def _test_client():
    import time
    global n
    n = NetClient('localhost', 7777)
    n.add(_callback, '/foo')
    n.sendMsg('/foo');

if __name__ == '__main__':
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
        


