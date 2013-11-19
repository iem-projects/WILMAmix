#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2013, IOhannes m zmölnig, IEM

# This file is part of WILMix
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
# along with WILMix.  If not, see <http://www.gnu.org/licenses/>.
import logging as logging_
logging = logging_.getLogger('WILMA.gui.SMconfig')

from PySide import QtCore, QtGui
from PySide.QtGui import *

import WILMA.utils
from qsynthMeter import qsynthMeter
import DirChooser

import SMconfig_ui


_dictKeys=[
    '/mode',
    '/stream/protocol',
    '/stream/profile',
    '/stream/channels',
    '/network/interface',
    '/version',
    ]
def _syncDicts(sourcedict, targetdict=None, clearFirst=True):

    if sourcedict is targetdict:
        return targetdict
    if targetdict is None:
        targetdict=dict()
    if clearFirst:
        targetdict.clear()
    for k in _dictKeys:
        try:
            targetdict[k]=sourcedict[k]
        except KeyError:
            logging.exception("missing key in source dictionary %s" %sourcedict)
    return targetdict

#_streamProtocols=['RTP', 'RTSP']
#_streamProfiles =['L16', 'L24']
#_streamChannels =(4,5)
_streamProtocols=['RTP']
_streamProfiles =['L16']
_streamChannels =(4,4)

