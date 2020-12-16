# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor_initialise_system_gui.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1015, 537)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.message_box = QtWidgets.QTextBrowser(self.centralwidget)
        self.message_box.setGeometry(QtCore.QRect(50, 410, 491, 61))
        self.message_box.setObjectName("message_box")
        self.select_starting_variables = QtWidgets.QComboBox(self.centralwidget)
        self.select_starting_variables.setGeometry(QtCore.QRect(740, 60, 211, 25))
        self.select_starting_variables.setObjectName("select_starting_variables")
        self.ontology_name_label = QtWidgets.QLabel(self.centralwidget)
        self.ontology_name_label.setGeometry(QtCore.QRect(0, 0, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.ontology_name_label.setFont(font)
        self.ontology_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ontology_name_label.setObjectName("ontology_name_label")
        self.model_name_label = QtWidgets.QLabel(self.centralwidget)
        self.model_name_label.setGeometry(QtCore.QRect(280, 0, 301, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.model_name_label.setFont(font)
        self.model_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.model_name_label.setObjectName("model_name_label")
        self.save_model_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_model_button.setGeometry(QtCore.QRect(790, 410, 141, 25))
        self.save_model_button.setObjectName("save_model_button")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(750, 40, 131, 17))
        self.label.setObjectName("label")
        self.display_topology = QtWidgets.QGraphicsView(self.centralwidget)
        self.display_topology.setGeometry(QtCore.QRect(50, 40, 491, 361))
        self.display_topology.setObjectName("display_topology")
        self.initialise_system_button = QtWidgets.QPushButton(self.centralwidget)
        self.initialise_system_button.setGeometry(QtCore.QRect(790, 300, 141, 25))
        self.initialise_system_button.setObjectName("initialise_system_button")
        self.build_equation_set_button = QtWidgets.QPushButton(self.centralwidget)
        self.build_equation_set_button.setGeometry(QtCore.QRect(790, 180, 141, 25))
        self.build_equation_set_button.setObjectName("build_equation_set_button")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1015, 22))
        self.menubar.setObjectName("menubar")
        self.menuModel_Factory = QtWidgets.QMenu(self.menubar)
        self.menuModel_Factory.setObjectName("menuModel_Factory")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionInitialise = QtWidgets.QAction(MainWindow)
        self.actionInitialise.setObjectName("actionInitialise")
        self.menuModel_Factory.addAction(self.actionInitialise)
        self.menubar.addAction(self.menuModel_Factory.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ontology_name_label.setText(_translate("MainWindow", "TextLabel"))
        self.model_name_label.setText(_translate("MainWindow", "TextLabel"))
        self.save_model_button.setText(_translate("MainWindow", "Save file"))
        self.label.setText(_translate("MainWindow", "Starting points"))
        self.initialise_system_button.setText(_translate("MainWindow", "Initialise system"))
        self.build_equation_set_button.setText(_translate("MainWindow", "Build equation set"))
        self.menuModel_Factory.setTitle(_translate("MainWindow", "Model Factory"))
        self.actionInitialise.setText(_translate("MainWindow", "Initialise"))
