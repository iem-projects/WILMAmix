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

## that's the main instance for SMi's GUI

from gui import SMconfig, SMchannels, ThreadedInvoke
import configuration, filesync
import os

class SMgui:
    def __init__(self, parent=None, name="SMi", confs=None, maxwidth=None):
        self.settings=configuration.getSM(name)
        self.confs=confs
        interfaces=[]
        if confs is not None:
            interfaces=sorted(confs.keys())
        self.channels=SMchannels.SMchannels(self, guiparent=parent, settings=self.settings, maxwidth=maxwidth)
        self.config=SMconfig.SMconfig(self, guiparent=parent, settings=self.settings, interfaces=interfaces)
        self.name = name

        if confs is not None:
            print "FIXXME: confs not yet used in SMgui"

    def widget(self):
        return self.channels

    def select(self, value=None):
        """(de)selects this SMi, or toggles selection"""
        if value is None: ## toggle
            pass
        elif value:       ## selected
            pass
        else:             ## deselected
            pass
    def selected(self):
        return self.isChecked()

    def ping(self):
        ## FIXME: compat implementation for SM.py
        pass

    ## callbacks from childs (SMchannels/SMconfig)
    def showConfig(self):
        self.config.applySettings(self.settings)
        self.config.show()

    def applySettings(self, settings):
        print "FIXME: applySettings"
    def copySettings(self, settings):
        print "FIXME: copySettings"
    def pull(self, path):
        source=self.settings['/user']+'@'+self.settings['/host']+':'+self.settings['/path/out']+'/' #remote
        target=os.path.join(path, self.name) #local
        self.config.pullEnable(False)
        f=filesync.filesync(source, target,
                            passphrases=[self.settings['/passphrase']],
                            deleteTarget=True,
                            doneCallback=ThreadedInvoke.Invoker(self.config.pullEnable))
    def push(self, path):
        source=path #local
        target=self.settings['/user']+'@'+self.settings['/host']+':'+self.settings['/path/in']+'/' #remote
        self.config.pushEnable(False)
        f=filesync.filesync(source, target,
                            passphrases=[self.settings['/passphrase']],
                            deleteTarget=True,
                            doneCallback=ThreadedInvoke.Invoker(self.config.pushEnable))
    def send(self, msg, data=None):
        print "FIXME: send"

######################################################################
if __name__ == '__main__':
    import sys
    from PySide import QtGui
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            self.d=dict()
            self.d['/network/interface']='eth0'
            self.d['/path/in' ]='/tmp/MINT/in'
            self.d['/path/out']='/tmp/MINT/out'
            self.d['/mode'    ]='stream'
            self.d['/stream/protocol']='RTP'
            self.d['/stream/profile' ]='L16'
            self.d['/stream/channels']=4
            self.d['/proxy/receiver/port']=9998
            self.d['/proxy/sender/host']='localhost'
            self.d['/proxy/sender/port']=9999
            layout = QtGui.QHBoxLayout()
            names=[]
            for i in range(10):
                names+=['SM#'+str(i)]
            self.meter=[]
            for n in names:
                m=SMgui(self, n)
                self.meter+=[m]
                layout.addWidget(m.widget())

            self.value = QtGui.QDoubleSpinBox(self)
            self.value.setMinimum(-10)
            self.value.setMaximum(120)
            layout.addWidget(self.value)
            self.setLayout(layout)
            self.value.valueChanged.connect(self.setValue)
        def setValue(self, value):
            for m in self.meter:
                m.setLevels([value-100]*4)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
