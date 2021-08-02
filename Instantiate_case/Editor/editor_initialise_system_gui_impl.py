import copy
# import itertools
from os import mkdir
from os import path

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets

from Common.common_resources import askForCasefileGivenLocation as afc
from Common.common_resources import askForModelFileGivenOntologyLocation as afm
from Common.common_resources import getData
from Common.common_resources import getOntologyName
# from Common.common_resources import putData
from Common.ontology_container import OntologyContainer
from Common.resource_initialisation import DIRECTORIES
# from Common.resource_initialisation import FILE_NAMES
from Common.resource_initialisation import FILES
from ModelBuilder.Instantiate_case.Editor.editor_initialise_system_gui import Ui_MainWindow
from ModelBuilder.z_Initialise_system_editor.Editor.object_initializer_gui import Ui_table_initilizer
from ModelBuilder.Instantiate_case.main import Instantiate_Case


class Ui_Initialise_system(QtWidgets.QMainWindow):
  def __init__(self):
    QtWidgets.QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.ontology_name = getOntologyName()
    # self.ontology_name = 'Flash_11'
    self.ontology = OntologyContainer(self.ontology_name)
    self.ontology_location = self.ontology.ontology_location
    models_file = DIRECTORIES["model_library_location"] % self.ontology_name
    self.mod_name = afm(models_file, alternative=False)[0]
    # self.mod_name = 'Flash_00'

    message = '<b>Set up</b> <br />Ontology: {}<br />Model: {}'
    display = message.format(self.ontology_name, self.mod_name)
    self.ui.message_box.setText(display)

    self.model_loc = DIRECTORIES["model_location"] % (self.ontology_name,
                                                      self.mod_name)
    self.ui.ontology_name_label.setText('{}'.format(self.ontology_name))
    self.ui.model_name_label.setText('{}'.format(self.mod_name))

    self.variable_file = FILES["variables_file"] % self.ontology_name
    self.equation_file = FILES["equations_file"] % self.ontology_name
    self.typed_token_file = FILES["typed_token_file"] % self.ontology_name
    self.model_file = FILES["model_file"] % (self.ontology_name, self.mod_name)

    self.cases_location = DIRECTORIES["cases_location"] % (self.ontology_name,
                                                           self.mod_name)
    self.check_for_directory(self.cases_location)
    self.case_name, new_case = afc(self.cases_location)
    # self.case_name = 'First_check'
    self.ui.case_name_label.setText('{}'.format(self.case_name))

    # print(self.case_name)
    self.case_location = DIRECTORIES["specific_case"] % (self.ontology_name,
                                                         self.mod_name,
                                                         self.case_name)
    self.already_exist_case = self.check_for_directory(self.case_location)

    self.table_initiliser = None

    self.calc_seq_file = FILES['calculation_sequence'] % (self.ontology_name,
                                                          self.mod_name,
                                                          self.case_name)
    if path.exists(self.calc_seq_file):
      self.calc_dict = getData(self.calc_seq_file)
      self.mod_dict = getData(self.model_file)
      self.nodes_file = FILES['init_nodes'] % (self.ontology_name,
                                               self.mod_name,
                                               self.case_name)
      self.arcs_file = FILES['init_arcs'] % (self.ontology_name,
                                             self.mod_name,
                                             self.case_name)
      self.globals_file = FILES['init_globals'] % (self.ontology_name,
                                                   self.mod_name,
                                                   self.case_name)
      self.typed_token_file = FILES['typed_token_file'] % (self.ontology_name)
      self.var_file = FILES['variables_file'] % (self.ontology_name)
      self.system = Instantiate_Case(self.ontology,
                                     self.model_file,
                                     self.calc_seq_file,
                                     self.var_file,
                                     self.case_location,
                                     self.typed_token_file,
                                     self
                                     )
    else:
      self.hide_all()
      self.display_message('Instantiate equation set before nodes!')
      raise Exception("Instantiate equation set before nodes!")

    self.single = None
    self.group = None
    self.fill_network_alternatives()

  def hide_all(self):
    self.ui.select_named_network.hide()
    self.ui.select_group.hide()
    self.ui.select_single.hide()
    self.ui.save_model_button.hide()
    self.ui.initialise_system_button.hide()

  def fill_network_alternatives(self):
    named_networks_used = list(self.calc_dict.keys())
    self.ui.select_named_network.clear()
    self.ui.select_named_network.addItems(sorted(list(named_networks_used)))

  def fill_groups_alternatives(self, nnw):
    self.group_troop = {}
    show_groups = []
    self.groups = self.system.make_groups()
    for troop, groups in self.groups[nnw].items():
      for group, things in groups.items():
        self.group_troop[group] = troop          # Placeholder for what remains
        show_groups.append(group)
    self.ui.select_group.clear()
    self.ui.select_group.addItems(show_groups)

  def fill_singles(self, group):
    # stuff = []
    # if group == 'single_nodes':
    self.ui.select_single.clear()
    labels = self.groups[self.named_network][self.group_troop[group]][group]
    text = []
    for label in labels:
      if group == 'single_nodes':
        text.append(self.mod_dict['nodes'][label]['name'])
      elif group == 'single_arcs':
        text.append(self.mod_dict['arcs'][label]['name'])
    self.ui.select_single.addItems(text)

  def display_message(self, message):
    self.ui.message_box.setText(message)

  def check_for_directory(self, loc):
    if not path.exists(loc):
      mkdir(loc)
      return False
    else:
      # DIR ALREADY EXISTS
      return True
    # return

  # def generate_groups(self, named_network):
  #   for node in self.model_

  # @QtCore.pyqtSignature('QString')
  def on_select_named_network_activated(self, named_network):
    self.named_network = named_network
    self.fill_groups_alternatives(named_network)


  # @QtCore.pyqtSignature('QString')
  def on_select_group_activated(self, group):
    self.group = group
    if group in ['single_nodes', 'single_arcs']:
      self.fill_singles(group)

  # @QtCore.pyqtSignature('QString')
  def on_select_single_activated(self, single):
    self.single = single

  def on_initialise_system_button_pressed(self):
    # pass
    selections = [self.group, self.single]
    self.table_initiliser = Table_widget(self.system, self, selections)
    self.table_initiliser.completed.connect(self.finished_edit_table)
    self.table_initiliser.show()

  def finished_edit_table(self, what):
    pass

  def on_save_model_button_pressed(self):
    self.system.save_dictionaries()

  def closeEvent(self, event):
    if self.table_initiliser:
      self.table_initiliser.closeEvent(event)
    self.deleteLater()
    return


