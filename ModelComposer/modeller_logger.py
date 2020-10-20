# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modeller_logger.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoggerForm(object):
    def setupUi(self, LoggerForm):
        LoggerForm.setObjectName("LoggerForm")
        LoggerForm.resize(750, 871)
        self.groupBox_2 = QtWidgets.QGroupBox(LoggerForm)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 20, 701, 381))
        self.groupBox_2.setObjectName("groupBox_2")
        self.Logger = QtWidgets.QTextBrowser(self.groupBox_2)
        self.Logger.setGeometry(QtCore.QRect(10, 40, 681, 331))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Logger.setFont(font)
        self.Logger.setObjectName("Logger")
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setGeometry(QtCore.QRect(240, 10, 451, 29))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushPrintArcs = QtWidgets.QPushButton(self.widget)
        self.pushPrintArcs.setObjectName("pushPrintArcs")
        self.horizontalLayout.addWidget(self.pushPrintArcs)
        self.pushPrintNodes = QtWidgets.QPushButton(self.widget)
        self.pushPrintNodes.setObjectName("pushPrintNodes")
        self.horizontalLayout.addWidget(self.pushPrintNodes)
        self.pushPrintScenes = QtWidgets.QPushButton(self.widget)
        self.pushPrintScenes.setObjectName("pushPrintScenes")
        self.horizontalLayout.addWidget(self.pushPrintScenes)
        self.pushPrintTree = QtWidgets.QPushButton(self.widget)
        self.pushPrintTree.setObjectName("pushPrintTree")
        self.horizontalLayout.addWidget(self.pushPrintTree)
        self.pushClearWindow = QtWidgets.QPushButton(self.widget)
        self.pushClearWindow.setObjectName("pushClearWindow")
        self.horizontalLayout.addWidget(self.pushClearWindow)
        self.groupBoxStandardOutput = QtWidgets.QGroupBox(LoggerForm)
        self.groupBoxStandardOutput.setGeometry(QtCore.QRect(20, 400, 691, 221))
        self.groupBoxStandardOutput.setObjectName("groupBoxStandardOutput")
        self.std_outbox = QtWidgets.QTextBrowser(self.groupBoxStandardOutput)
        self.std_outbox.setGeometry(QtCore.QRect(20, 20, 691, 191))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.std_outbox.setFont(font)
        self.std_outbox.setObjectName("std_outbox")
        self.groupBoxErrorOutput = QtWidgets.QGroupBox(LoggerForm)
        self.groupBoxErrorOutput.setGeometry(QtCore.QRect(20, 620, 691, 221))
        self.groupBoxErrorOutput.setObjectName("groupBoxErrorOutput")
        self.err_outbox = QtWidgets.QTextBrowser(self.groupBoxErrorOutput)
        self.err_outbox.setGeometry(QtCore.QRect(20, 20, 691, 191))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.err_outbox.setFont(font)
        self.err_outbox.setObjectName("err_outbox")

        self.retranslateUi(LoggerForm)
        QtCore.QMetaObject.connectSlotsByName(LoggerForm)

    def retranslateUi(self, LoggerForm):
        _translate = QtCore.QCoreApplication.translate
        LoggerForm.setWindowTitle(_translate("LoggerForm", "Form"))
        self.groupBox_2.setTitle(_translate("LoggerForm", "window  into the data"))
        self.pushPrintArcs.setText(_translate("LoggerForm", "arcs"))
        self.pushPrintNodes.setText(_translate("LoggerForm", "nodes"))
        self.pushPrintScenes.setText(_translate("LoggerForm", "scenes"))
        self.pushPrintTree.setText(_translate("LoggerForm", "tree"))
        self.pushClearWindow.setText(_translate("LoggerForm", "clear"))
        self.groupBoxStandardOutput.setTitle(_translate("LoggerForm", "standard output box"))
        self.groupBoxErrorOutput.setTitle(_translate("LoggerForm", "error output  box"))
