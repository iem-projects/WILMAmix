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

import os
import socket
import tempfile
import time
import gobject
import gstutils
from .. import Launcher

class RTSPserverX:
    def __init__(self, profile='L16', channels=2, source='audiotestsrc',
                 startCallback=None):
        self.startCb=startCallback
        binary= os.path.join(os.path.dirname(os.path.abspath(__file__)),'RTSPserverX')
        profile = profile.replace(' ', '')
        payelement='rtp'+profile+'pay'
        if not gstutils.checkElement(source):
            raise Exception("invalid source: '"+source+"'")
        if not gstutils.checkElement(payelement):
            raise Exception("invalid payloader: '"+payelement+"'")

        pipeline=source + " ! audioconvert ! audio/x-raw-int/channels="+str(channels)+" ! "+payelement+" name=pay0"
        mountpoint='/'+profile
        self.urifile=tempfile.NamedTemporaryFile()
        self.server = Launcher(binary, [pipeline, mountpoint, self.urifile.name])
        self.uri = None
        gobject.io_add_watch(self.urifile.file, gobject.IO_IN, self._callback)

    def _callback(self, f, bar):
        #print "callback0", self
        #print "callback1", f
        #print "callback2", bar
        #print "something happened to ", self.urifile.name

        if f is self.urifile.file:
            data=self.urifile.read()
            if len(data)>0:
                ip=socket.gethostbyname(socket.gethostname())
                self.uri=data.replace('@HOSTNAME@', ip)

                if self.startCb is not None:
                    self.startCb(self.uri)
                print "URI: ", self.uri
                return False

        return True

    def getURI(self):
        return self.uri

    def start(self):
        print "start", self
        self.server.launch()
        #while(self.server.isRunning() and self.uri is None):
        #    time.sleep(0.1)

    def stop(self):
        #print "stop", self
        # ouch, how to do that?
        print "server stopping"
        self.server.shutdown()
        self.uri=None
        self.urifile=None

    def dumpInfo(self):
        print "server: ", self.server
        print "server running", self.server.isRunning()
        print "URI   : ", self.uri


######################################################################

if __name__ == '__main__':
    s=RTSPserverX()
    s.start()
    print "URI: ", s.getURI()
    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    s.stop()
    print "bye"
