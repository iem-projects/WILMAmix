# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SMchannel.ui'
#
# Created: Thu Jun 13 15:23:55 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SMchannel(object):
    def setupUi(self, SMchannel):
        SMchannel.setObjectName("SMchannel")
        SMchannel.resize(144, 376)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SMchannel.sizePolicy().hasHeightForWidth())
        SMchannel.setSizePolicy(sizePolicy)
        SMchannel.setCheckable(True)
        self.verticalLayout = QtGui.QVBoxLayout(SMchannel)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.meter = qsynthMeter(SMchannel)
        self.meter.setObjectName("meter")
        self.verticalLayout.addWidget(self.meter)
        self.launchButton = QtGui.QPushButton(SMchannel)
        self.launchButton.setCheckable(True)
        self.launchButton.setObjectName("launchButton")
        self.verticalLayout.addWidget(self.launchButton)
        self.configButton = QtGui.QPushButton(SMchannel)
        self.configButton.setObjectName("configButton")
        self.verticalLayout.addWidget(self.configButton)

        self.retranslateUi(SMchannel)

    def retranslateUi(self, SMchannel):
        SMchannel.setWindowTitle(QtGui.QApplication.translate("SMchannel", "SMi", None, QtGui.QApplication.UnicodeUTF8))
        SMchannel.setTitle(QtGui.QApplication.translate("SMchannel", "SMi", None, QtGui.QApplication.UnicodeUTF8))
        self.launchButton.setText(QtGui.QApplication.translate("SMchannel", "START", None, QtGui.QApplication.UnicodeUTF8))
        self.configButton.setText(QtGui.QApplication.translate("SMchannel", "Config", None, QtGui.QApplication.UnicodeUTF8))

from qsynthMeter import qsynthMeter
