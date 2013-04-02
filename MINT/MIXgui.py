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

import metro, configuration
import SMgui
import net
from gui import SMmixer, MIXctl, MIXconfig

class MIXgui:
    class smi2process:
        def __init(self, name, callback):
            self.name=name
            self._callback=callback
        def callback(self, msg, src):
            addr=msg[0].split('/')
            addr[1]='process'
            data=msg[2:]
            self._callback('/'.join(addr), data)

    def __init__(self, parent=None):
        self.settings=configuration.getMIX()
        service=(self.settings['/service']+'._'+self.settings['/protocol'])
        self.discover=net.discoverer(service=service)

        self.dict=None
        self.pushing=dict()
        self.pulling=dict()

        self.proxyserver = None
        self.proxyclient = None

        self.mixconfig = MIXconfig.MIXconfig(self, guiparent=parent, settings=self.settings)
        self.mixctl = MIXctl.MIXctl(self, guiparent=parent, settings=self.settings)
        self.sm     = [] ## array of active SMi's
        self.smmixer=SMmixer(guiparent=parent, mixctl=self.mixctl)

        self.metro = metro.metro(self.ping, 100)

        self.scanSM()
        self.smmixer.show()

        self._proxyServer()
        self._proxyClient()

    def widget(self):
        return self.smmixer

    def _config(self):
        self.mixconfig.show()

    def _proxyServer(self):
        self.proxyserver = None
        port=int(self.settings['/proxy/server/port'])
        if (port>0) and (port<65536):
            self.proxyserver = net.server(port=port, transport='udp', backend='gui')
            self.proxyserver.add(self._proxyCallback, None)
    def _proxyClient(self):
        self.proxyclient = None
        port=int(self.settings['/proxy/client/port'])
        host=self.settings['/proxy/client/host']
        if (port>0) and (port<65536):
            self.proxyclient = net.client(host=host, port=port, transport='udp', backend='gui')
            self.proxyclient.add(self._proxyCallback, None)

    def _nullCallback(self, msg, src):
        pass

    def _proxyCallback(self, msg, src):
        """new data from the remote add, forward it to the SMi's"""
        # FIXXME: only sent messages relevant for the given proxy
        ###  e.g.: '/SM[12]/foo/bar'
        ###  should translate to
        ###        '/SM1/process/foo/bar'
        ###        '/SM2/process/foo/bar'
        addr=msg[0]
        addr='/process'+addr

        data=msg[2:]

        self.send(addr, data)
        pass

    def sendProxy(self, addr, msg=None):
        """send data to the proxy/proxies"""
        if self.proxyclient is not None:
            self.proxyclient.send(addr, msg)
        if self.proxyserver is not None:
            self.proxyserver.send(addr, msg)

    def send(self, addr, msg=None):
        """send an OSC-message to all SMi's"""
        for s in self.selected():
            s.send(addr, msg)

    def scanSM(self):
        self.dict = self.discover.getDict()
        for sm in self.sm:
            sm.shutdown()
        self.sm=[]

        for sm in sorted(self.dict.keys()):
            d=self.dict[sm]
            smi=SMgui.SMgui(mixer=self, guiparent=self.smmixer, name=sm, confs=d)
            self.sm+=[smi]
        self.smmixer.setSM(self.sm)

    def printIt(self):
        print self.dict

    def ping(self):
        for sm in self.sm:
            sm.ping()

    def selected(self):
        # FIXME: i'm sure this can be done very elegant with some lambda function
        result=[]
        for sm in self.sm:
            if sm.selected():
                result+=[sm]
        return result
    def select(self, state):
        for sm in self.sm:
            sm.select(state)

    def launch(self, state):
        ts=self.syncTimestamps()
        for s in self.selected():
            s.launch(state, ts)
    def pull(self, path):
        if path is None:
            self.mixctl.pushpulled(False)
            return
        self.pulling.clear()
        for s in self.selected():
            self.pulling[s]=True
            s.pull(path, self._pulled)
    def push(self, path):
        if path is None:
            self.mixctl.pushpulled(True)
            return
        self.pushing.clear()
        for s in self.selected():
            self.pushing[s]=True
            s.push(path, self._pushed)
    def _hasSettingChanged(self, key, newsettings):
        if not key in newsettings:
            return False
        if (key in self.settings) and (self.settings[key]==newsettings[key]):
            return False
        self.settings[key]=newsettings[key]
        return True
    def applySMiSettings(self, settings):
        for s in self.selected():
            s.applySettings(settings)
    def applyMixSettings(self, settings):
        proxyclientchanged = (self._hasSettingChanged('/proxy/client/port', settings) or
                              self._hasSettingChanged('/proxy/client/host', settings))
        proxyserverchanged = (self._hasSettingChanged('/proxy/server/port', settings))
        if proxyclientchanged:
            self._proxyClient()
        if proxyserverchanged:
            self._proxyServer()

    def syncTimestamps(self):
        ts=[]
        for s in self.selected():
            ts+=[s.getTimestamp()]
        return (max(ts), min(ts))

    def _pulled(self, sm, ret):
        self.pulling[sm]=False
        if not True in self.pulling.values():
            self.mixctl.pushpulled(False)
    def _pushed(self, sm, ret):
        self.pushing[sm]=False
        if not True in self.pushing.values():
            self.mixctl.pushpulled(True)
