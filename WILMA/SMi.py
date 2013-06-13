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

from net import server as NetServer
from urlparse import urlparse

from net.osc import Bundle

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
        self.sync_external = False
        self.sync_internal = False

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
        self.sync_external = self.health.sync_external
        self.sync_internal = self.health.sync_internal

    def addToBundle(self, bundle):
        bundle.append(('/gain', self.gains))
        bundle.append(('/level', self.levels))
        bundle.append(('/timestamp', self.timestamp))
        bundle.append(('/state/cpu', self.health.cpu))
        bundle.append(('/state/memory', self.health.mem))
        bundle.append(('/state/disk', self.health.disk))
        bundle.append(('/state/battery', self.health.battery))
        bundle.append(('/state/runtime', self.health.runtime))
        bundle.append(('/state/sync/internal', self.health.sync_internal))
        bundle.append(('/state/sync/external', self.health.sync_external))

class PdCommunicator:
    def __init__(self, smi):
        self.smi=smi
        self.server=pdserver.pdserver(mainpatch='_WILMAsm.pd',
                                      workingdir=smi.settings['/path/out'],
                                      patchdir=smi.settings['/path/in'])
        self.server.add(self._catchall, None)
        self.server.add(self._meter, "/meter")
        self.server.add(self._timestamp, "/timestamp")
        self.server.add(self._forward, "/process/")
        self.server.start()

    def _meter(self, addr, typetags, data, source):
        self.smi.state.levels=data
    def _timestamp(self, addr, typetags, data, source):
        hi=int(data[0])
        lo=int(data[1])
        ts=((hi<<16)+lo)
        self.smi.state.timestamp=ts
    def _catchall(self, addr, typetags, data, source):
        self.smi.server.sendMsg(addr[0], data)
        print "got message: ", (addr, typetags, data, source)
    def _forward(self, addr, typetags, data, source):
        self.smi.server.sendMsg(addr[1], data)

    def stop(self):
        self.server.stop()

    def send(self, addr, data=None):
        self.server.send(addr, data)
    def ping(self):
        self.server.send('/ping', [])


