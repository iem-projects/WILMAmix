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



import gst

class AudioMeter:
    def __init__(self):
        self.name = 'mymeter'
        pipestring='jackaudiosrc ! audio/x-raw-float,channels=4 ! audioconvert ! level name='+self.name+' ! fakesink'
        self.pipeline = gst.parse_launch(pipestring)
        self.meter = self.pipeline.get_by_name(self.name)
        self.bus = self.pipeline.get_bus()
        self.meterWatch = self.bus.add_watch(self._handler, None);
        self.levels=[0]

    def _handler(self, bus, message, data):
        if (gst.MESSAGE_ELEMENT is message.type) and (message.src.get_name() == self.name):
            self.levels = message.structure['rms']
        return True

    def start(self):
        self.pipeline.set_state(gst.STATE_PLAYING)

    def stop(self):
        self.pipeline.set_state(gst.STATE_NULL)

    def getLevels(self):
        return self.levels

if __name__ == '__main__':
    meter = AudioMeter()
    meter.start()

    class ShowMeter:
        def __init__(self, meter):
            self.meter = meter
        def printMeters(self):
            print "levels:",self.meter.getLevels()
    
    try:
        import gobject
        sm = ShowMeter(meter)
        gobject.idle_add(sm.printMeters)
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    meter.stop()

