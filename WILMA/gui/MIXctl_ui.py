# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MIXctl.ui'
#
# Created: Wed Apr  3 13:18:25 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MIXctl(object):
    def setupUi(self, MIXctl):
        MIXctl.setObjectName("MIXctl")
        MIXctl.setEnabled(True)
        MIXctl.resize(213, 281)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MIXctl.sizePolicy().hasHeightForWidth())
        MIXctl.setSizePolicy(sizePolicy)
        MIXctl.setWindowTitle("WILMix")
        self.verticalLayout = QtGui.QVBoxLayout(MIXctl)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.selectFrame = QtGui.QGroupBox(MIXctl)
        self.selectFrame.setObjectName("selectFrame")
        self.horizontalLayout = QtGui.QHBoxLayout(self.selectFrame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.selectNoneButton = QtGui.QCheckBox(self.selectFrame)
        self.selectNoneButton.setText("")
        self.selectNoneButton.setObjectName("selectNoneButton")
        self.horizontalLayout.addWidget(self.selectNoneButton)
        spacerItem1 = QtGui.QSpacerItem(18, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.selectAllButton = QtGui.QCheckBox(self.selectFrame)
        self.selectAllButton.setText("")
        self.selectAllButton.setChecked(True)
        self.selectAllButton.setObjectName("selectAllButton")
        self.horizontalLayout.addWidget(self.selectAllButton)
        spacerItem2 = QtGui.QSpacerItem(18, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.selectToggleButton = QtGui.QCheckBox(self.selectFrame)
        self.selectToggleButton.setText("")
        self.selectToggleButton.setChecked(False)
        self.selectToggleButton.setTristate(True)
        self.selectToggleButton.setObjectName("selectToggleButton")
        self.horizontalLayout.addWidget(self.selectToggleButton)
        spacerItem3 = QtGui.QSpacerItem(18, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addWidget(self.selectFrame)
        self.fileFrame = QtGui.QGroupBox(MIXctl)
        self.fileFrame.setObjectName("fileFrame")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.fileFrame)
        self.horizontalLayout_2.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtGui.QPushButton(self.fileFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pullButton = QtGui.QPushButton(self.fileFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pullButton.sizePolicy().hasHeightForWidth())
        self.pullButton.setSizePolicy(sizePolicy)
        self.pullButton.setObjectName("pullButton")
        self.horizontalLayout_2.addWidget(self.pullButton)
        self.verticalLayout.addWidget(self.fileFrame)
        self.setupFrame = QtGui.QGroupBox(MIXctl)
        self.setupFrame.setObjectName("setupFrame")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.setupFrame)
        self.horizontalLayout_3.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.horizontalLayout_3.setContentsMargins(9, -1, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.configButton = QtGui.QPushButton(self.setupFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.configButton.sizePolicy().hasHeightForWidth())
        self.configButton.setSizePolicy(sizePolicy)
        self.configButton.setObjectName("configButton")
        self.horizontalLayout_3.addWidget(self.configButton)
        self.scanButton = QtGui.QPushButton(self.setupFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scanButton.sizePolicy().hasHeightForWidth())
        self.scanButton.setSizePolicy(sizePolicy)
        self.scanButton.setObjectName("scanButton")
        self.horizontalLayout_3.addWidget(self.scanButton)
        self.verticalLayout.addWidget(self.setupFrame)
        self.launchButton = QtGui.QPushButton(MIXctl)
        self.launchButton.setCheckable(True)
        self.launchButton.setObjectName("launchButton")
        self.verticalLayout.addWidget(self.launchButton)
        self.quitLayout = QtGui.QHBoxLayout()
        self.quitLayout.setObjectName("quitLayout")
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.quitLayout.addItem(spacerItem4)
        self.quitButton = QtGui.QPushButton(MIXctl)
        self.quitButton.setObjectName("quitButton")
        self.quitLayout.addWidget(self.quitButton)
        self.verticalLayout.addLayout(self.quitLayout)

        self.retranslateUi(MIXctl)

    def retranslateUi(self, MIXctl):
        MIXctl.setTitle(QtGui.QApplication.translate("MIXctl", "WILMix", None, QtGui.QApplication.UnicodeUTF8))
        self.selectFrame.setTitle(QtGui.QApplication.translate("MIXctl", "Selection", None, QtGui.QApplication.UnicodeUTF8))
        self.selectNoneButton.setToolTip(QtGui.QApplication.translate("MIXctl", "deselect all SMi\'s", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllButton.setToolTip(QtGui.QApplication.translate("MIXctl", "select all SMi\'s", None, QtGui.QApplication.UnicodeUTF8))
        self.selectToggleButton.setToolTip(QtGui.QApplication.translate("MIXctl", "toggle SMi selection", None, QtGui.QApplication.UnicodeUTF8))
        self.fileFrame.setTitle(QtGui.QApplication.translate("MIXctl", "FileSync", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MIXctl", "PUSH", None, QtGui.QApplication.UnicodeUTF8))
        self.pullButton.setText(QtGui.QApplication.translate("MIXctl", "PULL", None, QtGui.QApplication.UnicodeUTF8))
        self.setupFrame.setTitle(QtGui.QApplication.translate("MIXctl", "Setup", None, QtGui.QApplication.UnicodeUTF8))
        self.configButton.setText(QtGui.QApplication.translate("MIXctl", "Config", None, QtGui.QApplication.UnicodeUTF8))
        self.scanButton.setText(QtGui.QApplication.translate("MIXctl", "Scan", None, QtGui.QApplication.UnicodeUTF8))
        self.launchButton.setText(QtGui.QApplication.translate("MIXctl", "START", None, QtGui.QApplication.UnicodeUTF8))
        self.quitButton.setText(QtGui.QApplication.translate("MIXctl", "QUIT", None, QtGui.QApplication.UnicodeUTF8))

