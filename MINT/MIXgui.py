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
    def __init__(self, parent=None):
        self.conf=configuration.getMIX()
        service=(self.conf['/service']+'._'+self.conf['/protocol'])
        self.discover=net.discoverer(service=service)

        self.dict=None
        self.pushing=dict()
        self.pulling=dict()

        self.mixconfig = MIXconfig.MIXconfig(self, guiparent=parent, settings=self.conf)
        self.mixctl = MIXctl.MIXctl(self, guiparent=parent, settings=self.conf)
        self.sm     = [] ## array of active SMi's
        self.smmixer=SMmixer(guiparent=parent, mixctl=self.mixctl)

        self.metro = metro.metro(self.ping, 100)

        self.scanSM()
        self.smmixer.show()

    def widget(self):
        return self.smmixer

    def _config(self):
        self.mixconfig.show()

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
    def applySMiSettings(self, settings):
        for s in self.selected():
            s.applySettings(settings)
    def applyMixSettings(self, settings):
        print "FIXME: applyMixSettings"
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
