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

from PySide import QtCore, QtGui

from qsynthMeter import qsynthMeter
from PySide.QtGui import *

import MINT

class SM(QtGui.QGroupBox):
    
    def __init__(self, parent=None, name="SMi", confs=None):
        super(SM, self).__init__(parent)
        self.setTitle(name)
        #if confs is not None:
        #    print confs

        defaultconf = sorted(confs.keys())[0]
        config = confs[defaultconf]

        self.connection = MINT.NetClient(config['address'], config['port'], oscprefix='/'+name)

        # Create widgets
        self.stream = QtGui.QCheckBox(self.tr("streaming"), self)
        self.stream.setDown(True)

        mixframe=QtGui.QFrame(self)
        sublayout=QHBoxLayout()
        sublayout.setContentsMargins(0,0,0,0)
        mixframe.setLayout(sublayout)

        self.fader = QSlider()
        sublayout.addWidget(self.fader)
        self.meter = qsynthMeter(self, 4, [-1])
        #self.meter = qsynthMeter(self, 4, [])
        sublayout.addWidget(self.meter)
        
        self.iface = QtGui.QComboBox()
        if confs != None:
            for conf in sorted(confs.keys()):
                self.iface.addItem(conf)

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)

        layout.addWidget(self.stream)
        layout.addWidget(mixframe)
        layout.addWidget(self.iface)
   
        self.setLayout(layout)
        

