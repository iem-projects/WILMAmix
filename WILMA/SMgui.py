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

## that's the main instance for SMi's GUI
import logging as logging_
logging = logging_.getLogger('WILMA.SMgui')
import warnings
import os, os.path
import datetime as _datetime


import configuration, filesync
from gui import SMconfig, SMchannel, ThreadedInvoke
from net import client as _NetClient
from net.osc import Bundle

class SMgui:
    def __init__(self, mixer=None, guiparent=None, name="SMi", netconfs=None, maxwidth=None):
        oscprefix=name
        while oscprefix.startswith('/'):
            oscprefix=oscprefix[1:]
        interfaces=[]
        if netconfs is not None:
            interfaces=sorted(netconfs.keys())

        self.settings=configuration.getSM(name)
        for path in ['/path/out', '/path/in']:
            p=os.path.expanduser(self.settings[path])
            self.settings[path]=p
        self._enabled = True
        self.running=False
        self.netconfs=netconfs
        self.connection=None
        self.critical=[False]*7
        self.pingcounter=0
        self.pullCb = None
        self.pushCb = None
        self.mixer = mixer
        self.timestamp = 0
        self.oscprefix='/'+oscprefix

        try:
            defaultconf=interfaces[0]
            config = netconfs[defaultconf]
            self.settings['/host'] = config['address']
            self._makeConnection(defaultconf)
        except IndexError:
            logging.exception("no network configurations -> no connection")

        self.channels=SMchannel.SMchannel(self, guiparent=guiparent, settings=self.settings, maxwidth=maxwidth)
        self.config=SMconfig.SMconfig(self, guiparent=guiparent, settings=self.settings, interfaces=interfaces)
        self.name = name

        self.channels.launchButton.setText(self.settings['/mode'].upper())
        if netconfs is not None:
            warnings.warn("FIXXME: netconfs not yet used in SMgui: %s" % str(netconfs))

    def __del__(self):
        self.shutdown()
    def shutdown(self):
        logging.info("shutdown %s" % str(self))
        if self.connection is not None:
            self.connection.shutdown()

    def _makeConnection(self, iface):
        if self.connection:
            self.connection.shutdown()

        try:
            config=self.netconfs[iface]
            address=config['address']
            port=config['port']
            oscprefix=self.oscprefix
            transport=self.settings['/protocol']
        except IndexError, KeyError:
            logging.exception("failed to guess network configurations -> no connection")
            return None

        self.connection = _NetClient(address,
                                     port,
                                     oscprefix=oscprefix,
                                     transport=transport)
        self.connection.add(self._smiMode,      '/mode')
        self.connection.add(self._smiUser,      '/user')
        self.connection.add(self._smiOutpath,   '/path/out')
        self.connection.add(self._smiInpath,    '/path/in')
        self.connection.add(self._smiFader,     '/gain')
        self.connection.add(self._smiLevel,     '/level')
        self.connection.add(self._smiTimestamp, '/timestamp')
        self.connection.add(self._smiStreamURI, '/stream/uri')
        self.connection.add(self._smiStateCpu,  '/state/cpu')
        self.connection.add(self._smiStateMem,  '/state/memory')
        self.connection.add(self._smiStateDisk, '/state/disk')
        self.connection.add(self._smiStateBatt, '/state/battery')
        self.connection.add(self._smiStateRuntime,'/state/runtime')
        self.connection.add(self._smiStateSyncExternal, '/state/sync/external')
        self.connection.add(self._smiStateSyncInternal, '/state/sync/internal')
        self.connection.add(self._smiStateLogLevel,      '/log/level')

        self.connection.add(self._smiStatePd,   '/state/process')

        ## the /process message itself will be forwarded t both smiState and smiProcess
        self.connection.add(self._smiState,     '/process')
        self.connection.add(self._smiProcess,   '/process/')

        self.settings ['/network/interface']=iface
        return self.connection

    def widget(self):
        return self.channels

    def select(self, value=None):
        """(de)selects this SMi, or toggles selection"""
        if value is None: ## toggle
            self._enabled = not self._enabled
        elif value:       ## selected
            self._enabled=True
        else:             ## deselected
            self._enabled=False
        self.channels.setChecked(self._enabled)
    def selected(self):
        return self._enabled and self.channels.isChecked()
    def getTimestamp(self):
        return self.timestamp

    def alive(self, isAlive=False):
        if isAlive:
            self.pingcounter=0
        else:
            self.pingcounter+=1
        if self.pingcounter >= 100:
            if self.channels.isChecked():
                self.channels.setChecked(False)
                self.config.closeButtons.setEnabled(False)
                self.config.copyConfigButton.setEnabled(False)
            if self.pingcounter > 65535:
                self.pingcounter = 100
        elif self._enabled and not self.channels.isChecked():
            self.channels.setChecked(True)
            self.config.closeButtons.setEnabled(True)
            self.config.copyConfigButton.setEnabled(True)

    def ping(self):
        self.alive()
        self.connection.sendMsg('/ping')
    def send(self, msg, data=None):
        self.connection.send(msg, data)


    ## callbacks from childs (SMchannel/SMconfig)
    def showConfig(self):
        self.config.applySettings(self.settings)
        self.config.show()

    def _hasSettingChanged(self, key, newsettings):
        if not key in newsettings:
            return False
        if (key in self.settings) and (self.settings[key]==newsettings[key]):
            return False
        self.settings[key]=newsettings[key]
        return True
    def applySettings(self, settings):
        changed=False
        oldiface=self.settings ['/network/interface']
        newiface=settings ['/network/interface']
        bundle = Bundle(oscprefix=self.oscprefix)
        for s in settings:
            changed|=self._hasSettingChanged(s, settings)
            bundle.append((s, [self.settings[s]]))

        self.channels.launchButton.setText(self.settings['/mode'].upper())

        ## TODO: if things have changed significantly, stop processing
        if changed:
            self.launch(False)

        if oldiface != newiface:
            self._makeConnection(newiface)

        ## in any case, we just dump the entire configuration to the SMi
        self.connection.send(bundle)

    def copySettings(self, settings):
        self.mixer.applySMiSettings(settings)
    def pull(self, path, fun=None):
        if path is None:
            return
        source=self.settings['/user']+'@'+self.settings['/host']+':'+self.settings['/path/out']+'/' #remote
        target=os.path.join(path, self.name, '') #local
        self.config.pullEnable(False)
        self.pullCb=fun
        f=filesync.filesync(source, target,
                            passphrases=[self.settings['/passphrase']],
                            deleteTarget=True,
                            doneCallback=ThreadedInvoke.Invoker(self.pullDone))
    def pullDone(self, state):
        self.config.pullEnable(True)
        pullCb=self.pullCb
        self.pullCb=None
        if pullCb is not None:
            pullCb(self, state)
    def push(self, path, fun=None):
        if path is None:
            return
        source=os.path.join(path, '') #local
        target=self.settings['/user']+'@'+self.settings['/host']+':'+self.settings['/path/in']+'/' #remote
        self.config.pushEnable(False)
        self.pushCb=fun
        f=filesync.filesync(source, target,
                            passphrases=[self.settings['/passphrase']],
                            deleteTarget=True,
                            doneCallback=ThreadedInvoke.Invoker(self.pushDone))
    def pushDone(self, state):
        self.config.pushEnable(True)
        pushCb=self.pushCb
        self.pushCb=None
        if pushCb is not None:
            pushCb(self, state)

    def launch(self, state, ts=None):
        bundle = Bundle(oscprefix=self.oscprefix)
        mode=self.settings['/mode']
        starttime=0
        if ts is not None: ## (TSmax, TSmin)
            starttime=ts[1]+10000
        bundle.append(('/record/timestamp', [starttime]))
        bundle.append(('/record/filename',  [_datetime.datetime.now().strftime('%Y%m%d-%H%M')]))
        bundle.append(('/process', [state]))
        self.running=state
        self.channels.setLaunched(self.running)
        self.connection.send(bundle)

    def _smiMode(self, addr, typetags, data, source):
        self.settings['/mode']=data[0]
        self.channels.launchButton.setText(self.settings['/mode'].upper())
    def _smiState(self, addr, typetags, data, source):
        state=data[0]
        self.running=state
        self.channels.setLaunched(self.running)
    def _smiStatePd(self, addr, typetags, data, source):
        state=data[0]
        # Pd either crashed or recovered; in any case, we stop
        self.launch(False)
    def _smiUser(self, addr, typetags, data, source):
        self.settings['/user']=data[0]
    def _smiFader(self, addr, typetags, data, source):
        if len(data)>0:
          self.config.setFader(data[0])
    def _smiLevel(self, addr, typetags, data, source):
        self.alive(True)
        levels=data
        self.channels.setLevels(levels)
        self.config.setLevels  (levels)
    def _smiTimestamp(self, addr, typetags, data, source):
        self.timestamp=data[0]
        self.config.setTimestamp(self.timestamp)
    def _smiOutpath(self, addr, typetags, data, source):
        self.settings['/path/out']=data[0]
    def _smiInpath (self, addr, typetags, data, source):
        self.settings['/path/in']=data[0]
    def _smiStreamURI(self, addr, typetags, data, source):
        warnings.warn("FIXME: smiURI")
    def _smiStateCpu(self, addr, typetags, data, source):
        value=data[0]
        index=0
        self.config.setState(index, value)
        self.critical[index]=value>0.9
    def _smiStateMem(self, addr, typetags, data, source):
        value=data[0]
        index=1
        self.config.setState(index, value)
        self.critical[index]=value>0.9
    def _smiStateDisk(self, addr, typetags, data, source):
        value=data[0]
        index=2
        self.config.setState(index, value)
        self.critical[index]=value>0.9
        if (self.running) and (value>=0.99) and ("record" == self.settings['/mode']):
            self.launch(False)
    def _smiStateBatt(self, addr, typetags, data, source):
        value=data[0]
        index=3
        self.config.setState(index, value)
        self.critical[index]=value<0.1
    def _smiStateRuntime(self, addr, typetags, data, source):
        value=data[0]
        index=4
        self.config.setState(index, value)
        self.critical[index]=value<10
    def _smiStateSyncExternal(self, addr, typetags, data, source):
        value=data[0]
        self.config.setSyncExternal(value)
        self.critical[5]=not value
    def _smiStateSyncInternal(self, addr, typetags, data, source):
        value=data[0]
        self.config.setSyncInternal(value)
        self.critical[6]=not value
    def _smiStateLogLevel(self, addr, typetags, data, source):
        value=data[0]
        self.config.setLogLevel(value)
    def _smiProcess(self, addr, typetags, data, source):
        self.mixer.sendProxy(self.oscprefix+addr[0], data)

    def proxyForward(self, addr, data=None, prefix=''):
        """proxy->SMi"""
        if not self.selected():
            return
        self.send(prefix+addr, data)

    def _processProxyCallback(self, addr, typetags, data, source):
        """proxyreceiver -> SMi (for /process data)"""
        self.proxyForward(addr[0], data, '/process')

    def _proxyCallback(self, addr, typetags, data, source):
        """proxyreceiver -> SMi (for trusted data)"""
        self.proxyForward(addr[0], data)

    def addProcessProxy(self, proxy):
        """register a callback in the process-proxy, that will automatically forward any important data in the proxy to the SMi"""
        subtree=self.oscprefix+'/'
        proxy.add(self._processProxyCallback, subtree)

    def addProxy(self, proxy):
        """add a callback for our SMi in the proxy.
        whenever the proxy receives data for us, it will then call our callback
        (so we can forward it to the SMi.
        we trust the sender to use the correct prefix"""
        subtree=self.oscprefix+'/'
        proxy.add(self._proxyCallback, subtree)


######################################################################
if __name__ == '__main__':
    import sys
    from PySide import QtGui
    class Form(QtGui.QDialog):
        def __init__(self, guiparent=None):
            super(Form, self).__init__(guiparent)
            self.d=dict()
            self.d['/network/interface']='eth0'
            self.d['/path/in' ]='/tmp/WILMA/in'
            self.d['/path/out']='/tmp/WILMA/out'
            self.d['/mode'    ]='stream'
            self.d['/stream/protocol']='RTP'
            self.d['/stream/profile' ]='L16'
            self.d['/stream/channels']=4
            self.d['/proxy/server/port']=9998
            self.d['/proxy/client/host']='localhost'
            self.d['/proxy/client/port']=9999
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
            self.meter[0]._smiFader()
        def setValue(self, value):
            for m in self.meter:
                m.setLevels([value-100]*4)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
