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

import socket, gobject
import SocketServer
from Discovery import Publisher
import serverAbstract
from SLIP import SLIP

class OSCRequestHandler(SocketServer.BaseRequestHandler):

class serverTCP(serverAbstract.serverAbstract):
    """ OSC-server running on SMi.
    publishes connection information (via zeroconf),
    receives OSC-messages (and emits signals with the data),
    sends back OSC-messages
    """

    def __init__(self, host='', port=0, oscprefix=None, service=None, verbose=False):
        """creates a listener on any (or specified) port"""
        super(serverTCP, self).__init__(port=port, oscprefix=oscprefix, verbose=verbose)
        self.remotes = dict()
        self.publisher=None
        self.keepListening=True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        ip, port = self.socket.getsockname()
        gobject.io_add_watch(self.socket, gobject.IO_IN, self._accept)
        self.socket.listen(1)

        if service is not None:
            self.publisher = Publisher(port=port, name=self.publishname, service=service+'._tcp')

    def __del__(self):
        self.shutdown()

    def _shutdown(self, sock):
        if sock is not None:
            try:
                sock.shutdown()
                sock.close()
            except:
                pass
        if self.remotes.has_key(sock):
            del self.remotes[sock]

    def shutdown(self, sock=None):
        if sock is None:
            self.keepListening=False
            self._shutdown(self.socket)
            if self.publisher is not None:
                self.publisher.shutdown()
                del self.publisher
                self.publisher = None
            if self.addressManager is not None:
                del self.addressManager
                self.addressManager = None
            for s in self.remotes:
                self._shutdown(s)
            self.remotes = None
            self.socket = None
        else:
            self._shutdown(sock)

    def _accept(self, sock, *args):
        '''Asynchronous connection listener. Starts a handler for each connection.'''
        conn, addr = sock.accept()
#        print "Connected", sock
        self.remotes[conn]=SLIP()
        gobject.io_add_watch(conn, gobject.IO_IN, self._callback)
        self.remote=(len(self.remotes)>0 or None)

        return True

    def _callback(self, sock, *args):
        '''Asynchronous connection listener. Handles incoming data.'''
        # sock == self.socket
        data, address = sock.recvfrom(8192)
##        print "DATA", data
##        for d in data:
##            print "data: ",ord(d)
        try:
            slip=self.remotes[sock]
        except KeyError:
            slip=None
        am=self.addressManager

        if len(data):
            if (slip is not None) and (am is not None):
                slip=self.remotes[sock]
                slip.append(data)
                for d in slip.get():
                    am.handle(d, address)
        elif (slip is not None):
            del self.remotes[sock]
        self.remote=(len(self.remotes)>0 or None)
        return (len(data)>0) and self.remotes.has_key(sock)

    def _send(self, data):
        if self.remotes is not None:
            for s in self.remotes:
                if self.verbose:
                    print "sending '", data, "' to ", self.remotes[s]
                slip = SLIP();
                slip+=data;
                s.sendall( slip.getData() )

######################################################################

if __name__ == '__main__':
    def _callback(message, source):
        print "callback (no class): ", message

    class _TestServer:
        def __init__(self, port=0):
            self.serv = serverTCP(port=port)
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

    n = _TestServer(port=7777)

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    print n
    if n is not None:
        n.shutdown()
        del n
    print "bye"
