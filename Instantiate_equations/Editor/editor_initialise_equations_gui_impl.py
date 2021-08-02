from os import path, mkdir
import itertools

from PyQt5 import QtCore, QtGui

from Common.common_resources import getData, getOntologyName
from Common.common_resources import askForModelFileGivenOntologyLocation as afm
from Common.common_resources import askForCasefileGivenLocation as afc
from Common.resource_initialisation import DIRECTORIES, FILES
from Common.ontology_container import OntologyContainer
from ModelBuilder.Instantiate_equations.Editor.editor_initialise_equations_gui import Ui_MainWindow
from ModelBuilder.Instantiate_equations import Ui_Eq_selector
from ModelBuilder.Instantiate_equations.Editor.fix_selected_equations import Ui_Var_fixer
from ModelBuilder.Instantiate_equations import Instantiate_Eqs


class Ui_Initialise_equations(QtGui.QMainWindow):
  def __init__(self):
    QtGui.QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.ontology_name = getOntologyName()
    #self.ontology_name = "Flash_11"
    self.ontology = OntologyContainer(self.ontology_name)
    self.ontology_location = self.ontology.ontology_location
    models_file = DIRECTORIES["model_library_location"] % self.ontology_name
    self.mod_name = afm(models_file, alternative = False)[0]
    #self.mod_name = 'Flash_With_out_intraface'
    self.cases_location = DIRECTORIES["cases_location"] % (self.ontology_name,
                                                           self.mod_name)
    self.check_for_directory(self.cases_location)
    self.case_name, new_case = afc(self.cases_location)
    #self.case_name = 'Simple'
    message = '<b>Set up</b> <br />Ontology: {}<br />Model: {}'
    display = message.format(self.ontology_name, self.mod_name)
    self.ui.message_box.setText(display)

    self.model_loc = DIRECTORIES["model_location"] % (self.ontology_name,
                                                      self.mod_name)

    self.variable_file = FILES["variables_file"] % self.ontology_name
    self.equation_file = FILES["equations_file"] % self.ontology_name
    self.typed_token_file = FILES["typed_token_file"] % self.ontology_name
    self.model_file = FILES["model_file"] % (self.ontology_name, self.mod_name)
    self.mod_dict = getData(self.model_file)
    self.eqs_dict = getData(self.equation_file)
    self.vars_dict = getData(self.variable_file)
    self.check_for_directory(self.cases_location)

    self.case_location = DIRECTORIES["specific_case"] % (self.ontology_name,
                                                         self.mod_name,
                                                         self.case_name)
    self.already_exist_case = self.check_for_directory(self.case_location)

    self.ui.ontology_name_label.setText('{}'.format(self.ontology_name))
    self.ui.model_name_label.setText('{}'.format(self.mod_name))
    self.ui.case_name_label.setText("{}".format(self.case_name))
    self.bi_part = Instantiate_Eqs(self.ontology, self.model_file,
                                   self.equation_file, self.variable_file,
                                   self.case_location, ui = self)
    self.fill_network_alternatives()
    self.eq_selector = None
    self.var_fixer = None

    self.hide_buttons()

    # self.start_equations_selector()

  def hide_buttons(self):
    self.ui.build_equation_set_button.hide()
    self.ui.save_model_button.hide()
    self.ui.trim_set.hide()
    self.ui.reset.hide()

  def show_buttons(self):
    self.ui.build_equation_set_button.show()
    self.ui.save_model_button.show()
    self.ui.trim_set.show()
    self.ui.reset.show()

  def check_for_directory(self, loc):
    if not path.exists(loc):
      mkdir(loc)
      return False
    else:
      return True

  def fill_network_alternatives(self):
    named_networks = []
    named_networks_used = set()
    self.named_network_network = {}
    for nw, nnws in self.mod_dict['named_networks'].items():
      for nnw in nnws:
        self.named_network_network[nnw] = nw
        named_networks.append(nnw)
    for label, node in self.mod_dict['nodes'].items():
      if node['named_network'] in named_networks:
        named_networks_used.add(node['named_network'])
    self.ui.select_network.clear()
    self.ui.select_network.addItems(sorted(list(named_networks_used)))
    # return list(named_networks_used)

  @QtCore.pyqtSignature('QString')
  def on_select_network_activated(self, nnw):
    self.named_network = nnw
    self.fill_starting_points(nnw)

  def fill_starting_points(self, nnw):
    vars_dict = getData(self.variable_file)
    states = []
    nw = self.named_network_network[nnw]
    for label, var in vars_dict.items():
      if var["type"] == 'state':
        if nw == var["network"] or nw in self.ontology.heirs_network_dictionary[var["network"]]:
          states.append(label)

    combos = []
    for i in range(len(states)):
      states_combos = itertools.combinations(states, i+1)
      for state_alt in states_combos:
        str_rep = ', '.join(state_alt)
        combos.append(str(str_rep))
    self.ui.select_starting_variables.clear()
    self.ui.select_starting_variables.addItems(combos)

  @QtCore.pyqtSignature('QString')
  def on_select_starting_variables_activated(self, vars):
    vars_alts = vars.split(', ')
    self.state_variables = vars_alts
    network = self.named_network_network[self.named_network]
    self.bi_part.set_state_network(self.state_variables, network,
                                   self.named_network)
    self.show_buttons()


  def on_trim_set_pressed(self):
    alternatives = self.bi_part.collect_fixed_candidates()
    self.start_variable_fixer()
    self.var_fixer.fill_area_radio(alternatives)

  def on_build_equation_set_button_pressed(self):
    if self.state_variables:
      message = self.bi_part.equationSetBuilder()
      # nnw = self.bi_part.named_network
      # cnn = self.bi_part.cnn
      eq_order = str(self.bi_part.cnn['eq_order'])
      # print(self.bi_part.eq_order)
      # print(self.bi_part.states)
      # self.bi_part.addVariablesAndStates()
      self.ui.message_box.setText('{}\nOrder:\n{}'.format(message, eq_order))
    else:
      self.ui.message_box.setText('Have not selected state variables')
      return

  # def write_equation_state_file(self, file_loc):
  #   out_dict = {}
  #   out_dict['calculation_order'] = self.bi_part.eq_order
  #   out_dict['states'] = self.bi_part.states
  #   out_dict['vars'] = self.bi_part.vars_used_const
  #   outfile = path.join(file_loc, FILE_NAMES["calculation_sequence"])
  #   putData(out_dict, outfile)

  def on_save_model_button_pressed(self):
    self.bi_part.write_equation_state_file()

  def on_reset_pressed(self):
    self.bi_part.set_unused_to_used()
    self.display_message('Reset the equation set... Build again')

  def display_message(self, message):
    self.ui.message_box.setText(message)

  def closeEvent(self, event):
    if self.eq_selector:
      self.eq_selector.closeEvent(event)
    if self.var_fixer:
      self.var_fixer.closeEvent(event)
    self.deleteLater()
    return

  def connection(self, what):
    pass

  def start_variable_fixer(self):
    self.var_fixer = Equation_fixer(self.bi_part, self)
    self.var_fixer.completed.connect(self.connection)
    self.var_fixer.show()

  def start_equations_selector(self):
    self.eq_selector = Equation_selector(self.bi_part, self)
    self.eq_selector.completed.connect(self.connection)
    self.eq_selector.show()
  #   self.radio_test()
  #
  # def radio_test(self):
  #   alternatives = ['asdf', 'sdfg', 'dfgh']
  #   self.eq_selector.fill_area_radio(alternatives)

  def fill_radio(self, alternatives):
    self.eq_selector.fill_area_radio(alternatives)


