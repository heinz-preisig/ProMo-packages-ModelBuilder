#!/usr/bin/python3.5
# encoding: utf-8
# !/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 APP for editing automaton used in ModelComposer
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2009. 04. 17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

from PyQt5 import QtGui

from ModelBuilder.AutomataEditor import GraphEditorDialogImpl

cwd = os.getcwd()
sys.path.append(cwd)

a = QtGui.QApplication(sys.argv)

a.setWindowIcon(QtGui.QIcon("./Common/icons/automaton.svg"))
# k = ModelAgents()

w = GraphEditorDialogImpl()
# msg_box.connectMe(k)
w.show()
a.exec_()
