# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor_initialise_system_gui.ui'
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1015, 537)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.message_box = QtGui.QTextBrowser(self.centralwidget)
        self.message_box.setGeometry(QtCore.QRect(50, 410, 491, 61))
        self.message_box.setObjectName(_fromUtf8("message_box"))
        self.select_named_network = QtGui.QComboBox(self.centralwidget)
        self.select_named_network.setGeometry(QtCore.QRect(740, 60, 211, 25))
        self.select_named_network.setObjectName(_fromUtf8("select_named_network"))
        self.ontology_name_label = QtGui.QLabel(self.centralwidget)
        self.ontology_name_label.setGeometry(QtCore.QRect(0, 0, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.ontology_name_label.setFont(font)
        self.ontology_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ontology_name_label.setObjectName(_fromUtf8("ontology_name_label"))
        self.model_name_label = QtGui.QLabel(self.centralwidget)
        self.model_name_label.setGeometry(QtCore.QRect(290, 0, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.model_name_label.setFont(font)
        self.model_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.model_name_label.setObjectName(_fromUtf8("model_name_label"))
        self.save_model_button = QtGui.QPushButton(self.centralwidget)
        self.save_model_button.setGeometry(QtCore.QRect(790, 410, 141, 25))
        self.save_model_button.setObjectName(_fromUtf8("save_model_button"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(750, 40, 131, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.display_topology = QtGui.QGraphicsView(self.centralwidget)
        self.display_topology.setGeometry(QtCore.QRect(50, 40, 491, 361))
        self.display_topology.setObjectName(_fromUtf8("display_topology"))
        self.initialise_system_button = QtGui.QPushButton(self.centralwidget)
        self.initialise_system_button.setGeometry(QtCore.QRect(790, 360, 141, 25))
        self.initialise_system_button.setObjectName(_fromUtf8("initialise_system_button"))
        self.select_group = QtGui.QComboBox(self.centralwidget)
        self.select_group.setGeometry(QtCore.QRect(740, 120, 211, 25))
        self.select_group.setObjectName(_fromUtf8("select_group"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(750, 100, 131, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(750, 170, 151, 17))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.select_single = QtGui.QComboBox(self.centralwidget)
        self.select_single.setGeometry(QtCore.QRect(740, 190, 211, 25))
        self.select_single.setObjectName(_fromUtf8("select_single"))
        self.case_name_label = QtGui.QLabel(self.centralwidget)
        self.case_name_label.setGeometry(QtCore.QRect(630, 0, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.case_name_label.setFont(font)
        self.case_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.case_name_label.setObjectName(_fromUtf8("case_name_label"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1015, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuModel_Factory = QtGui.QMenu(self.menubar)
        self.menuModel_Factory.setObjectName(_fromUtf8("menuModel_Factory"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionInitialise = QtGui.QAction(MainWindow)
        self.actionInitialise.setObjectName(_fromUtf8("actionInitialise"))
        self.menuModel_Factory.addAction(self.actionInitialise)
        self.menubar.addAction(self.menuModel_Factory.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.ontology_name_label.setText(_translate("MainWindow", "TextLabel", None))
        self.model_name_label.setText(_translate("MainWindow", "TextLabel", None))
        self.save_model_button.setText(_translate("MainWindow", "Save file", None))
        self.label.setText(_translate("MainWindow", "Named network", None))
        self.initialise_system_button.setText(_translate("MainWindow", "Initialise system", None))
        self.label_2.setText(_translate("MainWindow", "Select group", None))
        self.label_3.setText(_translate("MainWindow", "Single nodes or arcs", None))
        self.case_name_label.setText(_translate("MainWindow", "TextLabel", None))
        self.menuModel_Factory.setTitle(_translate("MainWindow", "Model Factory", None))
        self.actionInitialise.setText(_translate("MainWindow", "Initialise", None))

