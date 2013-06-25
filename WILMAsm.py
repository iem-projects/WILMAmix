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

import gobject

from WILMA import SMi, logger

if __name__ == '__main__':
    l = logger.logger("WILMAsm.log")
    logging.info("SM...")
    gobject.threads_init()
    sm = SMi()
    import time

    try:
        gobject.MainLoop().run()
    except KeyboardInterrupt:
        logging.exception("WILMAsm KeyboardInterrupt")
        pass
    sm.cleanup()


