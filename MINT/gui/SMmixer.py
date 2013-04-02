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

from PySide import QtGui

class SMmixer(QtGui.QFrame):
    def __init__(self, guiparent=None, mixctl=None):
        super(SMmixer, self).__init__(guiparent)
        self.sm=[]

        self.layout = QtGui.QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.smilayout = QtGui.QHBoxLayout()
        self.smilayout.setSpacing(0)
        smiframe=QtGui.QFrame(self)
        smiframe.setLayout(self.smilayout)
        self.smilayout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(smiframe)

        if mixctl is not None:
            self.layout.addWidget(mixctl)

        self.build()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        guiparent.setSizePolicy(sizePolicy)

    def build(self):
        while self.smilayout.count() > 0:
            item = self.smilayout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()

        # Create widgets
        count = 0
        SMs=self.sm
        for sm in SMs:
            self.smilayout.addWidget(sm.widget())
            count+=1

    def setSM(self, SMs=[]):
        self.sm=SMs
        self.build()

