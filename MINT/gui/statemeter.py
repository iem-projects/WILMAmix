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



class statemeterValue(QtGui.QFrame):
    def __init__(self, pMeter, label=None, scale=None, height=4, inverse=False):
        QtGui.QFrame.__init__(self, pMeter)
        #print "statemeter for :", label
        # Local instance variables.
        self.paint_time = 0.
        self.m_pMeter      = pMeter
        self.m_fValue      = 0.0
        self.m_maxValue    = 1.0
        self.inverse       = inverse
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        if label is not None:
            self.label         = label+": "
            self.setToolTip(label)
        if scale is None:
            self.suffix = '%'
            self.dynamic = False
        else:
            self.suffix=scale
            self.dynamic = True
        self.setBackgroundRole(QtGui.QPalette.NoRole)
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
    # Frame value one-way accessors.
    def setValue(self, fValue):
        val = fValue
        if self.dynamic:
            if val > self.m_maxValue:
                self.m_maxValue = 1.0*val
            val = val/self.m_maxValue
        if val < 0.:
            val=0.
        elif val > 1.:
            val = 1.
        self.m_fValue = val
        self.refresh()
        if self.label is not None:
            if self.dynamic:
                self.setToolTip(self.label+str(fValue)+self.suffix)
            else:
                percentage=str(int((fValue*100)*100)/100.)
                self.setToolTip(self.label+percentage+"%")

    def refresh(self):
        self.update()
    # Resize event handler.
    def resizeEvent(self, pResizeEvent):
        QtGui.QWidget.resizeEvent(self, pResizeEvent)
        #QtGui.QWidget.repaint(true)
    def paintEvent(self, event):
        t = QtCore.QTime()
        t.start()
        painter = QtGui.QPainter(self)
        w = self.width()
        h = self.height()

        # background(?)
        if self.isEnabled():
            painter.fillRect(0, 0, w, h,
                             self.m_pMeter.color(self.m_pMeter.ColorBack))
            #y = self.m_pMeter.iec_level(self.m_pMeter.Color0dB)
            #painter.setPen(self.m_pMeter.color(self.m_pMeter.ColorFore))
            #painter.drawLine(0, h - y, w, h - y)
        else:
            painter.fillRect(0, 0, w, h, self.palette().dark().color())

        # foreground(?)
        val = self.m_fValue
        if self.inverse:
            val = 1-val
        if val >= 0.95:
            color=self.m_pMeter.ColorOver
        elif val > .90:
            color=self.m_pMeter.ColorHigh
        elif val > .60:
            color=self.m_pMeter.ColorHigh#self.m_pMeter.ColorMid
        else:
            color=self.m_pMeter.ColorLow

        painter.fillRect(0, 0, int(w*(self.m_fValue)), h,
                         self.m_pMeter.color(color))

        self.paint_time = (95.*self.paint_time + 5.*t.elapsed())/100.




#----------------------------------------------------------------------------
# statemeter -- Meter bridge slot widget.

class statemeter(QtGui.QFrame):
    # Constructor.
    def __init__(self, pParent=None, ports=['foo'], scale=[], inverse=[], maxheight=None):
        QtGui.QFrame.__init__(self, pParent)
        self.ports = ports
        self.meterheight=4
        self.inverse = [False]*len(ports)
        self.scale =   [None ]*len(ports)
        for i in range(len(ports)):
            try:
                self.inverse[i]=inverse[i]
            except IndexError:
                self.inverse[i]=False
            try:
                self.scale[i]=scale[i]
            except IndexError:
                self.scale[i]=None

        if maxheight is not None:
            self.setMaxheight(maxheight)

        colorcount=0
        self.ColorLow    = colorcount; colorcount+=1
        self.ColorMid    = colorcount; colorcount+=1
        self.ColorHigh   = colorcount; colorcount+=1
        self.ColorOver   = colorcount; colorcount+=1
        self.ColorBack   = colorcount; colorcount+=1
        self.ColorFore   = colorcount; colorcount+=1
        self.ColorCount  = colorcount  # last

        self.m_colors = [QtGui.QColor(0,  0, 0)]*self.ColorCount
        self.m_colors[self.ColorBack] = QtGui.QColor( 20, 40, 20)
        self.m_colors[self.ColorFore] = QtGui.QColor( 80, 80, 80)
        self.m_colors[self.ColorLow ] = QtGui.QColor( 40,160, 40)
        self.m_colors[self.ColorMid ] = QtGui.QColor(220,220, 20)
        self.m_colors[self.ColorHigh] = QtGui.QColor(240,160, 20)
        self.m_colors[self.ColorOver] = QtGui.QColor(240,  0, 20)

        self.m_layout = QtGui.QVBoxLayout()
        self.m_layout.setSpacing(1)
        self.m_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.m_layout)

        self.setBackgroundRole(QtGui.QPalette.NoRole)
        self.build()
        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))

    def build(self):
        while self.m_layout.count() > 0:
            item = self.m_layout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()

        minheight=0
        maxheight=0
        self.m_values = []
        for i,p in enumerate(self.ports):
            value=statemeterValue(self, label=p, inverse=self.inverse[i], scale=self.scale[i], height=self.meterheight)
            self.m_values += [value]
            self.m_layout.addWidget(value)
            minheight+=value.minimumHeight()+1
            maxheight+=value.maximumHeight()+1
        #self.setMinimumSize(100,100)
        self.setMinimumHeight(minheight)
        self.setMaximumHeight(maxheight)

    def color ( self, iIndex ):
        return self.m_colors[iIndex]

    def setValue (self, iPort, fValue):
        self.m_values[iPort].setValue(fValue)


    def setPort(self, port):
        self.ports=port
    def setScale(self, scale):
        ports=len(self.ports)
        self.scale = [None]*ports
        for i in range(ports):
            try:
                self.scale[i]=scale[i]
            except IndexError:
                self.scale[i]=None
    def setInverse(self, inverse):
        ports=len(self.ports)
        self.inverse = [False]*ports
        for i in range(ports):
            try:
                self.inverse[i]=inverse[i]
            except IndexError:
                self.inverse[i]=False
    def setMaxheight(self, maxheight):
        numports=len(self.ports)
        height=maxheight/numports
        if(height<1):
            height=1
        self.meterheight=height
######################################################################
if __name__ == '__main__':
    import sys
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            layout = QtGui.QHBoxLayout()
            self.meter = statemeter(self, ['foo', 'bar', 'paz'])
            self.value = QtGui.QDoubleSpinBox(self)
            self.value.setMinimum(0)
            self.value.setMaximum(100)
            layout.addWidget(self.meter)
            layout.addWidget(self.value)
            self.setLayout(layout)
            self.value.valueChanged.connect(self.setValue)
        def setValue(self, value):
            self.meter.setValue(0, value*0.01)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
