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

from PySide.QtGui import *

class MIXctl(QtGui.QGroupBox):
    """
    this is the 'Master Control' for all SMi channels.
    - handle selections (all on, all off, toggle)
    - start/stop selected
    - push files (to selected)
    - pull files (from selected)
    - quit
    """
    def __init__(self, parent=None):
        super(MIXctl, self).__init__(parent)
        self.name = "MINTmix"

        self.setTitle(self.tr(self.name))

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)

        # Create widgets

        ## select none/all/toggle
        selectlayout = QHBoxLayout()
        selectlayout.setContentsMargins(0,0,0,0)
        
        self.selectNoneButton = QtGui.QCheckBox(self)
        self.selectNoneButton.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.selectNoneButton.clicked.connect(self.selectNone)
        selectlayout.addWidget(self.selectNoneButton)
        
        self.selectAllButton = QtGui.QCheckBox(self)
        self.selectAllButton.setCheckState(QtCore.Qt.CheckState.Checked)
        self.selectAllButton.clicked.connect(self.selectAll)
        selectlayout.addWidget(self.selectAllButton)
        
        self.selectToggleButton = QtGui.QCheckBox(self)
        self.selectToggleButton.setTristate(True)
        self.selectToggleButton.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        self.selectToggleButton.clicked.connect(self.selectToggle)
        selectlayout.addWidget(self.selectToggleButton)

        selectframe=QtGui.QFrame(self)
        selectframe.setLayout(selectlayout)
        layout.addWidget(selectframe)

        ## PUSH/PULL buttons
        fileslayout = QVBoxLayout()
        fileslayout.setContentsMargins(0,0,0,0)

        self.pushButton = QtGui.QPushButton("PUSH")
        self.pushButton.clicked.connect(self.push)
        fileslayout.addWidget(self.pushButton)

        self.pullButton = QtGui.QPushButton("PULL")
        self.pullButton.clicked.connect(self.pull)
        fileslayout.addWidget(self.pullButton)

        filesframe=QtGui.QGroupBox(self)
        filesframe.setTitle("Files...")
        filesframe.setLayout(fileslayout)
        layout.addWidget(filesframe)

        #a button is missing here


        ## Launch Button
        self.launchButton = QtGui.QPushButton("START") # should be "RECORD", "STREAM" or "PROCESS"
        self.launchButton.setCheckable(True)           # so the button stays clicked (even when window is left)
        self.launchButton.clicked.connect(self.launchB)
        layout.addWidget(self.launchButton)

        ## Quit Button
        self.quitButton = QtGui.QPushButton("QUIT")
        self.quitButton.clicked.connect(self._quit)
        layout.addWidget(self.quitButton)

        ## Scan Button
        self.scanButton = QtGui.QPushButton("SCAN")
        self.scanButton.clicked.connect(self._scan)
        layout.addWidget(self.scanButton)
        


        self.setLayout(layout)
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

    def selectNone(self, value=None):
        self.selectNoneButton.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.select(False)
    def selectAll(self, value=None):
        self.selectAllButton.setCheckState(QtCore.Qt.CheckState.Checked)
        self.select(True)
    def selectToggle(self, value=None):
        self.selectToggleButton.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        self.select(None)

    def select(self, value=None):
        """(de)selects the SMis, or toggles selection"""
        print "select", value
        if value is None: ## toggle
            pass
        elif value:       ## selected
            pass
        else:             ## deselected
            pass
    def selected(self):
        print "FIXME: current selection state"
        pass

    def push(self):
        ## open up directory selector (with last push-dir pre-selected)
        ## then check whether the directory contains MAIN.pd
        ## call the SMi's push methods with this directory
        print "FIXME: push"
        pass
    def pull(self):
        ## open up directory selector (with last pull-dir pre-selected)
        ## (warn if directory exists)
        ## call the SMi's pull methods with this directory
        print "FIXME: pull"
        pass

    def _launch(self, state): ## start launch
        """start/stop the engine on the remote SMi"""
        self.setChecked(state)
        self.launched(state) ## reflect new launch state
    def launched(self, state):
        """called from outside to set/get the current state.
        MUST NOT call launch again (but should update GUI if needed)"""
        if state is not None:
            self.launchButton.setChecked(state)
        return self.launchButton.isChecked()
    def launchB(self): ## launchButton callback, toggles the launch state
        self._launch(self.launchButton.isChecked())
        pass
    def _quit(self):
        sys.exit(0)
    def _scan(self):
        print "FIXME: scanning"
        pass

    
    def setLevels(self, levels_dB=[-100.,-100.,-100.,-100.]):
        self.meter.setValues(levels_dB)

    def setState(self, level, msg):
        ## FIXME: add a status widget
        ## that gets green/red and displays the error as tooltip
        pass



######################################################################
if __name__ == '__main__':
    import sys
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            layout = QtGui.QHBoxLayout()
            self.ctl=MIXctl(self)
            layout.addWidget(self.ctl)
            self.setLayout(layout)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
