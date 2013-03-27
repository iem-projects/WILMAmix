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
import sys
import MIXctl_ui
import DirChooser, MIXconfig

class MIXctl(QtGui.QGroupBox, MIXctl_ui.Ui_MIXctl):
    """
    this is the 'Master Control' for all SMi channels.
    - handle selections (all on, all off, toggle)
    - start/stop selected
    - push files (to selected)
    - pull files (from selected)
    - quit
    """
    def __init__(self, smmix, guiparent=None, settings={}):
        super(MIXctl, self).__init__(guiparent)
        if guiparent is None:
            guiparent=self
        self.settings=settings
        self.smmix=smmix
        self.control=MIXconfig.MIXconfig(self, guiparent, self.settings)
        self.pullChooser=DirChooser.PullDirChooser(self)
        self.pushChooser=DirChooser.PushDirChooser(self)

        self.setupUi(self)
        self.selectNoneButton.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.selectAllButton.setCheckState(QtCore.Qt.CheckState.Checked)
        self.selectToggleButton.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._connect()
    def _connect(self):
        self.selectNoneButton.clicked.connect(self._selectNone)
        self.selectAllButton.clicked.connect(self._selectAll)
        self.selectToggleButton.clicked.connect(self._selectToggle)
        self.pushButton.clicked.connect(self._do_push)
        self.pullButton.clicked.connect(self._do_pull)
        self.launchButton.clicked.connect(self._do_launch)
        self.scanButton.clicked.connect(self._scan)
        self.configButton.clicked.connect(self._config)
        self.quitButton.clicked.connect(self._quit)

    def _selectNone(self, value=None):
        self.selectNoneButton.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.select(False)
    def _selectAll(self, value=None):
        self.selectAllButton.setCheckState(QtCore.Qt.CheckState.Checked)
        self.select(True)
    def _selectToggle(self, value=None):
        self.selectToggleButton.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        self.select(None)

    def select(self, value=None):
        """(de)selects the SMis, or toggles selection"""
        self.smmix.select(value)

    def _do_push(self):
        ## open up directory selector (with last push-dir pre-selected)
        ## then check whether the directory contains MAIN.pd
        ## call the SMi's push methods with this directory
        self.pushButton.setEnabled(False)
        self.pushChooser.choose(self.smmix.push)
    def _do_pull(self):
        ## open up directory selector (with last pull-dir pre-selected)
        ## (warn if directory exists)
        ## call the SMi's pull methods with this directory
        self.pullButton.setEnabled(False)
        self.pullChooser.choose(self.smmix.pull)
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
    def _do_launch(self): ## launchButton callback, toggles the launch state
        self._launch(self.launchButton.isChecked())
    def _quit(self):
        sys.exit(0)
    def _scan(self):
        self.smmix.scanSM()
    def _config(self):
        pass

    def setState(self, level, msg):
        ## FIXME: add a status widget
        ## that gets green/red and displays the error as tooltip
        pass
    def pushpulled(self, pushed):
        if pushed:
            self.pushButton.setEnabled(True)
        else:
            self.pullButton.setEnabled(True)

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
