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
    def __init__(self, configmanager, smifactory, parent=None, guiparent=None, SMs=None):
        super(SMmixer, self).__init__(guiparent)
        self.sm=[]
        self.master=parent
        self.sms=SMs
        self.smifactory=smifactory

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.smilayout = QHBoxLayout()
        self.smilayout.setSpacing(0)
        smiframe=QtGui.QFrame(self)
        smiframe.setLayout(self.smilayout)
        self.smilayout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(smiframe)

        self.mixctl = MIXctl(self, settings=configmanager.getMIX())
        self.layout.addWidget(self.mixctl)

        self.build()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        guiparent.setSizePolicy(sizePolicy)

        self.pushing=dict()
        self.pulling=dict()

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
                smi=self.smifactory(parent=self, name=name)
                self.sm+=[smi]
                self.smilayout.addWidget(smi.widget())
    def setSM(self, SMs=None):
        self.sms=SMs
        self.build()
    def scanSM(self):
        self.master.refreshIt()

    def selected(self):
        # FIXME: i'm sure this can be done very elegant with some lambda function
        result=[]
        for sm in self.sm:
            if sm.selected():
                result+=[sm]
        return result
    def select(self, state):
        for sm in self.sm:
            sm.select(state)

    def ping(self):
        for sm in self.sm:
            sm.ping()
    def launch(self, state):
        for s in self.selected():
            s.launch(state)
    def pull(self, path):
        if path is None:
            self.mixctl.pushpulled(False)
            return
        self.pulling.clear()
        for s in self.selected():
            self.pulling[s]=True
            s.pull(path, self._pulled)
    def push(self, path):
        if path is None:
            self.mixctl.pushpulled(True)
            return
        self.pushing.clear()
        for s in self.selected():
            self.pushing[s]=True
            s.push(path, self._pushed)
    def applySettings(self, settings):
        for s in self.selected():
            s.applySettings(settings)

    def _pulled(self, sm, ret):
        self.pulling[sm]=False
        if not True in self.pulling.values():
            self.mixctl.pushpulled(False)
    def _pushed(self, sm, ret):
        self.pushing[sm]=False
        if not True in self.pushing.values():
            self.mixctl.pushpulled(True)