class SMconfig(QtGui.QDialog, SMconfig_ui.Ui_SMconfig):
    def __init__(self, sm=None, guiparent=None, settings={}, interfaces=[]):
        super(SMconfig, self).__init__(guiparent)
        name=settings['/id']
        self.interfaces=interfaces
        self.loglevel = -1
        self.sm=sm
        self.settings=_syncDicts(settings)
        self.setupUi(self)
        self.setModal(False)

        self.pullChooser=DirChooser.PullDirChooser(self, None)
        self.pushChooser=DirChooser.PushDirChooser(self, None)

        self.meter.setPortCount(4)
        self.meter.setScales(None)

        self.statemeter.setPort(['CPU', 'memory', 'disk', "battery", "runtime"])
        self.statemeter.setScale([None, None, None, None, " minutes"])
        self.statemeter.setInverse([False, False, False, True, True])
        self.statemeter.setMaxheight(50)
        self.statemeter.build()
        self.setWindowTitle(QtGui.QApplication.translate("SMconfig", "Configuration of", None, QtGui.QApplication.UnicodeUTF8)+" '"+name+"'")

        self.streamProtocol.clear()
        self.streamProtocol.addItems(_streamProtocols)
        self.streamProfile.clear()
        self.streamProfile.addItems(_streamProfiles)
        self.streamChannels.setMinimum(_streamChannels[0])
        self.streamChannels.setMaximum(_streamChannels[1])
        self.networkInterface.clear()
        self.networkInterface.addItems(self.interfaces)
        self.applySettings(settings)
        self.setLogLevel(WILMA.logger.getLevel())
        self._connect()
    def _connect(self):
        self.closeButtons.accepted.connect(self._do_accept)
        self.closeButtons.rejected.connect(self._do_reject)

        self.copyConfigButton.clicked.connect(self._do_copyConfig)
        self.pullButton.clicked.connect(self._do_pull)
        self.pushButton.clicked.connect(self._do_push)

        self.streamProtocol.currentIndexChanged.connect(self._select_streamProtocol)
        self.streamProfile.currentIndexChanged.connect(self._select_streamProfile)
        self.streamChannels.valueChanged.connect(self._select_streamChannels)
        self.modeSelector.currentIndexChanged.connect(self._select_mode)
        self.networkInterface.currentIndexChanged.connect(self._select_networkInterface)

        self.gainFader.valueChanged.connect(self._moved_gainFader)
        self.debugLevel.currentIndexChanged.connect(self._select_debugLevel)

    def _do_accept(self):
        self.hide()
        self.sm.applySettings(self.settings)
    def _do_reject(self):
        self.hide()
    def _do_copyConfig(self):
        self.sm.copySettings(self.settings)

    def _do_pull(self):
        self.pullChooser.choose(self._set_pullDir)
    def _do_push(self):
        self.pushChooser.choose(self._set_pushDir)

    def _select_streamProtocol(self, value):
        self.settings['/stream/protocol']=_streamProtocols[value]
    def _select_streamProfile(self, value):
        self.settings['/stream/profile']=_streamProfiles[value]
    def _select_streamChannels(self, value):
        self.settings['/stream/channels']=value
    def _select_networkInterface(self, value):
        self.settings['/network/interface']=self.interfaces[value]
    def _select_mode(self, value):
        # ['stream', 'record', 'process', 'idle']
        mode=self.settings['/mode']
        if value is 0:
            mode='stream'
        elif value is 1:
            mode='record'
        elif value is 2:
            mode='process'
        elif value is 3:
            mode='idle'
        else:
            logging.warn("invalid mode '%s': falling back to '%s'" % (str(value), mode))
        self.settings['/mode']=mode
    def _select_debugLevel(self, value):
        lvl=int(logging_.getLevelName(self.debugLevel.currentText()))
        self.sm.send('/log/level', [lvl])
    def _moved_gainFader(self, value): ## this should immediately be sent to the SMi
        gain=WILMA.utils.SCALE(value, self.gainFader.minimum(), self.gainFader.maximum(), 0., 1., True)
        self.sm.send('/gain', [gain])

    def _set_pullDir(self, path):
        self.sm.pull(path)
    def _set_pushDir(self, path):
        self.sm.push(path)

    def pullEnable(self, enable=True):
        self.pullButton.setEnabled(enable)
    def pushEnable(self, enable=True):
        self.pushButton.setEnabled(enable)

    def applySettings(self, settings):
        """applies settings to the config-panel
        this really only sets the values in the selection boxes to the proper values.
        it doesn't do anything on the remote end"""
        _syncDicts(settings, self.settings)
        # mode
        mode=self.settings['/mode']
        imode=0
        if   'stream'  == mode: imode=0
        elif 'record'  == mode: imode=1
        elif 'process' == mode: imode=2
        elif 'idle'    == mode: imode=3
        self.modeSelector.setCurrentIndex(imode)
        # stream: protocol
        mode=self.settings['/stream/protocol']
        for i in range(self.streamProtocol.count()):
            if self.streamProtocol.itemText(i) == mode:
                self.streamProtocol.setCurrentIndex(i)
                break
        # stream: profile
        mode=self.settings['/stream/profile']
        for i in range(self.streamProfile.count()):
            if self.streamProfile.itemText(i) == mode:
                self.streamProfile.setCurrentIndex(i)
                break
        # stream: channels
        i=int(self.settings['/stream/channels'])
        self.streamChannels.setValue(i)
        # network: interface
        mode=self.settings['/network/interface']
        for i in range(self.networkInterface.count()):
            if self.networkInterface.itemText(i) == mode:
                self.networkInterface.setCurrentIndex(i)
                break

        self.label_version.setText(str(self.settings['/version']))

    def setLogLevel(self, loglevel):
        index=0
        level=WILMA.logger.getLevel(loglevel)
        print("loglevel: %s -> %s" % (self.loglevel, loglevel))
        if(level == self.loglevel):
            return
        self.loglevel = level

        levelname=logging_.getLevelName(level)

        # check whether this is a selectable log-level
        lvls=[self.debugLevel.itemText(i) for i in range(self.debugLevel.count())]

        print("LOG: %s in %s" % (levelname, lvls))

        self.debugLevel.blockSignals(True)
        try:
            index=lvls.index(levelname)
            print("found at %d" % index)
        except ValueError, e:
            lvls=WILMA.logger.getLogLevels()
            print("new levels %s" % str(lvls))
            self.debugLevel.clear()
            self.debugLevel.addItems(lvls)
            try:
                print("Found at %d" % index)
                index=lvls.index(levelname)
            except ValueError, e:
                print("fall back")
                pass
        self.debugLevel.setCurrentIndex(index)

        self.debugLevel.blockSignals(False)

    def setLevels(self, levels_dB=[-100.,-100.,-100.,-100.]):
        self.meter.setValues(levels_dB)
    def setFader(self, value):
        gain=WILMA.utils.SCALE(value, 0., 1., self.gainFader.minimum(), self.gainFader.maximum(), True)
        self.gainFader.blockSignals(True)
        self.gainFader.setValue(gain)
        self.gainFader.blockSignals(False)
    def setState(self, index, value):
        self.statemeter.setValue(index, value)
    def setTimestamp(self, value):
        self.timestamp.setText(str(value))
    def setSyncExternal(self, value):
        self.stateSyncExt.setChecked(value)
    def setSyncInternal(self, value):
        self.stateSyncInt.setChecked(value)

######################################################################
if __name__ == '__main__':
    import sys
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            self.d=dict()
            self.d['/network/interface']='auto'
            self.d['/path/in' ]='/tmp/WILMA/in'
            self.d['/path/out']='/tmp/WILMA/out'
            self.d['/mode'    ]='stream'
            self.d['/stream/protocol']='RTP'
            self.d['/stream/profile' ]='L16'
            self.d['/stream/channels']=4
            self.d['/version']='0.0'
            self.smconf=SMconfig(name="foo", settings=self.d)
            layout = QtGui.QHBoxLayout()
            self.openButton= QtGui.QPushButton("Config")
            self.openButton.clicked.connect(self.openB)
            layout.addWidget(self.openButton)
            self.quitButton= QtGui.QPushButton("Quit")
            self.quitButton.clicked.connect(self.quitB)
            layout.addWidget(self.quitButton)

            self.setLayout(layout)
        def openB(self):
            self.smconf.applySettings(self.d)
            self.smconf.show()
        def quitB(self):
            sys.exit(0)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