class Table_widget(QtWidgets.QWidget):
  completed = QtCore.pyqtSignal(str)

  def __init__(self, initialise_system, mother, selections):
    QtGui.QWidgets.__init__(self)
    self.mother = mother
    self.selections = selections
    self.system = initialise_system
    self.ui = Ui_table_initilizer()
    self.ui.setupUi(self)
    self.tw = self.ui.tableWidget
    self.tw.itemChanged.connect(self.check_if_update)

    self.aliases = {         # This is a simple solution to a "complex" problem
                    'single_nodes': 'nodes',
                    'reservoirs': 'nodes',
                    'event_nodes': 'nodes',
                    'dynamic_nodes': 'nodes',
                    'vars_const': 'globals',
                    'single_arcs': 'arcs'
                    }
    self.values = {}
    self.values['nodes'] = self.system.nodes_dict
    self.values['arcs'] = self.system.arcs_dict
    self.values['globals'] = self.system.globals_dict

    self.setup()

  def resizeEvent(self, event):
    geo_tw = self.tw.geometry()
    tab_geo_left = copy.copy(geo_tw.left())
    tab_geo_top = copy.copy(geo_tw.top())
    tab_geo_right = copy.copy(geo_tw.right())
    tab_geo_bottom = copy.copy(geo_tw.bottom())

    geo = self.geometry()
    win_geo_left = geo.left()
    win_geo_top = geo.top()
    win_geo_right = geo.right()
    win_geo_bottom = geo.bottom()

    new_right_tw = win_geo_right - win_geo_left - 10 - tab_geo_left
    new_bottom_tw = win_geo_bottom - win_geo_top - 10 - tab_geo_top
    new_geo_tw = QtCore.QRect(tab_geo_left, tab_geo_top, new_right_tw, new_bottom_tw)

    mes_mego = self.ui.message_browser.geometry()
    mes_geo_left = mes_mego.left()
    mes_geo_top = mes_mego.top()
    mes_geo_bottom = mes_mego.bottom()
    new_mes_geo = QtCore.QRect(mes_geo_left, mes_geo_top, new_right_tw, mes_geo_bottom)
    self.ui.message_browser.setGeometry(new_mes_geo)
    self.tw.setGeometry(new_geo_tw)

  def setup(self):
    self.build_unit_list()

  def build_unit_list(self):
    self.selector_list = []
    self.selector_dict = {}

    dict = self.aliases[self.selections[0]]
    print('Hello: ', dict)
    if dict == 'globals':
      nnw = self.mother.named_network
      self.fill_globals_table(dict, nnw)
    elif self.selections[1]:
      # Single node or arc selcted
      label = self.system.name_to_label_dict[self.selections[1]]
      self.fill_table_normal(dict, label)

  def fill_globals_table(self, dict, nnw):
    self.tw.clear()
    self.tw.setRowCount(0)
    self.tw.setColumnCount(5)

    item_v = QtGui.QTableWidgetItem()
    item_v.setText("Variable:")
    self.tw.setHorizontalHeaderItem(0, item_v)

    item_d = QtGui.QTableWidgetItem()
    item_d.setText("Documentation:")
    self.tw.setHorizontalHeaderItem(1, item_d)

    item_u = QtGui.QTableWidgetItem()
    item_u.setText("Units:")
    self.tw.setHorizontalHeaderItem(2, item_u)

    item_i = QtGui.QTableWidgetItem()
    item_i.setText("Index:")
    self.tw.setHorizontalHeaderItem(3, item_i)

    item_n = QtGui.QTableWidgetItem()
    item_n.setText("Value:")
    self.tw.setHorizontalHeaderItem(4, item_n)

    for var, values in self.values[dict][nnw].items():
      rowPosition = self.ui.tableWidget.rowCount()
      self.tw.insertRow(rowPosition)
      item_symbol = QtGui.QTableWidgetItem()
      item_symbol.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
      item_symbol.setText(var)
      self.tw.setItem(rowPosition, 0, item_symbol)

      item_doc = QtGui.QTableWidgetItem()
      item_doc.setFlags(QtCore.Qt.ItemIsEnabled)
      item_doc.setText(self.system.vars_dict[var]['doc'])
      self.tw.setItem(rowPosition, 1, item_doc)

      item_units = QtGui.QTableWidgetItem()
      item_units.setFlags(QtCore.Qt.ItemIsEnabled)
      unit_str = self.system.vars_dict[var]['units_latex']
      item_units.setText(unit_str)
      self.tw.setItem(rowPosition, 2, item_units)

      item_index = QtGui.QTableWidgetItem()
      item_index.setFlags(QtCore.Qt.ItemIsEnabled)
      index_set = 'None'
      item_index.setText(index_set)
      self.tw.setItem(rowPosition, 3, item_index)

      item_value = QtGui.QTableWidgetItem()
      item_value.value = self.values[dict][nnw][var]
      item_value.dict = dict
      item_value.nnw = nnw
      item_value.var = var
      item_value.type = 'globals'
      item_value.indexed = False
      item_value.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
      item_value.setText(str(values))
      self.tw.setItem(rowPosition, 4, item_value)

  def fill_table_normal(self, dict, label):
    if dict == 'nodes':
      extra_length = len(self.system.mod_dict[dict][label]['tokens']['mass'])
      headers = copy.copy(self.system.mod_dict[dict][label]['tokens']['mass'])
    elif dict == 'arcs':
      extra_length = len(self.system.mod_dict[dict][label]['typed_tokens'])
      headers = copy.copy(self.system.mod_dict[dict][label]['typed_tokens'])
    else:
      raise Exception('Neither node nor arc')

    item = QtGui.QTableWidgetItem()
    item.dict = dict
    item.label = label

    self.tw.clear()
    self.tw.setRowCount(0)
    self.tw.setColumnCount(5 + extra_length)

    item_v = QtGui.QTableWidgetItem()
    item_v.setText("Variable:")
    self.tw.setHorizontalHeaderItem(0, item_v)

    item_d = QtGui.QTableWidgetItem()
    item_d.setText("Documentation:")
    self.tw.setHorizontalHeaderItem(1, item_d)

    item_u = QtGui.QTableWidgetItem()
    item_u.setText("Units:")
    self.tw.setHorizontalHeaderItem(2, item_u)

    item_i = QtGui.QTableWidgetItem()
    item_i.setText("Index:")
    self.tw.setHorizontalHeaderItem(3, item_i)

    item_n = QtGui.QTableWidgetItem()
    item_n.setText(self.selections[1])
    self.tw.setHorizontalHeaderItem(4, item_n)

    for i, header in enumerate(headers):
      item_val = QtGui.QTableWidgetItem()
      item_val.setText(header)
      self.tw.setHorizontalHeaderItem(5+i, item_val)

    for var, values in self.values[dict][label]['vars'].items():
      rowPosition = self.ui.tableWidget.rowCount()
      self.tw.insertRow(rowPosition)
      item_symbol = QtGui.QTableWidgetItem()
      item_symbol.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
      item_symbol.setText(var)
      self.tw.setItem(rowPosition, 0, item_symbol)

      item_doc = QtGui.QTableWidgetItem()
      item_doc.setFlags(QtCore.Qt.ItemIsEnabled)
      item_doc.setText(self.system.vars_dict[var]['doc'])
      self.tw.setItem(rowPosition, 1, item_doc)

      item_units = QtGui.QTableWidgetItem()
      item_units.setFlags(QtCore.Qt.ItemIsEnabled)
      unit_str = self.system.vars_dict[var]['units_latex']
      item_units.setText(unit_str)
      self.tw.setItem(rowPosition, 2, item_units)

      item_index = QtGui.QTableWidgetItem()
      item_index.setFlags(QtCore.Qt.ItemIsEnabled)
      index_set = self.system.vars_dict[var]['index_structures'][0]
      item_index.setText(index_set)
      self.tw.setItem(rowPosition, 3, item_index)

      if index_set == 'node' or index_set == 'arc':
        item_value = QtGui.QTableWidgetItem()
        item_value.value = self.values[dict][label]['vars'][var]
        item_value.dict = dict
        item_value.label = label
        item_value.var = var
        item_value.indexed = False
        item_value.type = 'regular'
        item_value.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        item_value.setText(str(values))
        self.tw.setItem(rowPosition, 4, item_value)

        for i in range(extra_length):
          item_tmp = QtGui.QTableWidgetItem()
          item_tmp.setFlags(QtCore.Qt.NoItemFlags)
          self.tw.setItem(rowPosition, 5 + i, item_tmp)

      else:
        item_value = QtGui.QTableWidgetItem()
        item_value.setFlags(QtCore.Qt.NoItemFlags)
        self.tw.setItem(rowPosition, 4, item_value)

        for i, val in enumerate(values):
          item_values = QtGui.QTableWidgetItem()
          item_values.value = self.values[dict][label]['vars'][var][i]
          item_values.dict = dict
          item_values.label = label
          item_values.var = var
          item_values.indexed = True
          item_values.type = 'regular'
          item_values.index = i
          item_values.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
          item_values.setText(str(val))
          self.tw.setItem(rowPosition, 5 + i, item_values)

  def check_if_update(self, item):
    """
    Filter for checking if update of value in dict...
    """
    if item.text() and int(item.column()) >= 4 and 'value' in dir(item):
      new_value = eval(item.text())
      if new_value != item.value and item.type is 'regular':
        self.setValue(item)
      if new_value != item.value and item.type is 'globals':
        self.setValueGlobals(item)

  def setValueGlobals(self, item):
    new_value = eval(item.text())
    mes_str = 'Changed value of var: {}\nChanged from {} to {}'
    self.ui.message_browser.setText(mes_str.format(item.var, item.value, new_value))
    self.values[item.dict][item.nnw][item.var] = new_value
    item.value = copy.copy(new_value)

  def setValue(self, item):
    """
    Tried to reduce the number of times this is called, seem to be ok
    """
    new_value = eval(item.text())
    if item.indexed is False:         # It this the simples solution ever??? :)
      mes_str = 'Changed value of var: {}\nChanged from {} to {}'
      self.ui.message_browser.setText(mes_str.format(item.var, item.value, new_value))
      self.values[item.dict][item.label]['vars'][item.var] = new_value
      item.value = copy.copy(new_value)
    elif item.indexed is True:        # It this the simples solution ever??? :)
      mes_str = 'Changed value of var: {}\nChanged from {} to {}'
      self.ui.message_browser.setText(mes_str.format(item.var, item.value, new_value))
      self.values[item.dict][item.label]['vars'][item.var][item.index] = new_value
      item.value = copy.copy(new_value)
    else:
      raise Exception('Nothing changed')

  def activate_item(self, item):
    print(item.text(), 'Activated')

  def on_pushFinished_button_pressed(self):
    self.system.save_dictionaries()
    self.mother.ui.message_box.setText('Updated inital case')
    self.closeEvent('closing')

  def closeEvent(self, event):
    self.mother.table_initiliser = None
    self.deleteLater()
    return
