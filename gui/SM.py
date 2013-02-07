#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013, IOhannes m zm?g, IEM

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

from PySide import QtCore, QtGui

from qsynthMeter import qsynthMeter
from PySide.QtGui import *

class SM(QtGui.QGroupBox):
    
    def __init__(self, parent=None, name="SM??", confs=None):
        super(SM, self).__init__(parent)
        self.setTitle(name)
        # Create widgets
        self.meter = qsynthMeter(self, 4, [])
        
        self.iface = QtGui.QComboBox()
        for conf in confs:
            self.iface.addItem(conf['iface'])

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)

        layout.addWidget(self.meter)
        layout.addWidget(self.iface)
   
        self.setLayout(layout)
