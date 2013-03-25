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
import SMconfig_ui

class SMconfig(QtGui.QDialog, SMconfig_ui.Ui_SMconfig):
    def __init__(self, parent=None, name="SMi", settings={}, confs=None):
        super(SMconfig, self).__init__(parent)
        self.setupUi(self)
        self.meters.setPortCount(4)
        self.meters.setScales(None)
        self.statemeter.setPort(['CPU', 'memory', 'disk', "battery", "runtime"])
        self.statemeter.setScale([None, None, None, None, " minutes"])
        self.statemeter.setInverse([False, False, False, True, True])
        self.statemeter.build()
        self.setWindowTitle(QtGui.QApplication.translate("SMconfig", "Configuration of", None, QtGui.QApplication.UnicodeUTF8)+" '"+name+"'")

        self.closeButtons.accepted.connect(self.do_accept)
        self.closeButtons.rejected.connect(self.do_reject)

        self.copyConfigButton.clicked.connect(self.do_copyConfig)
        self.pullButton.clicked.connect(self.do_pull)
        self.pullDirButton.clicked.connect(self.do_pullDir)
        self.pushButton.clicked.connect(self.do_push)
        self.pushDirButton.clicked.connect(self.do_pushDir)

        self.streamProtocol.currentIndexChanged.connect(self.select_streamProtocol)
        self.streamProfile.currentIndexChanged.connect(self.select_streamProfile)
        self.streamChannels.valueChanged.connect(self.select_streamChannels)
        self.modeSelector.currentIndexChanged.connect(self.select_mode)
        self.networkInterface.currentIndexChanged.connect(self.select_networkInterface)
    def do_accept(self):
        print "ok"
        self.hide()
    def do_reject(self):
        print "ko"
        self.hide()
    def do_copyConfig(self):
        print "FIXME: copyConfig"
    def do_pull(self):
        print "FIXME: pull"
    def do_pullDir(self):
        print "FIXME: pullDir"
    def do_push(self):
        print "FIXME: push"
    def do_pushDir(self):
        print "FIXME: pushDir"

    def select_streamProtocol(self, value):
        print "FIXME: select streamProtocol:", value
    def select_streamProfile(self, value):
        print "FIXME: select streamProfile:", value
    def select_streamChannels(self, value):
        print "FIXME: select streamChannels:", value
    def select_networkInterface(self, value):
        print "FIXME: select networkInterface:", value
    def select_mode(self, value):
        print "FIXME: select mode:", value


######################################################################
if __name__ == '__main__':
    import sys
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            d=dict()
            d['/path/in' ]='/tmp/MINT/in'
            d['/path/out']='/tmp/MINT/out'
            self.smconf=SMconfig(name="foo", settings=d)
            layout = QtGui.QHBoxLayout()
            self.openButton= QtGui.QPushButton("Config")
            self.openButton.clicked.connect(self.openB)
            layout.addWidget(self.openButton)
            self.quitButton= QtGui.QPushButton("Quit")
            self.quitButton.clicked.connect(self.quitB)
            layout.addWidget(self.quitButton)

            self.setLayout(layout)
        def openB(self):
            self.smconf.show()
        def quitB(self):
            sys.exit(0)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
