"""
Author:  Arne Tobias Elve
What:    Equations handling
Started: 2019-07-03
Reason:  Split into different networks and have a standalone system
Status:  Production
Contact: arne.t.elve(at)ntnu.no
"""
import copy
import sys
from os import path

from Common.common_resources import getData, putData
from Common.resource_initialisation import FILES


class Instantiate_Eqs(object):
  """docstring for Instantiate_Eqs."""

  def __init__(self, ontology, model_file, equations_file, variable_file,
               case_location, ui = None):
    self.ontology = ontology
    self.onto_name = self.ontology.ontology_name
    self.model_file = model_file
    self.equation_file = equations_file
    self.variable_file = variable_file
    self.case_loc = case_location
    self.ui = ui

    self.rules = getData(FILES["rules_file"] % (self.onto_name))
    self.eq_dict = getData(self.equation_file)
    self.mod_dict = getData(self.model_file)
    self.vars_dict = getData(self.variable_file)
    mod_name = self.ui.model_name
    case_name = self.ui.case_name
    self.calc_seq_file = FILES['calculation_sequence'] % (self.onto_name,
                                                          mod_name,
                                                          case_name)
    if path.exists(self.calc_seq_file):
      self.eq_set = getData(self.calc_seq_file)
    else:
      self.eq_set = {}

  def build_new_equation_set(self, states, network, named_network):
    container = {}
    container['eq_used'] = []
    container['eq_order'] = []
    container['eq_implicit'] = []
    container['vars_used'] = []
    container['vars_const'] = []
    container['unused_equations'] = []
    container['fixed_vars'] = []
    container['states'] = states
    container['network'] = network
    container['named_network'] = named_network
    self.eq_set[named_network] = copy.copy(container)

  def write_equation_state_file(self):
    putData(self.eq_set, self.calc_seq_file)
    # pass
    # out_dict = {}
    # out_dict['calculation_order'] = self.initialization.eq_order
    # out_dict['states'] = self.initialization.states
    # out_dict['vars'] = self.initialization.vars_used_const
    # outfile = path.join(file_loc, FILE_NAMES["calculation_sequence"])
    # putData(out_dict, outfile)

  def set_state_network(self, states, network, named_network):
    if named_network in self.eq_set.keys():
      if self.eq_set[named_network]['states'] == states:
        message = 'Already initialised this network\nEq order:\n{}'
        disp = message.format(self.eq_set[named_network]['eq_order'])
        self.ui.display_message(disp)

    else:
      self.build_new_equation_set(states, network, named_network)

    self.cnn = self.eq_set[named_network]
    self.network = network
    self.named_network = named_network

  def set_fixed_variables(self, fixed_vars):
    self.cnn['fixed_vars'] = fixed_vars

  def equationSetBuilder(self):
    self.cnn['eq_order'] = []
    self.cnn['eq_used'] = []
    self.cnn['vars_used'] = []
    self.cnn['vars_const'] = []

    self.alt_eqs = False
    for state in self.cnn['states']:
      eq_list = set(self.vars_dict[state]['equation_list']).difference(set(self.cnn['unused_equations']))
      if len(list(eq_list)) > 1:
        self.ui.start_equations_selector()
        self.ui.fill_radio(list(eq_list))
      else:
        eq_needed = list(eq_list)[0]
        self.cnn['vars_const'].append(state)
        self.cnn['vars_used'].append(state)
        self.rec_func(eq_needed)
    if self.alt_eqs:
      return 'Error:: Still have altenative equations within the network'
    else:
      self.cnn['eq_order'] = self.arragne_equations()
      return 'Equation set has been instansiated.'

  def arragne_equations(self):
    self.cnn['vars_const'] = list(set(self.cnn['vars_const']))

    order = []
    for eq in list(reversed(self.cnn['eq_used'])):
      if eq not in order:
        order.append(eq)
      else:
        pass
    return order

  def set_unused_equations(self, id):
    self.cnn['unused_equations'].append(id)

  def set_unused_to_used(self):
    self.cnn['unused_equations'] = []

  def rec_func(self, eq_needed):
    self.cnn['eq_used'].append(eq_needed)
    vars_needed = self.eq_dict[eq_needed]['incidence_list']
    for var in vars_needed:

      if self.cnn['vars_used'].__contains__(var):
        pass               # already taken care of but need to get the sequence
      elif var in self.cnn['states']:
        continue                # to be handled
      else:
        self.cnn['vars_used'].append(var)

      if self.vars_dict[var]['equation_list'] == []:
        if self.vars_dict[var]["type"] in self.rules['variable_classes_having_port_variables']: # TODO: What about rest?
          self.cnn['vars_const'].append(var)
        else:
          raise Exception('Something is odd. Equation list empty, but no port reqognized')
      else:
        if self.vars_dict[var]["type"] == 'state' or var in self.cnn['fixed_vars']:
          self.cnn['vars_const'].append(var)
          continue                                    # Have to be instantiated
        else:
          eq_needed = self.handle_equations(var)
          if eq_needed:
            self.rec_func(eq_needed)

  def handle_equations(self, var):
    equations_needed = self.vars_dict[var]['equation_list']
    eq_list = list(set(equations_needed).difference(set(self.cnn['unused_equations'])))
    remainer_list = []
    for eq in list(eq_list):              # Check if applicatble in network
      equation = self.eq_dict[eq]
      if self.network in self.ontology.heirs_network_dictionary[equation['network']] or self.network == equation['network']:
        remainer_list.append(eq)
    if len(list(remainer_list)) > 1:
      self.make_popup(var, remainer_list)
      return
    elif len(remainer_list) == 0:
      message = 'SHIT... Variable: {}, not available for the network: {},\nPlease fix in equation editor'.format(var, self.network)
      if self.ui:
        self.ui.display_message(message)
      raise Exception(message)
    else:
      eq_needed = list(remainer_list)[0]
    return eq_needed

  def make_popup(self, var, remainer_list):
    self.alt_eqs = True
    if self.ui:
      message = 'Further inputs required:\n{} as alternatives, select one of the following alternatives:\n{}'
      out = message.format(var, remainer_list)
      self.ui.display_message(out)
      self.ui.start_equations_selector()
      self.ui.fill_radio(list(remainer_list))
    else:
      print('Missing enough information to construct equations set...')
      print('Please select which of these equations should be ignorded:')
      print('{}'.format(remainer_list))
    # Exception handling
    try:
      raise Alternatives('More alternatives')
    except Exception as e:
      pass

  def collect_fixed_candidates(self):
    alternatives = []
    for label, var in self.vars_dict.items():
      if self.network in self.ontology.heirs_network_dictionary[var['network']]:
        if var["type"] in self.rules['can-be-fixed-vars']:
          alternatives.append(label)
    return alternatives


class Alternatives(Exception):
  """docstring for alternatives."""

  def __init__(self, message):
    # sys.tracebacklimit = 0                      # Dont need the traceback now
    self.message = message
    print('ERROR:: Alternative equations for the same variable available')
