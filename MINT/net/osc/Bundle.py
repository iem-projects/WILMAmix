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

from OSC import OSCMessage
import socket

class Bundle:
    def __init__(self, oscprefix=None, timestamp=None):
        b = OSCMessage()
        b.address = ""
        b.append("#bundle")
        b.append(0)
        b.append(0)
        self.b=b
        self.prefix=oscprefix
        if self.prefix is None:
            self.prefix=''
    def append(self, message):
        m = OSCMessage()
        address=self.prefix+message[0]
        data=message[1]
        m.address = address
        for x in data:
            m.append(x)        
        self.b.append(m.getBinary(), 'b')
        return self
    def __iadd__(self, message):
        return self.append(message)
    def data(self):
        return self.b.message
