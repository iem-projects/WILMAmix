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

from PySide.QtCore import *
from PySide.QtGui import *
import sys
from MINT import metro, configuration
from MINT import SMgui as smifactory
from MINT.gui import SMmixer, Translator
import MINT.net

class Form(QDialog):
   
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.conf=configuration.getMIX()
        service=(self.conf['/service']+'._'+self.conf['/protocol'])
        self.discover=MINT.net.discoverer(service=service)
        # Create widgets
        self.dict=self.discover.getDict()
        print self.dict
        self.mixer=SMmixer(smifactory.SMgui, self, self.dict)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.mixer)
        # Set dialog layout
        self.setLayout(layout)

        self.metro = metro(self.ping, 100)

        self.refreshIt()

    def refreshIt(self):
        self.dict = self.discover.getDict()
        self.mixer.setSM(self.dict)
        self.show()

    def printIt(self):
        print self.dict

    def ping(self):
        self.mixer.ping()

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    translator = Translator(app)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())



