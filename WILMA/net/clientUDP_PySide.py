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
logging = logging_.getLogger('WILMA.net.client.UDP.PySide')

from PySide.QtNetwork import QUdpSocket, QHostAddress

import clientAbstract

class clientUDP(clientAbstract.clientAbstract):
    """ OSC-client running on GOD.
    sends OSC-messages to SMi.
    receives OSC-messages from SMi (and emits signals with the data)
    """

    def __init__(self, host, port, oscprefix='', verbose=False):
        super(clientUDP, self).__init__(oscprefix=oscprefix, verbose=verbose)
        self.keepListening=True

        self.socket = QUdpSocket()
        self.socket.readyRead.connect(self._callback)
        self.socket.connectToHost(host, port);
        self.remote = (self.socket.peerName(), self.socket.peerPort())

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

    def _send(self, data):
        if self.socket is not None and self.remote is not None:
            logging.log(1, "sending '%s' to %s" % (str(data), str(self.remote)))

            self.socket.writeDatagram(data, QHostAddress(self.remote[0]), self.remote[1])

######################################################################

def _callback(addr, typetags, message, source):
    print "callback (no class): ", (addr, typetags, message, source)

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