class Equation_selector(QtGui.QWidget):
  completed = QtCore.pyqtSignal(str)

  def __init__(self, eq_system, mother):
    QtGui.QWidget.__init__(self)
    self.mother = mother
    self.ui = Ui_Eq_selector()
    self.system = eq_system
    self.ui.setupUi(self)
    self.con = self.ui.scrollAreaWidgetContents
    self.setup()
    self.eqs = self.mother.eqs_dict
    # self.ui.tableWidget.itemChanged.connect(self.setValue)

  def setup(self):
    pass

  def connection(self, what):
    pass

  def fill_area_radio(self, alternatives):
    label = '{} := {}'
    self.alternatives = alternatives
    self.button_group = QtGui.QButtonGroup()
    self.buttons = []
    for i, alternative in enumerate(alternatives):
      eq = self.eqs[alternative]
      self.the_button = QtGui.QRadioButton("{}".format(alternative))
      self.the_button.setCheckable(True)
      self.the_button.alternative = alternative
      self.the_button.setObjectName("radiobtn_{}".format(alternative))
      self.the_button.setText(label.format(eq["lhs"], eq["rhs"]))
      self.button_group.addButton(self.the_button, i)
      self.buttons.append(self.the_button)
      self.ui.verticalLayout.addWidget(self.the_button)

  def check_for_selection(self):
    nonChecked = True
    for button in self.buttons:
      if button.isChecked():
        # button = button.text()
        nonChecked = False
        alt = button.alternative
    if nonChecked:
      self.ui.message_browser.setText("No alternative selected!")
    else:
      self.mother.display_message('Selected equation no: {}'.format(alt))
      self.select_alternative(alt)

  def select_alternative(self, alternative):
    """
    Remove the alternative equations that shall not be used in this network
    """
    for alt_ID in self.alternatives:
      if alt_ID != alternative:
        self.system.set_unused_equations(alt_ID)

  def on_pushSelect_button_pressed(self):
    self.check_for_selection()
    self.closeEvent('close')

  def closeEvent(self, event):
    self.mother.eq_selector = None
    self.deleteLater()
    return

