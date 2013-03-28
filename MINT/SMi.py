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

from net import server as NetServer
from urlparse import urlparse

from net.osc import Bundle

from streaming import Server as StreamingServer
from audio import AudioMixer
import systemhealth
import pdserver
import pdfile
import configuration


import os

class State:
    def __init__(self, config):
        self.mixer=None
        self.gains =[]
        self.levels=[]
        try:
          self.mixer = AudioMixer(config)
        except IOError as e:
          print "failed to open audio mixer:",e
        self.health = systemhealth.systemhealth()
        self.cpu = 1.
        self.mem = 1.
        self.disk = 1.
        self.battery = 1.
        self.runtime = 0
        self.timestamp = 0L

    def update(self):
        if self.mixer is not None:
          self.gains=self.mixer.gain()
##        statvfs.frsize * statvfs.f_blocks     # Size of filesystem in bytes
##        statvfs.frsize * statvfs.f_bfree      # Actual number of free bytes
        self.health.update()
        self.cpu = self.health.cpu
        self.mem = self.health.mem
        self.disk = self.health.disk
        self.battery = self.health.battery
        self.runtime = self.health.runtime

    def addToBundle(self, bundle):
        bundle.append(('/gain', self.gains))
        bundle.append(('/level', self.levels))
        bundle.append(('/timestamp', self.timestamp))
        bundle.append(('/state/cpu', self.health.cpu))
        bundle.append(('/state/memory', self.health.mem))
        bundle.append(('/state/disk', self.health.disk))
        bundle.append(('/state/battery', self.health.battery))
        bundle.append(('/state/runtime', self.health.runtime))

class PdCommunicator:
    def __init__(self, smi):
        self.smi=smi
        self.server=pdserver.pdserver(workingdir=smi.settings['/path/out'], patchdir=smi.settings['/path/in'])
        self.server.add(self._catchall, None)
        self.server.add(self._meter, "/meter")
        self.server.add(self._timestamp, "/timestamp")
        self.server.add(self._forward, "/process/")
        self.server.start()

    def _meter(self, msg, source):
        self.smi.state.levels=msg[2:]
    def _timestamp(self, msg, source):
        hi=int(msg[2])
        lo=int(msg[3])
        ts=((hi<<16)+lo)
        self.smi.state.timestamp=ts
    def _catchall(self, msg, source):
        self.smi.server.sendMsg(msg[0], msg[2:])
        print "got message: ", msg
        print "       from: ", source
    def _forward(self, msg, source):
        self.smi.server.sendMsg(msg[0], msg[2:])

    def stop(self):
        self.server.stop()

    def send(self, addr, data=None):
        self.server.send(addr, data)


