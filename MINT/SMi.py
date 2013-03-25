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
from net.osc import Bundle

from streaming import Server as StreamingServer
from audio import AudioMixer
import systemhealth
import pdserver
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
        bundle.append(('/state/cpu', self.health.cpu))
        bundle.append(('/state/mem', self.health.mem))
        bundle.append(('/state/disk', self.health.disk))
        bundle.append(('/state/battery', self.health.battery))
        bundle.append(('/state/runtime', self.health.runtime))

class PdCommunicator:
    def __init__(self, smi):
        self.smi=smi
        self.server=pdserver.pdserver(workingdir=smi.settings['/path/out'], patchdir=smi.settings['/path/in'])
        self.server.add(self._catchall, None)
        self.server.add(self._meter, "/meter")
        self.server.start()

    def _meter(self, msg, source):
        self.smi.state.levels=msg[2:]
    def _catchall(self, msg, source):
        self.smi.server.sendMsg(msg[0], msg[2:])
        print "got message: ", msg
        print "       from: ", source

    def stop(self):
        self.server.stop()

    def send(self, addr, data=None):
        self.server.send(addr, data)


class SMi:
    def __init__(self):
        constants=configuration.getSM()
        self.settings=None
        self._initSettings()
        self.state=State(constants)
        self.oscprefix='/'+constants['/id']
        self.server = NetServer(port=constants['/port'], oscprefix=self.oscprefix, type=constants['/protocol'], service=constants['/service'])
        self.server.add(self.ping, '/ping')
        self.server.add(self.setGain, '/gain')

        self.server.add(self.controlStream, '/stream')
        self.server.add(self.controlStreamType, '/stream/settings/type')
        self.server.add(self.controlStreamProfile, '/stream/settings/profile')
        self.server.add(self.controlStreamChannels, '/stream/settings/channels')
        self.server.add(self.controlStreamDestination, '/stream/settings/destination')
        self.server.add(self.dumpInfo, '/dump') ## debugging
        self.mixer = self.state.mixer
        self.pd = PdCommunicator(self)

    def cleanup(self):
        self.pd.stop()
    def __del__(self):
        self.cleanup()

    def _initSettings(self):
        d=dict()
        try:
            import getpass
            d['/user']=getpass.getuser()
        except ImportError:
            d['/user']='unknown'

        d['/stream/type'    ]='rtp' # const
        d['/stream/channels']=4 # const
        d['/stream/profile' ]='L16' # const for now

        d['/path/in'        ]='/tmp/MINT/in'
        d['/path/out'       ]='/tmp/MINT/out'

        self.settings=d


    def setGain(self, msg, src):
        if self.mixer is not None:
            gains=self.mixer.gain(msg[2:])

    def controlStreamType(self, msg, src):
        self.settings['/stream/type']=msg[2]

    def controlStreamProfile(self, msg, src):
        self.settings['/stream/profile']=msg[2]

    def controlStreamChannels(self, msg, src):
        self.settings['/stream/channels']=msg[2]
    def controlStreamDestination(self, msg, src):
        self.settings['/stream/destination']=msg[2:4]

    def controlStream(self, msg, src):
        state=msg[2]
        #print "controlStream", msg
        if state is not None and int(state) > 0:
            self.startStream()
        else:
            self.stopStream()

    def streamStarted(self, uri):
        self.server.sendMsg('/stream/uri', uri)


    def startStream(self):
        self.pd.send("/control/load/stream")
        self.pd.send("/stream/start", ["localhost", 8888])

    def stopStream(self):
        self.pd.send("/stream/stop")

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


