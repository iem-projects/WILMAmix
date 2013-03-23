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

class SMsmall(QtGui.QGroupBox):
    def __init__(self, parent=None, name="SMi", maxwidth=None):
        super(SMsmall, self).__init__(parent)
        self.name = name
        self.maxWidth=maxwidth

        self.setTitle(self.name)

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)

        # Create widgets
        self.selector = QtGui.QCheckBox(self.name, self)
        self.selector.stateChanged.connect(self.select)
        layout.addWidget(self.selector)

        mixframe=QtGui.QFrame(self)
        sublayout=QHBoxLayout()
        sublayout.setContentsMargins(0,0,0,0)
        mixframe.setLayout(sublayout)
        layout.addWidget(mixframe)

        self.meter = qsynthMeter(self, 4, [-1], maxwidth=self.maxWidth) # maxwidth should be dynamic and ack the fader width
        sublayout.addWidget(self.meter)

        self.launchButton = QtGui.QPushButton("Launch")
        self.launchButton.clicked.connect(self.launch)
        layout.addWidget(self.launchButton)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))

    def select(self, value=None):
        """(de)selects this SMi, or toggles selection"""
        if value is None: ## toggle
            pass
        elif value:       ## selected
            pass
        else:             ## deselected
            pass
    def selected(self):
        print "FIXME: current selection state"
        pass

    def launch(self):
        #self.launchButton.setEnabled(False)
        pass
    
    def setLevels(self, levels_dB=[-100.,-100.,-100.,-100.]):
        self.meter.setValues(levels_dB)

    def setState(self, level, msg):
        pass



######################################################################
if __name__ == '__main__':
    import sys
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            layout = QtGui.QHBoxLayout()
            names=['foo', 'bar', 'paz']
            self.meter=[]
            for n in names:
                m=SMsmall(self, n)
                self.meter+=[m]
                layout.addWidget(m)

            self.value = QtGui.QDoubleSpinBox(self)
            self.value.setMinimum(0)
            self.value.setMaximum(100)
            layout.addWidget(self.value)
            self.setLayout(layout)
            self.value.valueChanged.connect(self.setValue)
        def setValue(self, value):
            self.meter.setValue(0, value*0.01)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
