# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'object_initializer_gui.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_table_initilizer(object):
    def setupUi(self, table_initilizer):
        table_initilizer.setObjectName("table_initilizer")
        table_initilizer.resize(594, 812)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(table_initilizer.sizePolicy().hasHeightForWidth())
        table_initilizer.setSizePolicy(sizePolicy)
        self.pushFinished_button = QtWidgets.QPushButton(table_initilizer)
        self.pushFinished_button.setGeometry(QtCore.QRect(10, 10, 97, 27))
        self.pushFinished_button.setObjectName("pushFinished_button")
        self.message_browser = QtWidgets.QTextBrowser(table_initilizer)
        self.message_browser.setGeometry(QtCore.QRect(10, 40, 571, 51))
        self.message_browser.setObjectName("message_browser")
        self.object_selecter_box = QtWidgets.QComboBox(table_initilizer)
        self.object_selecter_box.setGeometry(QtCore.QRect(130, 10, 451, 25))
        self.object_selecter_box.setObjectName("object_selecter_box")
        self.tableWidget = QtWidgets.QTableWidget(table_initilizer)
        self.tableWidget.setGeometry(QtCore.QRect(10, 100, 571, 501))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.verticalHeader().setVisible(False)

        self.retranslateUi(table_initilizer)
        QtCore.QMetaObject.connectSlotsByName(table_initilizer)

    def retranslateUi(self, table_initilizer):
        _translate = QtCore.QCoreApplication.translate
        table_initilizer.setWindowTitle(_translate("table_initilizer", "Form"))
        self.pushFinished_button.setText(_translate("table_initilizer", "finished"))
