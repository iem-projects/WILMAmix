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

## TODO: bundle should be converted to nested arrays

## TODO: handle timetags in bundles
## TODO: escape FUDI special characters (space, semicolon,...)


class FUDI(object):
    def __init__(self):
        self.fudiarray=[]
        self.manager = OSC.CallbackManager()
        self.manager.add(self._fudiMsg, None)
        self.manager.add(self._fudiBundle, "#bundle")
    def _fudiMsg(self, addr, typetags, data, src):
        s=addr[0]
        for a in data:
            s+=" "
            if isinstance(a, basestring):
                s+=a.replace(' ', '\\ ').replace(';', '\\;').replace(',', '\\,')
            elif a is None:
                s+="bang"
            elif a is True:
                s+="1"
            elif a is False:
                s+="0"
            else:
                s+=str(a)
        self.fudiarray+=[s+";"]
    def _fudiBundle(self, timetag, starting, depth, source):
        if starting:
            s="[ %d" % depth
#            if timetag:
#                s+=" %s" % timetag
#                self.fudiarray+=[timetag]
            s+=";"
        else:
            s="] %d;" % depth
        self.fudiarray+=[s]

    def getFUDI(self, osc):
        self.fudiarray=[]
        self.manager.handle(osc.data())
        return self.fudiarray

    def getOSC(self, fudi):
        """get OSC from FUDI"""
        arr=fudi.split(' ') # LATER handle escaped spaces ('\ ')
        osc=OSC.OSCMessage()
        addr=str(arr[0])
        if not addr.startswith('/'):
            addr='/'+addr
        osc.setAddress(addr)
        for a in arr[1:]:
            if "bang" == a:
                osc.append(None)
                continue

            try:
                osc.append(int(a))
                continue
            except ValueError: pass
            try:
                osc.append(float(a))
                continue
            except ValueError: pass

            osc.append(a)
        return osc

if __name__ == "__main__":
    #    print("Welcome to the OSC/FUDI testing program.")
    def getFUDI(msg):
        f=FUDI()
        return f.getFUDI(msg)
    def testFUDI():
        message = OSC.OSCMessage()
        message.setAddress("/foo/play")
        message.append(44)
        message.append(11)
        message.append(4.5)
        #message.append(True)
        #message.append(None)
        message.append("the white shiny cliffs of dover")
        for a in getFUDI(message):  print a

        bundle = OSCBundle()
        bundle.append(message)
        bundle+=message
        #print("bundle: %s" % getFUDI(bundle))
        for a in getFUDI(bundle):  print a

    testFUDI()
