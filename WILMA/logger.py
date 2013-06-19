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

import logging, logging.handlers

class logger:
    def __init__(self, name=None):
        formatter = logging.Formatter('%(asctime)s %(levelname)s(%(name)s): %(message)s')
        lh = None
        if name is not None:
            if lh is None:
                try:
                    lh = logging.FileHandler(name+'.log')
                except IOError:
                    pass
            if lh is None:
                try:
                    lh = logging.FileHandler('/tmp/'+name+'.log')
                except IOError:
                    pass
        if lh is not None:
            lh.setFormatter(formatter)
        self.lh = lh

        logger = logging.getLogger('WILMA')
        osclogger = logging.getLogger('OSC')

        for l in [logger, osclogger]:
            l.propagate = (name is None)
            l.setLevel(logging.INFO)
            if lh is not None:
                l.addHandler(lh)
##            l.addHandler(logging.handlers.SysLogHandler(address='/dev/log'))

    def getFiles(self):
        try:
            return [self.lh.stream]
        except:
            pass
        return None


####################################################


if __name__ == '__main__':
    l = logger()
    log = logging.getLogger("WILMA")
    log.debug("debug")
    log.info("info")
    log.warn("warning")
    log.error("error")
    log.critical("critical")

