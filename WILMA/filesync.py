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


## syncs directories between two hosts using rsync


## sketch
# query output directory from client
# run rsync

import pexpect
from threading import Thread

class _FileSyncer(Thread):
    def __init__(self, prog,
                 passphrase=None,   ## in case we need authentication
                 doneCallback=None, ## get's called once files have been transmitted
                 ):
        Thread.__init__(self)
        #self.setDaemon(True)

        self.expects = [
            "Enter passphrase for key '.*':",                          # ssh-key (try all passphrases)
            "[Pp]assword:",                                            # ordinary password (try all passphrases)
            "Are you sure you want to continue connecting (yes/no)\?", # unknown host
            pexpect.EOF                                                # shutdown
            ]
        self.passphrases=['yes']*3
        if passphrase is None:
            passphrase=['']
        passlist=[]
        try:
            passlist+=passphrase
        except TypeError:
            passlist+=[passphrase]
        self.passphrases[0]=passlist[:]
        self.passphrases[1]=passlist[:]
        self.passlist=passlist

        self.prog=prog[0]
        self.progargs=prog[1:]
        self.doneCb=doneCallback
        self.p=None

    def run(self):
        self.p=pexpect.spawn(self.prog, self.progargs)
        while self.p.isalive():
            i=self.p.expect(self.expects)
            print "expectation met:",i
            if i is 3: # EOF
                break
            elif i is 2: # yes/no
                self.p.sendline('yes')
            elif (i is 0) or (i is 1): ## some password required
                if len(self.passphrases[i]) < 1:
                    self.passphrases[i] = self.passlist[:]
                pwd=self.passphrases[i].pop()
                self.p.sendline(pwd)
        self.p.close()
        if self.doneCb is not None:
                self.doneCb(self.p.exitstatus is 0)

class filesync:
    """
    syncs a local directory with a remote directory.
    LATER: think about moving to python-libssh2
    """

    def __init__(self, source, target,
                 passphrases=None,  ## in case we need authentication
                 doneCallback=None, ## get's called once files have been transmitted
                 deleteSource=False,## delete files from source-folder after transmission
                 deleteTarget=False,## delete extra files in target-folder
                 ):
        self.doneCb=doneCallback

        prog=['rsync' ]
        prog+=['--archive']
        prog+=['--compress']
        if deleteTarget:
            prog+=['--delete']
        if deleteSource:
            prog+=['--remove-source-files']
        prog+=[source, target]
        print "FileSync:", prog
        self.syncer=_FileSyncer(prog,
                                passphrases,
                                doneCallback=self._callback)
        self.syncer.start()

    def _callback(self, success):
        if self.doneCb is not None:
            self.doneCb(success)

######################################################################

if __name__ == '__main__':
    def foo(success):
        print "Finished with", success
    f=filesync('/tmp/tex', 'iem@beaglebone:/tmp/foo', passphrases=['mo', 'iem'], doneCallback=foo)

