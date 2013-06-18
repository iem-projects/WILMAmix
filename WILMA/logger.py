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

import logging

class logger:
    def __init__(self, name=None):
        formatter = logging.Formatter('%(levelname)s(%(name)s): %(message)s')
        lh = None
        if name is not None:
            lh = logging.FileHandler(name+'.log')
        if lh is not None:
            lh.setFormatter(formatter)

        logger = logging.getLogger('WILMA')
        logger.propagate = (name is None)
        logger.setLevel(logging.INFO)
        if lh is not None:
            logger.addHandler(lh)

        osclogger = logging.getLogger('OSC')
        osclogger.setLevel(logging.INFO)
        osclogger.propagate = (name is None)
        if lh is not None:
            osclogger.addHandler(lh)

####################################################


if __name__ == '__main__':
    l = logger()
    log = logging.getLogger("WILMA")
    log.debug("debug")
    log.info("info")
    log.warn("warning")
    log.error("error")
    log.critical("critical")

