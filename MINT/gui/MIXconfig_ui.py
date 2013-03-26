# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MIXconfig.ui'
#
# Created: Tue Mar 26 19:17:23 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(240, 320)
        Dialog.setWindowTitle("MINTmix configuration")
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 270, 221, 41))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.frame_proxy = QtGui.QGroupBox(Dialog)
        self.frame_proxy.setGeometry(QtCore.QRect(20, 20, 191, 131))
        self.frame_proxy.setObjectName("frame_proxy")
        self.proxy_recvPort = QtGui.QSpinBox(self.frame_proxy)
        self.proxy_recvPort.setGeometry(QtCore.QRect(120, 20, 61, 22))
        self.proxy_recvPort.setMaximum(65535)
        self.proxy_recvPort.setObjectName("proxy_recvPort")
        self.proxy_sendHost = QtGui.QLineEdit(self.frame_proxy)
        self.proxy_sendHost.setGeometry(QtCore.QRect(10, 100, 101, 20))
        self.proxy_sendHost.setObjectName("proxy_sendHost")
        self.proxy_sendPort = QtGui.QSpinBox(self.frame_proxy)
        self.proxy_sendPort.setGeometry(QtCore.QRect(119, 100, 61, 22))
        self.proxy_sendPort.setMaximum(65535)
        self.proxy_sendPort.setObjectName("proxy_sendPort")
        self.label_fromProcess = QtGui.QLabel(self.frame_proxy)
        self.label_fromProcess.setGeometry(QtCore.QRect(10, 80, 101, 16))
        self.label_fromProcess.setObjectName("label_fromProcess")
        self.label_toProcess = QtGui.QLabel(self.frame_proxy)
        self.label_toProcess.setGeometry(QtCore.QRect(50, 20, 60, 20))
        self.label_toProcess.setObjectName("label_toProcess")

        self.retranslateUi(Dialog)

    def retranslateUi(self, Dialog):
        self.frame_proxy.setTitle(QtGui.QApplication.translate("Dialog", "Proxy Process Data", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy_recvPort.setToolTip(QtGui.QApplication.translate("Dialog", "data sent to this port is forwarded to the SMi\'s /process/", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy_sendHost.setToolTip(QtGui.QApplication.translate("Dialog", "process-data gets forwarded to this host", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy_sendPort.setToolTip(QtGui.QApplication.translate("Dialog", "process-data gets forwarded to this port", None, QtGui.QApplication.UnicodeUTF8))
        self.label_fromProcess.setText(QtGui.QApplication.translate("Dialog", "process →", None, QtGui.QApplication.UnicodeUTF8))
        self.label_toProcess.setText(QtGui.QApplication.translate("Dialog", "process↔", None, QtGui.QApplication.UnicodeUTF8))

