# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SMchannels.ui'
#
# Created: Wed Apr  3 13:18:25 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SMchannels(object):
    def setupUi(self, SMchannels):
        SMchannels.setObjectName("SMchannels")
        SMchannels.resize(144, 376)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SMchannels.sizePolicy().hasHeightForWidth())
        SMchannels.setSizePolicy(sizePolicy)
        SMchannels.setCheckable(True)
        self.verticalLayout = QtGui.QVBoxLayout(SMchannels)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.meter = qsynthMeter(SMchannels)
        self.meter.setObjectName("meter")
        self.verticalLayout.addWidget(self.meter)
        self.launchButton = QtGui.QPushButton(SMchannels)
        self.launchButton.setCheckable(True)
        self.launchButton.setObjectName("launchButton")
        self.verticalLayout.addWidget(self.launchButton)
        self.configButton = QtGui.QPushButton(SMchannels)
        self.configButton.setObjectName("configButton")
        self.verticalLayout.addWidget(self.configButton)

        self.retranslateUi(SMchannels)

    def retranslateUi(self, SMchannels):
        SMchannels.setWindowTitle(QtGui.QApplication.translate("SMchannels", "SMi", None, QtGui.QApplication.UnicodeUTF8))
        SMchannels.setTitle(QtGui.QApplication.translate("SMchannels", "SMi", None, QtGui.QApplication.UnicodeUTF8))
        self.launchButton.setText(QtGui.QApplication.translate("SMchannels", "START", None, QtGui.QApplication.UnicodeUTF8))
        self.configButton.setText(QtGui.QApplication.translate("SMchannels", "Config", None, QtGui.QApplication.UnicodeUTF8))

from qsynthMeter import qsynthMeter