class Equation_fixer(QtGui.QWidget):
  completed = QtCore.pyqtSignal(str)

  def __init__(self, eq_system, mother):
    QtGui.QWidget.__init__(self)
    self.mother = mother
    self.ui = Ui_Var_fixer()
    self.system = eq_system
    self.ui.setupUi(self)
    self.con = self.ui.scrollAreaWidgetContents
    self.setup()
    self.eqs = self.mother.eqs_dict
    # self.ui.tableWidget.itemChanged.connect(self.setValue)

  def setup(self):
    pass

  def connection(self, what):
    pass

  def fill_area_radio(self, alternatives):
    label = '{}'
    self.alternatives = alternatives
    self.button_group = QtGui.QButtonGroup()
    self.button_group.setExclusive(False)
    self.check_boxes = []
    for i, alternative in enumerate(alternatives):
      # var = self.eqs[alternative]
      self.the_checkBox = QtGui.QCheckBox()
      if alternative in self.system.cnn['fixed_vars']:
        self.the_checkBox.setChecked(True)
      else:
        self.the_checkBox.setChecked(False)
      # self.the_checkBox = QtGui.QRadioButton("{}".format(alternative))
      self.the_checkBox.setCheckable(True)
      self.the_checkBox.alternative = alternative
      self.the_checkBox.setObjectName("checkBox_{}".format(alternative))
      self.the_checkBox.setText(label.format(alternative))
      self.the_checkBox.toggled.connect(self.checkbox_checked)
      self.button_group.addButton(self.the_checkBox, i)
      self.check_boxes.append(self.the_checkBox)
      self.ui.verticalLayout.addWidget(self.the_checkBox)

  def checkbox_checked(self, signal):
    checked = self.checked_variables()
    self.ui.message_browser.clear()
    str = 'The following variables are fixed:\n{}'
    self.ui.message_browser.setText(str.format(', '.join(checked)))

  def checked_variables(self):
    checked = []
    for box in self.check_boxes:
      if box.isChecked():
        checked.append(box.alternative)
    return checked

  def on_pushSelect_button_pressed(self):
    checked_vars = self.checked_variables()
    self.mother.ui.message_box.setText('Fixed variables:\n{}'.format(', '.join(checked_vars)))
    self.system.set_fixed_variables(checked_vars)
    self.closeEvent('close')

  def closeEvent(self, event):
    self.mother.var_fixer = None
    self.deleteLater()
    return
