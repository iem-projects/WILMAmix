#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2013, IOhannes m zmölnig, IEM

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
from MINTmix import DiscoverSM
from MINTmix.gui import SMmixer, Translator

class Form(QDialog):
   
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.discover=DiscoverSM()
        # Create widgets
        self.dict=self.discover.getDict()
        print self.dict
        self.mixer=SMmixer(self, self.dict)
        self.bRefresh = QPushButton("Refresh")
        self.bPrint   = QPushButton("Print")
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.mixer)
        layout.addWidget(self.bRefresh)
        layout.addWidget(self.bPrint)
        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.bRefresh.clicked.connect(self.refreshIt)
        self.bPrint.clicked.connect(self.printIt)

        self.refreshIt()

    def refreshIt(self):
        self.dict = self.discover.getDict()
        self.mixer.setSM(self.dict)
        self.show()

    def printIt(self):
        print self.dict

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    translator = Translator(app)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())



