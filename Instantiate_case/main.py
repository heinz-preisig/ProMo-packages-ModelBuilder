"""
Author:  Arne Tobias Elve
What:    System to  instantiate the nodes and arcs and the models
Started: 2019-07-11
Reason:  To have a simple version, to read in and out
Status:  Production
Contact: arne.t.elve(at)ntnu.no
"""

import sys

from Common.common_resources import getData, putData
from Common.resource_initialisation import FILES
from Common.common_resources import CONNECTION_NETWORK_SEPARATOR


class Instantiate_Case(object):
  """
  Generate a new instantiation of a case
  """

  def __init__(self, ontology, model_file, calc_seq_file, variable_file,
               case_location, typed_token_file, ui = None):
    self.ontology = ontology
    self.onto_name = self.ontology.ontology_name
    self.model_file = model_file
    self.calc_seq_file = calc_seq_file
    self.variable_file = variable_file
    self.case_loc = case_location
    self.typed_token_file = typed_token_file
    self.ui = ui

    self.indices = self.ontology.readIndices()
    self.blk_inds = {k: v for k, v in self.indices.items()
                     if v["type"] == 'block_index'}

    self.mod_dict = getData(self.model_file)
    self.vars_dict = getData(self.variable_file)
    self.calc_dict = getData(self.calc_seq_file)
    self.ttk_dict = getData(self.typed_token_file)

    self.groups = {}
    self.setup_things()
    self.load_dictionaries()
    # self.make_groups()
    # self.make_new_dictionaries()

  def setup_things(self):
    self.named_network_network = {}
    for nw, nnws in self.mod_dict['named_networks'].items():
      for nnw in nnws:
        self.named_network_network[nnw] = nw

    self.typedtoken_token = {}
    for nw, tk_ttk in self.ontology.token_typedtoken_on_networks.items():
      for tk, ttks in tk_ttk.items():
        for ttk in ttks:
          self.typedtoken_token[ttk] = tk

    self.nodes_file = FILES['init_nodes'] % (self.onto_name,
                                             self.ui.model_name,
                                             self.ui.case_name)
    self.arcs_file = FILES['init_arcs'] % (self.onto_name,
                                           self.ui.model_name,
                                           self.ui.case_name)
    self.globals_file = FILES['init_globals'] % (self.onto_name,
                                                 self.ui.model_name,
                                                 self.ui.case_name)
    self.name_to_label_dict = self.make_name_to_label_dict()

  def make_name_to_label_dict(self):
    name_to_label_dict = {}
    for label, arc in self.mod_dict['arcs'].items():
      name_to_label_dict[arc['name']] = label
    for label, node in self.mod_dict['nodes'].items():
      name_to_label_dict[node['name']] = label
    return name_to_label_dict

  def make_groups(self):
    for nnw in self.calc_dict.keys():
      self.groups[nnw] = {}
      self.make_node_groups(nnw)
      self.make_arc_groups(nnw)
      self.make_globals_groups(nnw)
    return self.groups

  def make_globals_groups(self, nnw):
    self.groups[nnw]['globals'] = {}
    self.groups[nnw]['globals']['vars_const'] = []
    for i_var in self.calc_dict[nnw]['vars_const']:
      var = self.vars_dict[i_var]
      if var["type"] != 'network':
        self.groups[nnw]['globals']['vars_const'].append(i_var)

  def make_node_groups(self, nnw):
    self.groups[nnw]['nodes'] = {}
    self.groups[nnw]['nodes']['reservoirs'] = []
    self.groups[nnw]['nodes']['single_nodes'] = []
    self.groups[nnw]['nodes']['event_nodes'] = []
    self.groups[nnw]['nodes']['dynamic_nodes'] = []

    tokens_set = set()

    for label, node in self.mod_dict['nodes'].items():

      if node['named_network'] == nnw:
        self.groups[nnw]['nodes']['single_nodes'].append(label)
        if node["type"] == 'constant':
          self.groups[nnw]['nodes']['reservoirs'].append(label)
        elif node["type"] == 'dynamic':
          self.groups[nnw]['nodes']['dynamic_nodes'].append(label)
        elif node["type"] == 'event':
          self.groups[nnw]['nodes']['event_nodes'].append(label)
        # print(node['tokens'].keys())
        # tokens_set.add(set(node['tokens'].keys()))
        for token in node['tokens'].keys():
          tokens_set.add(token)

  def make_arc_groups(self, nnw):
    self.groups[nnw]['arcs'] = {}
    self.groups[nnw]['arcs']['single_arcs'] = []

    token_set = set()
    mechanism_set = set()
    for label, arc in self.mod_dict['arcs'].items():
      if arc['named_network'] == nnw:
        self.groups[nnw]['arcs']['single_arcs'].append(label)
        mechanism_set.add(arc['mechanism'])
        token_set.add(arc['token'])

    mech_map = {}
    for mech in mechanism_set:
      name = 'arc_mech_{}'.format(mech)
      mech_map[mech] = name
      self.groups[nnw]['arcs'][name] = []

    token_map = {}
    for token in token_set:
      name = 'arc_token_{}'.format(token)
      token_map[token] = name
      self.groups[nnw]['arcs'][name] = []

    for label, arc in self.mod_dict['arcs'].items():
      if arc['named_network'] == nnw:
        group_name = mech_map[arc['mechanism']]
        self.groups[nnw]['arcs'][group_name].append(label)

  def make_new_dictionaries(self):
    self.nodes_dict = {}
    self.arcs_dict = {}
    self.globals_dict = {}
    self.fill_node_dict_with_init_values()
    self.fill_arc_dict_with_ones()
    self.fill_globals_dict_with_ones()

  def fill_node_dict_with_init_values(self):
    for label, node in self.mod_dict['nodes'].items():
      self.nodes_dict[label] = {'vars': {}}

      nnw_single = node['named_network']
      if nnw_single not in self.calc_dict.keys():
        if nnw_single is None:
          continue
        elif CONNECTION_NETWORK_SEPARATOR in nnw_single:
          regular_node = False
          nnws = nnw_single.split(CONNECTION_NETWORK_SEPARATOR)
        else:
          continue
      else:
        regular_node = True
        nnws = [nnw_single]
      for nnw in nnws:
        for i_var in self.calc_dict[nnw]['vars_const']:
          unfixed_flag = i_var not in self.calc_dict[nnw]['fixed_vars']
          token_flag = True
          var = self.vars_dict[i_var]
          ind_sets = var['index_structures']

          if 'node' in ind_sets and len(ind_sets) == 1:
            self.nodes_dict[label]['vars'][i_var] = 1.0 * unfixed_flag * regular_node

          elif len(ind_sets) == 1 and ind_sets[0] in self.blk_inds.keys():
            ind = self.blk_inds[ind_sets[0]]
            if ind['outer'] == 'node':
              inner = ind['inner']
              token = self.typedtoken_token[ind['inner']]
              if inner.endswith('_conversion'):  # Only conversion in regular
                if 'injected_conversions' in node.keys():
                  conversion_flag = True
                  length = len(node['injected_conversions'][token])
                else:
                  conversion_flag = False
                  length = 1
                self.nodes_dict[label]['vars'][i_var] = [1.0 * unfixed_flag * regular_node * conversion_flag] * length
              else:
                if regular_node:
                  if token not in node['tokens']:
                    length = 1
                    token_flag = False
                  else:
                    length = len(node['tokens'][token])
                  self.nodes_dict[label]['vars'][i_var] = [1.0 * unfixed_flag * token_flag] * length
                else:
                  if token not in node['tokens']:
                    length = 1
                    token_flag = False
                  else:
                    length = len(node['tokens_right'][token])
                  self.nodes_dict[label]['vars'][i_var] = [1.0 * unfixed_flag * token_flag] * length
            else:
              continue
          else:
            continue

          # else:
          #   for name, ind in self.blk_inds.items():
          #     if ind['outer'] == 'node' and name in ind_sets and len(ind_sets) == 1:
          #       inner = ind['inner']
          #       token = self.typedtoken_token[inner]
          #       if token in node['tokens']:
          #         token_flag = True
          #       if inner.endswith('_conversion'):  # Only conversion in regular
          #         length = len(node['injected_conversions'][token])
          #       else:                                                    # Normal
          #         if inter_or_intra:
          #           if token in node['tokens']:
          #             length = len(node['tokens_right'][token])
          #           else:
          #             length = 1
          #         else:
          #           if token in node['tokens']:
          #             token_flag = True
          #             length = len(node['tokens'][token])
          #       if i_var in self.calc_dict[nnw]['fixed_vars']:
          #         self.nodes_dict[label]['vars'][i_var] = [0.0] * length
          #       else:
          #         self.nodes_dict[label]['vars'][i_var] = [1.0] * length

  def fill_arc_dict_with_ones(self):
    for label, arc in self.mod_dict['arcs'].items():
      self.arcs_dict[label] = {'vars': {}}

      nnw = arc['named_network']
      if nnw not in self.calc_dict.keys():
        continue

      for i_var in self.calc_dict[nnw]['vars_const']:
        var = self.vars_dict[i_var]
        ind_sets = var['index_structures']
        if 'arc' in ind_sets and len(ind_sets) == 1:
          if i_var in self.calc_dict[nnw]['fixed_vars']:
            self.arcs_dict[label]['vars'][i_var] = 0.0
          else:
            self.arcs_dict[label]['vars'][i_var] = 1.0
        else:
          for name, ind in self.blk_inds.items():
            if ind['outer'] == 'arc' and name in ind_sets and len(ind_sets) == 1:
              inner = ind['inner']
              token = self.typedtoken_token[inner]
              if token == arc['token']:
                length = len(arc['typed_tokens'])
              if i_var in self.calc_dict[nnw]['fixed_vars']:
                self.arcs_dict[label]['vars'][i_var] = [0.0] * length
              else:
                self.arcs_dict[label]['vars'][i_var] = [1.0] * length

  def fill_globals_dict_with_ones(self):

    for nnw in self.calc_dict.keys():
      self.globals_dict[nnw] = {}

      for var_i in self.calc_dict[nnw]['vars_const']:
        var = self.vars_dict[var_i]
        ind_sets = var['index_structures']
        if len(ind_sets) > 1:
          if var["type"] == 'network':
            continue
          else:
            self.globals_dict[nnw][var_i] = [[]]
        if var['index_structures'] == []:
          self.globals_dict[nnw][var_i] = 1.

        elif var['index_structures'][0] in self.typedtoken_token.keys():
          # print(self.ttk_dict)
          length = len(self.ttk_dict[ind_sets[0]]['instances'])
          self.globals_dict[nnw][var_i] = [1.0] * length
        elif var['index_structures'][0].endswith('_conversion'):
          ind_set = self.indices[var['index_structures'][0]]
          if ind_set['inner'] in self.typedtoken_token.keys():
            length = len(self.ttk_dict[ind_sets[0]]['conversions'])
          self.globals_dict[nnw][var_i] = [1.0] * length

  def save_dictionaries(self):
    putData(self.nodes_dict, self.nodes_file)
    putData(self.arcs_dict, self.arcs_file)
    putData(self.globals_dict, self.globals_file)

  def load_dictionaries(self):

    n_d = getData(self.nodes_file)
    a_d = getData(self.arcs_file)
    g_d = getData(self.globals_file)

    if n_d and a_d and g_d:
      self.nodes_dict = n_d
      self.arcs_dict = a_d
      self.globals_dict = g_d
    else:
      # raise LoadException('No files available, making fresh ones')
      # sys.tracebacklimit = None                   # Dont need the traceback now
      self.make_new_dictionaries()


class LoadException(Exception):
  """docstring for LoadException."""

  def __init__(self, message):
    sys.tracebacklimit = 0                      # Dont need the traceback now
    self.message = message
    print('ERROR:: Cannot load the files!')
