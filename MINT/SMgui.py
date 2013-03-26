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

import configuration, filesync
from gui import SMconfig, SMchannels, ThreadedInvoke
from net import client as _NetClient

import os

class SMgui:
    def __init__(self, parent=None, name="SMi", confs=None, maxwidth=None):
        oscprefix=name
        while oscprefix.startswith('/'):
            oscprefix=oscprefix[1:]
        interfaces=[]
        if confs is not None:
            interfaces=sorted(confs.keys())

        self.settings=configuration.getSM(name)
        self.confs=confs
        self.connection=None
        self.critical=[False]*5

        try:
            defaultconf=interfaces[0]
            config = confs[defaultconf]
            self.settings['/host'] = config['address']
            self.connection = _NetClient(config['address'],
                                         config['port'],
                                         oscprefix='/'+oscprefix,
                                         type=self.settings['/protocol'])
            self._connect()
        except IndexError:
            print "no network configurations -> no connection"

        self.channels=SMchannels.SMchannels(self, guiparent=parent, settings=self.settings, maxwidth=maxwidth)
        self.config=SMconfig.SMconfig(self, guiparent=parent, settings=self.settings, interfaces=interfaces)
        self.name = name

        if confs is not None:
            print "FIXXME: confs not yet used in SMgui"

    def _connect(self):
        self.connection.add(self._smiUser,      '/user')
        self.connection.add(self._smiOutpath,   '/path/out')
        self.connection.add(self._smiInpath,    '/path/in')
        self.connection.add(self._smiFader,     '/gain')
        self.connection.add(self._smiLevel,     '/level')
        self.connection.add(self._smiStreamURI, '/stream/uri')
        self.connection.add(self._smiStateCpu,  '/state/cpu')
        self.connection.add(self._smiStateMem,  '/state/mem')
        self.connection.add(self._smiStateDisk, '/state/disk')
        self.connection.add(self._smiStateBatt, '/state/battery')
        self.connection.add(self._smiStateRuntime, '/state/runtime')

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
        self.connection.sendMsg('/ping')

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
        self.connection.send(msg, data)

    def _smiUser(self, msg, src):
        self.settings['/user']=msg[2]
    def _smiFader(self, msg, src):
        self.config.setFader(msg[2])
    def _smiLevel(self, msg, src):
        levels=msg[2:]
        self.channels.setLevels(levels)
        self.config.setLevels  (levels)
    def _smiOutpath(self, msg, src):
        self.settings['/path/out']=msg[2]
    def _smiInpath (self, msg, src):
        self.settings['/path/in']=msg[2]
    def _smiStreamURI(self, msg, src):
        print "FIXME: smiURI"
    def _smiStateCpu(self, msg, src):
        value=msg[2]
        index=0
        self.config.setState(index, value)
        self.critical[index]=value>0.9
    def _smiStateMem(self, msg, src):
        value=msg[2]
        index=1
        self.config.setState(index, value)
        self.critical[index]=value>0.9
    def _smiStateDisk(self, msg, src):
        value=msg[2]
        index=2
        self.config.setState(index, value)
        self.critical[index]=value>0.9
    def _smiStateBatt(self, msg, src):
        value=msg[2]
        index=3
        self.config.setState(index, value)
        self.critical[index]=value<0.1
    def _smiStateRuntime(self, msg, src):
        value=msg[2]
        index=4
        self.config.setState(index, value)
        self.critical[index]=value<10


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
