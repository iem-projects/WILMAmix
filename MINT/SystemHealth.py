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

import os
import time

class SystemHealth:
    def __init__(self, path=None):
        try:
            if path is None:
                path='.'
            os.statvfs(path)
            self.path=path
        except:
            self.path=os.path.expanduser('~')
        self.cpu = 1.
        self.mem = 1.
        self.disk= 1.
        self.have_psutil=True
        self.last=0

        self.update()

    def update(self):
        now=time.time()
        if(now - self.last < 2):
            return
        self.last=now
        
        s=os.statvfs(self.path)
        self.disk=(s.f_blocks-s.f_bfree)*1./s.f_blocks

        if self.have_psutil:
            try:
                import psutil
                self.cpu=psutil.cpu_percent(interval=0.0)/100.
                used=psutil.used_phymem()
                avail=psutil.avail_phymem()
                #self.mem=psutil.phymem_usage().percent/100.
                self.mem=(1.0*used)/(used+avail)
            except ImportError:
                if self.have_psutil:
                    print "failed to import 'psutil'. do you have 'python-psutil' installed?"
                self.have_psutil=False

        

######################################################################

if __name__ == '__main__':
    print "SystemHealth..."
    s=SystemHealth()
    print "CPU: ", s.cpu
    print "MEM: ", s.mem
    print "DISK: ", s.disk
    
    


