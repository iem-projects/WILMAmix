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

from PySide import QtCore, QtGui
import os
import warnings

class PullDirChooser:
    def __init__(self, parent=None, startdir=None):
        self.callback=None
        self.dialog=QtGui.QFileDialog(parent, "select directory to store files from SMi", startdir)
        self.dialog.setFileMode(self.dialog.FileMode.Directory)
        #self.dialog.setAcceptMode(self.dialog.AcceptMode.AcceptSave)
        self.dialog.setConfirmOverwrite (True)
        self.dialog.fileSelected.connect(self._callback)
        self.dialog.rejected.connect(self._cancelled)
    def _cancelled(self):
        callback=self.callback
        self.callback=None
        if callback is not None:
            callback(None)
    def _callback(self, path):
        #TODO: check for non-empty directories
        if self.callback is None:
            return
        callback=self.callback
        self.callback=None
        if len(os.listdir(path))>0:
            ret=QtGui.QMessageBox.warning(self.dialog,
                                          "WILMix: non-empty PULL Directory",
                                          ("The selected directory '"+path+"' is not empty. "
                                            "Pulling data from the SMi might overwrite any files therein.\n"
                                            "Do you really want to pull data from the SMi into this directory?"),
                                           QtGui.QMessageBox.Ok | QtGui.QMessageBox.Discard,
                                           QtGui.QMessageBox.Ok)
            if ret is QtGui.QMessageBox.Discard:
                return
        if callback is not None:
            callback(path)

    def choose(self, callback):
        self.callback=callback
        self.dialog.show()

class PushDirChooser:
    def __init__(self, parent=None, startdir=None):
        self.callback=None
        self.dialog=QtGui.QFileDialog(parent, "select directory to transmit to SMi", startdir)
        self.dialog.setFileMode(self.dialog.FileMode.Directory)
        self.dialog.fileSelected.connect(self._callback)
        self.dialog.rejected.connect(self._cancelled)
    def _cancelled(self):
        callback=self.callback
        self.callback=None
        if callback is not None:
            callback(None)
    def _callback(self, path):
        if self.callback is None:
            return
        callback=self.callback
        self.callback=None
        try:
            with open(os.path.join(path, 'MAIN.pd')): pass
        except IOError:
            ret=QtGui.QMessageBox.critical(self.dialog,
                                           "WILMix: invalid PUSH Directory",
                                           ("The selected directory '"+path+"' does not contain a 'MAIN.pd' file. "
                                            "Pushing it to the SMi will make any PROCESS void.\n"
                                            "Do you really want to push this directory to the SMi?"),
                                           QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                           QtGui.QMessageBox.Cancel)
            if ret is QtGui.QMessageBox.Cancel:
                return
        if callback is not None:
            callback(path)

    def choose(self, callback):
        self.callback=callback
        self.dialog.show()

######################################################################
if __name__ == '__main__':
    import sys
    class Form(QtGui.QDialog):
        def __init__(self, parent=None):
            super(Form, self).__init__(parent)
            self.pushchooser=PushDirChooser(self, '/tmp')
            self.pullchooser=PullDirChooser(self, '/tmp')

            layout = QtGui.QHBoxLayout()
            self.pullButton= QtGui.QPushButton("->PullDir")
            self.pullButton.clicked.connect(self.do_pulldir)
            layout.addWidget(self.pullButton)
            self.pushButton= QtGui.QPushButton("->PushDir")
            self.pushButton.clicked.connect(self.do_pushdir)
            layout.addWidget(self.pushButton)
            self.quitButton= QtGui.QPushButton("Quit")
            self.quitButton.clicked.connect(self.quitB)
            layout.addWidget(self.quitButton)

            self.setLayout(layout)
        def do_pushdir(self):
            self.pushchooser.choose(self.got_pushdir)
        def got_pushdir(self, path):
            warnings.warn("PUSH: '%s'" % path)
        def do_pulldir(self):
            self.pullchooser.choose(self.got_pulldir)
        def got_pulldir(self, path):
            warnings.warn("PULL: '%s'" % path)

        def quitB(self):
            sys.exit(0)

    app = QtGui.QApplication(sys.argv)
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
