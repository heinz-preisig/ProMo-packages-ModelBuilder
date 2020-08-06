# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fix_selected_equations.ui'
#
# Created by: PyQt5 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

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

class Ui_Var_fixer(object):
    def setupUi(self, Var_fixer):
        Var_fixer.setObjectName(_fromUtf8("Var_fixer"))
        Var_fixer.resize(588, 602)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Var_fixer.sizePolicy().hasHeightForWidth())
        Var_fixer.setSizePolicy(sizePolicy)
        self.pushSelect_button = QtGui.QPushButton(Var_fixer)
        self.pushSelect_button.setGeometry(QtCore.QRect(10, 10, 97, 27))
        self.pushSelect_button.setObjectName(_fromUtf8("pushSelect_button"))
        self.message_browser = QtGui.QTextBrowser(Var_fixer)
        self.message_browser.setGeometry(QtCore.QRect(10, 40, 571, 51))
        self.message_browser.setObjectName(_fromUtf8("message_browser"))
        self.scrollArea = QtGui.QScrollArea(Var_fixer)
        self.scrollArea.setGeometry(QtCore.QRect(10, 100, 571, 481))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 569, 479))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayoutWidget = QtGui.QWidget(self.scrollAreaWidgetContents)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 571, 481))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(Var_fixer)
        QtCore.QMetaObject.connectSlotsByName(Var_fixer)

    def retranslateUi(self, Var_fixer):
        Var_fixer.setWindowTitle(_translate("Var_fixer", "Form", None))
        self.pushSelect_button.setText(_translate("Var_fixer", "select", None))

