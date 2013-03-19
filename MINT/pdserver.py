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
    def __init__(self, port, cwd=None, cpd=None, runningCb=None):
        self.runningCb=runningCb
        if cwd is None: ## working directory
            cwd=tempfile.mkdtemp()
        self.cwd=cwd
        self.args=[]
        self.args+=['-path', ".:/usr/lib/pd/extra/iemnet:/usr/lib/pd/extra/osc:~/src/cvs/MINT/pd/MINT/iemrtp"]
        if cpd is not None: ## patch directory
            self.args+=['-path', cpd]
        self.args+=['-path', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pd')]

        ## NOTE: "sent" messages are executed _after_ loadbang
        self.args+=['-send', "_MINT_pwd "+cwd]
        self.args+=['-send', "_MINT_port "+str(port)]
        self.args+=['-open', "_MINT.pd"]
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
    def __init__(self, workingdir=None, patchdir=None):
        self.server = NetServer(type='udp')
        self.pd=_pdprocess(self.server.getPort(), cwd=workingdir, cpd=patchdir, runningCb=self._runningCb)
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
            self.stateCb(msg, None)

    def add(self, callback, oscAddress):
        if oscAddress is None:
            self.stateCb=callback
        elif oscAddress is '/state':
            self.stateCb=callback
        self.server.add(callback, oscAddress)
    def send(self, addr, data=None):
        if type(addr) is str: # it's an addr/data pair
            self.server.sendMsg(addr, data)
        elif data is None:    # it's a bundle
            self.server.sendBundle(addr)
        else:
            raise Exception("usage: send(addr, data) OR send(bundle)")

if __name__ == '__main__':
    class PingPong:
        def __init__(self, pd):
            self.pd=pd
        def callback(self, message, source):
            print "received: ",message
            print "  source: ", source
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


