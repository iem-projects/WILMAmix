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

###############################
# start a UDP-server and the Pd-workinghorse
# Pd communicates with use through the UDP-server

from net import server as NetServer
from net.osc import Bundle


from launcher import launcher

import os
import tempfile

def _createDirIfNeeded(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

class _pdprocess:
    def __init__(self, port, patch=None, cwd=None, cpd=None, runningCb=None):
        self.runningCb=runningCb
        if cwd is None: ## working directory
            cwd=tempfile.mkdtemp()
        self.cwd=cwd
        self.args=[]
        self.args+=['-path', "."]
        #self.args+=['-path', ".:/usr/lib/pd/extra/iemnet:/usr/lib/pd/extra/osc:~/src/cvs/WILMA/pd/iemrtp"]
        if cpd is not None: ## patch directory
            self.args+=['-path', cpd]
        self.args+=['-path', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pd')]
        self.args+=['-path', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pd', 'lib')]

        ## NOTE: "sent" messages are executed _after_ loadbang
        self.args+=['-send', "_WILMA_pwd "+cwd]
        self.args+=['-send', "_WILMA_port "+str(port)]
        if patch is not None:
            self.args+=['-open', patch]
        self.shouldRun=False
        self.pd=None

    def _launch(self):
        _createDirIfNeeded(self.cwd)
        self.pd = launcher("pd",
                           self.args,
                           cwd=self.cwd,
                           doneCb=self._doneCb)
        self.pd.launch()
        if self.runningCb is not None: self.runningCb(True)
        self.shouldRun=True

    def _doneCb(self):
        print "Pd exited", self.shouldRun
        if self.runningCb is not None: self.runningCb(False)
        if self.shouldRun: ## ouch: crashed, so restart
            self._launch()

    def start(self):
        if self.pd is None: ## not yet running
            self._launch()
    def stop(self):
        self.shouldRun=False
        if self.pd is not None: ## not yet running
            self.pd.shutdown()
        self.pd=None

class pdserver:
    def __init__(self, mainpatch='MAIN.pd', workingdir=None, patchdir=None):
        self.server = NetServer(transport='udp')
        self.pd=_pdprocess(self.server.getPort(), patch=mainpatch, cwd=workingdir, cpd=patchdir, runningCb=self._runningCb)
        self.stateCb = None
    def __del__(self):
        self.pd.stop()

    def start(self):
        self.pd.start()
    def stop(self):
        self.pd.stop()

    def _runningCb(self, state):
        if self.stateCb is not None:
            msg=['/state']
            if state:
                msg+=[',T', True]
            else:
                msg+=[',F', False]
            self.stateCb([msg[0], msg[0]], msg[1], [msg[2]], None)

    def add(self, callback, oscAddress):
        if oscAddress is None:
            self.stateCb=callback
        elif oscAddress is '/state':
            self.stateCb=callback
        self.server.add(callback, oscAddress)
    def send(self, addr, data=None):
        self.server.send(addr, data)

if __name__ == '__main__':
    class PingPong:
        def __init__(self, pd):
            self.pd=pd
        def callback(self, addr, typetag, data, source):
            print "received: ",(addr, typetag, data, source)
            self.pd.send("/pong")
    print "Pd-Server..."
    import gobject
    gobject.threads_init()

    pd = pdserver()
    reply=PingPong(pd)
    pd.add(reply.callback, "/meter")
    pd.start()

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pd.stop()
        pass


