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
import SMgui as smifactory
from gui import SMmixer, Translator
import net

class MIXgui:
    def __init__(self, parent=None):
        self.conf=configuration.getMIX()
        service=(self.conf['/service']+'._'+self.conf['/protocol'])
        self.discover=net.discoverer(service=service)
        # Create widgets
        self.dict=self.discover.getDict()
        self.mixer=SMmixer(configuration, smifactory.SMgui, parent=self, guiparent=parent, SMs=self.dict)

        self.metro = metro.metro(self.ping, 100)

        self.refreshIt()
        self.mixer.show()

    def widget(self):
        return self.mixer

    def refreshIt(self):
        self.dict = self.discover.getDict()
        self.mixer.setSM(self.dict)

    def printIt(self):
        print self.dict

    def ping(self):
        self.mixer.ping()
