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

import MINT, MINT.utils, MINT.osc
import GUILauncher

class SM(QtGui.QGroupBox):
    class Setting:
        def __init__(self):
            self.streamtype='rtsp'
            self.streamprofile='L16'
    
    def __init__(self, parent=None, name="SMi", confs=None, maxwidth=None):
        super(SM, self).__init__(parent)
        self.setting = SM.Setting()
        self.name = name
        self.maxWidth=maxwidth
        self.launcher = None
        self._createLauncher()

        self.setTitle(name)
        #if confs is not None:
        #    print confs

        defaultconf = sorted(confs.keys())[0]
        config = confs[defaultconf]

        oscprefix=name
        while oscprefix.startswith('/'):
            oscprefix=oscprefix[1:]

        self.connection = MINT.net.Client(config['address'], config['port'], oscprefix='/'+oscprefix)
        self.connection.add(self.faderCb, '/gain')
        self.connection.add(self.levelCb, '/level')
        self.connection.add(self.streamURI, '/stream/uri')

        layout = QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)

        # Create widgets
        self.stream = QtGui.QCheckBox(self.tr("streaming"), self)
        self.stream.stateChanged.connect(self.streamSet)
        layout.addWidget(self.stream)

        mixframe=QtGui.QFrame(self)
        sublayout=QHBoxLayout()
        sublayout.setContentsMargins(0,0,0,0)
        mixframe.setLayout(sublayout)
        layout.addWidget(mixframe)

        self.fader = QSlider()
        self.fader.setEnabled(False)
        self.fader.valueChanged.connect(self.faderSet)
        sublayout.addWidget(self.fader)
        self.meter = qsynthMeter(self, 4, [-1], maxwidth=self.maxWidth) # maxwidth should be dynamic and ack the fader width
        sublayout.addWidget(self.meter)

        self.iface = QtGui.QComboBox()
        if confs != None:
            for conf in sorted(confs.keys()):
                self.iface.addItem(conf)
        layout.addWidget(self.iface)

        getinfo = QtGui.QPushButton("Dump")
        getinfo.clicked.connect(self.dumpInfo)
        layout.addWidget(getinfo)


        self.launchButton = QtGui.QPushButton("LaunchGUI")
        self.launchButton.clicked.connect(self.launch)
        layout.addWidget(self.launchButton)

        self.launchRemote = QtGui.QPushButton("LaunchSM")
        self.launchRemote.clicked.connect(self.rlaunch)
        layout.addWidget(self.launchRemote)
        self.connection.add(self.rlaunchState, '/launch/state')


        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))

    def faderSet(self, value):
        gain=MINT.utils.SCALE(value, self.fader.minimum(), self.fader.maximum(), 0., 1., True)
        self.connection.sendMsg('/gain', [gain,]) #FIXME get max.value from slider

    def faderCb(self, msg, src):
        gainF=msg[2]
        gain=MINT.utils.SCALE(gainF, 0., 1., self.fader.minimum(), self.fader.maximum(), True)
        self.fader.blockSignals(True)
        self.fader.setValue(gain)
        self.fader.blockSignals(False)

    def levelCb(self, msg, src):
        levels_dB=msg[2:]
        self.meter.setValues(levels_dB)

    def ping(self):
        self.connection.sendMsg('/ping')

    def streamSet(self, value):
        if value is 0:
            self.stopStream()
        else:
            self.startStream()

    def startStream(self):
        b=MINT.osc.Bundle(oscprefix='/'+self.name)
        b+=('/stream/settings/type', [self.setting.streamtype])
        b+=('/stream/settings/profile', [self.setting.streamprofile])
        b+=('/stream/settings/channels', [4])
        b+=('/stream', [True])
        self.connection.sendBundle(b)
        pass

    def stopStream(self):
        self.connection.sendMsg('/stream', [False])
        pass

    def streamURI(self, msg, src):
        print "URI: ", msg[2]

    def dumpInfo(self):
        self.connection.sendMsg('/dump')

    def launch(self):
        self.launchButton.setEnabled(False)
        self.launcher.start()
    def launchDone(self):
        self._createLauncher()
        self.launchButton.setEnabled(True)
    def _createLauncher(self):
        self.launcher = GUILauncher.GUILauncher('pd', doneCb=self.launchDone, cwd='/tmp')

    def rlaunch(self):
        self.launchRemote.setEnabled(False)
        self.connection.sendMsg('/launch', 'xclock')
    def rlaunchState(self, msg, src):
        self.launchRemote.setEnabled(not msg[2])