class SMi:
    def __init__(self):
        self.settings=configuration.getSM()
        self.state=State(self.settings)
        self.mode=None

        self.oscprefix='/'+self.settings['/id']
        self.server = NetServer(port=int(self.settings['/port']), oscprefix=self.oscprefix, type=self.settings['/protocol'], service=self.settings['/service'])
        self.server.add(self.ping, '/ping')
        self.server.add(self.setGain, '/gain')

        self.server.add(self._mode, '/mode')

        self.server.add(self._process, '/process')
        self.server.add(self._record, '/record')
        self.server.add(self._stream, '/stream')
        self.server.add(self._streamProtocol, '/stream/protocol')
        self.server.add(self._streamProfile , '/stream/profile')
        self.server.add(self._streamChannels, '/stream/channels')
        self.server.add(self._recordTimestamp, '/record/timestamp')
        self.server.add(self._recordFilename, '/record/filename')
        self.server.add(self._streamURI, '/stream/uri')
        self.server.add(self.dumpInfo, '/dump') ## debugging
        self.mixer = self.state.mixer
        self.pd = PdCommunicator(self)

    def cleanup(self):
        self.pd.stop()
    def __del__(self):
        self.cleanup()

    def _ignoreMessage(self, msg, src):
        pass
    def _forwardMessageToPd(self, msg, src):
        self.pd.send(msg[0], msg[2:])

    def setGain(self, msg, src):
        if self.mixer is not None:
            gains=self.mixer.gain(msg[2:])

    def _reloadStream(self):
        if 'stream' == self.mode:
            self.pd.send('/control/load/stream', [self.settings['/stream/protocol'], self.settings['/stream/profile'], self.settings['/stream/channels']])
            return True
        return False
    def _reloadRecord(self):
        if 'record' == self.mode:
            self.pd.send('/control/load/record',[])
            return True
        return False
    def _reloadProcess(self):
        if 'process' != self.mode:
            return False
        inlets=0
        outlets=0
        try:
            pd = pdfile.pdfile(os.path.join(self.settings['/path/in'], 'MAIN.pd'))
            inlets=pd.getInlets()[0]
            outlets=pd.getOutlets()[0]
        except IOError:
            pass
        self.pd.send('/control/load/process',[inlets, outlets, 'MAIN'])
        return True

    def _mode(self, msg, src):
        self.mode=str(msg[2]).lower()
        if self._reloadStream() or self._reloadRecord() or self._reloadProcess():
            pass

    def _streamProtocol(self, msg, src):
        protocol=str(msg[2]).lower()
        if self.settings['/stream/protocol'] == protocol:
            return
        self.settings['/stream/protocol']=protocol
        self._reloadStream()

    def _streamProfile(self, msg, src):
        profile=str(msg[2]).upper()
        if self.settings['/stream/profile'] == profile:
            return
        self.settings['/stream/profile' ]=profile
        self._reloadStream()
    def _streamChannels(self, msg, src):
        channels=int(msg[2])
        if channels == self.settings['/stream/channels' ]:
            return
        self.settings['/stream/channels' ] = channels
        self._reloadStream()

    def _streamURI(self, msg, src):
        o=urlparse(msg[2])
        port=o.port
        host=o.hostname
        self.settings['/stream/destination']=[host, port]

    def _stream(self, msg, src):
        state=msg[2]
        if state is not None and int(state) > 0:
            self.startStream()
        else:
            self.stopStream()
    def streamStarted(self, uri):
        self.server.sendMsg('/stream/uri', uri)
    def startStream(self):
        self.pd.send("/stream/start", self.settings['/stream/destination'])
    def stopStream(self):
        self.pd.send("/stream/stop")

    def _recordFilename(self, msg, src):
        self.settings['/stream/filename' ] = msg[2]
    def _recordTimestamp(self, msg, src):
        self.settings['/stream/timestamp' ] = int(msg[2])

    def _record(self, msg, src):
        state=msg[2]
        filename=self.settings['/record/filename']
        timestamp=int(self.settings['/record/timestamp'])
        TShi=(timestamp>>16)&0xFFFF
        TSlo=(timestamp>> 0)&0xFFFF
        if state is not None and int(state) > 0:
            self.pd.send("/record/start", [filename, TSlo, TShi])
        else:
            self.pd.send("/record/stop")
    def _process(self, msg, src):
        state=msg[2]
        if state is not None and int(state) > 0:
            self.pd.send("/process/start")
        else:
            self.pd.send("/process/stop")


    def ping(self, msg, src):
        self.state.update()
        bundle = Bundle(oscprefix=self.oscprefix)

        self.state.addToBundle(bundle)
        for a in ['/user', '/path/in', '/path/out' ]:
            bundle.append((a, [self.settings[a]]))
        self.server.sendBundle(bundle)

    def dumpInfo(self, msg, src):
        print "setting: ", self.settings
        print "state  : ", self.state.__dict__
        if self.streamer is not None:
            self.streamer.dumpInfo()

if __name__ == '__main__':
    print "SMi..."
    import gobject
    sm = SMi()
    import time

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass


