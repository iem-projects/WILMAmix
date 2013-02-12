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

from MINT import NetServer
from MINT.osc import createBundle, appendToBundle

import gobject

class State:
    def __init__(self):
        self.mixer=None
        self.gains=[]
        try:
            from MINT.audio import AudioMixer
            self.mixer = AudioMixer()
        except ImportError:
            print "no AudioMixer available"

    def update(self):
        if self.gains is not None:
            self.gains=self.mixer.gain()


class MINTsm:
    def __init__(self):
        self.state=State()
        self.server = NetServer()
        self.server.add(self.ping, '/ping')
        self.server.add(self.setGain, '/gain')
        self.mixer = self.state.mixer

    def setGain(self, msg, src):
        if self.mixer is not None:
            gains=self.mixer.gain(msg[2:])

    def ping(self, msg, src):
        self.state.update()
        print "gains", self.state.gains
        bundle = createBundle()
        appendToBundle(bundle, '/ferrari/gain', self.state.gains)
        self.server.sendBundle(bundle)
        
        

if __name__ == '__main__':
    print "SM..."
    sm = MINTsm()
    import time
    
    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass


