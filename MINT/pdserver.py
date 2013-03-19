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

class _pdprocess:
    def __init__(self, port, cwd=None):
        if cwd is None:
            cwd=tempfile.mkdtemp()
        self.cwd=cwd

        self.args=[]
        self.args+=['-path', ".:/usr/lib/pd/extra/iemnet:/usr/lib/pd/extra/osc:~/src/cvs/MINT/pd/MINT/iemrtp"]
        ## NOTE: "sent" messages are executed _after_ loadbang
        self.args+=['-send', "_MINT_pwd "+cwd]
        self.args+=['-send', "_MINT_port "+str(port)]
        self.args+=['-path', "/Net/iem/Benutzer/zmoelnig/src/cvs/MINT/MINTmix/MINT/pd"]
        #self.args+=['-nogui']
        self.args+=['-open', "_MINT.pd"]
        self.shouldRun=False
        self.pd=None

    def _launch(self):
        self.pd = launcher("pd",
                           self.args,
                           cwd=self.cwd,
                           doneCb=self._doneCb)
        self.pd.launch()
        self.shouldRun=True

    def _doneCb(self):
        print "Pd exited", self.shouldRun
        if self.shouldRun: ## ouch: crashed, so restart
            self._launch()

    def start(self):
        if self.pd is None: ## not yet running
            self._launch()
    def stop(self):
        self.shouldRun=False
        self.pd.shutdown()

class pdserver:
    def __init__(self):
        self.server = NetServer(type='udp')
        self.pd=_pdprocess(self.server.getPort())
    def __del__(self):
        self.pd.stop()

    def start(self):
        self.pd.start()
    def stop(self):
        self.pd.stop()

    def add(self, callback, oscAddress):
        self.server.add(callback, oscAddress)
    def send(self, addr, data=None):
        if type(addr) is str: # it's an addr/data pair
            self.server.sendMsg(addr, data)
        elif data is None:    # it's a bundle
            self.server.sendBundle(addr)
        else:
            raise Exception("usage: send(addr, data) OR send(bundle)")

if __name__ == '__main__':
    print "Pd-Server..."
    import gobject
    gobject.threads_init()

    pd = pdserver()
    pd.start()

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pd.stop()
        pass


