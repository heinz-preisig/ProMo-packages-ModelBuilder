# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/heinz/1_Gits/ProcessModeller/ProcessModeller_v5_01/packages/ModelComposer/modeller_logger.ui'
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

class Ui_LoggerForm(object):
    def setupUi(self, LoggerForm):
        LoggerForm.setObjectName(_fromUtf8("LoggerForm"))
        LoggerForm.resize(750, 871)
        self.groupBox_2 = QtGui.QGroupBox(LoggerForm)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 701, 381))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.Logger = QtGui.QTextBrowser(self.groupBox_2)
        self.Logger.setGeometry(QtCore.QRect(10, 40, 681, 331))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Logger.setFont(font)
        self.Logger.setObjectName(_fromUtf8("Logger"))
        self.widget = QtGui.QWidget(self.groupBox_2)
        self.widget.setGeometry(QtCore.QRect(240, 10, 451, 29))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushPrintArcs = QtGui.QPushButton(self.widget)
        self.pushPrintArcs.setObjectName(_fromUtf8("pushPrintArcs"))
        self.horizontalLayout.addWidget(self.pushPrintArcs)
        self.pushPrintNodes = QtGui.QPushButton(self.widget)
        self.pushPrintNodes.setObjectName(_fromUtf8("pushPrintNodes"))
        self.horizontalLayout.addWidget(self.pushPrintNodes)
        self.pushPrintScenes = QtGui.QPushButton(self.widget)
        self.pushPrintScenes.setObjectName(_fromUtf8("pushPrintScenes"))
        self.horizontalLayout.addWidget(self.pushPrintScenes)
        self.pushPrintTree = QtGui.QPushButton(self.widget)
        self.pushPrintTree.setObjectName(_fromUtf8("pushPrintTree"))
        self.horizontalLayout.addWidget(self.pushPrintTree)
        self.pushClearWindow = QtGui.QPushButton(self.widget)
        self.pushClearWindow.setObjectName(_fromUtf8("pushClearWindow"))
        self.horizontalLayout.addWidget(self.pushClearWindow)
        self.groupBoxStandardOutput = QtGui.QGroupBox(LoggerForm)
        self.groupBoxStandardOutput.setGeometry(QtCore.QRect(20, 400, 691, 221))
        self.groupBoxStandardOutput.setObjectName(_fromUtf8("groupBoxStandardOutput"))
        self.std_outbox = QtGui.QTextBrowser(self.groupBoxStandardOutput)
        self.std_outbox.setGeometry(QtCore.QRect(20, 20, 691, 191))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.std_outbox.setFont(font)
        self.std_outbox.setObjectName(_fromUtf8("std_outbox"))
        self.groupBoxErrorOutput = QtGui.QGroupBox(LoggerForm)
        self.groupBoxErrorOutput.setGeometry(QtCore.QRect(20, 620, 691, 221))
        self.groupBoxErrorOutput.setObjectName(_fromUtf8("groupBoxErrorOutput"))
        self.err_outbox = QtGui.QTextBrowser(self.groupBoxErrorOutput)
        self.err_outbox.setGeometry(QtCore.QRect(20, 20, 691, 191))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.err_outbox.setFont(font)
        self.err_outbox.setObjectName(_fromUtf8("err_outbox"))

        self.retranslateUi(LoggerForm)
        QtCore.QMetaObject.connectSlotsByName(LoggerForm)

    def retranslateUi(self, LoggerForm):
        LoggerForm.setWindowTitle(_translate("LoggerForm", "Form", None))
        self.groupBox_2.setTitle(_translate("LoggerForm", "window  into the data", None))
        self.pushPrintArcs.setText(_translate("LoggerForm", "arcs", None))
        self.pushPrintNodes.setText(_translate("LoggerForm", "nodes", None))
        self.pushPrintScenes.setText(_translate("LoggerForm", "scenes", None))
        self.pushPrintTree.setText(_translate("LoggerForm", "tree", None))
        self.pushClearWindow.setText(_translate("LoggerForm", "clear", None))
        self.groupBoxStandardOutput.setTitle(_translate("LoggerForm", "standard output box", None))
        self.groupBoxErrorOutput.setTitle(_translate("LoggerForm", "error output  box", None))

