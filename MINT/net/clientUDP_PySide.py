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
from PySide.QtNetwork import QUdpSocket

class clientUDP:
    """ OSC-client running on GOD.
    sends OSC-messages to SMi.
    receives OSC-messages from SMi (and emits signals with the data)
    """

    def __init__(self, host, port, oscprefix='', verbose=False):
        self.addressManager = osc.CallbackManager(verbose=verbose)
        self.keepListening=True
        self.oscPrefix=oscprefix
        self.verbose=verbose
        self.remote =None

        self.socket = QUdpSocket()
        self.socket.readyRead.connect(self._callback)
        self.socket.connectToHost(host, port);
        self.remote = (host, port) ## FIXXME: 'host' is not canonicalized


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
        '''Asynchronous connection listener. Receives data and passes it to OSC-addressManager.'''
        while self.socket.hasPendingDatagrams():
            datagram, sender, senderPort = self.socket.readDatagram(self.socket.pendingDatagramSize())
            self.addressManager.handle(datagram.data(), (sender.toString(), senderPort))

    def add(self, callback, oscAddress):
        """add a callback for oscAddress"""
        if self.addressManager is not None:
            if oscAddress is None:
                if self.oscPrefix is not '': oscAddress = self.oscPrefix+'/'
            else:
                oscAddress=self.oscPrefix+oscAddress
            self.addressManager.add(callback, oscAddress)

    def _send(self, data):
        from PySide.QtNetwork import QHostAddress
        if self.socket is not None and self.remote is not None:
            if self.verbose:
                print "sending '", data, "' to ", self.remote

            self.socket.writeDatagram(data, QHostAddress(self.remote[0]), self.remote[1])

    def sendMsg(self, oscAddress, dataArray=[]):
        """send an OSC-message to the server"""
        self._send( osc.createBinaryMsg(self.oscPrefix+oscAddress, dataArray) )
    def sendBundle(self, bundle):
        """send an OSC-bundle to the server"""
        if isinstance(bundle, osc.Bundle):
            self._send(bundle.data())
        else:
            self._send(bundle.message)
    def send(self, addr, data=None):
        if type(addr) is str: # it's an addr/data pair
            self.sendMsg(addr, data)
        elif data is None:    # it's a bundle
            self.sendBundle(addr)
        else:
            raise Exception("usage: send(addr, data) OR send(bundle)")

    def getRemote(self):
        return self.remote



######################################################################

def _callback(message, source):
    print "callback (no class): ", message

n = None

def _test_client():
    import time
    global n
    n = clientUDP('localhost', 7777)
    n.add(_callback, '/foo')
    n.sendMsg('/foo');

if __name__ == '__main__':
    _test_client()

    try:
        import gobject
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    print n
    if n is not None:
        n.shutdown()
        del n
    print "bye"