class SMi:
    def __init__(self):
        self.settings=configuration.getSM()
        self.state=State(self.settings)
        self.mode=None

        self.oscprefix='/'+self.settings['/id']
        self.server = NetServer(
            port=int(self.settings['/port']), transport=self.settings['/protocol'],
            service=self.settings['/service'],
            oscprefix=self.oscprefix,
            verbose=False)
        self.server.add(self.ping, '/ping')
        self.server.add(self._gain, '/gain')

        self.server.add(self._mode, '/mode')

        self.server.add(self._process, '/process')
        self.server.add(self._processProxy, '/process/')

        self.server.add(self._streamTransport, '/stream/transport/protocol')
        self.server.add(self._streamTransportPort, '/stream/transport/port')
        self.server.add(self._streamProtocol, '/stream/protocol')
        self.server.add(self._streamProfile , '/stream/profile')
        self.server.add(self._streamChannels, '/stream/channels')
        self.server.add(self._streamURI, '/stream/uri')

        self.server.add(self._recordTimestamp, '/record/timestamp')
        self.server.add(self._recordFilename, '/record/filename')

        self.server.add(self.dumpInfo, '/dump') ## debugging
        self.server.add(self._catchall, None) ## debugging

        self.mixer = self.state.mixer
        self.pd = PdCommunicator(self)

    def cleanup(self):
        self.pd.stop()
    def __del__(self):
        self.cleanup()

    def _gain(self, addr, typetags, data, source):
        if self.mixer is not None:
            gains=self.mixer.gain(data)

    def _reloadStream(self):
        if 'stream' == self.mode:
            self.pd.send('/control/load/stream', [self.settings['/stream/transport/protocol'],
                                                  self.settings['/stream/transport/port'],
                                                  self.settings['/stream/protocol'],
                                                  self.settings['/stream/profile'],
                                                  self.settings['/stream/channels']
                                                  ])
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
            inlets=pd.getInlets()[1]
            outlets=pd.getOutlets()[1]
        except IOError:
            pass
        self.pd.send('/control/load/process',[inlets, outlets, 'MAIN'])
        return True

    def _mode(self, addr, typetags, data, source):
        self.mode=str(data[0]).lower()
        if self._reloadStream() or self._reloadRecord() or self._reloadProcess():
            pass
    def _hasSettingChanged(self, key, value):
        if not key in self.settings:
            self.settings[key] = value
            return True
        if self.settings[key] == value:
            return False
        self.settings[key] = value
        return True

    def _streamTransport(self, addr, typetags, data, source):
        transport=str(data[0]).lower()
        if self._hasSettingChanged('/stream/transport/protocol', transport):
            self._reloadStream()
    def _streamTransportPort(self, addr, typetags, data, src):
        port=data[0]
        if self._hasSettingChanged('/stream/transport/port', port):
            self._reloadStream()

    def _streamProtocol(self, addr, typetags, data, src):
        protocol=str(data[0]).lower()
        if self._hasSettingChanged('/stream/protocol', protocol):
            self._reloadStream()

    def _streamProfile(self, addr, typetags, data, src):
        profile=str(data[0]).upper()
        if self._hasSettingChanged('/stream/profile', profile):
            self._reloadStream()

    def _streamChannels(self, addr, typetags, data, src):
        channels=int(data[0])
        if self._hasSettingChanged('/stream/channels', channels):
            self._reloadStream()

    def _streamURI(self, addr, typetags, data, src):
        uri=data[0]
        o=urlparse(uri)
        protocol='udp'
        ## rtp:// = RTP
        ## rtp.udp:// = RTP over UDP (the default)
        ## rtp.tcp:// = RTP over TCP/IP (non-standard)
        schemelist=o.scheme.lower().split('.')
        scheme=schemelist[0]
        if scheme == 'rtp':
            transport='udp'
        else:
            print "ERROR: unsupported scheme in", uri
        if len(schemelist)>1:
            transport=schemelist[1]
        if not (('udp' == transport) or ('tcp' == transport)):
            print "ERROR: unsupported transport protocol in", uri
            transport='udp'
        restart=False
        if self._hasSettingChanged('/stream/transport/protocol', transport):
            print "ERROR: transport protocol changed to", transport
            restart=True

        if self._hasSettingChanged('/stream/protocol', scheme):
            print "ERROR: stream protocol changed to", scheme
            restart=True

        host=o.hostname
        if host == '':
            host=src[0]
        port=o.port
        self.settings['/stream/destination']=[host, port]

        bundle = Bundle()
        if restart:
            bundle.append(('/stream/transport/protocol', self.settings['/stream/transport/protocol']))
            bundle.append(('/stream/transport/port', self.settings['/stream/transport/port']))
            bundle.append(('/stream/protocol', self.settings['/stream/protocol']))
            bundle.append(('/stream/profile', self.settings['/stream/profile']))
            #self._reloadStream()

        bundle.append(('/stream/destination', self.settings['/stream/destination']))
        self.pd.send(bundle)

    def streamStarted(self, uri):
        self.server.sendMsg('/stream/uri', uri)
    def startStream(self):
        self.pd.send("/stream/destination", self.settings['/stream/destination'])
        self.pd.send("/stream/start", self.settings['/stream/destination'])
    def stopStream(self):
        self.pd.send("/stream/stop")

    def _recordFilename(self, addr, typetags, data, src):
        self.settings['/record/filename' ] = data[0]
    def _recordTimestamp(self, addr, typetags, data, src):
        self.settings['/record/timestamp' ] = int(data[0])

    def _process(self, addr, typetags, data, src):
        print "++++++++++++++++++++++++ _process +++++++++++++++++++++"
        state=data[0]

        ## hacks for specific modes: RECORD
        filename=self.settings['/record/filename']
        timestamp=int(self.settings['/record/timestamp'])
        TShi=(timestamp>>16)&0xFFFF
        TSlo=(timestamp>> 0)&0xFFFF
        self.pd.send('/record/filename', [filename])
        self.pd.send('/record/timestamp', [TSlo, TShi])
        ## hacks for specific modes: STREAM
        self.pd.send("/stream/destination", self.settings['/stream/destination'])

        ## ready, steady, GO!
        if state is not None and int(state) > 0:
            self.pd.send("/start")
        else:
            self.pd.send("/stop")

    def _processProxy(self, addr, typetags, data, src):
        self.pd.send('/process'+addr[0], data)

    def ping(self, addr, typetags, data, src):
        self.state.update()
        bundle = Bundle(oscprefix=self.oscprefix)

        self.state.addToBundle(bundle)
        for a in ['/user', '/path/in', '/path/out' ]:
            bundle.append((a, [self.settings[a]]))
        self.server.sendBundle(bundle)
        self.pd.ping()

    def dumpInfo(self, addr, typetags, data, src):
        print "setting: ", self.settings
        print "state  : ", self.state.__dict__
        if self.streamer is not None:
            self.streamer.dumpInfo()
    def _catchall(self, addr, typetags, data, src):
        print "SMi:catchall", (self, addr, typetags, data, src)
        print "OSC-callbacks", self.server.addressManager.__dict__

if __name__ == '__main__':
    print "SMi..."
    import gobject
    sm = SMi()
    import time

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass


