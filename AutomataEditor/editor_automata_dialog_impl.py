#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
GUI for automata editor

Automata control the user interface of the ModelComposer
===============================================================================
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL planned -- until further notice for internal Bio4Fuel & MarketPlace use only"
__version__ = "5.04 or later"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# TODO: enabledactions should come from graph-object file
# commes currently from resources.


import os as OS
import shutil  as U
import subprocess

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets

import Common.common_resources as CR
import Common.qt_resources as QR

from Common.graphics_objects import getGraphData
from Common.automata_objects import BUTTONS
from Common.automata_objects import getAutomata
from Common.automata_objects import GRAPH_EDITOR_STATES
from Common.automata_objects import KeyAutomatonEntry
from Common.graphics_objects import PHASES
from Common.ontology_container import OntologyContainer
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from ModelBuilder.AutomataEditor.editor_automata_dialog import Ui_Dialog
from ModelBuilder.ModelComposer.resources import ACTIONS
from ModelBuilder.ModelComposer.resources import M_None
from ModelBuilder.ModelComposer.resources import ModellerCursor

DEBUGG_ME = True

KEY_POSITION = {'state'}

HEADER = ['object', 'left action', 'left: next state', 'right action',
          'right: next state', 'cursor']

JOIN = OS.path.join


class Doc(list):
  def __call__(self, newline):
    self.append(newline + '\n')


