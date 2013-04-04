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

from PySide import QtCore
from PySide.QtCore import QObject

from WILMA import launcher
import ThreadedInvoke

class GUILauncher(launcher):
    """ launches an external program, and provide callbacks for run, exit, stdout,..."""
    def __init__(self, prog, args=[], cwd=None, doneCb=None):
        super(GUILauncher, self).__init__(prog=prog, args=args, cwd=cwd, doneCb=self._callback)
        self.__doneCb=doneCb
    def _callback(self):
        if self.__doneCb is not None:
            ThreadedInvoke.callback(self.__doneCb)

if __name__ == '__main__':
    def foo():
        print "done"
    l = GUILauncher("ls", doneCb=foo)
    
