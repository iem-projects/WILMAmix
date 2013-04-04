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

import osc

class serverAbstract(object):
    """ OSC-server.
    receives OSC-messages (and emits signals with the data),
    sends back OSC-messages
    """

    def __init__(self, port=0, oscprefix=None, verbose=False):
        """creates a listener on any (or specified) port"""
        self.verbose=verbose
        self.keepListening=True
        self.oscPrefix = oscprefix
        if oscprefix is None:
            self.oscPrefix=''

        self.remote = None # tuple describing the remote-side (host, port)
        self.port   = port # local listening port
        self.addressManager = osc.CallbackManager(verbose=verbose)
        self.publisher=None
        publishname=oscprefix
        if publishname is not None:
            while publishname.startswith('/'):
                publishname=publishname[1:]
        self.publishname=publishname
    def __del__(self):
        self.shutdown()

    def shutdown(self):
        """ABSTRACT: tear down the connection"""
        if self.addressManager is not None:
            del self.addressManager
            self.addressManager = None
        self.remote = None
        raise Exception("shutdown()")

    def removeAll(self):
        """remove all callbacks"""
        if self.addressManager is not None:
            self.addressManager.removeAll()

    def add(self, callback, oscAddress):
        """add a callback for oscAddress"""
        if self.addressManager is not None:
            if oscAddress is None:
                if self.oscPrefix is not '': oscAddress = self.oscPrefix+'/'
            else:
                oscAddress=self.oscPrefix+oscAddress
            self.addressManager.add(callback, oscAddress)

    def _send(self, data):
        """ABSTRACT: send raw data to the server"""
        raise Exception("_send()")

    def sendMsg(self, oscAddress, dataArray=[]):
        """send an OSC-message to connected client(s)"""
        self._send(osc.createBinaryMsg(self.oscPrefix+oscAddress, dataArray))
    def sendBundle(self, bundle):
        """send an OSC-bundle to connected client(s)"""
        if self.socket is not None and self.remote is not None:
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

    def getPort(self):
        return self.port
    def getRemote(self):
        return self.remote

######################################################################
## no testing (this is an abstract class)
