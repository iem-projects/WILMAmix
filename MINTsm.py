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

from MINT import NetServer
import gobject

class MINTsm:
    def __init__(self):
        self.server = NetServer(port=7777)
        self.server.add(self.setGain, '/gain')
        print "MINTsm for server", self.server

    def setGain(self, msg, src):
        print "gain msg: ", msg
        print "gain src: ", src

if __name__ == '__main__':
    print "SM..."
    sm = MINTsm()
    import time
    
    main_loop = gobject.MainLoop()
    print "start loop"
    try:
        main_loop.run()
    except KeyboardInterrupt:
        pass


