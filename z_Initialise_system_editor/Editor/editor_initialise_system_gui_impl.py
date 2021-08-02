import copy
import itertools
from os import mkdir
from os import path

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets

from Common.common_resources import askForCasefileGivenLocation as afc
from Common.common_resources import askForModelFileGivenOntologyLocation as afm
from Common.common_resources import getData
from Common.common_resources import getOntologyName
from Common.common_resources import putData
from Common.ontology_container import OntologyContainer
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILE_NAMES
from Common.resource_initialisation import FILES
from ModelBuilder.z_Initialise_system_editor.Editor.editor_initialise_system_gui import Ui_MainWindow
from ModelBuilder.z_Initialise_system_editor.Editor.object_initializer_gui import Ui_table_initilizer
from ModelBuilder.z_Initialise_system_editor.master_project import Initialization



# FOLDERS = ['variables', 'model_json', 'equations']


class Ui_Initialise_system(QtWidgets.QMainWindow):
  def __init__(self):
    QtWidgets.QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.ontology_name = getOntologyName()
    self.ontology = OntologyContainer(self.ontology_name)
    self.ontology_location = self.ontology.ontology_location
    models_file = DIRECTORIES["model_library_location"]%self.ontology_name
    self.mod_name = afm(models_file)[0]

    message = '<b>Set up</b> <br />Ontology: {}<br />Model: {}'
    display = message.format(self.ontology_name, self.mod_name)
    self.ui.message_box.setText(display)

    self.model_loc = DIRECTORIES["model_location"]%(self.ontology_name,
                                                    self.mod_name)
    self.ui.ontology_name_label.setText('{}'.format(self.ontology_name))
    self.ui.model_name_label.setText('{}'.format(self.mod_name))

    self.variable_file = FILES["variables_file"]%self.ontology_name
    self.equation_file = FILES["equations_file"]%self.ontology_name
    self.typed_token_file = FILES["typed_token_file"]%self.ontology_name
    self.model_file = FILES["model_file"]%(self.ontology_name, self.mod_name)

    self.cases_location = DIRECTORIES["cases_location"]%(self.ontology_name,
                                                         self.mod_name)
    self.check_for_directory(self.cases_location)
    self.case_name, new_case = afc(self.cases_location)

    # print(self.case_name)
    self.case_location = DIRECTORIES["specific_case"]%(self.ontology_name,
                                                       self.mod_name,
                                                       self.case_name)
    self.already_exist_case = self.check_for_directory(self.case_location)

    self.initialized_objects = []
    self.state_variables = None
    self.table_initiliser = None
    self.fill_starting_points()

  def check_for_directory(self, loc):
    if not path.exists(loc):
      mkdir(loc)
      return False
    else:
      # DIR ALREADY EXISTS
      return True
    # return

  def fill_starting_points(self):
    vars_dict = self.ontology.variables #getData(self.variable_file)
    states = []
    for var_ID in vars_dict:
      if vars_dict[var_ID]["type"] == 'state':
        states.append(var_ID)
    combos = []
    for i in range(len(states)):
      states_combos = itertools.combinations(states, i + 1)
      for state_alt in states_combos:
        str_rep = ', '.join(str(state_alt))
        combos.append(str(str_rep))

    self.ui.select_starting_variables.clear()
    self.ui.select_starting_variables.addItems(combos)

  @QtCore.pyqtSlot(str)
  def on_select_starting_variables_activated(self, vars):
    vars_alts = vars.split(', ')

    self.state_variables = vars_alts
    self.initialization = Initialization(self.model_file,
                                         self.equation_file,
                                         self.variable_file,
                                         self.typed_token_file,
                                         self.state_variables)

    self.ui.message_box.setText('State variables: {}\nInitialization initialized!'.format(vars_alts))

  def on_build_equation_set_button_pressed(self):
    if self.state_variables:
      message = self.initialization.equationSetBuilder()
      eq_order = str(self.initialization.eq_order)
      print(self.initialization.eq_order)
      print(self.initialization.states)
      self.initialization.addVariablesAndStates()
      self.ui.message_box.setText('{}\nOrder:\n{}'.format(message, eq_order))
    else:
      self.ui.message_box.setText('Have not selected state variables')
      return

  def on_initialise_system_button_pressed(self):
    self.table_initiliser = Table_widget(self.initialization, self)
    self.table_initiliser.completed.connect(self.finished_edit_table)
    self.table_initiliser.show()

  def write_equation_state_file(self, file_loc):
    out_dict = {}
    out_dict['calculation_order'] = self.initialization.eq_order
    out_dict['states'] = self.initialization.states
    out_dict['vars'] = self.initialization.vars_used_const
    outfile = path.join(file_loc, FILE_NAMES["calculation_sequence"])
    putData(out_dict, outfile)

  def finished_edit_table(self, what):
    pass

  def on_save_model_button_pressed(self):
    print("Saved case to location: {}".format(self.case_location))
    self.write_equation_state_file(self.case_location)
    self.initialization.writeToFile(self.case_location)

  def closeEvent(self, event):
    if self.table_initiliser:
      self.table_initiliser.closeEvent(event)
    self.deleteLater()
    return


