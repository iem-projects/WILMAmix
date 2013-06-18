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
import logging
import sys

from PySide.QtGui import QDialog, QApplication, QVBoxLayout

from WILMA import MIXgui, logger

class _Form(QDialog):
   
    def __init__(self, parent=None):
        super(_Form, self).__init__(parent)
        self.mix=MIXgui.MIXgui(self)
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.mix.widget())
        # Set dialog layout
        self.setLayout(layout)
if __name__ == '__main__':
    l = logger.logger("WILMix")
    import gobject
    gobject.threads_init()
    # Create the Qt Application
    app = QApplication(sys.argv)
    #translator = Translator(app)
    # Create and show the form
    form = _Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())



