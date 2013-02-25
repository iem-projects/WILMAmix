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
        self.update()

    def update(self):
        try:
            import psutil
            self.cpu=psutil.cpu_percent()/100.
            self.mem=psutil.phymem_usage().percent/100.
        except ImportError:
            if not hasattr(self, 'importfailed_psutil'):
                print "failed to import 'psutil'. do you have 'python-psutil' installed?"
            self.importfailed_psutil=True
        s=os.statvfs(self.path)
        self.disk=(s.f_blocks-s.f_bfree)*1./s.f_blocks

        

######################################################################

if __name__ == '__main__':
    print "SystemHealth..."
    s=SystemHealth()
    print "CPU: ", s.cpu
    print "MEM: ", s.mem
    print "DISK: ", s.disk
    
    


