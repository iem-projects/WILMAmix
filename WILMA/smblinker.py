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
logging = logging_.getLogger('WILMA.SMi')
import time
from threading import Thread, Event

class GPIO:
    def __init__(self, gpio):
        filename=('/sys/class/gpio/gpio%d/value' % (gpio))
        self.oldstate=None
        try:
            with open(filename, 'r') as f:
                self.oldstate=GPIO._value(f.read())
                self.file=open(filename, 'w')
        except IOError:
            import sys
            self.file=sys.stdout
    def set(self, value=1):
        self.file.write(GPIO._value(value))
        self.file.flush()
    def reset(self):
        if self.oldstate is not None:
            self.file.write(self.oldstate)
            self.file.flush()
    @staticmethod
    def _value(v):
        try:
            return str(int(bool(int(v))))
        except ValueError:
            pass
        return '0'

class smblinker:
    class SMBlinkThread(Thread):
        def __init__(self, parent):
            Thread.__init__(self)
            self.parent=parent

        def run(self):
            gpio=self.parent.gpio
            if gpio:
                hi=self.parent.hi_time
                lo=self.parent.lo_time
                stoptime=time.time()+self.parent.duration
                while time.time() < stoptime:
                    gpio.set(1)
                    time.sleep(hi)
                    gpio.set(0)
                    time.sleep(lo)
            self.parent.stop()

    def __init__(self, gpio=45):
        self.thread=None
        self.gpio=GPIO(gpio)
        self.hi_time = 0.25
        self.lo_time = 0.25
        self.duration = 5

    def start(self, duration=None):
        if self.thread:
            return False
        if duration is not None:
            self.duration=duration
        if self.duration is None:
            self.duration = 5
        self.thread = self.SMBlinkThread(self)
        self.thread.start()
        return True
    def stop(self):
        self.gpio.reset()
        self.thread = None


######################################################################

if __name__ == '__main__':
    dur=3
    print("SM-blinker...%d sec" % (dur))
    try:
        s=smblinker()
        s.start(dur)
        print("started")
        time.sleep(1)
        print("milestone 1")
        time.sleep(dur)
    except IOError, e:
        print("ops: s", e)
    print("bye")
