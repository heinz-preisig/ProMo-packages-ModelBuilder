#!/usr/bin/python3
# encoding: utf-8
"""

"""
# __docformat__ = "restructuredtext en"

from PyQt5 import QtGui
from ModelBuilder.Instantiate_equations.Editor.editor_initialise_equations_gui_impl import Ui_Initialise_equations
# from Initialise_system_editor.master_project import Initialization
import sys
import os


cwd = os.getcwd()
sys.path.append(cwd)

if __name__ == '__main__':
  # mode = 'use'
  # mode = 'development ModelFactory'
  # if mode == 'development ModelFactory':
  #   ontology_name = 'Ball_02'
  #   ontology = OntologyContainer(ontology_name)
  #   ontology_location = ontology.onto_path
  #   mod_name = 'ball_fall'
  #   language = 'python'
  #   model_loc = '{}/models/{}'.format(ontology_location, mod_name)
  #   mf = ModelFactory(ontology, mod_name, language, model_loc)
  #   mf.produce_code()
  # else:
  a = QtGui.QApplication(sys.argv)
  a.setWindowIcon(QtGui.QIcon("./Common/icons/otter.png"))
  w = Ui_Initialise_equations()
  w.setWindowTitle('Initialise equations')
  w.show()
  r = a.exec_()
  sys.exit(r)
