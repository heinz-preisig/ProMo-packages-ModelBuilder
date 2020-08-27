# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modeller_mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1953, 983)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(100, 0))
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks|QtWidgets.QMainWindow.ForceTabbedDocks|QtWidgets.QMainWindow.VerticalTabs)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 1111, 38))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 4, 0, 4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelOntology = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelOntology.sizePolicy().hasHeightForWidth())
        self.labelOntology.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.labelOntology.setFont(font)
        self.labelOntology.setObjectName("labelOntology")
        self.horizontalLayout.addWidget(self.labelOntology)
        self.labelModel = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelModel.sizePolicy().hasHeightForWidth())
        self.labelModel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.labelModel.setFont(font)
        self.labelModel.setObjectName("labelModel")
        self.horizontalLayout.addWidget(self.labelModel)
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(10, 60, 1121, 880))
        self.graphicsView.setMinimumSize(QtCore.QSize(750, 0))
        self.graphicsView.setObjectName("graphicsView")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidgetMain = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetMain.sizePolicy().hasHeightForWidth())
        self.dockWidgetMain.setSizePolicy(sizePolicy)
        self.dockWidgetMain.setMinimumSize(QtCore.QSize(730, 346))
        self.dockWidgetMain.setFloating(False)
        self.dockWidgetMain.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.dockWidgetMain.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dockWidgetMain.setObjectName("dockWidgetMain")
        self.dockWidgetContents = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setMinimumSize(QtCore.QSize(730, 0))
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.groupBox = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 451, 201))
        self.groupBox.setObjectName("groupBox")
        self.formLayoutWidget = QtWidgets.QWidget(self.groupBox)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 40, 141, 151))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formKeyAutomaton = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formKeyAutomaton.setContentsMargins(0, 0, 0, 0)
        self.formKeyAutomaton.setObjectName("formKeyAutomaton")
        self.layoutWidget1 = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget1.setGeometry(QtCore.QRect(200, 40, 250, 92))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.labelObject = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelObject.sizePolicy().hasHeightForWidth())
        self.labelObject.setSizePolicy(sizePolicy)
        self.labelObject.setMinimumSize(QtCore.QSize(120, 20))
        self.labelObject.setAlignment(QtCore.Qt.AlignCenter)
        self.labelObject.setObjectName("labelObject")
        self.horizontalLayout_5.addWidget(self.labelObject)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.pixmapCursor = QtWidgets.QLabel(self.layoutWidget1)
        self.pixmapCursor.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pixmapCursor.sizePolicy().hasHeightForWidth())
        self.pixmapCursor.setSizePolicy(sizePolicy)
        self.pixmapCursor.setMinimumSize(QtCore.QSize(32, 32))
        self.pixmapCursor.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.pixmapCursor.setText("")
        self.pixmapCursor.setTextFormat(QtCore.Qt.PlainText)
        self.pixmapCursor.setScaledContents(True)
        self.pixmapCursor.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.pixmapCursor.setObjectName("pixmapCursor")
        self.horizontalLayout_3.addWidget(self.pixmapCursor)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelLeft = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelLeft.sizePolicy().hasHeightForWidth())
        self.labelLeft.setSizePolicy(sizePolicy)
        self.labelLeft.setMinimumSize(QtCore.QSize(100, 20))
        self.labelLeft.setAlignment(QtCore.Qt.AlignCenter)
        self.labelLeft.setObjectName("labelLeft")
        self.horizontalLayout_2.addWidget(self.labelLeft)
        self.labelRight = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelRight.sizePolicy().hasHeightForWidth())
        self.labelRight.setSizePolicy(sizePolicy)
        self.labelRight.setMinimumSize(QtCore.QSize(100, 20))
        self.labelRight.setAlignment(QtCore.Qt.AlignCenter)
        self.labelRight.setObjectName("labelRight")
        self.horizontalLayout_2.addWidget(self.labelRight)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.groupBoxMainControl = QtWidgets.QGroupBox(self.dockWidgetContents)
        self.groupBoxMainControl.setGeometry(QtCore.QRect(510, 10, 211, 141))
        self.groupBoxMainControl.setObjectName("groupBoxMainControl")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.groupBoxMainControl)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 20, 92, 111))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushSave = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.pushSave.setEnabled(True)
        self.pushSave.setMinimumSize(QtCore.QSize(0, 30))
        self.pushSave.setObjectName("pushSave")
        self.verticalLayout_3.addWidget(self.pushSave)
        self.pushSaveAs = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.pushSaveAs.setEnabled(True)
        self.pushSaveAs.setMinimumSize(QtCore.QSize(0, 30))
        self.pushSaveAs.setObjectName("pushSaveAs")
        self.verticalLayout_3.addWidget(self.pushSaveAs)
        self.pushExit = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        self.pushExit.setMinimumSize(QtCore.QSize(0, 30))
        self.pushExit.setObjectName("pushExit")
        self.verticalLayout_3.addWidget(self.pushExit)
        self.layoutWidget_2 = QtWidgets.QWidget(self.dockWidgetContents)
        self.layoutWidget_2.setGeometry(QtCore.QRect(220, 220, 501, 31))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.formLayout_3 = QtWidgets.QFormLayout(self.layoutWidget_2)
        self.formLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.formLayout_3.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.formLayout_3.setObjectName("formLayout_3")
        self.pushSchnipsel = QtWidgets.QPushButton(self.layoutWidget_2)
        self.pushSchnipsel.setObjectName("pushSchnipsel")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.pushSchnipsel)
        self.labelSchnipsel = QtWidgets.QLabel(self.layoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelSchnipsel.sizePolicy().hasHeightForWidth())
        self.labelSchnipsel.setSizePolicy(sizePolicy)
        self.labelSchnipsel.setText("")
        self.labelSchnipsel.setObjectName("labelSchnipsel")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.labelSchnipsel)
        self.widgetInteraction = QtWidgets.QWidget(self.dockWidgetContents)
        self.widgetInteraction.setGeometry(QtCore.QRect(0, 280, 721, 641))
        self.widgetInteraction.setObjectName("widgetInteraction")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.widgetInteraction)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 230, 701, 221))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.layoutInteractiveWidgetBottom = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.layoutInteractiveWidgetBottom.setContentsMargins(0, 0, 0, 0)
        self.layoutInteractiveWidgetBottom.setObjectName("layoutInteractiveWidgetBottom")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.widgetInteraction)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(20, 10, 211, 221))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.layoutInteractiveWidgetTop = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.layoutInteractiveWidgetTop.setContentsMargins(0, 0, 0, 0)
        self.layoutInteractiveWidgetTop.setObjectName("layoutInteractiveWidgetTop")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.widgetInteraction)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(240, 10, 401, 221))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.layoutNetworks = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.layoutNetworks.setContentsMargins(0, 0, 0, 0)
        self.layoutNetworks.setObjectName("layoutNetworks")
        self.groupBoxNamedNetworks = QtWidgets.QGroupBox(self.widgetInteraction)
        self.groupBoxNamedNetworks.setGeometry(QtCore.QRect(650, 19, 71, 171))
        self.groupBoxNamedNetworks.setObjectName("groupBoxNamedNetworks")
        self.pushAddNamedNetwork = QtWidgets.QPushButton(self.groupBoxNamedNetworks)
        self.pushAddNamedNetwork.setGeometry(QtCore.QRect(0, 30, 61, 29))
        self.pushAddNamedNetwork.setObjectName("pushAddNamedNetwork")
        self.pushEditNamedNetwork = QtWidgets.QPushButton(self.groupBoxNamedNetworks)
        self.pushEditNamedNetwork.setGeometry(QtCore.QRect(0, 60, 61, 29))
        self.pushEditNamedNetwork.setObjectName("pushEditNamedNetwork")
        self.pushDeleteNamedNetwork = QtWidgets.QPushButton(self.groupBoxNamedNetworks)
        self.pushDeleteNamedNetwork.setGeometry(QtCore.QRect(0, 90, 61, 29))
        self.pushDeleteNamedNetwork.setObjectName("pushDeleteNamedNetwork")
        self.groupNamed_NetworkColour = QtWidgets.QGroupBox(self.groupBoxNamedNetworks)
        self.groupNamed_NetworkColour.setGeometry(QtCore.QRect(10, 120, 51, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(248, 248, 248))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(121, 121, 121))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(161, 161, 161))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(248, 248, 248))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(248, 248, 248))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(121, 121, 121))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(161, 161, 161))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(248, 248, 248))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(121, 121, 121))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(248, 248, 248))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(121, 121, 121))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(161, 161, 161))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(121, 121, 121))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(121, 121, 121))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(242, 242, 242))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.groupNamed_NetworkColour.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.groupNamed_NetworkColour.setFont(font)
        self.groupNamed_NetworkColour.setObjectName("groupNamed_NetworkColour")
        self.toolNamed_NetworkColour = QtWidgets.QToolButton(self.groupNamed_NetworkColour)
        self.toolNamed_NetworkColour.setGeometry(QtCore.QRect(10, 20, 31, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.toolNamed_NetworkColour.setFont(font)
        self.toolNamed_NetworkColour.setText("")
        self.toolNamed_NetworkColour.setAutoRaise(False)
        self.toolNamed_NetworkColour.setObjectName("toolNamed_NetworkColour")
        self.layoutWidget2 = QtWidgets.QWidget(self.dockWidgetContents)
        self.layoutWidget2.setGeometry(QtCore.QRect(20, 220, 171, 31))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.layoutEditorPhase = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.layoutEditorPhase.setContentsMargins(0, 0, 0, 0)
        self.layoutEditorPhase.setObjectName("layoutEditorPhase")
        self.comboEditorPhase = QtWidgets.QComboBox(self.layoutWidget2)
        self.comboEditorPhase.setObjectName("comboEditorPhase")
        self.layoutEditorPhase.addWidget(self.comboEditorPhase)
        self.textStatus = QtWidgets.QPlainTextEdit(self.dockWidgetContents)
        self.textStatus.setGeometry(QtCore.QRect(220, 150, 501, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
        brush = QtGui.QBrush(QtGui.QColor(166, 162, 159))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0, 128))
        brush.setStyle(QtCore.Qt.NoBrush)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
        self.textStatus.setPalette(palette)
        self.textStatus.setObjectName("textStatus")
        self.dockWidgetMain.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidgetMain)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setOrientation(QtCore.Qt.Vertical)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)
        self.dockWidgetLogger = QtWidgets.QDockWidget(MainWindow)
        self.dockWidgetLogger.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea)
        self.dockWidgetLogger.setObjectName("dockWidgetLogger")
        self.dockWidgetContents_2 = QtWidgets.QWidget()
        self.dockWidgetContents_2.setObjectName("dockWidgetContents_2")
        self.dockWidgetLogger.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockWidgetLogger)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Process Modeller"))
        self.labelOntology.setText(_translate("MainWindow", "ontology"))
        self.labelModel.setText(_translate("MainWindow", "model      "))
        self.dockWidgetMain.setWindowTitle(_translate("MainWindow", "main"))
        self.groupBox.setTitle(_translate("MainWindow", "Navigation"))
        self.labelObject.setText(_translate("MainWindow", "object"))
        self.labelLeft.setText(_translate("MainWindow", "left"))
        self.labelRight.setText(_translate("MainWindow", "right"))
        self.groupBoxMainControl.setTitle(_translate("MainWindow", "controls"))
        self.pushSave.setText(_translate("MainWindow", "save"))
        self.pushSaveAs.setText(_translate("MainWindow", "save as"))
        self.pushExit.setText(_translate("MainWindow", "exit"))
        self.pushSchnipsel.setText(_translate("MainWindow", "schnipsel"))
        self.groupBoxNamedNetworks.setTitle(_translate("MainWindow", "edit"))
        self.pushAddNamedNetwork.setText(_translate("MainWindow", "add"))
        self.pushEditNamedNetwork.setText(_translate("MainWindow", "edit"))
        self.pushDeleteNamedNetwork.setText(_translate("MainWindow", "delete"))
        self.groupNamed_NetworkColour.setTitle(_translate("MainWindow", "colour"))
        self.dockWidgetLogger.setWindowTitle(_translate("MainWindow", "logger"))
