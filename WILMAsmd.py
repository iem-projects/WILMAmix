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
logging = logging_.getLogger('WILMA')


import daemon, daemon.pidlockfile
from WILMA import SMi, logger

import gobject


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pid", type=str,
                    help="PID-file to use")
args = parser.parse_args()
print args


if __name__ == '__main__':
    l = logger.logger("WILMAsmd")

    pidfile=None
    if args.pid is not None:
        pidfile=daemon.pidlockfile.TimeoutPIDLockFile(args.pid, 10)
    print "WILMAsmd", l.getFiles()

    with daemon.DaemonContext(files_preserve=l.getFiles(),
                              pidfile=pidfile):
        gobject.threads_init()
        logging.info("SMd...")

        sm = SMi()
        try:
            gobject.MainLoop().run()
        except KeyboardInterrupt:
            logging.info("WILMAsm KeyboardInterrupt")
        except:
            logging.exception("?")
        sm.cleanup()
    logging.fatal("BYE")

