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

class clientAbstract(object):
    """OSC-client.
    sends OSC-messages to server.
    receives OSC-messages from server (and passes them on)
    """

    def __init__(self, oscprefix=None, verbose=False):
        self.realAddressManager = osc.CallbackManager(prefix=oscprefix, verbose=verbose)
        if oscprefix is None:
            self.oscPrefix=''
        else:
            self.oscPrefix=oscprefix
        self.verbose=verbose
        self.remote =None

        self.disabled=False
        self.addressManager=None
        self.enable(True)

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
            self.addressManager.add(callback, oscAddress)

    def _send(self, data):
        """ABSTRACT: send raw data to the server"""
        raise Exception("_send()")

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
        """send an OSC-bundle `send(bundle)` or an OSC-message `send('/address', [data])` to remote-side"""
        if self.disabled: return
        if type(addr) is str: # it's an addr/data pair
            self.sendMsg(addr, data)
        elif data is None:    # it's a bundle
            self.sendBundle(addr)
        else:
            raise Exception("usage: send(addr, data) OR send(bundle)")

    def getRemote(self):
        """returns a (host, port) tuple of the remote-side (aka: server)"""
        return self.remote

    def enable(self, state=None):
        if state is not None:
            self.disabled = not bool(state)
        if self.disabled:
            self.addressManager = None
        else:
            self.addressManager = self.realAddressManager
        return self.disabled


######################################################################
## no testing (this is an abstract class)
