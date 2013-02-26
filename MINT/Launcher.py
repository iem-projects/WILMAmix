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

    def __init__(self, prog, args=[], cwd=None, doneCb=None):
        Thread.__init__(self)
        self.prog=[prog]+args
        self.cwd=cwd
        self.process=None
        self._starting=False
        self.out = None
        self.err = None
        self.doneCb = doneCb

    def run(self):
        out=None
        #out=subprocess.PIPE
        self.process = subprocess.Popen(self.prog, cwd=self.cwd, stdout=out, stderr=out)
        self._starting = False
        if out is subprocess.PIPE:
            ## attaching to the stdout/stderr will make the process defunct
            ## between it's natural death and a shutdown()
            self.out, self.err = self.process.communicate()
        else:
            self.process.wait()
        self.process=None
        if self.doneCb is not None:
            self.doneCb()

    def launch(self):
        if self.process is not None:
            self.shutdown()
        self._starting=True
        self.start()
        while self._starting and self.is_alive():
            pass

    def shutdown(self, timeout=0):
        if self.process is None:
            return
        if True or self.process.poll():
            #print "shutting down process", self.process.pid
            self.join(timeout)
            if self.is_alive():
                try:
                    self.process.terminate()
                except OSError:
                    print "failed to terminate"
                self.join()
                #pid=self.process.pid
                #os.kill(self.process.pid, signal.SIGKILL)
        self.process = None

    def wait(self, timeout=None):
        if self.is_alive():
            self.join(timeout)

    def isRunning(self):
        if self.process is None:
            return False
        return 0 is not self.process.poll()

######################################################################

if __name__ == '__main__':
    p = Launcher('pd', [
        '-nogui',
        '-open', 'pd/test.pd',
        '-send', '_config foo bar',
        ])
    print "launcher", p
    p.launch()
    #time.sleep( 1 )
    import gobject

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass

    if p is not None:
        print "\nrunning: ", p.isRunning()
        print "<ERR: ",p.err
        print "<OUT: ",p.out
        time.sleep(1)
        p.shutdown(1)
        time.sleep(1)
        print ">ERR: ",p.err
        print ">OUT: ",p.out

    print "\nbye"
