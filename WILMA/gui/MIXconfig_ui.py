# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MIXconfig.ui'
#
# Created: Mon Jun 17 16:45:51 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MIXconfig(object):
    def setupUi(self, MIXconfig):
        MIXconfig.setObjectName("MIXconfig")
        MIXconfig.resize(206, 320)
        MIXconfig.setWindowTitle("WILMix configuration")
        self.closeButtons = QtGui.QDialogButtonBox(MIXconfig)
        self.closeButtons.setGeometry(QtCore.QRect(10, 270, 191, 41))
        self.closeButtons.setOrientation(QtCore.Qt.Horizontal)
        self.closeButtons.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.closeButtons.setObjectName("closeButtons")
        self.frame_proxy = QtGui.QGroupBox(MIXconfig)
        self.frame_proxy.setGeometry(QtCore.QRect(10, 10, 191, 101))
        self.frame_proxy.setObjectName("frame_proxy")
        self.proxy_recvPort = QtGui.QSpinBox(self.frame_proxy)
        self.proxy_recvPort.setGeometry(QtCore.QRect(120, 20, 61, 22))
        self.proxy_recvPort.setMaximum(65535)
        self.proxy_recvPort.setObjectName("proxy_recvPort")
        self.proxy_sendHost = QtGui.QLineEdit(self.frame_proxy)
        self.proxy_sendHost.setGeometry(QtCore.QRect(10, 70, 101, 20))
        self.proxy_sendHost.setObjectName("proxy_sendHost")
        self.proxy_sendPort = QtGui.QSpinBox(self.frame_proxy)
        self.proxy_sendPort.setGeometry(QtCore.QRect(119, 70, 61, 22))
        self.proxy_sendPort.setMaximum(65535)
        self.proxy_sendPort.setObjectName("proxy_sendPort")
        self.label_fromProcess = QtGui.QLabel(self.frame_proxy)
        self.label_fromProcess.setGeometry(QtCore.QRect(10, 50, 101, 16))
        self.label_fromProcess.setObjectName("label_fromProcess")
        self.label_toProcess = QtGui.QLabel(self.frame_proxy)
        self.label_toProcess.setGeometry(QtCore.QRect(50, 20, 60, 20))
        self.label_toProcess.setObjectName("label_toProcess")
        self.frame_sync = QtGui.QGroupBox(MIXconfig)
        self.frame_sync.setGeometry(QtCore.QRect(10, 120, 191, 81))
        self.frame_sync.setObjectName("frame_sync")
        self.syncButton = QtGui.QPushButton(self.frame_sync)
        self.syncButton.setGeometry(QtCore.QRect(24, 50, 141, 23))
        self.syncButton.setCheckable(True)
        self.syncButton.setObjectName("syncButton")
        self.label_sync = QtGui.QLabel(self.frame_sync)
        self.label_sync.setGeometry(QtCore.QRect(30, 20, 71, 20))
        self.label_sync.setObjectName("label_sync")
        self.label_syncTS = QtGui.QLabel(self.frame_sync)
        self.label_syncTS.setGeometry(QtCore.QRect(60, 20, 101, 20))
        self.label_syncTS.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_syncTS.setText("")
        self.label_syncTS.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_syncTS.setObjectName("label_syncTS")

        self.retranslateUi(MIXconfig)

    def retranslateUi(self, MIXconfig):
        self.frame_proxy.setTitle(QtGui.QApplication.translate("MIXconfig", "Proxy Process Data", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy_recvPort.setToolTip(QtGui.QApplication.translate("MIXconfig", "data sent to this port is forwarded to the SMi\'s /process/", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy_sendHost.setToolTip(QtGui.QApplication.translate("MIXconfig", "process-data gets forwarded to this host", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy_sendPort.setToolTip(QtGui.QApplication.translate("MIXconfig", "process-data gets forwarded to this port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fromProcess.setText(QtGui.QApplication.translate("MIXconfig", "process →", None, QtGui.QApplication.UnicodeUTF8))
        self.label_toProcess.setText(QtGui.QApplication.translate("MIXconfig", "process↔", None, QtGui.QApplication.UnicodeUTF8))
        self.frame_sync.setTitle(QtGui.QApplication.translate("MIXconfig", "SyncStreams", None, QtGui.QApplication.UnicodeUTF8))
        self.syncButton.setText(QtGui.QApplication.translate("MIXconfig", "Sync", None, QtGui.QApplication.UnicodeUTF8))
        self.label_sync.setText(QtGui.QApplication.translate("MIXconfig", "freewheeling", None, QtGui.QApplication.UnicodeUTF8))

