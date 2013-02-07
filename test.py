#!/usr/bin/python
# -*- coding: utf-8 -*-


from DiscoverSM import DiscoverSM
from PySide.QtCore import *
from PySide.QtGui import *
import sys
from gui import SMmixer, Translator

class Form(QDialog):
   
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.discover=DiscoverSM()
        # Create widgets
        self.dict=self.discover.getDict()
        print self.dict
        self.mixer=SMmixer(self, self.dict)
        self.bRefresh = QPushButton("Refresh")
        self.bPrint   = QPushButton("Print")
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.mixer)
        layout.addWidget(self.bRefresh)
        layout.addWidget(self.bPrint)
        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.bRefresh.clicked.connect(self.refreshIt)
        self.bPrint.clicked.connect(self.printIt)

        self.refreshIt()

    def refreshIt(self):
        self.dict = self.discover.getDict()
        self.mixer.setSM(self.dict)
        self.show()

    def printIt(self):
        print self.dict

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    translator = Translator(app)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())



