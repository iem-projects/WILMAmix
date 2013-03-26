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
import DirChooser

def _syncDicts(sourcedict, targetdict=None, clearFirst=True):
    if sourcedict is targetdict:
        return targetdict
    if targetdict is None:
        targetdict=dict()
    if clearFirst:
        targetdict.clear()
    for k in sourcedict:
        targetdict[k]=sourcedict[k]
    return targetdict

_streamProtocols=['RTP', 'RTSP']
_streamProfiles =['L16', 'L24']
_streamChannels =(4,5)
_networkInterfaces = ['eth0', 'wlan0']
class SMconfig(QtGui.QDialog, SMconfig_ui.Ui_SMconfig):
    def __init__(self, parent=None, name="SMi", settings={}, confs=None):
        super(SMconfig, self).__init__(parent)
        self.parent=parent
        self.settings=settings
        self.localsettings=_syncDicts(self.settings)
        self.setupUi(self)

        self.pullChooser=DirChooser.PullDirChooser(self, self.settings['/path/in'])
        self.pushChooser=DirChooser.PushDirChooser(self, self.settings['/path/out'])

        self.meters.setPortCount(4)
        self.meters.setScales(None)
        self.statemeter.setPort(['CPU', 'memory', 'disk', "battery", "runtime"])
        self.statemeter.setScale([None, None, None, None, " minutes"])
        self.statemeter.setInverse([False, False, False, True, True])
        self.statemeter.build()
        self.setWindowTitle(QtGui.QApplication.translate("SMconfig", "Configuration of", None, QtGui.QApplication.UnicodeUTF8)+" '"+name+"'")

        self.set_pullDir(self.settings['/path/in'])
        self.set_pushDir(self.settings['/path/out'])

        self.streamProtocol.clear()
        self.streamProtocol.addItems(_streamProtocols)
        self.streamProfile.clear()
        self.streamProfile.addItems(_streamProfiles)
        self.streamChannels.setMinimum(_streamChannels[0])
        self.streamChannels.setMaximum(_streamChannels[1])
        self.networkInterface.clear()
        self.networkInterface.addItems(_networkInterfaces)

        self._connect()
    def _connect(self):
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

        self.gainFader.valueChanged.connect(self.moved_gainFader)


    def do_accept(self):
        print "FIXME ok"
        _syncDicts(self.localsettings, self.settings)
        self.hide()
    def do_reject(self):
        print "ko"
        self.hide()
    def do_copyConfig(self):
        if self.parent is not None:
            self.parent.copyConfigToSelected()

    def do_pull(self):
        if self.parent is not None:
            self.parent.pull()
    def do_pullDir(self):
        self.pullChooser.choose(self.set_pullDir)
    def do_push(self):
        if self.parent is not None:
            self.parent.push()
    def do_pushDir(self):
        self.pushChooser.choose(self.set_pushDir)

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

    def moved_gainFader(self, value):
        print "FIXME: fader", value

    def set_pullDir(self, path):
        print "setting pulldir", path
        self.settings['/path/in']=path
        self.pullDir.setText(path)
        pass
    def set_pushDir(self, path):
        print "setting pushdir", path
        self.settings['/path/out']=path
        self.pushDir.setText(path)
        pass

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
