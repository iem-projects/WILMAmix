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

from MINT import NetServer, AudioMixer
from MINT.osc import createBundle, appendToBundle

from MINT.streaming import Server as StreamingServer

import gobject

class State:
    def __init__(self):
        self.mixer = AudioMixer()

    def update(self):
        self.gains=self.mixer.gain()


class MINTsm:
    def __init__(self):
        self.state=State()
        self.server = NetServer(port=7777)
        self.server.add(self.ping, '/ping')
        self.server.add(self.setGain, '/gain')
        self.server.add(self.controlStream, '/stream')
        self.mixer = self.state.mixer
        self.streamer = None

    def setGain(self, msg, src):
        gains=self.mixer.gain(msg[2:])

    def controlStream(self, msg, src):
        state=msg[2]
        print "controlStream", state
        if state is not None and int(state) > 0:
            self.startStream()
        else:
            self.stopStream()

    def startStream(self):
        print "startstream"
        if self.streamer is not None:
            self.stopStream()
        self.streamer = StreamingServer(type='rtsp')
        self.streamer.start()
        print self.streamer.getURI()

    def stopStream(self):
        print "stopstream"
        if self.streamer is not None:
            self.streamer.stop()
        self.streamer = None

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


