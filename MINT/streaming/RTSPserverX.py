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

from .. import Launcher
import os
import socket

import gstutils


class RTSPserverX:
    def __init__(self, profile='L16', channels=2, source='audiotestsrc',
                 startCallback=None):
        self.startCb=startCallback
        binary= os.path.join(os.path.dirname(os.path.abspath(__file__)),'RTSPserverX')
        profile = profile.replace(' ', '')
        depayelement='rtp'+profile+'pay'
        if not ( gstutils.checkElement(source) and gstutils.checkElement(depayelement) ):
            print ouch
            return

        pipeline=source + " ! audioconvert ! audio/x-raw-int/channels="+str(channels)+" ! "+depayelement+" name=pay0"
        mountpoint='/'+profile
        self.server = Launcher(binary, [pipeline, mountpoint])
        self.uri = None

    def getURI(self):
        return self.uri

    def start(self):
        print "start", self
        self.server.launch()
        stdout=None
        while self.server.isRunning() and stdout is None:
            stdout = self.server.process.stdout.readline();
        ip=socket.gethostbyname(socket.gethostname())
        if stdout is not None:
            self.uri=stdout.replace('@HOSTNAME@', ip)

    def stop(self):
        #print "stop", self
        # ouch, how to do that?
        print "server stopping"
        self.server.shutdown()
        self.uri=None

    def dumpInfo(self):
        print "server: ", self.server
        print "server running", self.server.isRunning()
        print "URI   : ", self.uri


######################################################################

if __name__ == '__main__':
    import time, gobject
    s=RTSPserverX()
    s.start()
    print "URI: ", s.getURI()
    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    s.stop()
    print "bye"
