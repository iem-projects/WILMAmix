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

import subprocess
import os, signal

from threading import Thread

import time

class Launcher(Thread):
    """ Launches an external program in a thread """

    def __init__(self, prog, args=[], cwd=None):
        Thread.__init__(self)
        self.prog=[prog]+args
        self.cwd=cwd
        self.process=None
        self._starting=False

    def run(self):
        self.process = subprocess.Popen(self.prog, cwd=self.cwd)
        self._starting = False
        #self.out, self.err = self.process.communicate()
        self.process.wait()

    def launch(self):
        if self.process is not None:
            self.shutdown()
        self._starting=True
        self.start()
        while self._starting and self.is_alive():
            pass
        

    def shutdown(self, timeout=0):
        print "stopping ", self.process.pic
        if (self.process is not None) and self.process.poll():
            self.process.join(timeout)
            if self.is_alive():
                self.process.terminate()
                self.join()
                #pid=self.process.pid
                #os.kill(self.process.pid, signal.SIGKILL)
        self.process = None

######################################################################

if __name__ == '__main__':
    p = Launcher('pd', [
        '-open', 'MINT/pd/test.pd',
        '-send', '_config foo bar',
        ])
    print "launcher", p
    p.launch()
    #time.sleep( 1 )
    print "starting"
    import gobject

    #try:
    if True:
        gobject.MainLoop().run()
    #except KeyboardInterrupt:
    #    pass

    print p
    if p is not None:
        #p.shutdown()
        #del p
        pass
    print "bye"
