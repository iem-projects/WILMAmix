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

from PySide import QtCore

class _InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        QtCore.QEvent.__init__(self, _InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class _Invoker(QtCore.QObject):
    def event(self, event):
        event.fn(*event.args, **event.kwargs)

        return True

_invoker = _Invoker()


def callback(fn, *args, **kwargs):
    """
    call a function in the main (GUI) thread.
    this will return immediately, the function will be executed later
    """
    QtCore.QCoreApplication.postEvent(_invoker,
                                      _InvokeEvent(fn, *args, **kwargs))

class Invoker:
    def __init__(self, fn):
        self.fn=fn
    def __call__(self, *args, **kwargs):
        callback(self.fn, *args, **kwargs)

if __name__ == '__main__':
    def foo(name):
        print name
    callback(foo, "hello")
