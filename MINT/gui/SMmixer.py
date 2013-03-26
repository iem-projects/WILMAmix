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

from PySide import QtCore, QtGui
from PySide.QtGui import *

from MIXctl import MIXctl

class SMmixer(QtGui.QFrame):
    def __init__(self, smifactory, parent=None, SMs=None):
        super(SMmixer, self).__init__(parent)
        self.sm=[]
        self.sms=SMs
        self.smifactory=smifactory

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.smilayout = QHBoxLayout()
        self.smilayout.setSpacing(0)
        smiframe=QtGui.QFrame(self)
        smiframe.setLayout(self.smilayout)

        self.mixctl = MIXctl()

        self.layout.addWidget(smiframe)

        mixctl = MIXctl()
        self.layout.addWidget(mixctl)
        self.build()

    def build(self):
        self.sm=[]

        while self.smilayout.count() > 0:
            item = self.smilayout.takeAt(0)
            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()

        # Create widgets
        count = 0
        SMs=self.sms
        if True:
            for sm in sorted(SMs.keys()):
                d=SMs[sm]
                smi=self.smifactory(parent=self, name=sm, confs=d)
                self.sm+=[smi]
                self.smilayout.addWidget(smi.widget())
                count+=1
        else:
            for count in range(16):
                name="SM"+str(count)
                self.sm+=[SM(parent=self, name=name)]
                self.smilayout.addWidget(self.sm[count])

    def setSM(self, SMs=None):
        self.sms=SMs
        self.build()

    def ping(self):
        for sm in self.sm:
            sm.ping()
