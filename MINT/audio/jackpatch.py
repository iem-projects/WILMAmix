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



import jack
import os
import re

_counter=0.1

def _defer(fun):
    gobject.timeout_add(0, fun)

### pattern substitution
##>>> a
##'SuperCollider:out_(.*)'
##>>> r=re.compile(a)
##>>> b
##'system:playback_\\1'
##>>> re.sub(r, b, "SuperCollider:out_abc")
##'system:playback_abc'



class patcher:
    def __init__(self, deferFunction=None):
        self.running=False
        self.rules=[]
        global _counter
        ID="jackpatch["+str(os.getpid())+"]_"+str(_counter)
        _counter+=1
        self.jack = jack.Client(ID, processing=False)
        self.jack.set_port_connect_callback(self._connection)
        self.jack.activate()
        if deferFunction is None:
            self.defer=_defer
        else:
            self.defer=deferFunction
        self.already = False

    def _connection(self, a, b, state):
        print "callback: ",self.running
        if not self.running:
            return
        print "callbackAgain: ",self.already
        if not self.already:
            self.already=False
            self.defer(self._applyRules)
        if True:
            if state:
                print "connection "+str(a)+"->"+str(b)
            else:
                print "disconnection "+str(a)+"->"+str(b)

    def start(self):
        self.running=True

    def stop(self):
        self.running=False


    def _applyRules(self):
        print "applying:", self.already
        self.already=False
        for r in self.rules:
            r[0](*r[1])
        return False

    def _doconnect(self, source, target):
        print "Connect: "+source+"->"+target
        r=re.compile(source)
        for s in self.jack.get_ports(source,'',jack.IsOutput):
            for t in self.jack.get_ports(re.sub(r, target, s), '', jack.IsInput): ## all matching targetports
                self.jack.connect(s,t)
    def _dodisconnect(self, source, target):
        print "Disconnect: "+source+"->"+target
        r=re.compile(source)
        for s in self.jack.get_ports(source,'',jack.IsOutput):
            for t in self.jack.get_ports(re.sub(r, target, s), '', jack.IsInput): ## all matching targetports
                self.jack.disconnect(s,t)
    def _doduplicate(self, reference, target):
        print "Duplicate: "+reference+"->"+target
        r=re.compile(reference)
        for p in self.jack.get_ports(reference):
            flags=self.jack.get_port_flags(p) & (jack.IsInput | jack.IsOutput)
            for t in self.jack.get_ports(re.sub(r, target, p), '', flags): ## all matching dupports in the same direction
                if flags & jack.IsOutput:
                    for conn in self.jack.get_connections(p): self.jack.connect(t, conn)
                elif flags & jack.IsInput:
                    for conn in self.jack.get_connections(p): self.jack.connect(conn, t)

    def connect(self, source, target):
        """connects source to target"""
        args=[source, target]
        self._doconnect(*args)
        self.rules+=[[self._doconnect, args]]

    def disconnect(self, source, target):
        """disconnects source from target"""
        args=[source, target]
        self._dodisconnect(*args)
        self.rules+=[[self._dodisconnect, args]]

    def duplicate(self, reference, target):
        """make sure that whatever is connected to reference is also connected to target"""
        args=[reference, target]
        self._doduplicate(*args)
        self.rules+=[[self._doduplicate, args]]

    def clear(self):
        """clear all rules"""
        self.rules=[]



######################################################################

if __name__ == '__main__':
    p = patcher()
    p.connect(r"pure_data_0:output(.*)", r"pure_data_.*:input\1")
    p.disconnect(r"pure_data_0:output0", r"pure_data_.*:input0")
    #p.duplicate("pure_data_0:input0", "system:playback_1")
    p.start()
    #po=patcher()

    try:
        import gobject
        loop=gobject.MainLoop()
        gobject.threads_init()
        loop.run()
    except KeyboardInterrupt:
        pass
    p.stop()