class Table_widget(QtWidgets.QWidget):
  completed = QtCore.pyqtSignal(str)

  def __init__(self, initialise_system, mother):
    QtWidgets.QWidget.__init__(self)
    self.mother = mother
    self.ui = Ui_table_initilizer()
    self.system = initialise_system
    self.ui.setupUi(self)
    self.tw = self.ui.tableWidget
    self.setup()
    self.ui.tableWidget.itemChanged.connect(self.setValue)

  def setup(self):
    self.build_unit_list()
    # print(self.selector_list)
    self.fill_combo_selector(self.selector_list)

  def build_unit_list(self):

    self.selector_list = []
    self.selector_dict = {}
    # Groups
    group_str = 'Group nodes: {}'
    for label, group in self.system.groupDict.items():
      str = group_str.format(label)
      self.selector_dict[str] = {}
      self.selector_dict[str]['dict'] = group
      self.selector_dict[str]['label'] = label
      self.selector_dict[str]['piece'] = 'node'
      self.selector_list.append(group_str.format(label))

    # Single nodes
    node_str = 'Single node: {}'
    for label, node in self.system.singleDict.items():
      str = node_str.format(label)
      self.selector_dict[str] = {}
      self.selector_dict[str]['dict'] = node
      self.selector_dict[str]['label'] = label
      self.selector_dict[str]['piece'] = 'node'
      self.selector_list.append(str)

    res_str = 'Reservoir: {}'
    for label, res in self.system.reservoirDict.items():
      str = res_str.format(label)
      self.selector_dict[str] = {}
      self.selector_dict[str]['dict'] = res
      self.selector_dict[str]['label'] = label
      self.selector_dict[str]['piece'] = 'node'
      self.selector_list.append(str)

    arc_str = 'Single arc: {}'
    g_arc_str = 'Group arcs: {}'
    g_arc_b_n_str = 'Group arcs between nodes: {}'

    for label, thing in self.system.singleArcs.items():
      str = arc_str.format(label)
      self.selector_dict[str] = {}
      self.selector_dict[str]['dict'] = thing
      self.selector_dict[str]['label'] = label
      self.selector_dict[str]['piece'] = 'arc'
      self.selector_list.append(str)

    for label, thing in self.system.groupArcs.items():
      str = g_arc_str.format(label)
      self.selector_dict[str] = {}
      self.selector_dict[str]['dict'] = thing
      self.selector_dict[str]['label'] = label
      self.selector_dict[str]['piece'] = 'arc'
      self.selector_list.append(g_arc_str.format(label))

    for label, thing in self.system.groupArcsBetweenNode.items():
      str = g_arc_b_n_str.format(label)
      self.selector_dict[str] = {}
      self.selector_dict[str]['dict'] = thing
      self.selector_dict[str]['label'] = label
      self.selector_dict[str]['piece'] = 'arc'
      self.selector_list.append(str)

    var_str = 'Global variables'
    # for label, thing in self.system.constNotNodeOrArc.items():
    str = var_str.format()
    self.selector_dict[str] = {}
    self.selector_dict[str]['dict'] = self.system.constNotNodeOrArc
    self.selector_dict[str]['label'] = str
    self.selector_dict[str]['piece'] = 'global_variable'
    self.selector_list.append(str)

  # @QtCore.pyqtSignature('QString')
  def on_object_selecter_box_activated(self, input_str):

    self.fill_table(input_str)
    self.ui.message_browser.setText('HELLO:\nPicked: {}'.format(input_str))

  def fill_table(self, input_str):
    self.curr_input_str = copy.copy(input_str)
    self.obj = self.selector_dict[input_str]

    self.ui.tableWidget.clear()
    self.ui.tableWidget.setRowCount(0)
    self.ui.tableWidget.setColumnCount(4)

    item = QtGui.QTableWidgetItem()
    item.setText("Variable:")
    self.ui.tableWidget.setHorizontalHeaderItem(0, item)

    item = QtGui.QTableWidgetItem()
    item.setText("Documentation:")
    self.ui.tableWidget.setHorizontalHeaderItem(1, item)

    item = QtGui.QTableWidgetItem()
    item.setText("Units:")
    self.ui.tableWidget.setHorizontalHeaderItem(2, item)

    item = QtGui.QTableWidgetItem()
    item.setText("Value:")
    self.ui.tableWidget.setHorizontalHeaderItem(3, item)

    if self.obj['piece'] == "global_variable":
      for var, item in self.obj['dict'].items():
        rowPosition = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(rowPosition)
        item_symbol = QtGui.QTableWidgetItem()
        item_symbol.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item_symbol.setText(var)
        self.ui.tableWidget.setItem(rowPosition, 0, item_symbol)

        item_doc = QtGui.QTableWidgetItem()
        item_doc.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item_doc.setText(self.system.variables[var]['doc'])
        self.ui.tableWidget.setItem(rowPosition, 1, item_doc)

        item_units = QtGui.QTableWidgetItem()
        item_units.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        unit_str = self.system.variables[var]['units_latex']
        item_units.setText(unit_str)
        self.ui.tableWidget.setItem(rowPosition, 2, item_units)

        item_value = QtGui.QTableWidgetItem()
        item_value.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        item_value.setText(str(item['value']))
        self.ui.tableWidget.setItem(rowPosition, 3, item_value)

      return

    if self.obj['piece'] == 'node' or (self.obj['piece'] == 'arc' and self.obj['label'] in self.system.singleArcs):
      for label, other in self.obj['dict']["vars"].items():
        rowPosition = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(rowPosition)
        item_symbol = QtGui.QTableWidgetItem()
        item_symbol.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item_symbol.setText(label)
        self.ui.tableWidget.setItem(rowPosition, 0, item_symbol)

        item_doc = QtGui.QTableWidgetItem()
        item_doc.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item_doc.setText(self.system.variables[label]['doc'])
        self.ui.tableWidget.setItem(rowPosition, 1, item_doc)

        item_units = QtGui.QTableWidgetItem()
        item_units.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        unit_str = self.system.variables[label]['units_latex']
        item_units.setText(unit_str)
        self.ui.tableWidget.setItem(rowPosition, 2, item_units)

        item_value = QtGui.QTableWidgetItem()
        item_value.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        item_value.setText(str(other))
        self.ui.tableWidget.setItem(rowPosition, 3, item_value)
    else:
      for tokens in self.obj['dict']['tokens']:
        for label, other in self.obj['dict']['tokens'][tokens]['vars'].items():
          rowPosition = self.ui.tableWidget.rowCount()
          self.ui.tableWidget.insertRow(rowPosition)
          item_symbol = QtGui.QTableWidgetItem()
          item_symbol.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
          item_symbol.setText(label)
          self.ui.tableWidget.setItem(rowPosition, 0, item_symbol)

          item_doc = QtGui.QTableWidgetItem()
          item_doc.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
          item_doc.setText(self.system.variables[label]['doc'])
          self.ui.tableWidget.setItem(rowPosition, 1, item_doc)

          item_units = QtGui.QTableWidgetItem()
          item_units.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
          unit_str = self.system.variables[label]['units_latex']
          item_units.setText(unit_str)
          self.ui.tableWidget.setItem(rowPosition, 2, item_units)

          item_value = QtGui.QTableWidgetItem()
          item_value.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
          item_value.setText(str(other))
          self.ui.tableWidget.setItem(rowPosition, 3, item_value)

    if self.obj['piece'] == 'node':
      for label, other in self.obj['dict']["states"].items():
        rowPosition = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(rowPosition)
        item_symbol = QtGui.QTableWidgetItem()
        item_symbol.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item_symbol.setText(label)
        self.ui.tableWidget.setItem(rowPosition, 0, item_symbol)

        item_doc = QtGui.QTableWidgetItem()
        item_doc.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        item_doc.setText(self.system.variables[label]['doc'])
        self.ui.tableWidget.setItem(rowPosition, 1, item_doc)

        item_units = QtGui.QTableWidgetItem()
        item_units.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        unit_str = self.system.variables[label]['units_latex']
        item_units.setText(unit_str)
        self.ui.tableWidget.setItem(rowPosition, 2, item_units)

        item_value = QtGui.QTableWidgetItem()
        item_value.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        # val =
        item_value.setText(str(other))
        self.ui.tableWidget.setItem(rowPosition, 3, item_value)

  def fill_combo_selector(self, things):
    self.ui.object_selecter_box.clear()
    self.ui.object_selecter_box.addItems(things)

  def on_pushFinished_button_pressed(self):
    self.completed.emit("Saved something")
    self.closeEvent('close')

  def setValue(self, item):
    col = item.column()
    if col != 3:
      return
    row = item.row()
    value = eval(item.text())
    # print(self.obj)
    variable = self.ui.tableWidget.item(row, 0).text()

    # if self.obj['piece'] == 'node' or (self.obj['piece'] == 'arc' and self.obj['label'] in self.system.singleArcs):
    if self.obj['piece'] == 'global_variable':
      previous_value = copy.copy(self.obj['dict'][variable]['value'])
      self.obj['dict'][variable]['value'] = value
    elif variable in self.obj['dict']['vars'].keys():
      previous_value = copy.copy(self.obj['dict']['vars'][variable])
      self.obj['dict']['vars'][variable] = value
    elif variable in self.obj['dict']['states'].keys():
      previous_value = copy.copy(self.obj['dict']['states'][variable])
      self.obj['dict']['states'][variable] = value
    print('Changed variable from: {}\n to: {}'.format(previous_value, value))
    # else:
    #   for tokens in self.obj['dict']['tokens']:
    #     if self.obj['piece'] == 'global_variable':
    #       previous_value = copy.copy(self.obj['dict'][variable]['value'])
    #       self.obj['dict'][variable]['value'] = value
    #     elif variable in self.obj['dict']['tokens'][tokens]['vars'].keys():
    #       previous_value = copy.copy(self.obj['dict']['tokens'][tokens]['vars'][variable])
    #       self.obj['dict']['tokens'][tokens]['vars'][variable] = value
    #     print('Changed variable from: {}\n to: {}'.format(previous_value, value))

    if previous_value != value:
      #   pass
      self.system.assembleOutput()
    # self.system.updatedDict(self.obj['label'], self.obj['piece'], self.obj['dict'])
    # self.system.updatedDict()
    # dict_obj = self.curr_input_str

  def closeEvent(self, event):
    self.mother.table_initiliser = None
    self.deleteLater()
    return
