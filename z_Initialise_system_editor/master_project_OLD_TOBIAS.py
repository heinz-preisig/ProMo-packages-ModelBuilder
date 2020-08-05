# Master project
# Author: Andreas Johannesen
# Contact: johannesen.and@gmail.com
# Created: 29.01.19


import json
from collections import OrderedDict
import numpy as np
import os
import copy
from Common.resource_initialisation import FILE_NAMES


class Initialization(object):

	def __init__(self, filename_model, filename_equations, filename_variables, filename_typed_tokens, states):
		self.filename_model = filename_model
		self.filename_equations = filename_equations
		self.filename_variables = filename_variables
		self.filename_typed_tokens = filename_typed_tokens

		self.openingFunction() # Opens all the files
		############# Nodes ###############
		self.states = states
		self.groupDict = OrderedDict()
		self.singleDict = OrderedDict()
		self.reservoirDict = OrderedDict()
		self.nodeOrder = []

		self.orderFunc()
		self.separateNodes()
		self.addNumberOfSpecies()

		############# ARCS ################

		self.tokenDict = OrderedDict()
		self.singleArcs = OrderedDict()
		self.groupArcs = OrderedDict()
		self.groupArcsBetweenNode = OrderedDict()
		self.arcOrder = []
		self.singles = []  # Dummy list to keep track of unsorted single arcs

		self.orderArcs()
		self.separateArcs()
		self.setorderOfspecies()

		############ Constants/Equations ##############

		self.eq_used = [] # list containing all equation used to create the equation set
		self.eq_order = [] # list containing equations from eq_used in correct computational order
		self.vars_used = [] # list of all variables used for the models
		self.vars_used_const = [] # list of all constants used for the model
		self.constNotNodeOrArc = OrderedDict() # Dictionary containing initialized constatns whom does not belong to arcs or nodes
		self.initializedNodes = [] # list containing nodes initialized as a unsing instansiateUnit
		self.initializedArcs = [] # list containing arcs initialized as a unsing instansiateUnit
		self.outputNodes = {} # Dictionary containing initialized nodes after assembleOutput() has been executed
		self.outputArcs = {} # Dictionary containing initialized arcs after assembleOutput() has been executed
		self.outputConst = {} # Dictionary containing initialized constants that does not belong to arcs or nodes
							  # after assembleOutput() has been executed

		########## Initial state calculation ###########

		self.variableTree = {} # dictionary with a tree expantion of all the vaiables in the system
		self.vars_used_VT = [] # Variables used to make the variable tree
		self.compVarSet = [] # Set of variables that can calculate the initial states. If empty, the sugested set was
							 # not complete or there has been no sugested sets.
		self.eq_used_VT = [] # Equations used to calculate initial states
		self.eq_order_VT = [] # Equations used to calculate initial states in correct computational order

	############################## NODE SEPARATION ############################

	def openingFunction(self):
		with open(self.filename_model, 'r') as json_data:
			self.data = json.load(json_data, object_pairs_hook=OrderedDict)
		# Opening the equations and variable file for the ontology used for
		with open(self.filename_equations, 'r') as json_data:
			self.equations = json.load(json_data, object_pairs_hook=OrderedDict)
		with open(self.filename_variables, 'r') as json_data:
			self.variables = json.load(json_data, object_pairs_hook=OrderedDict)
		with open(self.filename_typed_tokens, 'r') as json_data:
			self.typed = json.load(json_data, object_pairs_hook=OrderedDict)

	def orderFunc(self):
		for nodes, items in self.data['nodes'].items():
			if items['class'] == 'node_simple':
				self.nodeOrder.append(nodes)

	def recursionGroups(self, node, children):
		groupChildren = []
		for child in children:
			if self.data['ID_tree'][str(child)]['children'] != []:
				self.recursionGroups(str(child), self.data['ID_tree'][str(child)]['children'])
				index = children.index(child)
				groupChildren.append(children[index])
				children.pop(index)
		if children  == []:
			print('{node} contains only group nodes'.format(node = node))
		else:
			for child in children:
				if self.data['nodes'][str(child)]["type"] == 'constant':
					index = children.index(child)
					children.pop(index)
			self.groupDict[node] = {}
			self.groupDict[node]['name'] = self.data['nodes'][node]['name']
			self.groupDict[node]['children'] = children
			self.groupDict[node]['groupChildren'] = groupChildren

	def separateNodes(self):

		# First groups

		for nodes in self.data['ID_tree']:
			if nodes == '0':
				continue
			elif self.data['ID_tree'][nodes]['children'] != []:
				self.recursionGroups(nodes, self.data['ID_tree'][nodes]['children'])


		# Then single and reservoir

		for nodes in self.data['nodes']:
			if nodes == '0':
				continue
			elif self.data['nodes'][nodes]["type"] == 'node_composite':
				for node in self.groupDict:
					if nodes == node:
						self.groupDict[node]['name'] =  self.data['nodes'][nodes]['name']
			elif self.data['nodes'][nodes]["type"] == 'constant':
				self.reservoirDict[nodes] = {}
				self.reservoirDict[nodes]['name'] = self.data['nodes'][nodes]['name']
			elif self.data['nodes'][nodes]["type"] == 'dynamic':
				add = True
				for node in self.groupDict:
					if self.groupDict[node]['children'].__contains__(int(nodes)):
						add = False
				if add == True:
					self.singleDict[nodes] = {}
					self.singleDict[nodes]['name'] = self.data['nodes'][nodes]['name']

	def addNumberOfSpecies(self):
		for node, feature in self.groupDict.items():
			feature['orderOfspecies'] = []
			feature['conversions'] = []
			for i in range(len(feature['children'])):
				feature['orderOfspecies'].append([])
				feature['conversions'].append([])

		for nodes, items in self.data['nodes'].items():
			# Run through groups first
			for node, feature in self.groupDict.items():
				if feature['children'].__contains__(int(nodes)):
					index = feature['children'].index(int(nodes))
					for tokens in items['tokens']:
						if tokens == 'mass':
							if self.data['nodes'][nodes]['tokens'][tokens] == []:
								feature['orderOfspecies'][index] = None
							else:
								feature['orderOfspecies'][index] = self.data['nodes'][nodes]['tokens'][tokens]
							if not items['injected_conversions']:
								feature['conversions'][index] = None
							else:
								feature['conversions'][index] = items['injected_conversions']['mass']

			for node, feature in self.reservoirDict.items():
				if node == nodes:
					for tokens in items['tokens']:
						if tokens == 'mass':
							if self.data['nodes'][nodes]['tokens'][tokens] == []:
								feature['orderOfspecies'] = None
							else:
								feature['orderOfspecies'] = self.data['nodes'][nodes]['tokens'][tokens]

			for node, feature in self.singleDict.items():
				if node == nodes:
					for tokens in items['tokens']:
						if tokens == 'mass':
							if self.data['nodes'][nodes]['tokens'][tokens] == []:
								feature['orderOfspecies'] = None
							else:
								feature['orderOfspecies'] = self.data['nodes'][nodes]['tokens'][tokens]
							if not items['injected_conversions']:
								feature['conversions'] = None
							else:
								feature['conversions'] = items['injected_conversions']['mass']
		# Creats a list of all species within a group
		for nodes, items in self.groupDict.items():
			items['species'] = []
			for node in items['orderOfspecies']:
				if node == None:
					continue
				else:
					for index in range(len(node)):
						if items['species'].__contains__(node[index]):
							continue
						else:
							items['species'].append(node[index])
			if items['species'] == []:
				items['species'].append(None)


	############################### ARC SEPARATION ################################

	def orderArcs(self):
		for arcs in self.data['arcs']:
			self.arcOrder.append(arcs)

	def separateArcs(self):
		self.singles = self.arcOrder # Dummy list to keep track of unsorted arcs
		######## Extracting arcs that are connected to reservoirs first #########
		for arcs, items in self.data['arcs'].items():
			if str(items['source']) in self.reservoirDict or str(items['sink']) in self.reservoirDict:
				self.singleArcs[arcs] = {}
				self.singleArcs[arcs]['source'] = str(items['source'])
				self.singleArcs[arcs]['sink'] = str(items['sink'])
				self.singleArcs[arcs]['token'] = items['token']
				# Removing already sorted arcs to determine remaining arcs to be put into the single dictionary
				index = self.singles.index(arcs)
				self.singles.pop(index)

		####### Extract groups within nodes ########
		for scenes, items in self.data['scenes'].items():
			if scenes == '0':
				continue
			elif len(items['nodes']) == 0:
				continue
			else:
				self.groupArcs[scenes] = {}
				self.groupArcs[scenes]['tokens'] = {}
				for arcs in items['arcs']:
					if ((self.groupDict[scenes]['children'].__contains__(self.data['arcs'][arcs]['source'])
						or
						self.groupDict[scenes]['groupChildren'].__contains__(self.data['arcs'][arcs]['source']))
						and
						(self.groupDict[scenes]['children'].__contains__(self.data['arcs'][arcs]['sink'])
						or
						self.groupDict[scenes]['groupChildren'].__contains__(self.data['arcs'][arcs]['sink']))):
						if self.data['arcs'][arcs]['token'] in self.groupArcs[scenes]['tokens']:
							self.groupArcs[scenes]['tokens'][self.data['arcs'][arcs]['token']]['arcs'].append(arcs)
						else:
							self.groupArcs[scenes]['tokens'][self.data['arcs'][arcs]['token']] = {}
							self.groupArcs[scenes]['tokens'][self.data['arcs'][arcs]['token']]['arcs'] = []
							self.groupArcs[scenes]['tokens'][self.data['arcs'][arcs]['token']]['arcs'].append(arcs)
						# Removing already sorted arcs to determine remaining arcs to be put into the single dictionary
						index = self.singles.index(arcs)
						self.singles.pop(index)
		####### Groups outside/between group nodes ###########
		# Establish all arcs that are connected to the group
		for groups in self.groupArcs:
			connected_arcs = list(self.data['scenes'][groups]['arcs'].keys())
			self.groupArcs[groups]['conn_arcs'] = connected_arcs
		# Check if lists in different groups contain some of the same elements
		for groups, items in self.groupArcs.items():
			for group, item in self.groupArcs.items():
				if groups == group:
					continue
				else:
					string = '{name2}|{name1}'.format(name1 = groups,
														  name2 = group)
					if self.groupArcsBetweenNode.__contains__(string):
						continue
					else:
						commonarcs = list(set(items['conn_arcs'])&set(item['conn_arcs']))
						string = '{name1}|{name2}'.format(name1 = groups,
														  name2 = group)
						self.groupArcsBetweenNode[string] = {}
						self.groupArcsBetweenNode[string]['com_arcs'] = commonarcs
		# Establish tokens of the arcs between group nodes
		for groups , items in self.groupArcsBetweenNode.items():
			items['tokens'] = {}
			for arcs in items['com_arcs']:
				if self.data['arcs'][arcs]['token'] in items['tokens']:
					items['tokens'][self.data['arcs'][arcs]['token']]['arcs'].append(arcs)
				else:
					items['tokens'][self.data['arcs'][arcs]['token']] = {}
					items['tokens'][self.data['arcs'][arcs]['token']]['arcs'] = []
					items['tokens'][self.data['arcs'][arcs]['token']]['arcs'].append(arcs)
				# Removing already sorted arcs to determine remaining arcs to be put into the single dictionary
				index = self.singles.index(arcs)
				self.singles.pop(index)
		######## Collect remaining single arcs #########
		for arcs in self.singles:
			self.singleArcs[arcs] = {}
			self.singleArcs[arcs]['source'] = self.data['arcs'][arcs]['source']
			self.singleArcs[arcs]['sink'] = self.data['arcs'][arcs]['sink']
			self.singleArcs[arcs]['token'] = self.data['arcs'][arcs]['token']

	def setorderOfspecies(self):
		for arcs, items in self.data['arcs'].items():
			# Setting order for single arcs
			if arcs in self.singleArcs:
				self.singleArcs[arcs]['orderOfspecies'] = items['typed_tokens']
			# Setting order for arcs within nodes
			for groups, item in self.groupArcs.items():
				for tokens in item['tokens']:
					if 'orderOfspecies' in item['tokens'][tokens]:
						if item['tokens'][tokens]['arcs'].__contains__(arcs):
							index = item['tokens'][tokens]['arcs'].index(arcs)
							item['tokens'][tokens]['orderOfspecies'][index] = items['typed_tokens']
					else:
						item['tokens'][tokens]['orderOfspecies'] = [0]*len(item['tokens'][tokens]['arcs'])
						if item['tokens'][tokens]['arcs'].__contains__(arcs):
							index = item['tokens'][tokens]['arcs'].index(arcs)
							item['tokens'][tokens]['orderOfspecies'][index] = items['typed_tokens']
			# Setting order for arcs between groups
			for groups, item in self.groupArcsBetweenNode.items():
				for tokens in item['tokens']:
					if 'orderOfspecies' in item['tokens'][tokens]:
						if item['tokens'][tokens]['arcs'].__contains__(arcs):
							index = item['tokens'][tokens]['arcs'].index(arcs)
							item['tokens'][tokens]['orderOfspecies'][index] = items['typed_tokens']
					else:
						item['tokens'][tokens]['orderOfspecies'] = [0]*len(item['tokens'][tokens]['arcs'])
						if item['tokens'][tokens]['arcs'].__contains__(arcs):
							index = item['tokens'][tokens]['arcs'].index(arcs)
							item['tokens'][tokens]['orderOfspecies'][index] = items['typed_tokens']

    ############################ CONSTANTS/EQUATIONS ##############################

	def recFunc(self,eq_needed):
		if self.eq_used.__contains__(eq_needed):
			pass
		else:
			self.eq_used.append(eq_needed)
			vars_needed = self.equations[eq_needed]['incidence_list']
			for var in vars_needed:
				if self.vars_used.__contains__(var):
					continue
				elif var in self.states:
					continue
				else:
					self.vars_used.append(var)
					if self.variables[var]['equation_list'] == []:
						if self.variables[var]["type"] == 'constant':
							self.vars_used_const.append(var)
					else:
						equations_needed = self.variables[var]['equation_list']
						if len(equations_needed) > 1:
							for eq in equations_needed:
								string = '{lhs} = {rhs} ({num}) \n'.format(lhs = self.equations[eq]['lhs'],
																		rhs = self.equations[eq]['rhs'],
																		num = eq)
								print(string)
							string = 'Which equation would you like to use to calculate {lhs}?\nSelect one of the equations above: '.format(lhs = self.equations[eq]['lhs'])
							eq = str(input(string))
							self.recFunc(eq)
						else:
							self.recFunc(equations_needed[0])

	def addVarSet(self,varSet):
		for var in varSet:
			# Determining if the variable is a state or a constant
			if self.variables[var]["type"] == 'state':
				if var in self.compVarSet:
					continue
				elif self.compVarSet == []:
					key = 'states'
				else:
					continue
			elif var in self.compVarSet:
				key = 'states'
			else:
				key = 'vars'
			# Adding constant with index set for nodes

			if self.variables[var]['index_structures'] == ['node'] or self.variables[var]['index_structures'] == ['node & species']:
				for nodes, items in self.reservoirDict.items():
					if self.variables[var]['index_structures'] == ['node & species']:
						if items['orderOfspecies'] == None:
							items[key][var] = np.ones((1,1))
						else:
							items[key][var] = np.ones((len(items['orderOfspecies']),1))
					else:
						items[key][var] = np.ones((1,1))

				for nodes, items in self.singleDict.items():
					if self.variables[var]['index_structures'] == ['node & species']:
						if items['orderOfspecies'] == None:
							items[key][var] = np.ones((1,1))
						else:
							items[key][var] = np.ones((len(items['orderOfspecies']),1))
					else:
						items[key][var] = np.ones((1,1))

				for nodes, items in self.groupDict.items():
					if self.variables[var]['index_structures'] == ['node & species']:
						array = []
						for i in range(len(items['orderOfspecies'])):
							if items['orderOfspecies'][i] == None:
								temp = np.ones((1,1))
							else:
								temp = np.ones((len(items['orderOfspecies'][i]),1))
							array.append(temp)
						items[key][var] = array
					else:
						array = []
						for i in range(len(items['orderOfspecies'])):
							array.append(np.ones((1,1)))
						items[key][var] = array
			# Adding constants with index set for arcs
			elif self.variables[var]['index_structures'] == ['arc'] or self.variables[var]['index_structures'] == ['arc & species']:
				for arcs, items in self.singleArcs.items():
					if self.variables[var]['index_structures'] == ['arc & species']:
						if items['orderOfspecies'] == None:
							items[key][var] = np.ones((1,1))
						else:
							items[key][var] = np.ones((len(items['orderOfspecies']),1))
					else:
						items[key][var] = np.ones((1,1))
				for arcs, feature in self.groupArcs.items():
					for token, items in feature['tokens'].items():
						if self.variables[var]['index_structures'] == ['arc & species']:
							array = []
							for i in range(len(items['orderOfspecies'])):
								if items['orderOfspecies'][i] == None:
									temp = np.ones((1,1))
								else:
									temp = np.ones((len(items['orderOfspecies'][i]),1))
								array.append(temp)
							items[key][var] = array
						else:
							array = []
							for i in range(len(items['orderOfspecies'])):
								array.append(np.ones((1,1)))
							items[key][var] = array
				for arcs, feature in self.groupArcsBetweenNode.items():
					for token, items in feature['tokens'].items():
						if self.variables[var]['index_structures'] == ['arc & species']:
							array = []
							for i in range(len(items['orderOfspecies'])):
								if items['orderOfspecies'][i] == None:
									temp = np.ones((1,1))
								else:
									temp = np.ones((len(items['orderOfspecies'][i]),1))
								array.append(temp)
							items[key][var] = array
						else:
							array = []
							for i in range(len(items['orderOfspecies'])):
								array.append(np.ones((1,1)))
							items[key][var] = array
			else:
				self.addConstNotNodeOrArc(var)

	def addConstNotNodeOrArc(self, var):
		if self.variables[var]['index_structures'] == []:
			indexing = None
		else:
			indexing = self.variables[var]['index_structures'][0]
		temp = True
		for token, item in self.typed.items():
			string = '{tokens}_conversion'.format(tokens = token)
			if indexing == token:
				self.constNotNodeOrArc[var] = {}
				self.constNotNodeOrArc[var]['value'] = np.ones((len(item['instances']),1))
				self.constNotNodeOrArc[var]['order'] = item['instances']
				temp = False
			elif string == indexing:
				conversions = []
				for conversion in item['conversions']:
					temps = '{reactants} -> {products}'.format(reactants = conversion['reactants'],
															  products = conversion['products'])
					conversions.append(temps)
				self.constNotNodeOrArc[var] = {}
				self.constNotNodeOrArc[var]['value'] = np.ones((len(conversions),1))
				self.constNotNodeOrArc[var]['order'] = conversions
				temp = False
			elif indexing == 'node & species_conversion':
				size = 0
				order = []
				nodesOrder = []
				for node, item in self.groupDict:
					for slot in item['conversions']:
						index = item['conversions'].index(slot)
						nodesOrder.append(str(item['children'][index]))
						order.append([])
						if slot == None:
							size += 1
							order[-1] = None
						else:
							size += len(slot)
							order[-1] = slot
				for node, item in self.singleDict:
					nodesOrder.append(node)
					order.append([])
					if item['conversions'] == None:
						size += 1
						order[-1] = None
					else:
						size += len(item['conversions'])
						order[-1] = slot
				self.constNotNodeOrArc[var] = {}
				self.constNotNodeOrArc[var]['value'] = np.ones((size,1))
				self.constNotNodeOrArc[var]['order'] = order
				self.constNotNodeOrArc[var]['nodeOrder'] = nodesOrder
				temp = False
		if temp:
			self.constNotNodeOrArc[var] = {}
			self.constNotNodeOrArc[var]['value'] = np.ones((1,1))
			self.constNotNodeOrArc[var]['order'] = ['none']

	def arrangeEquations(self):
		self.temp_order = []
		state_eq_indexes = []
		for eq in self.eq_used:
			if self.states.__contains__(self.equations[eq]['lhs']):
				index = self.eq_used.index(eq)
				state_eq_indexes.append(index)
		state_eq_indexes.pop(0)
		temp = []
		subsets = []
		for eqs in self.eq_used:
			index = self.eq_used.index(eqs)
			if state_eq_indexes.__contains__(index) or eqs == self.eq_used[-1]:
				if eqs == self.eq_used[-1]:
					temp.append(eqs)
				self.temp_order.append(list(reversed(temp)))
				temp = []
				temp.append(eqs)
			else:
				temp.append(eqs)
		for sets in self.temp_order:
			for i in range(len(sets)):
				self.eq_order.append(sets[i])

	### Main functions ###

	def equationSetBuilder(self):
		for state in self.states:
			eq_needed = self.variables[state]['equation_list'][0]
			self.vars_used.append(state)
			self.vars_used_const.append(state)
			self.recFunc(eq_needed)

		self.arrangeEquations()

		return 'Equation set has been instansiated.'

	# If a different set of variables is going to be used to calculated the inital states
	# calculateInitState() has be used with said variable set before addVariableAndStates() given
	# that the variable set is complete.

	def addVariablesAndStates(self):

		for nodes in self.reservoirDict:
			self.reservoirDict[nodes]['vars'] = {}
			self.reservoirDict[nodes]['states'] = {}
		for nodes in self.singleDict:
			self.singleDict[nodes]['vars'] = {}
			self.singleDict[nodes]['states'] = {}
		for nodes in self.groupDict:
			self.groupDict[nodes]['vars'] = {}
			self.groupDict[nodes]['states'] = {}
		for arcs, items in self.singleArcs.items():
			items['vars'] = {}
		for arcs, items in self.groupArcs.items():
			for tokens, item in items['tokens'].items():
				item['vars'] = {}
		for arcs, items in self.groupArcsBetweenNode.items():
			for tokens, item in items['tokens'].items():
				item['vars'] = {}
		self.addVarSet(self.compVarSet)
		self.addVarSet(self.vars_used_const)
		self.assembleOutput()

	######################## INITIAL STATE CALCULATION ###########################

	def recFuncVarTree(self, eq_needed):
		vars_needed = self.equations[eq_needed]['incidence_list']
		temp_dict = {}
		for var in vars_needed:
			if self.states.__contains__(var):
				temp_dict[var] = {}
			else:
				if var in self.vars_used_VT:
					continue
				else:
					self.vars_used_VT.append(var)
				if self.variables[var]['equation_list'] == []:
					continue
				else:
					if self.variables[var]["type"] == 'network':
						continue
					eq_needed = self.variables[var]['equation_list']
					if len(eq_needed) > 1:
						for eq in eq_needed:
							if self.eq_used.__contains__(eq):
								index = eq_needed.index(eq)
								break
						lower_dict = self.recFuncVarTree(eq_needed[index])
						temp_dict[var] = lower_dict
					else:
						lower_dict = self.recFuncVarTree(eq_needed[0])
						temp_dict[var] = lower_dict
		return temp_dict

	def makeVariableTree(self):
		for state in self.states:
			eq_needed = self.variables[state]['equation_list'][0]
			self.vars_used_VT = []
			self.vars_used_VT.append(state)
			temp_dict = self.recFuncVarTree(eq_needed)
			self.variableTree[state] = temp_dict
		with open('variableTree.json', 'msg_box') as fv:
		 	json.dump(self.variableTree, fv, sort_keys = True, indent = 4)

	def checkConst(self,var):
		eq = self.variables[var]['equation_list']
		val = True
		if len(eq) > 1:
			for e in eq:
				if e in self.eq_used:
					vars_used = self.equations[e]['incidence_list']
					for v in vars_used:
						if self.variables[v]["type"] == 'constant':
							continue
						elif self.variables[v]["type"] == 'network':
							continue
						else:
							val = False
					break
		else:
			e = eq[0]
			vars_used = self.equations[e]['incidence_list']
			for v in vars_used:
				if self.variables[v]["type"] == 'constant':
					continue
				elif self.variables[v]["type"] == 'network':
					continue
				else:
					val = False
		return val

	def recFuncVarCheck(self,varSet,treeDict):
		complete = False
		counter = 0
		check = 0
		for key in treeDict:
			check += 1
			if key in varSet:
				counter += 1
				if key in self.compVarSet:
					pass
				else:
					self.compVarSet.append(key)
			else:
				branch = treeDict[key]
				if not branch:
					val = self.checkConst(key)
				else:
					val = self.recFuncVarCheck(varSet,branch)
				if val == True:
					counter += 1
		if check == counter:
			complete = True
		return complete

	def checkCompleteVarSet(self,varSet):
		complete = False
		counter = 0
		check = 0
		for state in self.variableTree:
			check += 1
			if state in varSet:
				counter += 1
			else:
				branch = self.variableTree[state]
				val = self.recFuncVarCheck(varSet,branch)
				if val == True:
					counter += 1
		if check == counter:
			complete = True
		return complete

	def recFuncEqVT(self,eq_needed,varSet):
		if self.eq_used_VT.__contains__(eq_needed):
			pass
		else:
			self.eq_used_VT.append(eq_needed)
			vars_needed = self.equations[eq_needed]['incidence_list']
			for var in vars_needed:
				if varSet.__contains__(var):
					continue
				elif self.variables[var]['equation_list'] == []:
					continue
				else:
					equations_needed = self.variables[var]['equation_list']
					if len(equations_needed) > 1:
						for eqs in equations_needed:
							if eq_used.__contains__(eqs):
								index = equations_needed.index(eqs)
						self.recFuncEqVT(equations_needed[index],varSet)
					else:
						self.recFuncEqVT(equations_needed[0],varSet)

	def arrangeEquationsVT(self):
		self.temp_order = []
		state_eq_indexes = []
		for eq in self.eq_used_VT:
			if self.states.__contains__(self.equations[eq]['lhs']):
				index = self.eq_used_VT.index(eq)
				state_eq_indexes.append(index)
		state_eq_indexes.pop(0)
		temp = []
		subsets = []
		for eqs in self.eq_used_VT:
			index = self.eq_used_VT.index(eqs)
			if state_eq_indexes.__contains__(index) or eqs == self.eq_used_VT[-1]:
				if eqs == self.eq_used_VT[-1]:
					temp.append(eqs)
				self.temp_order.append(list(reversed(temp)))
				temp = []
				temp.append(eqs)
			else:
				temp.append(eqs)
		for sets in self.temp_order:
			for i in range(len(sets)):
				self.eq_order_VT.append(sets[i])

	def buildEquationSetVarTree(self,varSet):
		for state in self.states:
			if varSet.__contains__(state):
				continue
			eq_needed = self.variables[state]['equation_list'][0]
			self.recFuncEqVT(eq_needed,varSet)

		self.arrangeEquationsVT()

	### Main function ###

	def calculateInitState(self,varSet = []):
		self.makeVariableTree()
		val = self.checkCompleteVarSet(varSet)
		if val == True:
			self.buildEquationSetVarTree(self.compVarSet)
			message = 'Sugested variable set was a complete set'
		else:
			self.compVarSet = []
			message = 'The sugested variable set is not complete'
		return message

	############################## INITIALIZATION ################################

	#### Individual functions ####

	def initializeSingleNode(self,key):
		if self.initializedNodes.__contains__(key):
			pass
		else:
			self.initializedNodes.append(key)
		if key in self.reservoirDict:
			items = self.reservoirDict[key]
		if key in self.singleDict:
			items = self.singleDict[key]
		# Initializing variables
		for var in items['vars']:
			if self.variables[var]['index_structures'] == ['node & species']:
				if items['orderOfspecies'] == None:
					inputstr = 'Set value for {var} in {name}: '.format(var = var,
																		name = items['name'])
					val = float(input(inputstr))
					items['vars'][var] *= val
				else:
					for species in items['orderOfspecies']:
						index = items['orderOfspecies'].index(species)
						inputstr = 'Set value for {var} of {specie} in {name}: '.format(
																					  var = var,
																					  name = items['name'],
																					  specie = species)
						val = float(input(inputstr))
						items['vars'][var][index] *= val
			else:
				inputstr = 'Set value for {var} in {name}: '.format(var = var,
																	name = items['name'])
				val = float(input(inputstr))
				items['vars'][var] *= val
		# Initializing states
		for states in items['states']:
			if self.variables[states]['index_structures'] == ['node & species']:
				if items['orderOfspecies'] == None:
					inputstr = 'Set initial value for {state} in {name}: '.format(state = states,
																				  name = items['name'])
					val = float(input(inputstr))
					items['states'][states] *= val
				else:
					for species in items['orderOfspecies']:
						index = items['orderOfspecies'].index(species)
						inputstr = 'Set initial value for {state} of {specie} in {name}: '.format(
																					  state = states,
																					  name = items['name'],
																					  specie = species)
						val = float(input(inputstr))
						items['states'][states][index] *= val
			else:
				inputstr = 'Set initial value for {state} in {name}: '.format(state = states,
																				  name = items['name'])
				val = float(input(inputstr))
				items['states'][states] *= val

	def initializeGroupNode(self,key):
		if self.initializedNodes.__contains__(key):
			return
		else:
			self.initializedNodes.append(key)

		items = self.groupDict[key]

		for var in items['vars']:
			if self.variables[var]['index_structures'] == ['node & species']:
				for species in items['species']:
					if species == None:
						inputstr = 'Set value for {var} in all uninitalized nodes in group {name}: '.format(
																								var = var,
																								name = items['name'])
						val = float(input(inputstr))
						for i in range(len(items['vars'][var])):
							if self.initializedNodes.__contains__(str(items['children'][i])):
								continue
							items['vars'][var][i] *= val
					else:
						inputstr = 'Set value for {var} of {specie} in all uninitalized nodes in group {name}: '.format(
																								var = var,
																								name = items['name'],
																								specie = species)
						val = float(input(inputstr))
						for i in range(len(items['orderOfspecies'])):
							if self.initializedNodes.__contains__(str(items['children'][i])):
								continue
							if items['orderOfspecies'][i].__contains__(species):
								index = items['orderOfspecies'][i].index(species)
								items['vars'][var][i][index] *= val
			else:
				inputstr = 'Set value for {var} in all uninitalized nodes in group {name}: '.format(
																								var = var,
																								name = items['name'])
				val = float(input(inputstr))
				for i in range(len(items['vars'][var])):
					if self.initializedNodes.__contains__(str(items['children'][i])):
						continue
					items['vars'][var][i] *= val
		for states in items['states']:
			if self.variables[states]['index_structures'] == ['node & species']:
				for species in items['species']:
					if species == None:
						inputstr = 'Set initial value for {state} in all uninitalized nodes in group {name}: '.format(
																								state = states,
																								name = items['name'])
						val = float(input(inputstr))
						for i in range(len(items['vars'][var])):
							if self.initializedNodes.__contains__(str(items['children'][i])):
								continue
							else:
								items['vars'][var][i] *= val
					else:
						inputstr = 'Set initial value for {state} of {specie} in all uninitalized nodes in group {name}: '.format(
																								state = states,
																								name = items['name'],
																								specie = species)
						val = float(input(inputstr))
						for i in range(len(items['orderOfspecies'])):
							if self.initializedNodes.__contains__(str(items['children'][i])):
								continue
							if items['orderOfspecies'][i].__contains__(species):
								index = items['orderOfspecies'][i].index(species)
								items['states'][states][i][index] *= val
			else:
				inputstr = 'Set initial value for {state} in all uninitalized nodes in group {name}: '.format(
																								state = states,
																								name = items['name'])
				val = float(input(inputstr))
				for i in range(len(items['states'][states])):
					if self.initializedNodes.__contains__(str(items['children'][i])):
						continue
					items['states'][states][i] *= val
		self.initializeGroupArcs(key)

		for child in items['groupChildren']:
			if child in self.initializedNodes:
				pass
			else:
				self.initializeGroupNode(str(child))

	def initializeSingleArc(self, key):
		if self.initializedArcs.__contains__(key):
			pass
		else:
			self.initializedArcs.append(key)
		items = self.singleArcs[key]
		# for items in self.singleArcs[key]:
		for var in items['vars']:
			if self.variables[var]['index_structures'] == ['arc & species']:
				if items['orderOfspecies'] == None:
					inputstr = 'Set value for {var} in arc {name} with token {token}: '.format(
																					token = items['token'],
																					var = var,
																					name = key)
					val = float(input(inputstr))
					items['vars'][var] *= val
				else:
					for species in items['orderOfspecies']:
						index = items['orderOfspecies'].index(species)
						inputstr = 'Set value for {var} of {specie} in arc {name} with token {token}: '.format(
																						token = items['token'],
																					    var = var,
																					    name = key,
																					    specie = species)
						val = float(input(inputstr))
						items['vars'][var][index] *= val
			else:
				inputstr = 'Set value for {var} in arc {name}: '.format(var = var,
																				token = items['token'],
																				name = key)
				val = float(input(inputstr))
				items['vars'][var] *= val

	def initializeGroupArcs(self,key):
		if self.initializedArcs.__contains__(key):
			pass
		else:
			self.initializedArcs.append(key)
		feature = self.groupArcs[key]
		for tokens, items in feature['tokens'].items():
			for var in items['vars']:
					if self.variables[var]['index_structures'] == ['node & species']:
						for species in items['species']:
							if species == None:
								inputstr = 'Set value for {var} in all uninitalized arcs in group {name} with token {token}: '.format(
																										token = tokens,
																										var = var,
																										name = arcs)
								val = float(input(inputstr))
								for i in range(len(items['vars'][var])):
									if self.initializedArcs.__contains__(str(items['arcs'][i])):
										continue
									items['vars'][var][i] *= val
							else:
								inputstr = 'Set value for {var} of {specie} in all uninitalized arcs in group {name} with token {token}: '.format(
																										token = tokens,
																										var = var,
																										name = arcs,
																										specie = species)
								val = float(input(inputstr))
								for i in range(len(items['orderOfspecies'])):
									if items['orderOfspecies'][i].__contains__(species):
										if self.initializedArcs.__contains__(str(items['arcs'][i])):
											continue
										index = items['orderOfspecies'][i].index(species)
										items['vars'][var][i][index] *= val
					else:
						inputstr = 'Set value for {var} in all uninitalized arcs in group {name} with token {token}: '.format(
																										token = tokens,
																										var = var,
																										name = arcs)
						val = float(input(inputstr))
						for i in range(len(items['vars'][var])):
							if self.initializedArcs.__contains__(str(items['arcs'][i])):
								continue
							items['vars'][var][i] *= val

	def initializeGroupArcsBetweenNodes(self,key):
		if self.initializedArcs.__contains__(key):
			pass
		else:
			self.initializedArcs.append(key)
		feature = self.groupArcsBetweenNode[key]
		for tokens, items in feature['tokens'].items():
			for var in items['vars']:
					if self.variables[var]['index_structures'] == ['node & species']:
						for species in items['species']:
							if species == None:
								inputstr = 'Set value for {var} in all uninitalized arcs in group {name} with token {token}: '.format(
																										token = tokens,
																										var = var,
																										name = arcs)
								val = float(input(inputstr))
								for i in range(len(items['vars'][var])):
									if self.initializedArcs.__contains__(str(items['arcs'][i])):
										continue
									items['vars'][var][i] *= val
							else:
								inputstr = 'Set value for {var} of {specie} in all uninitalized arcs in group {name} with token {token}: '.format(
																										token = tokens,
																										var = var,
																										name = arcs,
																										specie = species)
								val = float(input(inputstr))
								for i in range(len(items['orderOfspecies'])):
									if items['orderOfspecies'][i].__contains__(species):
										if self.initializedArcs.__contains__(str(items['arcs'][i])):
											continue
										index = items['orderOfspecies'][i].index(species)
										items['vars'][var][i][index] *= val
					else:
						inputstr = 'Set value for {var} in all uninitalized arcs in group {name} with token {token}: '.format(
																										token = tokens,
																										var = var,
																										name = arcs)
						val = float(input(inputstr))
						for i in range(len(items['vars'][var])):
							if self.initializedArcs.__contains__(str(items['arcs'][i])):
								continue
							items['vars'][var][i] *= val

	def initializeNodeInGroup(self, groupNode, key):
	    if self.initializedNodes.__contains__(key):
	    	pass
	    else:
	    	self.initializedNodes.append(key)
	    items = self.groupDict[groupNode]
	    index = items['children'].index(int(key))
	    for var in items['vars']:
	    	if self.variables[var]['index_structures'] == ['node & species']:
	    		for species in items['species']:
	    			if species == None:
	    				inputstr = 'Set value for {var} in node {name}: '.format(
																						var = var,
																						name = key)
	    				val = float(input(inputstr))
	    				items['vars'][var][index] *= val
	    			else:
	    				inputstr = 'Set value for {var} of {specie} in node {name}: '.format(
																								var = var,
																								name = key,
																								specie = species)
	    				val = float(input(inputstr))
	    				if items['orderOfspecies'][index].__contains__(species):
	    					index2 = items['orderOfspecies'][index].index(species)
	    					items['vars'][var][index][index2] *= val
	    	else:
	    		inputstr = 'Set value for {var} in node {name}: '.format(
																								var = var,
																								name = key)
	    		val = float(input(inputstr))
	    		items['vars'][var][index] *= val
	    for var in items['states']:
	    	if self.variables[var]['index_structures'] == ['node & species']:
	    		for species in items['species']:
	    			if species == None:
	    				inputstr = 'Set initial value for {var} in node {name}: '.format(
																						var = var,
																						name = key)
	    				val = float(input(inputstr))
	    				items['states'][var][index] *= val
	    			else:
	    				inputstr = 'Set initial value for {var} of {specie} in node {name}: '.format(
																								var = var,
																								name = key,
																								specie = species)
	    				val = float(input(inputstr))
	    				if items['orderOfspecies'][index].__contains__(species):
	    					index2 = items['orderOfspecies'][index].index(species)
	    					items['states'][var][index][index2] *= val
	    	else:
	    		inputstr = 'Set initial value for {var} in node {name}: '.format(
																								var = var,
																								name = key)
	    		val = float(input(inputstr))
	    		items['states'][var][index] *= val

	def initializeArcInGroup(self, groupArc, token, index, key):
		if self.initializedArcs.__contains__(key):
			pass
		else:
			self.initializedArcs.append(key)
		if groupArc in self.groupArcsBetweenNode:
			feature = self.groupArcsBetweenNode[groupArc]
			items = feature['tokens'][token]
		if groupArc in self.groupArcs:
			feature = self.groupArcs[groupArc]
			items = feature['tokens'][token]
		for var in items['vars']:
			if self.variables[var]['index_structures'] == ['node & species']:
				for species in items['species']:
					if species == None:
						inputstr = 'Set value for {var} in arc {name} with token {token}: '.format(
																								token = token,
																								var = var,
																								name = key)
						val = float(input(inputstr))
						items['vars'][var][index] *= val
					else:
						if items['orderOfspecies'][index].__contains__(species):
							inputstr = 'Set value for {var} of {specie} in arc {name} with token {token}: '.format(
																									token = token,
																									var = var,
																									name = key,
																									specie = species)
							val = float(input(inputstr))
							index2 = items['orderOfspecies'][index].index(species)
							items['vars'][var][index][index2] *= val
			else:
				inputstr = 'Set value for {var} in all arcs in group {name} with token {token}: '.format(
																								token = token,
																								var = var,
																								name = key)
				val = float(input(inputstr))
				items['vars'][var][index] *= val

	def initializeConstNotNodeOrArc(self):
		for var, item in self.constNotNodeOrArc.items():
			if self.variables[var]['index_structures'][0] == 'node & species_conversion':
				counter = 0
				for i in range(len(item['order'])):
					if item['order'][i] == None:
						item['value'][counter] *= 0
						counter += 1
					if type(item['order'][i]) == type([]):
						if len(item['order'][i]) > 1:
							for j in range(len(item['order'][i])):
								inputstr = 'Set value of {var} for conversion {case} in {node}: '.format(var = var,
																									  case = item['order'][i][j],
																									  node = item['nodeOrder'][i])
								val = float(input(inputstr))
								item['value'][counter] *= val
								counter += 1
						else:
							inputstr = 'Set value of {var} for conversion {case} in {node}: '.format(var = var,
																									  case = item['order'][i],
																									  node = item['nodeOrder'][i])
							val = float(input(inputstr))
							item['value'][counter] *= val
							counter += 1
			else:
				for i in range(len(item['order'])):
					inputstr = 'Set value of {var} for {case} with index set {indexset}: '.format(var = var,
																								  case = item['order'][i],
																								  indexset = self.variables[var]['index_structures'])
					val = float(input(inputstr))
					item['value'][i] *= val

	# def updatedDict(self, key, piece, update):
	# 	if (key in self.groupDict) and (piece == 'node'):
	# 		if key in self.initializedNodes:
	# 			pass
	# 		else:
	# 			self.initializedNodes.append(key)
	# 		items = self.groupDict[key]
	# 		for var in update['vars']:
	# 			if self.variables[var]['index_structures'] == ['node & species']:
	# 				if update['species'] == None:
	# 					val = update['vars'][var][0]
	# 					for i in range(len(items['vars'][var])):
	# 						if self.initializedNodes.__contains__(str(items['children'][i])):
	# 							continue
	# 						items['vars'][var][i] *= val
	# 				else:
	# 					for species in update['species']:
	# 						ind = update['species'].index()
	# 						val = update['vars'][var][i]
	# 						for i in range(len(items['orderOfspecies'])):
	# 							if self.initializedNodes.__contains__(str(items['children'][i])):
	# 								continue
	# 							if items['orderOfspecies'][i].__contains__(species):
	# 								index = items['orderOfspecies'][i].index(species)
	# 								items['vars'][var][i][index] *= val
	# 			else:
	# 				val = update['vars'][var][0]
	# 				for i in range(len(items['vars'][var])):
	# 					if self.initializedNodes.__contains__(str(items['children'][i])):
	# 						continue
	# 					items['vars'][var][i] *= val
	# 		for child in items['groupChildren']:
	# 			if child in self.initializedNodes:
	# 				continue
	# 			else:
	# 				self.updatedDict(child, piece, update)
	# 		# Updating the ouput file
	# 		for node, item in self.groupDict.items():
	# 			if node == key:
	# 				for child in item['children']:
	# 					if str(child) in self.initializedNodes:
	# 						continue
	# 					index = item['children'].index(child)
	# 					for var in item['states']:
	# 						self.outputNodes[str(child)][var] = '{val}'.format(val = item['states'][var][index])
	# 					for var in item['vars']:
	# 						self.outputNodes[str(child)][var] = '{val}'.format(val = item['vars'][var][index])
	#
	# 	elif (piece == 'arc') and ((key in self.groupArcs) or (key in self.groupArcsBetweenNode)):
	# 		if key in self.initializedArcs:
	# 			pass
	# 		else:
	# 			self.initializedArcs.append(key)
	# 		if key in self.groupArcs:
	# 			feature = self.groupArcs[key]
	# 		else:
	# 			feature = self.groupArcsBetweenNode[key]
	# 		for tokens, items in feature['tokens'].items():
	# 			for var in update['vars']:
	# 				if self.variables[var]['index_structures'] == ['node & species']:
	# 					if species == None:
	# 						val = update['vars'][var][0]
	# 						for i in range(len(items['vars'][var])):
	# 							if self.initializedArcs.__contains__(str(items['arcs'][i])):
	# 								continue
	# 							items['vars'][var][i] *= val
	# 					else:
	# 						for species in update['species']:
	# 							ind = update['species'].index(species)
	# 							val = update['vars'][var][ind]
	# 							for i in range(len(items['orderOfspecies'])):
	# 								if items['orderOfspecies'][i].__contains__(species):
	# 									if self.initializedArcs.__contains__(str(items['arcs'][i])):
	# 										continue
	# 									index = items['orderOfspecies'][i].index(species)
	# 									items['vars'][var][i][index] *= val
	# 				else:
	# 					val = update['vars'][var][0]
	# 					for i in range(len(items['vars'][var])):
	# 						if self.initializedArcs.__contains__(str(items['arcs'][i])):
	# 							continue
	# 						items['vars'][var][i] *= val
	# 		# Updating the output file
	# 		if key in self.groupArcs:
	# 			for arc, item in self.groupArcs.items():
	# 				if arc == key:
	# 					for token, items in item['tokens'].items():
	# 						for arcs in items['arcs']:
	# 							if arcs in self.initializedArcs:
	# 								continue
	# 							index = items['arcs'].index(arcs)
	# 							for var in items['vars']:
	# 								self.outputArcs[arcs][var] = '{val}'.format(val = items['vars'][var][index])
	#
	# 		if key in self.groupArcsBetweenNode:
	# 			for arc, item in self.groupArcsBetweenNode.items():
	# 				if arc == key:
	# 					for token, items in item['tokens'].items():
	# 						for arcs in items['arcs']:
	# 							if arcs in self.initializedArcs:
	# 								continue
	# 							index = items['arcs'].index(arcs)
	# 							for var in items['vars']:
	# 								self.outputArcs[arcs][var] = '{val}'.format(val = items['vars'][var][index])
	# 	else:
	# 		if piece == 'node':
	# 			if key in self.initializedNodes:
	# 				pass
	# 			else:
	# 				self.initializedNodes.append(key)
	# 			self.outputNodes[key] = update['vars']
	# 		elif piece == 'arc':
	# 			if key in self.initializedArcs:
	# 				pass
	# 			else:
	# 				self.initializedArcs.append(key)
	# 			self.outputArcs[key] = update['vars']
	# 		else:
	# 			self.outputConst = update
	#
	# #### Main functions ####

	def initializeUnit(self, key, piece):
		'''
		Purpose: Initialize a single node, arc or a group node without initializing the rest of the system.
		'''
		if piece == 'node':
			if key in self.singleDict:
				self.initializeSingleNode(key)
			if key in self.reservoirDict:
				self.initializeSingleNode(key)
			if key in self.groupDict:
				self.initializeGroupNode(key)
			for node, item in self.groupDict.items():
				if item['children'].__contains__(int(key)):
					self.initializeNodeInGroup(node,key)
		if piece == 'arc':
			if key in self.singleArcs:
				self.initializeSingleArc(key)
			for arc, feature in self.groupArcs.items():
				for tokens, item in feature['tokens'].items():
					if item['arcs'].__contains__(key):
						self.initializeArcInGroup(arc, tokens, key)
			for arc, feature in self.groupArcsBetweenNode.items():
				for tokens, item in feature['tokens'].items():
					if item['arcs'].__contains__(key):
						index = item['arcs'].index(key)
						self.initializeArcInGroup(arc, tokens, index, key)

	def initializeSystem(self):
		'''
		Purpose: Function to initialize the entire system of nodes, arcs and constants.
				 Must be runned before the assemble function to ensure that every piece is initialized.
		'''
		### Nodes ###
		for nodes in self.reservoirDict:
			if self.initializedNodes.__contains__(nodes):
				continue
			self.initializeSingleNode(nodes)

		for nodes in self.singleDict:
			if self.initializedNodes.__contains__(nodes):
				continue
			self.initializeSingleNode(nodes)

		for nodes in self.groupDict:
			if self.initializedNodes.__contains__(nodes):
				continue
			self.initializeGroupNode(nodes)
		### ARCS ###
		for arcs in self.singleArcs:
			if self.initializedArcs.__contains__(arcs):
				continue
			self.initializeSingleArc(arcs)

		for arcs in self.groupArcs:
			if self.initializedArcs.__contains__(arcs):
				continue
			self.initializeGroupArcs(arcs)

		for arcs in self.groupArcsBetweenNode:
			if self.initializedArcs.__contains__(arcs):
				continue
			self.initializeGroupArcsBetweenNodes(arcs)
		### Constants outside arc or node space ###
		self.initializeConstNotNodeOrArc()
		message = "Finished initializing the system"
		return message

	# def assembleOutput(self):
	# 	for nodes in self.nodeOrder:
	# 		self.outputNodes[nodes] = {}
	# 		if nodes in self.singleDict:
	# 			for var in self.singleDict[nodes]['states']:
	# 				print('HALLA: ', self.singleDict[nodes]['states'][var])
	# 				self.outputNodes[nodes][var] = copy.copy(self.singleDict[nodes]['states'][var])
	# 			for var in self.singleDict[nodes]['vars']:
	# 				self.outputNodes[nodes][var] = copy.copy(self.singleDict[nodes]['vars'][var])
	# 			continue
	# 		if nodes in self.reservoirDict:
	# 			for var in self.reservoirDict[nodes]['states']:
	# 				self.outputNodes[nodes][var] = copy.copy(self.reservoirDict[nodes]['states'][var])
	# 			for var in self.reservoirDict[nodes]['vars']:
	# 				self.outputNodes[nodes][var] = copy.copy(self.reservoirDict[nodes]['vars'][var])
	# 			continue
	# 		for node, item in self.groupDict.items():
	# 			if item['children'].__contains__(int(nodes)):
	# 				index = item['children'].index(int(nodes))
	# 				for var in item['states']:
	# 					self.outputNodes[nodes][var] = copy.copy(item['states'][var][index])
	# 				for var in item['vars']:
	# 					self.outputNodes[nodes][var] = copy.copy(item['vars'][var][index])
	#
	# 	for arcs in self.data['arcs']:
	# 		self.outputArcs[arcs] = {}
	# 		if arcs in self.singleArcs:
	# 			for var in self.singleArcs[arcs]['vars']:
	# 				self.outputArcs[arcs][var] = copy.copy(self.singleArcs[arcs]['vars'][var])
	# 		for arc, item in self.groupArcs.items():
	# 			for token, items in item['tokens'].items():
	# 				if items['arcs'].__contains__(arcs):
	# 					index = items['arcs'].index(arcs)
	# 					for var in items['vars']:
	# 						self.outputArcs[arcs][var] = copy.copy(items['vars'][var][index])
	# 		for arc, item in self.groupArcsBetweenNode.items():
	# 			for token, items in item['tokens'].items():
	# 				if items['arcs'].__contains__(arcs):
	# 					index = items['arcs'].index(arcs)
	# 					for var in items['vars']:
	# 						self.outputArcs[arcs][var] = copy.copy(items['vars'][var][index])
	# 	for const in self.constNotNodeOrArc:
	# 		self.outputConst[const] = '{}'.format(self.constNotNodeOrArc[const]['value'])

	def assembleOutput(self):
		for nodes in self.nodeOrder:
			self.outputNodes[nodes] = {}
			if nodes in self.singleDict:
				for var in self.singleDict[nodes]['states']:
					self.outputNodes[nodes][var] = '{val}'.format(val = self.singleDict[nodes]['states'][var])
				for var in self.singleDict[nodes]['vars']:
					self.outputNodes[nodes][var] = '{val}'.format(val = self.singleDict[nodes]['vars'][var])
				continue
			if nodes in self.reservoirDict:
				for var in self.reservoirDict[nodes]['states']:
					self.outputNodes[nodes][var] = '{val}'.format(val = self.reservoirDict[nodes]['states'][var])
				for var in self.reservoirDict[nodes]['vars']:
					self.outputNodes[nodes][var] = '{val}'.format(val = self.reservoirDict[nodes]['vars'][var])
				continue
			for node, item in self.groupDict.items():
				if item['children'].__contains__(int(nodes)):
					index = item['children'].index(int(nodes))
					for var in item['states']:
						self.outputNodes[nodes][var] = '{val}'.format(val = item['states'][var][index])
					for var in item['vars']:
						self.outputNodes[nodes][var] = '{val}'.format(val = item['vars'][var][index])

		for arcs in self.data['arcs']:
			self.outputArcs[arcs] = {}
			if arcs in self.singleArcs:
				for var in self.singleArcs[arcs]['vars']:
					self.outputArcs[arcs][var] = '{val}'.format(val = self.singleArcs[arcs]['vars'][var])
			for arc, item in self.groupArcs.items():
				for token, items in item['tokens'].items():
					if items['arcs'].__contains__(arcs):
						index = items['arcs'].index(arcs)
						for var in items['vars']:
							self.outputArcs[arcs][var] = '{val}'.format(val = items['vars'][var][index])
			for arc, item in self.groupArcsBetweenNode.items():
				for token, items in item['tokens'].items():
					if items['arcs'].__contains__(arcs):
						index = items['arcs'].index(arcs)
						for var in items['vars']:
							self.outputArcs[arcs][var] = '{val}'.format(val = items['vars'][var][index])
		for const in self.constNotNodeOrArc:
			self.outputConst[const] = '{}'.format(self.constNotNodeOrArc[const]['value'])

	def writeToFile(self, fileloc = ''):
		node_file = os.path.join(fileloc, FILE_NAMES["init_nodes"])
		arc_file = os.path.join(fileloc, FILE_NAMES["init_arcs"])
		const_file = os.path.join(fileloc, FILE_NAMES["init_globals"])

		# node_file = 'nodes.json'
		# arc_file = 'arcs.json'
		# const_file = 'constants.json'

		with open(node_file, 'msg_box') as fn:
			json.dump(self.outputNodes, fn, sort_keys = True, indent = 4)
		with open(arc_file, 'msg_box') as fa:
			json.dump(self.outputArcs, fa, sort_keys = True, indent = 4)
		with open(const_file, 'msg_box') as fc:
			json.dump(self.outputConst, fc, sort_keys = True, indent = 4)
######################################### Tester ###########################################

if __name__ == '__main__':
	#model = "/home/elve/ProcessModeller/Model_Repository/HEX/models/Hex_groups.json"
	#eqs = "/home/elve/ProcessModeller/Model_Repository/HEX/equations.json"
	#var = "/home/elve/ProcessModeller/Model_Repository/HEX/variables.json"
	#typ = "/home/elve/ProcessModeller/Model_Repository/HEX/typed_tokens.json"
	#states = ["m", "H"]
	#test = Initialization(model, eqs, vars, typ, states)
	#test.equationSetBuilder()
	test = Initialization('HEX_groups.json', 'equations.json', 'variables.json', 'typed_tokens.json', ['m','H'])
	test.equationSetBuilder()
	test.calculateInitState(['m','H'])
	test.addVariablesAndStates()
	print(test.singleDict)
