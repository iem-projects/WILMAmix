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

import logging as logging_
logging = logging_.getLogger('WILMA.launcher')
import subprocess
import os, signal
import threading
import time

class launcher(threading.Thread):
    """ Launches an external program in a thread """

    def __init__(self, prog, args=[], env={}, cwd=None, doneCb=None):
        threading.Thread.__init__(self)
        self.prog=[prog]+args
        self.env=env
        self.cwd=cwd
        self.process=None
        self._starting=False
        self.out = None
        self.err = None
        self.__doneCb = doneCb

    def run(self):
        out=None
        env=os.environ.copy()
        for k in self.env: env[k]=self.env[k]
        #out=subprocess.PIPE
        self.process = subprocess.Popen(self.prog, env=env, cwd=self.cwd, stdout=out, stderr=out)
        self._starting = False
        try:
            if out is subprocess.PIPE:
                ## attaching to the stdout/stderr will make the process defunct
                ## between it's natural death and a shutdown()
                self.out, self.err = self.process.communicate()
            else:
                self.process.wait()
        except KeyboardInterrupt:
            logging.exception("............................................. KEYBOARD INTERRUPT ......")
        self.process=None
        if self.__doneCb is not None:
            self.__doneCb()

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
            #logging.info("shutting down process %d" % self.process.pid)
            self.join(timeout)
            if self.is_alive():
                try:
                    self.process.terminate()
                except OSError:
                    logging.exception("failed to terminate")
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
    p = launcher('pd', [
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
