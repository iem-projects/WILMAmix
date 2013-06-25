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
from WILMA import SMi, logger, user

import gobject


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--pidfile", type=str,
                    help="PID-file to use")
parser.add_argument("-u", "--user", type=str,
                    help="User to run as")
parser.add_argument("-g", "--group", type=str,
                    help="Group to run as")
parser.add_argument("--path", type=str,
                    help="Working directory to use")

args = parser.parse_args()


if __name__ == '__main__':
    pidfile=None
    uid=user.getUser(args.user),
    gid=user.getGroup(args.group),
    working_directory=user.getHome(args.path),
    logfiles=None
    if args.pidfile is not None:
        pidfile=daemon.pidlockfile.TimeoutPIDLockFile(args.pidfile, 10)

    if args.path is None:
        args.path=args.user

    l = logger.logger("WILMAsmd")
    logfiles=l.getFiles()

    with daemon.DaemonContext(files_preserve=logfiles,
                              pidfile=pidfile,
                              uid=uid, gid=gid,
                              working_directory=working_directory,
                              ):
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

