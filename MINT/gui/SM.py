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

import MINT, MINT.utils
import MINT.net.osc as osc
import GUILauncher, statemeter, ThreadedInvoke

from .. import FileSync

class SM(QtGui.QGroupBox):
    class Setting:
        def __init__(self):
            self.streamtype='rtsp'
            self.streamprofile='L16'
            self.user='iem'
            self.inpath=None
            self.outpath=None
    
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

        self.connection = MINT.net.Client(config['address'], config['port'], oscprefix='/'+oscprefix, type=MINT.constants.PROTOCOL)
        self.connection.add(self.faderCb, '/gain')
        self.connection.add(self.levelCb, '/level')
        self.connection.add(self.streamURI, '/stream/uri')
        self.connection.add(self.cpuCb, '/state/cpu')
        self.connection.add(self.memCb, '/state/mem')
        self.connection.add(self.diskCb, '/state/disk')
        self.connection.add(self.battCb, '/state/battery')
        self.connection.add(self.runtimeCb, '/state/runtime')

        self.connection.add(self.userCb   , '/user')
        self.connection.add(self.outpathCb, '/path/out')
        self.connection.add(self.inpathCb , '/path/in')


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

        self.statemeter = statemeter.statemeter(self,
                                                ['CPU', 'memory', 'disk', "battery", "runtime"],
                                                scale  =[None , None , None , None, " minutes"],
                                                inverse=[False, False, False, True, True],
                                                maxheight=16,
                                                )
        layout.addWidget(self.statemeter)

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

        self.syncher = QtGui.QPushButton("Sync")
        self.syncher.clicked.connect(self.doSync)
        layout.addWidget(self.syncher)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))

    def faderSet(self, value):
        gain=MINT.utils.SCALE(value, self.fader.minimum(), self.fader.maximum(), 0., 1., True)
        self.connection.sendMsg('/gain', [gain,]) #FIXME get max.value from slider

    def ping(self):
        self.connection.sendMsg('/ping')

    def streamSet(self, value):
        if value is 0:
            self.stopStream()
        else:
            self.startStream()

    def startStream(self):
        b=osc.Bundle(oscprefix='/'+self.name)
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
        print "launchDone"
        self._createLauncher()
        self.launchButton.setEnabled(True)
    def _createLauncher(self):
        self.launcher = GUILauncher.GUILauncher('pd', doneCb=self.launchDone, cwd='/tmp')

    def rlaunch(self):
        self.launchRemote.setEnabled(False)
        self.connection.sendMsg('/launch', 'xclock')
    def rlaunchState(self, msg, src):
        self.launchRemote.setEnabled(not msg[2])

    def doneSync(self, success):
        print "synched:",success
        self.syncher.setEnabled(True)
    def doSync(self):
        if self.setting.inpath is not None:
            print "synching to",self.setting.inpath
            self.syncher.setEnabled(False)
            host,port=self.connection.getRemote()
            f=FileSync.FileSync('/tmp/tex', self.setting.user+'@'+host+':'+self.setting.inpath,
                                passphrases=['iem'],
                                deleteTarget=True,
                                doneCallback=ThreadedInvoke.Invoker(self.doneSync))
        else:
            print "don't no where to sync data to..."


    def faderCb(self, msg, src):
        if len(msg)<3: ## that's only 'address' and 'typetags', no data
            return
        gainF=msg[2]
        gain=MINT.utils.SCALE(gainF, 0., 1., self.fader.minimum(), self.fader.maximum(), True)
        self.fader.blockSignals(True)
        self.fader.setValue(gain)
        self.fader.blockSignals(False)
    def levelCb(self, msg, src):
        levels_dB=msg[2:]
        self.meter.setValues(levels_dB)

    def cpuCb(self, msg, src):
        value=msg[2]
        self.statemeter.setValue(0, value)
    def memCb(self, msg, src):
        value=msg[2]
        self.statemeter.setValue(1, value)
    def diskCb(self, msg, src):
        value=msg[2]
        self.statemeter.setValue(2, value)
    def battCb(self, msg, src):
        value=msg[2]
        self.statemeter.setValue(3, value)
    def runtimeCb(self, msg, src):
        value=msg[2]
        self.statemeter.setValue(4, value)

    def userCb(self, msg, src):
        self.setting.user=msg[2]
    def outpathCb(self, msg, src):
        self.setting.outpath=msg[2]
    def inpathCb(self, msg, src):
        self.setting.inpath=msg[2]
