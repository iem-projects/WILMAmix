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

import gst.rtspserver
import gstutils
import glib, gobject
import socket

class RTSPserver:
    def __init__(self, profile='L16', channels=2, source='audiotestsrc'):
        profile = profile.replace(' ', '')
        depayelement='rtp'+profile+'pay'
        if not ( gstutils.checkElement(source) and gstutils.checkElement(depayelement) ):
            print ouch
            return
        
        pipeline=source + " ! audioconvert ! audio/x-raw-int/channels="+channels+" ! "+depayelement+" name=pay0"
        self.mountpoint='/'+profile

        self.server = gst.rtspserver.Server()
        #server.set_service('7777')                # port
        mapping =self.server.get_media_mapping()
        self.factory =gst.rtspserver.MediaFactory()
        self.factory.set_launch(pipeline)
        #print "pipeline: ", self.factory.get_launch()
        mapping.add_factory(self.mountpoint, self.factory)
        self.timeoutID=0L
        self.serverID=0L
  
        pass

    def getURI(self):
        if self.server is None:
            return None
        if self.serverID <= 0:
            return None
        port=int(self.server.get_service())
        ip=socket.gethostbyname(socket.gethostname())
        uri= 'rtsp://'+ip+':'+str(port)+self.mountpoint
        #print "URI: ", uri
        return uri

    def start(self):
        #print "start", self
        self.timeoutID=gobject.timeout_add_seconds(2, self._timeout)
        self.serverID=self.server.attach()
        #print "started: ", self.serverID
        #self.getURI()

    def stop(self):
        #print "stop", self
        # ouch, how to do that?
        print "server stopping"
        glib.source_remove(self.serverID)
        #glib.source_remove(self.timeoutID)
        self.serverID=0L
        self.timeoutID=0L

    def _timeout(self):
        """ timeout gets called periodically and should clean up all terminating sessions.
        it does NOT remove connected servers"""
        pool = self.server.get_session_pool()
        pool.cleanup()
        return True



######################################################################

if __name__ == '__main__':
    import time, gobject
    s=RTSPserver()
    s.start()
    print "URI: ", s.getURI()
    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    s.stop()
    print "bye"
