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
import os

class logger:
    def __init__(self, name=None):
        formatter = logging.Formatter('%(asctime)s %(levelname)s(%(name)s): %(message)s')
        lh = None
        if name is None:
            lh = logging.handlers.SysLogHandler(address='/dev/log')
        elif 'stderr' == name:
            # fall back to a stderr
            lh=logging.StreamHandler()
            pass
        else:
            if lh is None:
                try:
                    lh = self._getFileHandler(name)
                except IOError:
                    pass
            if lh is None:
                ## hmm, couldn't create a logfile at the desired place
                ## try creating it in /tmp
                try:
                    import tempfile
                    lh = self._getFileHandler(os.path.join(tempfile.tempdir, self._unabsPath(name)))
                except IOError, OSError:
                    pass
        if lh is not None:
            lh.setFormatter(formatter)
        else:
            lh=logging.StreamHandler()
        self.lh = lh

        logger = logging.getLogger('WILMA')
        osclogger = logging.getLogger('OSC')

        for l in [logger, osclogger]:
            l.propagate = (name is None)
            l.setLevel(logging.NOTSET)
            if lh is not None:
                l.addHandler(lh)

        ## set root-logger to INFO
        logging.getLogger().setLevel(logging.INFO)

    @staticmethod
    def _getFileHandler(filename):
        dir=os.path.split(filename)[0]
        if dir:
            try:
                os.makedirs(dir)
            except:
                pass
        return logging.FileHandler(filename)
    @staticmethod
    def _unabsPath(path):
      folders=[]
      while 1:
          path,folder=os.path.split(path)
          if folder:
              folders.append(folder)
          else:
              break
      folders.reverse()
      return os.path.join(*folders)

    def getFiles(self):
        try:
            return [self.lh.stream]
        except:
            pass
        return None
def getLogLevels():
    return [logging.getLevelName(lvl) for lvl in sorted(set(
            [logging.getLevelName(lvlname) for lvlname in logging._levelNames if isinstance(lvlname, basestring)]
            ))]
def getLevel():
    return logging.getLogger().getEffectiveLevel()
def setLevel(lvl):
    try:
        ## lvl should be int, e.g. 20
        level=int(lvl)
    except ValueError, TypeError:
        ## but somebody might have sent it as a string, e.g. 'INFO'
        level=logging.getLevelName(lvl)
        if not isinstance(level, (int, long)):
            ## cannot resolve logname, assume our own default
            level=getLevel()

    levelname=logging.getLevelName(level)
    if not levelname in getLogLevels()
        ## hmm, levelname is missing from levels, add it
        logging.addLevelName(level, levelname)
    logging.getLogger().setLevel(level)
    return level

####################################################


if __name__ == '__main__':
    l = logger()
    log = logging.getLogger("WILMA")
    log.debug("debug")
    log.info("info")
    log.warn("warning")
    log.error("error")
    log.critical("critical")
    print("LEVELS: %s" % (getLogLevels()))

