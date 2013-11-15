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

import OSC
from Bundle import Bundle as OSCBundle

class FUDI(object):
    def __init__(self):
        self.fudiarray=[]
        self.manager = OSC.CallbackManager()
        self.manager.add(self._fudiMsg, None)
        self.manager.add(self._fudiBundle, "#bundle")
    def _fudiMsg(self, addr, typetags, data, src):
        self.fudiarray+=[addr[0]]
        self.fudiarray+=data
    def _fudiBundle(self, timetag, starting, depth, source):
        if starting:
            self.fudiarray+=['[']
            self.fudiarray+=[depth]
            if timetag:
                self.fudiarray+=[timetag]
        else:
            self.fudiarray+=[']']
            self.fudiarray+=[depth]

    def getFUDI(self, msg):
        self.fudiarray=[]
        try:
            self.manager.handle(msg.data())
        except:
            self.manager.handle(msg.message)
        return self.fudiarray

if __name__ == "__main__":
    print("Welcome to the OSC/FUDI testing program.")
    def getFUDI(msg):
        f=FUDI()
        return f.getFUDI(msg)
    def testFUDI():
        message = OSC.OSCMessage()
        message.setAddress("/foo/play")
        message.append(44)
        message.append(11)
        message.append(4.5)
        message.append(True)
        message.append(None)
        message.append("the white cliffs of dover")
        print("MSG: %s" % getFUDI(message))

        print("msg: %s %s" % (isinstance(message, OSC.OSCMessage), type(message)))
        bundle = OSCBundle()
        bundle.append(message)
        bundle+=message
        print("bundle: %s" % getFUDI(bundle))

    testFUDI()
