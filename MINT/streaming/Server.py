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


def Server(type, profile='L16', channels=1, source='jackaudiosrc'):
    if 'rtsp' == type:
        try:
            import RTSPserver
            return RTSPserver.RTSPserver(profile, source)
        except ImportError:
            pass

    raise Exception("invalid streame type: "+type)



######################################################################

if __name__ == '__main__':
    import time
    import gobject

    timestamp=0
    state=0
    s=None
    def next():
        global timestamp
        now=time.time()
        delta=now-timestamp
        if delta>10:
            timestamp=now
            print "next"
            return True
        return False
    def idler():
        global state, s
        if not next():
            return True
        state+=1
        if 1 is state:
          s=Server('rtsp')
          s.start()
          print "URI: ", s.getURI()
        elif 2 is state:
            s.stop()
            s.start()
            print "URI: ", s.getURI()
        elif 3 is state:
            s.stop()
            s=Server('rtsp')
            s.start()
            print "URI: ", s.getURI()
        elif 4 is state:
            s.stop()
        elif state>4:
            print "bye"
            gobject.MainLoop().quit()

        return True


    s=Server(type='rtsp')
    gobject.idle_add(idler)

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        pass
    print "ciao"