class GraphEditorDialogImpl(QtWidgets.QWidget):
  """
   dialogue control for mouse menu design.
   puts up a list box for selecting the states
           and a table for editing the current state
   columns are
   object | mouse left            |  mouse right         | cursor
          | action |  next state  |  action | next state |

  """

  # setting up GUI --------------------------------------------------------------
  def __init__(self):
    super().__init__()
    self.ui = Ui_Dialog()
    self.initialise = True
    self.ui.setupUi(self)
    self.B_cursors = ModellerCursor()
    # self.__setupSignals()
    self.__setupControlLists()
    self.__buttonLogics('start')

    self.current_state = None
    self.current_phase = None
    self.mouse_automaton_entry = None

    self.ui.tableState.setHorizontalHeaderLabels(HEADER)

    self.cursors = ModellerCursor()


    self.ontology_name = CR.getOntologyName(task="task_automata")
    # self.file_resources = DataFileResources(self.ontology_name)

    #
    ontology = OntologyContainer(self.ontology_name)  # DIRECTORIES["ontology_location"] % self.ontology_name)
    self.application_node_types = ontology.node_type_list
    self.application_arcs_types = ontology.arc_type_list
    self.tokens = ontology.tokens

    # self.networks = ontology.list_leave_networks
    self.connection_networks = {}
    self.connection_networks.update(ontology.interconnection_network_dictionary)
    self.connection_networks.update(ontology.intraconnection_network_dictionary)

    # self.NETWORKS, self.TOKENS, self.DATA = GRO.getGraphData(self.networks, self.connection_networks,
    #                                                          self.application_node_types,
    #                                                          self.application_arcs_types, self.tokens,
    #                                                          FILES["graph_resource_file_spec"] % self.ontology_name)


    self.graph_resource_file_spec = FILES["graph_resource_file_spec"] % self.ontology_name
    self.NETWORK, \
    self.TOKENS, \
    self.DATA, \
    self.STATES_colours = getGraphData(ontology.list_leave_networks,
                                       ontology.list_interconnection_networks,
                                       ontology.list_intraconnection_networks,
                                       ontology.list_network_node_objects,
                                       ontology.list_intra_node_objects,
                                       ontology.list_inter_node_objects,
                                       ontology.list_arc_objects,
                                       ontology.tokens,
                                       self.graph_resource_file_spec)

    self.ui.comboPhase.clear()
    self.ui.comboPhase.addItems([M_None] + PHASES)

    active_objects_all_phases = self.DATA.getActiveObjectsRootDecorationState()
    self.mouse_automata, self.key_automata = \
      getAutomata(FILES["automata_file_spec"] % self.ontology_name, active_objects_all_phases)
    print("debugging -- loaded automata")

  # @QtCore.pyqtSignature('QString')
  def on_comboPhase_activated(self, index):
    s = self.ui.comboPhase.currentText()

    self.current_phase = str(s)

    if self.current_phase == M_None:
      return

    self.states = sorted(GRAPH_EDITOR_STATES[self.current_phase])

    self.active_objects = self.DATA.getActiveObjectsRootDecorationState()[self.current_phase]
    self.object_data = self.DATA[self.current_phase]
    # print("active objects", self.active_objects)

    self.mouse_automaton = self.mouse_automata[self.current_phase]
    self.key_automaton = self.key_automata[self.current_phase]

    self.__loadMouseStateSelectList()
    self.__loadKeyTable()

    self.__buttonLogics('edit_automata')

    self.ui.tableState.clearContents()
    self.ui.tableState.setRowCount(0)

  def __setupControlLists(self):
    self.GUI_components = [
            self.ui.comboPhase,  # 0
            #                self.ui.pushConstructGraph, #1
            #                self.ui.pushInstallAutomaton, #2
            self.ui.pushSaveAutomaton,  # 3
            self.ui.pushLaTex,  # 3
            self.ui.listSelectState,  # 4
            self.ui.listStates,  # 5
            self.ui.listActions,  # 6
            self.ui.listCursors,  # 7
            # self.ui.pushAddState, # 8
            # self.ui.pushDeleteState, # 9
            # self.ui.lineEditNewState, # 10
            self.ui.tableState,  # 11
            #
            self.ui.pushAddKey,  # 12
            self.ui.pushDeleteKey,  # 13
            #                self.ui.pushConstructGraph, #14
            self.ui.listActionsForKeyAutomaton,  # 15
            self.ui.listKeysForKeyAutomaton,  # 16
            self.ui.listStatesForKeyAutomaton,  # 17
            self.ui.tableKeyAutomaton,  # 18
            ]

    n_g = len(self.GUI_components)
    self.GUI_control = {
            'start'        : ([0], range(1, n_g)),
            'save'         : ([], []),
            'edit_automata': (range(0, n_g), []),
            }

  #    @QQtCore.pyqtSignature('QModelIndex')
  def on_tableState_cellPressed(self, row, column):
    if DEBUGG_ME: print('', '> selectedMouseAutomatonEntry >')
    what = HEADER[column]
    selected_object = self.active_objects[row]
    self.tableCoordinate = row, column

    self.ui.listStates.clear()
    self.ui.listActions.clear()
    self.ui.listCursors.clear()

    self.selected_object = selected_object
    if column == 0:
      self.button = None
      return

    self.button = what
    # print("what ", what)
    if what in [HEADER[1], HEADER[3]]:
      self.__loadMouseActionTable(selected_object)
    elif what in [HEADER[2], HEADER[4]]:
      self.__loadMouseNextStateSelectList()
    elif what == HEADER[5]:
      self.__loadCursorList()

  def on_listSelectState_itemPressed(self, item):
    state = str(item.text())
    self.__loadStateTable(state)
    self.current_state = state

  def on_listStates_itemPressed(self, item):
    s = self.button
    object_str = str(self.selected_object)
    assert s in [HEADER[2], HEADER[4]]

    state = str(item.text())

    if state == str(self.current_state): state = M_None
    row, column = self.tableCoordinate

    self.ui.tableState.setItem(row, column, self.__makeTextItem(state))

    entry = self.mouse_automaton[self.current_state][object_str]
    if s == HEADER[2]:
      entry["left"]["state"] = state
    else:
      entry["right"]["state"] = state

  def on_listActions_itemPressed(self, item):
    s = self.button
    object_str = str(self.selected_object)
    assert s in [HEADER[1], HEADER[3]]

    action = str(item.text())

    row, column = self.tableCoordinate
    if DEBUGG_ME: print('> modifyActionEntry>', action)

    self.ui.tableState.setItem(row, column, self.__makeTextItem(action))
    entry = self.mouse_automaton[self.current_state][object_str]

    if s == HEADER[1]:
      entry["left"]["output"] = action
    else:
      entry["right"]["output"] = action

  def on_listCursors_itemPressed(self, item):
    object_str = str(self.selected_object)

    cursor = str(item.text())
    row, column = self.tableCoordinate
    if DEBUGG_ME: print('> modifyCursorEntry>', cursor)

    item_ = self.__makeTextItem(cursor)
    item_.setIcon(self.cursors.getIcon(cursor))
    item_.setText(cursor)
    self.ui.tableState.setItem(row, column, item_)

    entry = self.mouse_automaton[self.current_state][object_str]
    entry["cursor"] = cursor

  # key automaton ---------------------------------------------------------------

  def on_tableKeyAutomaton_cellPressed(self, row, column):
    item = self.ui.tableKeyAutomaton.item(row, 0)
    key = str(item.text())
    self.current_key = key
    self.current_key_state = self.key_automaton[key]["state"]
    self.current_key_action = self.key_automaton[key]["output"]

    self.ui.listKeysForKeyAutomaton.clear()
    self.ui.listStatesForKeyAutomaton.clear()
    self.ui.listActionsForKeyAutomaton.clear()
    if column in [0]:  # action chosen
      if DEBUGG_ME: print('', ' select key')
      self.__loadKeySelectList()
    elif column in [1]:
      if DEBUGG_ME: print('', ' select state')
      self.__loadKeyStateSelectList()
    elif column in [2]:
      if DEBUGG_ME: print('', ' select action')
      self.__loadKeyActionSelectList()
    else:
      print('', ' error')

  def on_listStatesForKeyAutomaton_itemPressed(self, item):
    state = str(item.text())
    self.current_key_state = state
    self.updateKeyAutomaton('state', self.current_key)
    self.__loadKeyTable()

  def on_listKeysForKeyAutomaton_itemPressed(self, item):
    key = str(item.text())
    self.updateKeyAutomaton('key', key)

  def on_listActionsForKeyAutomaton_itemPressed(self, item):
    action = str(item.text())
    self.current_key_action = action
    self.updateKeyAutomaton('action', self.current_key)

  def on_pushAddKey_pressed(self):
    self.key_automaton.addEntry()
    self.__loadKeyTable()

  def on_pushDeleteKey_pressed(self):
    row = self.ui.tableKeyAutomaton.currentRow()
    key = str(self.ui.tableKeyAutomaton.item(row, 0).text())
    del self.key_automaton[key]
    self.__loadKeyTable()

  def on_pushSaveAutomaton_pressed(self):
    #
    vars = {
            'mouse': self.mouse_automata,
            'key'  : self.key_automata
            }

    automata_working_file_spec = FILES["automata_file_spec"] % self.ontology_name
    old, new, next_path = CR.saveBackupFile(automata_working_file_spec)
    print("saved to backup file ", new)

    CR.putData(vars, automata_working_file_spec, indent=2)

    self.__buttonLogics('save')

  def on_pushLaTex_pressed(self):
    self.__writeLaTexFileTable()



  # internal methods from old version ---------------------------------------------------

  def updateKeyAutomaton(self, what, key):  # , state, action):  # called by GUI

    state = self.current_key_state
    action = self.current_key_action

    if DEBUGG_ME: print('updateKeyAutomaton', '%s, %s, %s, %s' % (what, key, state, action))
    if what == 'key':
      old_key = self.current_key  # getKeyAutomatonKey((state, action))
      del self.key_automaton[old_key]
      self.key_automaton[key] = KeyAutomatonEntry(state, action)

    elif what in ['state', 'action']:
      self.key_automaton[self.current_key] = KeyAutomatonEntry(state, action)
    else:
      print("updateKeyAutomaton no such element :", what)

    self.__loadKeyTable()

  # internal methods ----------------------------------------------------------

  def __buttonLogics(self, action):
    keep = self.initialise
    list = self.GUI_components
    en = self.GUI_control

    e, d = en[action]
    for i in list:
      if list.index(i) in e:
        i.setEnabled(True)
      elif list.index(i) in d:
        i.setEnabled(False)

    self.initialise = keep

  def __loadMouseStateSelectList(self):
    self.ui.listSelectState.clear()
    self.ui.listSelectState.addItems(self.states)

  def __loadMouseNextStateSelectList(self):
    self.ui.listStates.clear()
    self.ui.listStates.addItems([M_None] + self.states)

  def __loadKeyTable(self):

    self.ui.listKeysForKeyAutomaton.clear()
    self.ui.listStatesForKeyAutomaton.clear()
    self.ui.listActionsForKeyAutomaton.clear()
    self.ui.tableKeyAutomaton.clearContents()

    keylist = sorted(self.key_automaton.keys())
    keylist.sort()
    n_setkeys = len(keylist)
    self.ui.tableKeyAutomaton.setRowCount(n_setkeys)
    n_rows = 0
    for key in keylist:
      # print("__loadTable :", self.key_automaton[key])
      state = self.key_automaton[key]["state"]
      action = self.key_automaton[key]["output"]
      self.ui.tableKeyAutomaton.setItem(n_rows, 0, self.__makeTextItem(key))
      self.ui.tableKeyAutomaton.setItem(n_rows, 1, self.__makeTextItem(state))
      self.ui.tableKeyAutomaton.setItem(n_rows, 2, self.__makeTextItem(action))
      n_rows = n_rows + 1

  def __makeTextItem(self, s):
    return QtWidgets.QTableWidgetItem(s)

  def __loadStateTable(self, editor_state):
    t = self.ui.tableState
    n_row = len(self.active_objects)
    t.setRowCount(n_row)

    for row in range(n_row):
      obj_str = str(self.active_objects[row])
      t.setItem(row, 0, self.__makeTextItem(obj_str))
      possible_actions = self.__getActions(self.active_objects[row])

      for button in BUTTONS:
        next_state = self.mouse_automaton[editor_state][obj_str][button]["state"]
        action = self.mouse_automaton[editor_state][obj_str][button]["output"]
        if button == 'left':
          t.setItem(row, 1, self.__makeTextItem(action))
          t.setItem(row, 2, self.__makeTextItem(next_state))
        elif button == 'right':
          t.setItem(row, 3, self.__makeTextItem(action))
          t.setItem(row, 4, self.__makeTextItem(next_state))

      cursor = self.mouse_automaton[editor_state][obj_str]["cursor"]
      item = self.__makeTextItem(cursor)
      item.setIcon(self.cursors.getIcon(cursor))
      item.setText(cursor)
      self.ui.tableState.setItem(row, 5, item)

      t.resizeColumnsToContents()

  def __loadKeySelectList(self):
    self.ui.listKeysForKeyAutomaton.clear()
    for k in QR.KEYS:
      key = QR.KEYS[k]
      self.ui.listKeysForKeyAutomaton.addItem(key)

  def __loadKeyStateSelectList(self):
    self.ui.listStatesForKeyAutomaton.clear()
    self.ui.listStatesForKeyAutomaton.addItem(M_None)
    self.ui.listStatesForKeyAutomaton.addItems(GRAPH_EDITOR_STATES[self.current_phase])

  def __loadKeyActionSelectList(self):
    self.ui.listActionsForKeyAutomaton.clear()
    self.ui.listActionsForKeyAutomaton.addItems([M_None] + ACTIONS[self.current_phase])

  def __loadCursorList(self):
    # cursor
    for i in self.cursors:
      item = QtWidgets.QListWidgetItem()
      item.setIcon(self.cursors.getIcon(i))
      item.setText(i)
      self.ui.listCursors.addItem(item)
      if DEBUGG_ME: print('', 'item ', i)
      # print("setup cursor", i)
    self.ui.listCursors.sortItems()

  def __loadMouseActionTable(self, obj):
    self.ui.listActions.clear()
    # #print("__loadActionTable", obj)
    actions = self.__getActions(obj)
    self.ui.listActions.addItems([M_None] + actions)

  def __getActions(self, obj):
    actions_all = []
    for root_object in self.DATA[self.current_phase]:
      if root_object == obj[0]:
        for decoration in self.DATA[self.current_phase][root_object]:
          if decoration == obj[1]:
            for application in self.DATA[self.current_phase][root_object][decoration]:
              for state in self.DATA[self.current_phase][root_object][decoration][application]:
                action = self.DATA[self.current_phase][root_object][decoration][application][state]["action"]
                actions_all.extend(action)
    actions = sorted(set(actions_all))
    return actions

  def __setMouseIndicator(self, cursor):
    if cursor != 'leave':
      self.pixmapCursor.setPixmap(cursor.bitmap())
    else:
      self.pixmapCursor.setPixmap(self.image0)

  def __writeLaTexFileTable(self):

    source = FILES["latex_automaton_resource"] % self.ontology_name
    latex_automaton_location = FILES["latex_automaton"] % self.ontology_name
    U.copyfile(source, latex_automaton_location)

    for phase in sorted(self.mouse_automata):
      # LATEX_DOC_FILE = self.file_resources["automata_LaTex_file_name"] + "_" + phase + ".tex"
      LATEX_DOC_FILE = FILES["latex_automaton_phase_file_name"] % (self.ontology_name, phase)
      f = open(LATEX_DOC_FILE, 'w')
      auto = self.mouse_automata[phase]
      lines = Doc()
      # header
      lines(r'\def\state#1{#1}')
      lines(r'\def\object#1{#1}')
      lines(r'\def\cursor#1{#1}')
      lines(r'\def\leftnextstate#1{#1}')
      lines(r'\def\leftaction#1{#1}')
      lines(r'\def\rightnextstate#1{#1}')
      lines(r'\def\rightaction#1{#1}')
      lines(r'\section{%s}' % phase.replace(r'_', r'\_'))
      for s in sorted(auto):
        lines(r'\subsection{%s}' % s.replace(r'_', r'\_'))
        lines(r'\begin{tabular}{|l|l|l|l|}')
        for o in sorted(auto[s]):
          curs = auto[s][o]['cursor']
          left_n_state = auto[s][o]["left"]["state"]
          left_action = auto[s][o]["left"]["output"]
          right_n_state = auto[s][o]["right"]["state"]
          right_action = auto[s][o]["right"]["output"]
          arg = []
          for i in [o, curs, left_n_state, left_action, right_n_state,
                    right_action]:
            a = i.replace(r'&', r'\&')
            arg.append(a.replace(r'_', r'\_'))
          lines(
                  r"\object{%s} &\cursor{%s} &(\leftnextstate{%s}, \leftaction{%s}) &("
                  r"\rightnextstate{%s}, \rightaction{%s})\\" \
                  % (arg[0], arg[1], arg[2], arg[3], arg[4], arg[5]))
        lines(r'\end{tabular}')
        lines(r'\\')

      for i in lines:
        f.write(i)

      f.close()

      f_name = FILES["latex_shell_automata_doc_command"] % self.ontology_name
      latex_location = DIRECTORIES["latex_location"] % self.ontology_name
      args = ['sh', f_name, latex_location]  # ontology_location + '/']
      print('ARGS: ', args)
      make_it = subprocess.Popen(
              args,
              # start_new_session=True,
              # stdout=subprocess.PIPE,
              # stderr=subprocess.PIPE
              )
      out, error = make_it.communicate()
