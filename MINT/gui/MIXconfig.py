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
import MIXconfig_ui

_dictKeys=[
    '/proxy/receiver/port',
    '/proxy/sender/port',
    '/proxy/sender/host',
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
            print "missing key '"+k+"' in source dictionary",sourcedict
    return targetdict

_streamProtocols=['RTP', 'RTSP']
_streamProfiles =['L16', 'L24']
_streamChannels =(4,5)

class MIXconfig(QtGui.QDialog, MIXconfig_ui.Ui_MIXconfig):
    def __init__(self, mix=None, guiparent=None, settings={}):
        super(MIXconfig, self).__init__(guiparent)
        self.mix=mix
        self.settings=_syncDicts(settings)
        self.orgsettings=_syncDicts(settings)
        self.setupUi(self)
        self.applySettings(settings)
        self._connect()
    def _connect(self):
        self.closeButtons.accepted.connect(self._do_accept)
        self.closeButtons.rejected.connect(self._do_reject)

    def _do_accept(self):
        self.hide()
        self._getSettings()
        self.mix.applySettings(self.settings)
    def _do_reject(self):
        _syncDicts(self.orgsettings, self.settings)
        self.hide()
    def _getSettings(self):
        # proxy
        self.settings['/proxy/receiver/port']=self.proxy_recvPort.value()
        self.settings['/proxy/sender/port'  ]=self.proxy_sendPort.value()
        self.settings['/proxy/sender/host'  ]=self.proxy_sendHost.text()


    def applySettings(self, settings):
        """applies settings to the config-panel
        this really only sets the values in the selection boxes to the proper values.
        it doesn't do anything on the remote end"""
        _syncDicts(settings, self.settings)
        _syncDicts(self.settings, self.orgsettings)
        print "settings", self.settings

        # proxy
        self.proxy_recvPort.setValue(self.settings['/proxy/receiver/port'])
        self.proxy_sendPort.setValue(self.settings['/proxy/sender/port'])
        self.proxy_sendHost.setText(self.settings['/proxy/sender/host'])

######################################################################
if __name__ == '__main__':
    import sys
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            self.d=dict()

            self.d['/proxy/receiver/port']=1
            self.d['/proxy/sender/port']=2
            self.d['/proxy/sender/host']='localhost'

            self.mixconf=MIXconfig(self, settings=self.d)
            layout = QtGui.QHBoxLayout()
            self.openButton= QtGui.QPushButton("Config")
            self.openButton.clicked.connect(self.openB)
            layout.addWidget(self.openButton)
            self.quitButton= QtGui.QPushButton("Quit")
            self.quitButton.clicked.connect(self.quitB)
            layout.addWidget(self.quitButton)

            self.setLayout(layout)
        def openB(self):
            self.mixconf.applySettings(self.d)
            self.mixconf.show()
        def quitB(self):
            sys.exit(0)
        def applySettings(self, settings):
            self.d=settings
            print "fake applying:", settings

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())