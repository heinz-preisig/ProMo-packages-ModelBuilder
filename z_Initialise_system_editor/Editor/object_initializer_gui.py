# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'object_initializer_gui.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_table_initilizer(object):
    def setupUi(self, table_initilizer):
        table_initilizer.setObjectName(_fromUtf8("table_initilizer"))
        table_initilizer.resize(594, 812)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(table_initilizer.sizePolicy().hasHeightForWidth())
        table_initilizer.setSizePolicy(sizePolicy)
        self.pushFinished_button = QtGui.QPushButton(table_initilizer)
        self.pushFinished_button.setGeometry(QtCore.QRect(10, 10, 97, 27))
        self.pushFinished_button.setObjectName(_fromUtf8("pushFinished_button"))
        self.message_browser = QtGui.QTextBrowser(table_initilizer)
        self.message_browser.setGeometry(QtCore.QRect(10, 40, 571, 51))
        self.message_browser.setObjectName(_fromUtf8("message_browser"))
        self.object_selecter_box = QtGui.QComboBox(table_initilizer)
        self.object_selecter_box.setGeometry(QtCore.QRect(130, 10, 451, 25))
        self.object_selecter_box.setObjectName(_fromUtf8("object_selecter_box"))
        self.tableWidget = QtGui.QTableWidget(table_initilizer)
        self.tableWidget.setGeometry(QtCore.QRect(10, 100, 571, 501))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.verticalHeader().setVisible(False)

        self.retranslateUi(table_initilizer)
        QtCore.QMetaObject.connectSlotsByName(table_initilizer)

    def retranslateUi(self, table_initilizer):
        table_initilizer.setWindowTitle(_translate("table_initilizer", "Form", None))
        self.pushFinished_button.setText(_translate("table_initilizer", "finished", None))

