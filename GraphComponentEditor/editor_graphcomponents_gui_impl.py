"""
Created on Jul 29, 2009

@author : "PREISIG, Heinz A"
@copyright : "Copyright 2015, PREISIG, Heinz A"

@changes : 2017-03-20 associate graphical object information with ontoloy
@changes : 2017-03-21 change to json for the graphics resource file
@changes : 2017-03-22 move json to common resources

"""

__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2017, PREISIG, Heinz A"
__since__ = "2017. 03. 20"
__license__ = "generic module"
__version__ = "0"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# ===============================================================================
# graph components editor dialog impl
# ===============================================================================

# import json

from copy import deepcopy

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.common_resources import getOntologyName
from Common.common_resources import putDataOrdered
from Common.common_resources import saveBackupFile
from Common.graphics_objects import ARCS
from Common.graphics_objects import DECORATIONS_with_state
from Common.graphics_objects import DEFAULT_PHASE
from Common.graphics_objects import INTERFACE
from Common.graphics_objects import INTRAFACE,NODES
from Common.graphics_objects import M_None
from Common.graphics_objects import NAMES
from Common.graphics_objects import OBJECTS_colour_defined_separate
from Common.graphics_objects import OBJECTS_with_state
from Common.graphics_objects import PHASES
from Common.graphics_objects import STATES
from Common.graphics_objects import STATE_OBJECT_COLOURED
from Common.graphics_objects import STRUCTURES_Graph_Item
from Common.graphics_objects import getGraphData
from Common.ontology_container import OntologyContainer
from Common.qt_resources import PEN_STYLES
from Common.resource_initialisation import FILES
from ModelBuilder.GraphComponentEditor.editor_graphcomponents_gui import Ui_MainWindow
from ModelBuilder.ModelComposer.resources import ACTIONS


def debugPrint(source, what):
  print(source, ': ', what)


# Debugging -------------------------------------------------------------------
DEBUG_ME = False


class EditorError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg


class EditorGraphComponentsDialogImpl(QtWidgets.QMainWindow):
  # setting up GUI --------------------------------------------------------------
  def __init__(self):
    QtWidgets.QWidget.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.__setupSignals()
    self.__setupControlLists()

    self.ontology_name = getOntologyName(task="task_graphic_objects")

    self.ui.labelOntology.setText(self.ontology_name)

    self.ontology = OntologyContainer(self.ontology_name)
    ontology = self.ontology
    self.networks = ontology.list_leave_networks

    connection_networks = {}
    connection_networks.update(ontology.interconnection_network_dictionary)
    connection_networks.update(ontology.intraconnection_network_dictionary)
    self.connection_network_list = sorted(connection_networks.keys())

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

    self.toolchoose = True
    self.newcomponent = False
    self.current_editor_phase = '*'
    self.structures = None
    self.current_colour = 0, 255, 0, 10
    self.current_token = None

    self.selected_state = STATE_OBJECT_COLOURED

    self.__makeComboEditorPhase()
    self.__makeListTokens()
    self.__makeListStates()

    # initialise colour dialogue
    self.colourDialog = QtWidgets.QColorDialog()

    for i in range(0, 16):  # reset all custom colours first to white
      colour = QtGui.QColor(255, 255, 255)
      self.colourDialog.setCustomColor(i, colour)

    count = 0
    tokens = sorted(self.TOKENS.keys())
    for token in tokens:
      print(token, ' : ', count)
      r, g, b, a = self.TOKENS[token]["colour"]
      colour = QtGui.QColor(r, g, b, a)
      self.colourDialog.setCustomColor(count, colour)
      count += 2  # makes it the first row
    colour_select = QtGui.QColor(255, 255, 0)
    self.colourDialog.setCustomColor(1, colour_select)
    colour_open = QtGui.QColor(0, 255, 255)
    self.colourDialog.setCustomColor(3, colour_open)
    colour_uni_directional = QtGui.QColor(85, 85, 85)
    self.colourDialog.setCustomColor(5, colour_uni_directional)
    colour_bi_directional = QtGui.QColor(170, 170, 170)
    self.colourDialog.setCustomColor(7, colour_bi_directional)
    colour_distributed = QtGui.QColor(225, 225, 225)
    self.colourDialog.setCustomColor(9, colour_distributed)

    # allow for filling of gui widgets
    self.ui.groupBoxEllipseColour.setAutoFillBackground(True)
    self.ui.groupBoxLineColour.setAutoFillBackground(True)
    self.ui.groupBoxPanelColour.setAutoFillBackground(True)
    self.ui.groupBoxNetworkColour.setAutoFillBackground(True)
    self.ui.groupBoxTokenColour.setAutoFillBackground(True)
    self.ui.groupBoxStateColour.setAutoFillBackground(True)

    self.__group_controls("start")

  def on_radioButtonTokens_pressed(self):
    self.__group_controls("edit_tokens")
    self.ui.stackedColouring.setCurrentIndex(0)

  def on_radioButtonStates_pressed(self):
    self.__group_controls("edit_states")
    self.ui.stackedColouring.setCurrentIndex(2)

  def on_comboEditorPhase_textActivated(self, phase):
    # phase = self.ui.comboEditorPhase.currentText()
    self.current_editor_phase = str(phase)
    component_data = self.__getComponentData()
    self.__makeListActivity(component_data["action"])
    self.__group_controls("selected_editor_phase")

  def on_comboEditorState_textActivated(self, state):
    print("debugging -- comboEditorState activated")
    # state = self.ui.comboEditorState.currentText()
    self.selected_state = str(state)
    component_data = self.__getComponentData()
    self.__makeListActivity(component_data["action"])
    self.__group_controls("selected_editor_phase")

  def on_listRootObjects_itemClicked(self, item):
    if DEBUG_ME:
      debugPrint('on_listRootObjects', item.text())
    self.selected_root_object = str(item.text())
    self.ui.Logger.clear()
    self.ui.stackedProperties.setCurrentIndex(0)
    self.__makeListComponents()
    self.__group_controls("selected_root_object")

  def on_comboApplication_textActivated(self, q_string):
    # q_string = self.ui.comboApplication.currentText()
    print("application selected", q_string)

    self.selected_application = str(q_string)
    self.__processSelectedComponent()
    self.ui.comboEditorState.setCurrentIndex(0)  # make activity lists
    state = self.ui.comboEditorState.currentText()
    self.on_comboEditorState_textActivated(state)

  def on_listComponents_itemClicked(self, item):

    print("component selected", item.text())
    self.__group_controls("edit_object")
    self.selected_component = str(item.text())
    self.__makeComboState()
    self.__selectedComponent()

    self.initialise = False

  def on_listNetworks_itemClicked(self, item):

    self.current_network = str(item.text())
    self.toolchoose = True
    self.current_colour = self.NETWORK.getData(self.current_network)
    self.__showColour(self.ui.groupBoxNetworkColour)
    self.__group_controls("network_selected")

  def on_radioButtonComponents_pressed(self):
    self.ui.groupShapes.hide()
    self.ui.groupObjects.hide()
    self.ui.groupComponents.show()
    self.__group_controls("edit_components")
    self.current_state = STATE_OBJECT_COLOURED  # rule: only the colour of the enabled element is variable

  def on_pushButtonNetworks_pressed(self):
    print("on_radioButtonNetworksComponents_pressed")
    self.network_type = "network"

    self.ui.listRootObjects.clear()
    structures = []
    for s in STRUCTURES_Graph_Item:
      if s not in [NAMES["intraface"], NAMES["interface"]]:
        structures.append(s)

    self.__makeObjectList(structures)

    self.__group_controls("select_components_network")

  def on_pushButtonIntraface_pressed(self):
    print("on_radioButtonIntrafacesComponents_pressed")
    self.network_type = "intraface"
    structures = INTRAFACE
    self.ui.listRootObjects.clear()
    self.__makeObjectList(structures)
    self.__group_controls("select_components_network")
    pass

  def on_pushButtonInterface_pressed(self):
    print("on_radioButtonInterfacesComponents_pressed")
    self.network_type = "interface"
    structures = INTERFACE
    self.ui.listRootObjects.clear()
    self.__makeObjectList(structures)
    self.__group_controls("select_components_network")
    pass

  def __makeObjectList(self, structures):
    self.__makeStructureList(structures)

    self.toolchoose = True
    self.ui.groupShapes.show()
    self.ui.groupObjects.show()

  def on_listTokens_itemClicked(self, item):
    self.current_token = str(item.text())
    self.current_token_colour = self.TOKENS.getData(self.current_token)

    self.toolchoose = True
    self.current_colour = self.TOKENS.getData(self.current_token)
    self.__showColour(self.ui.groupBoxTokenColour)
    self.__group_controls("token_selected")

  def on_listStates_itemPressed(self, item):
    self.current_state = str(item.text())
    self.current_state_colour = self.STATES_colours[self.current_state]

    self.toolchoose = True
    self.current_colour = self.current_state_colour
    self.__showColour(self.ui.groupBoxStateColour)
    self.__group_controls("state_selected")

  def on_toolNetworkColour_pressed(self):
    where = self.ui.groupBoxNetworkColour
    return self.__selectColour(where, what="network")

  def on_toolTokenColour_pressed(self):
    where = self.ui.groupBoxTokenColour
    return self.__selectColour(where, what="token")

  def on_toolStateColour_pressed(self):
    where = self.ui.groupBoxStateColour
    return self.__selectColour(where, what="state")

  def on_toolEllipseColour_pressed(self):
    where = self.ui.groupBoxEllipseColour
    return self.__selectColour(where)

  def on_toolLineColour_pressed(self):
    where = self.ui.groupBoxLineColour
    return self.__selectColour(where)

  def on_toolPanelColour_pressed(self):
    where = self.ui.groupBoxPanelColour
    return self.__selectColour(where)

  # @QtCore.pyqtSignature('int')
  def on_spinRelPositionX_valueChanged(self, x):
    self.__changeData('position_x', x)

  # @QtCore.pyqtSignature('int')
  def on_spinRelPositionY_valueChanged(self, y):
    # y = self.ui.spinEllipseWidth.value()
    self.__changeData('position_y', y)

  # @QtCore.pyqtSignature('int')
  # def on_spinLayer_valueChanged(self, value):
  #   self.__changeData("layer", value)

  # @QtCore.pyqtSignature('int')
  def on_spinEllipseWidth_valueChanged(self, w):
    self.__changeData('width', w)

  # @QtCore.pyqtSignature('int')
  def on_spinEllipseHeight_valueChanged(self, h):
    self.__changeData('height', h)

  # @QtCore.pyqtSignature('int')
  def on_spinPanelWidth_valueChanged(self, h):
    w = self.ui.spinPanelWidth.value()
    self.__changeData('width', w)

  # @QtCore.pyqtSignature('int')
  def on_spinPanelHeight_valueChanged(self, h):
    w = self.ui.spinPanelHeight.value()
    self.__changeData('height', w)

  # @QtCore.pyqtSignature('int')
  def on_spinLineWidth_valueChanged(self, h):
    w = self.ui.spinLineWidth.value()
    self.__changeData('width', w)

  def on_radioButtonNetworks_pressed(self):
    self.network_type = "network"
    self.__makeListNetwork("network", self.ui.listNetworks)
    self.__group_controls("edit_network_colours")
    self.ui.stackedColouring.setCurrentIndex(1)

  def on_radioButtonIntrafaces_pressed(self):
    self.network_type = "intraface"
    self.__makeListNetwork("intraface", self.ui.listNetworks)
    # self.__makeStructureList(INTRAFACE)
    self.__group_controls("edit_network_colours")
    self.ui.stackedColouring.setCurrentIndex(1)

  def on_radioButtonInterfaces_pressed(self):
    self.network_type = "interface"
    self.__makeListNetwork("interface", self.ui.listNetworks)
    self.__group_controls("edit_network_colours")
    self.ui.stackedColouring.setCurrentIndex(1)

  def on_radioMainPanel_pressed(self):
    self.__changeData("layer", "mainPanel")

  def on_radioSidePanel_pressed(self):
    self.__changeData("layer", "sidePanel")

  def on_radioNetwork_pressed(self):
    self.__changeData("layer", "network")

  def on_radioArc_pressed(self):
    self.__changeData("layer", "arc")

  def on_radioKnot_pressed(self):
    self.__changeData("layer", "knot")

  def on_radioNode_pressed(self):
    self.__changeData("layer", "node")

  def on_radioProperty_pressed(self):
    self.__changeData("layer", "property")

  def on_radioText_pressed(self):
    self.__changeData("layer", "text")

  def on_comboLineStyle_textActivated(self, style):
    # style = self.ui.comboLineStyle.currentText()
    self.__changeData('style', str(style))

  def on_comboLineWidth_valueChanged(self, w):
    W = self.ui.comboApplication.currentText()
    self.__changeData('width', w)

  def on_checkMovable_stateChanged(self, no):
    if no == QtCore.Qt.Unchecked:
      self.__changeData('movable', False)
    elif no == QtCore.Qt.Checked:
      self.__changeData('movable', True)
    else:
      debugPrint('on_checkMovable_stateChanged', 'error: no such state')

  def on_listAvailableActions_itemClicked(self, item):
    self.__listSwap(self.ui.listAvailableActions,
                    self.ui.listAssignedActions)

    self.__getEnabledActions()

  def on_listAssignedActions_itemClicked(self, item):
    self.__listSwap(self.ui.listAssignedActions,
                    self.ui.listAvailableActions)
    self.__getEnabledActions()

  def on_pushSaveBackup_pressed(self):
    saveBackupFile(self.graph_resource_file_spec)
    self.on_pushSave_pressed()

  def on_pushSave_pressed(self):
    p0 = PHASES[0]
    data0 = self.DATA[p0]
    # RULE: superimpose state colours to all state-dependent objects
    for o in data0:
      for d in data0[o]:
        for a in data0[o][d]:
          for s in data0[o][d][a]:
            attributes = sorted(data0[o][d][a][s].keys())
            if s != STATE_OBJECT_COLOURED:
              if s != M_None:
                for k in attributes:
                  if k == "colour":
                    if s in self.STATES_colours:
                      data0[o][d][a][s]["colour"] = deepcopy(self.STATES_colours[s])
                      print("debugging -- changing colour of ", o, d, a, s, k)
                  elif k == "action":
                    pass
                  else:
                    data0[o][d][a][s][k] = data0[o][d][a][STATE_OBJECT_COLOURED][k]

    for p in PHASES:
      datap = self.DATA[p]
      if p != p0:
        for o in datap:
          for d in datap[o]:
            for a in datap[o][d]:
              for s in datap[o][d][a]:
                for k in datap[o][d][a][s]:
                  if k != "action":
                    datap[o][d][a][s][k] = deepcopy(data0[o][d][a][s][k])

    saveBackupFile(self.graph_resource_file_spec)

    data_dict = {
            'networks': self.NETWORK,
            'data'    : self.DATA,
            'tokens'  : self.TOKENS,
            'states'  : self.STATES_colours,
            }
    putDataOrdered(data_dict, self.graph_resource_file_spec, indent=2)

  def on_pushCopyPhaseToPhases_pressed(self):
    # print(">>> copying phase topology data to the other phases - only keep actions")
    # self.__copyPhaseToPhase()
    print(">>>>>>>>>>>>>>>>>  deactivated")

  def on_pushExplainActions_pressed(self):
    with open(FILES["graph_resource_documentation"], 'r') as f:
      l = f.read()
      self.ui.Logger.append(l)

    # all signals ----------------------------------------------------------------

  def __setupSignals(self):

    self.LAYERS = {
            "mainPanel": self.ui.radioMainPanel,
            "sidePanel": self.ui.radioSidePanel,
            "network"  : self.ui.radioNetwork,
            "arc"      : self.ui.radioArc,
            "knot"     : self.ui.radioKnot,
            "node"     : self.ui.radioNode,
            "property" : self.ui.radioProperty,
            "text"     : self.ui.radioText
            }

  def __setupControlLists(self):
    u = self.ui
    self.gui_groups = {}
    self.gui_groups = \
      {
              "groupMain"            : u.groupMain,
              "groupNetworks"        : u.groupNetworks,
              "groupComponents"      : u.groupComponents,
              "groupControls"        : u.groupControls,
              "groupPosition"        : u.groupPosition,
              "stackedProperties"    : u.stackedProperties,
              "groupLayer"           : u.groupLayer,
              "groupActions"         : u.groupActions,
              "groupStateApplication": u.groupStateApplication,
              "groupTokens"          : u.groupTokens,
              "groupStates"          : u.groupStates,
              "groupShapes"          : u.groupShapes,
              "groupComponentEditor" : u.groupComponentEditor,
              "groupObjects"         : u.groupObjects,
              # "groupNetworksComponents": u.groupNetworksComponents,
              "toolNetworkColour"    : u.groupBoxTokenColour,
              "groupBoxNetworkColour": u.groupBoxNetworkColour,
              }

    self.gui_behaviour = \
      {
              "start"                       : ["groupMain",
                                               ],
              "edit_network_colours"        : ["groupMain",
                                               "groupControls",
                                               "groupNetworks",
                                               ],
              "network_selected"            : ["groupMain",
                                               "groupControls",
                                               "groupPhase",
                                               "groupNetworks",
                                               "groupBoxNetworkColour"
                                               ],
              "edit_tokens"                 : ["groupMain",
                                               "groupControls",
                                               "groupTokens",
                                               ],
              "edit_states"                 : ["groupMain",
                                               "groupControls",
                                               "groupStates",
                                               ],
              "state_selected"              : ["groupMain",
                                               "groupControls",
                                               "groupStates",
                                               "toolStateColour", ],
              "token_selected"              : ["groupMain",
                                               "groupControls",
                                               "groupTokens",
                                               "toolNetworkColour", ],
              "selected_editor_phase"       : ["groupMain",
                                               "groupControls",
                                               "groupComponentEditor",
                                               "groupPhase",
                                               # "groupNetworks",
                                               "groupComponents",
                                               "groupObjects",
                                               "groupShapes",
                                               "groupPosition",
                                               "stackedProperties",
                                               "groupLayer",
                                               "groupActions",
                                               "groupStateApplication",
                                               ],
              "selected_root_object"        : ["groupMain",
                                               "groupControls",
                                               "groupPhase",
                                               "groupActions",
                                               "groupComponents",
                                               "groupObjects",
                                               "groupShapes",
                                               "groupObjects",
                                               ],
              "edit_object"                 : ["groupMain",
                                               "groupControls",
                                               "groupPhase",
                                               "groupActions",
                                               "groupComponents",
                                               "groupObjects",
                                               "groupShapes",
                                               ],
              "no_state"                    : ["groupMain",
                                               "groupControls",
                                               "groupComponentEditor",
                                               "groupPhase",
                                               # "groupNetworks",
                                               "groupComponents",
                                               "groupObjects",
                                               "groupShapes",
                                               "groupPosition",
                                               "stackedProperties",
                                               "groupLayer",
                                               "groupActions"
                                               ],
              "with_state"                  : ["groupMain",
                                               "groupControls",
                                               "groupComponentEditor",
                                               "groupPhase",
                                               # "groupNetworks",
                                               "groupComponents",
                                               "groupObjects",
                                               "groupShapes",
                                               "groupPosition",
                                               "stackedProperties",
                                               "groupLayer",
                                               "groupActions",
                                               "groupStateApplication",
                                               ],
              "select_components_network"   : ["groupMain",
                                               "groupControls",
                                               # "groupComponentEditor",
                                               # "groupPhase",
                                               # "groupNetworks",
                                               "groupObjects",
                                               "groupComponents",
                                               "groupNetworksComponents",
                                               # "groupShapes",
                                               # "groupPosition",
                                               # "stackedProperties",
                                               # "groupLayer",
                                               # "groupActions",
                                               # "groupStateApplication",
                                               ],
              "select_edit_inter_intra_face": ["groupMain",
                                               "groupControls",
                                               # "groupComponentEditor",
                                               # "groupPhase",
                                               # "groupNetworks",
                                               "groupComponents",
                                               "groupObjects",
                                               # "groupNetworksComponents",
                                               # "groupShapes",
                                               # "groupPosition",
                                               # "stackedProperties",
                                               # "groupLayer",
                                               # "groupActions",
                                               # "groupStateApplication",
                                               ],
              "edit_components"             : ["groupMain",
                                               "groupControls",
                                               # "groupComponentEditor",
                                               # "groupPhase",
                                               # "groupNetworks",
                                               "groupComponents",
                                               # "groupObjects",
                                               # "groupNetworksComponents",
                                               # "groupShapes",
                                               # "groupPosition",
                                               # "stackedProperties",
                                               # "groupLayer",
                                               # "groupActions",
                                               # "groupStateApplication",
                                               ],
              "select_graphobject_network"  : ["groupMain",
                                               "groupControls",
                                               # "groupComponentEditor",
                                               "groupPhase",
                                               # "groupNetworks",
                                               "groupComponents",
                                               "groupObjects",
                                               "groupShapes",
                                               "groupPosition",
                                               "stackedProperties",
                                               "groupLayer",
                                               "groupActions",
                                               "groupStateApplication",
                                               ]
              }

  def __group_controls(self, state):
    for g in self.gui_groups:
      if g in self.gui_behaviour[state]:
        self.gui_groups[g].show()
      else:
        self.gui_groups[g].hide()
    pass

  def __makeComboEditorPhase(self):
    self.ui.comboEditorPhase.clear()
    self.ui.comboEditorPhase.addItems(list(STATES.keys()))
    self.current_editor_phase = str(self.ui.comboEditorPhase.currentText())

  def __makeComboState(self):
    self.ui.comboEditorState.clear()
    states = None
    if self.selected_root_object in OBJECTS_with_state:
      if self.selected_root_object in NODES:
        if self.selected_component in DECORATIONS_with_state:
          states = STATES[self.current_editor_phase]["nodes"]
      elif self.selected_root_object in ARCS:
        if self.selected_component in DECORATIONS_with_state:
          states = STATES[self.current_editor_phase]["arcs"]
    if not states:
      print("__makeComboState -- no state defined")

    if states:
      self.ui.comboEditorState.addItems(states)
      self.selected_object_state = str(self.ui.comboEditorState.currentText())
    else:
      self.ui.comboEditorState.clear()
    # self.ui.comboEditorState.show()

  def __makeComboApplication(self):

    if self.selected_root_object == NAMES["connection"]:
      applications = self.ontology.list_arc_objects
    else:
      if self.network_type == "network":
        applications = self.ontology.list_network_node_objects
      elif self.network_type == "interface":
        applications = self.ontology.list_inter_node_objects
      elif self.network_type == "intraface":
        applications = self.ontology.list_intra_node_objects
      else:
        print(">>>>>>>>>> should not come here")

    self.ui.comboApplication.clear()
    self.ui.comboApplication.addItems(set(applications))
    self.selected_application = str(self.ui.comboApplication.currentText())

  def __makeListNetwork(self, network_type, listNetworks):
    listNetworks.clear()
    if network_type == "network":
      listNetworks.addItems(self.networks)
    elif network_type == "intraface":
      cnw = sorted(self.ontology.intraconnection_network_dictionary.keys())
      listNetworks.addItems(cnw)
    elif network_type == "interface":
      cnw = sorted(self.ontology.interconnection_network_dictionary.keys())
      listNetworks.addItems(cnw)
    else:
      raise EditorError(">>> no such network type")

    # self.ui.listNetworks.addItems(self.connection_network_list)

  def __makeListTokens(self):
    self.ui.listTokens.clear()
    tokens = set()
    for nw in self.networks:
      [tokens.add(i) for i in self.ontology.tokens_on_networks[nw]]

    self.ui.listTokens.addItems(sorted(tokens))

  def __makeListStates(self):
    self.ui.listStates.clear()
    items = set()
    for s in sorted(self.STATES_colours.keys()):
      if s not in STATE_OBJECT_COLOURED:
        items.add(s)
    self.ui.listStates.addItems(sorted(items))

  def __makeListActivity(self, enabled_actions):
    self.ui.listAvailableActions.clear()
    self.ui.listAssignedActions.clear()
    set_actions = set(ACTIONS[self.current_editor_phase])
    set_enabled = set(enabled_actions)
    to_remove = []
    for i in set_enabled:  # remove what does not belong -- consequence of copying
      if i not in set_actions:
        to_remove.append(i)
    for i in to_remove:
      set_enabled.remove(i)

    set_available = set_actions - set_enabled
    self.ui.listAvailableActions.addItems(sorted(set_available))
    self.ui.listAssignedActions.addItems(sorted(set_enabled))

  def __makeStructureList(self, structures):

    # set up structure list
    self.ui.listRootObjects.clear()
    for i in structures:  # STRUCTURES:
      self.ui.listRootObjects.addItem(i)
    self.ui.listRootObjects.sortItems()
    self.initialise = False

  def __makeListComponents(self):
    self.ui.listComponents.clear()
    components = list(STRUCTURES_Graph_Item[self.selected_root_object])
    components.sort()
    for o in components:
      self.ui.listComponents.addItem(o)
      self.ui.listComponents.setEnabled(1)

  def __selectColour(self, where, what=""):
    # print("change colour for :", what)
    # without the toggle toolchoose the question for a colour is asked twice..... why ?
    # if not self.toolchoose:
    #   self.toolchoose = True
    #   return
    # else:
    #   self.toolchoose = False
    colour = self.__colourDialog()
    if what == "network":
      self.NETWORK[self.current_network]["colour"] = colour
    elif what == "token":
      self.TOKENS[self.current_token]["colour"] = colour
    elif what == "state":
      self.STATES_colours[self.current_state] = colour
    else:
      self.__changeData("colour", colour)
    self.current_colour = colour
    self.__showColour(where)
    return

  def __getEnabledActions(self):
    count = self.ui.listAssignedActions.count()
    actions = []
    for i in range(count):
      item = self.ui.listAssignedActions.item(i).text()
      actions.append(item)
    self.__changeData("action", actions)

  def __copyPhaseToPhase(self):

    # TODO somewhat too simple copies also the possible actions

    for root_object in self.DATA["topology"]:
      for component in self.DATA["topology"][root_object]:
        for application in self.DATA["topology"][root_object][component]:
          for state in self.DATA["topology"][root_object][component][application]:
            try:
              for phase in ["tokens", "token_topology"]:
                try:
                  keep = self.DATA[phase][root_object][component][application][state]["action"]
                  self.DATA[phase][root_object][component][application][M_None] = \
                    deepcopy(self.DATA["topology"][root_object][component][application]["selected"])
                  self.DATA[phase][root_object][component][application][state]["action"] = keep
                  # print("copied :", root_object, component, application, keep)
                except:
                  self.DATA[phase][root_object][component][application] = \
                    deepcopy(self.DATA["topology"][root_object][component][application])
                  # print("copied :", root_object, component, application)
                  pass
            except:
              # print("not copied :", root_object, component, application)
              pass

  def __printComponentData(self):
    self.ui.Logger.clear()
    s = 'root_object : %s \ncomponent data: %s\n\n' % (self.selected_root_object, self.selected_component)
    component_data = self.__getComponentData()
    for l in component_data:
      s += str(l) + ' : '
      s += str(component_data[l]) + '\n'
    self.ui.Logger.setText(s)

  def __changeData(self, what, value):
    # rule: phase -- only the actions are a function of the phase
    # rule: root object -- none
    # rule: selected component -- none
    # rule: selected application -- none
    # rule: state -- colour is the same for all editor phases, except root objects with state  STATE_OBJECT_COLOURED
    if what == "action":
      phase = self.current_editor_phase
      state = M_None
      if self.selected_root_object in OBJECTS_with_state:
        if self.selected_component in DECORATIONS_with_state:
          state = self.current_state
    else:
      phase = PHASES[0]
      state = M_None
      if self.selected_root_object in OBJECTS_with_state:
        if self.selected_component in DECORATIONS_with_state:
          state = STATE_OBJECT_COLOURED

    self.DATA.setData(what, value,
                      phase,
                      self.selected_root_object,
                      self.selected_component,
                      self.selected_application,
                      state,
                      )
    #   else:
    #     self.DATA.setData(what, value,
    #                       phase,  # self.current_editor_phase,
    #                       self.selected_root_object,
    #                       self.selected_component,
    #                       self.selected_application,
    #                       M_None,
    #                       )
    # else:
    #   self.DATA.setData(what, value,
    #                     phase,  # self.current_editor_phase,
    #                     self.selected_root_object,
    #                     self.selected_component,
    #                     self.selected_application,
    #                     M_None,
    #                     )
    #
    # for phase in phases:
    #   print("debugging -- going through the phases ", phase)
    #   if phase == "equation_topology":
    #     print("debugging -- now it is equation topology")
    #   if self.selected_root_object in OBJECTS_with_state:
    #     if self.selected_component in DECORATIONS_with_state:
    #       if self.selected_root_object in NODES:
    #         states = STATES[phase]["nodes"]
    #       elif self.selected_root_object in ARCS:
    #         states = STATES[phase]["arcs"]
    #       for state in states:
    #         if what == "colour":
    #           if state == STATE_OBJECT_COLOURED:
    #             _value = value
    #             # print("debugging -- colour being set ", value)
    #           else:
    #             _value = self.STATES_colours[state]
    #         else:
    #           _value = value
    #         self.DATA.setData(what, _value,
    #                           phase,  # self.current_editor_phase,
    #                           self.selected_root_object,
    #                           self.selected_component,
    #                           self.selected_application,
    #                           state,
    #                           )
    #     else:
    #       self.DATA.setData(what, value,
    #                         phase,  # self.current_editor_phase,
    #                         self.selected_root_object,
    #                         self.selected_component,
    #                         self.selected_application,
    #                         M_None,
    #                         )
    #   else:
    #     self.DATA.setData(what, value,
    #                       phase,  # self.current_editor_phase,
    #                       self.selected_root_object,
    #                       self.selected_component,
    #                       self.selected_application,
    #                       M_None,
    #                       )
    self.__printComponentData()

  def __getComponentData(self):
    return self.DATA.getData(DEFAULT_PHASE,  # self.current_editor_phase,
                             self.selected_root_object,
                             self.selected_component,
                             self.selected_application,
                             self.selected_state
                             # STATE_OBJECT_COLOURED  # ditto
                             )
    # self.selected_object_state)

  def __selectedComponent(self):

    debugPrint('__selectedComponent', self.selected_component)

    # RULE : only the root carry the state
    if (self.selected_component in DECORATIONS_with_state) and \
            (self.selected_root_object in OBJECTS_with_state):
      # self.__makeComboState()
      self.__makeComboApplication()
      self.__group_controls("with_state")
      self.__makeComboState()
    else:
      self.selected_object_state = M_None
      self.selected_application = M_None
      # self.ui.comboState.clear()
      self.ui.comboApplication.clear()
      self.__group_controls("no_state")

    self.__processSelectedComponent()

  def __processSelectedComponent(self):

    component_data = self.__getComponentData()
    self.__printComponentData()
    self.__makeListActivity(component_data["action"])
    x = component_data["position_x"]
    y = component_data["position_y"]
    self.ui.spinRelPositionX.setValue(x)
    self.ui.spinRelPositionY.setValue(y)
    movable = component_data["movable"]
    layer = component_data["layer"]
    self.LAYERS[layer].setChecked(True)

    if movable:
      self.ui.checkMovable.setCheckState(QtCore.Qt.Checked)
    else:
      self.ui.checkMovable.setCheckState(QtCore.Qt.Unchecked)
    shape = STRUCTURES_Graph_Item[self.selected_root_object][self.selected_component]
    self.current_shape = shape
    if shape == "ellipse":
      self.ui.stackedProperties.setCurrentIndex(1)
      w = component_data["width"]
      h = component_data["height"]
      self.ui.spinEllipseWidth.setValue(w)
      self.ui.spinEllipseHeight.setValue(h)

      self.current_colour = component_data["colour"]

      # RULE: network components are handled on a higher level
      if self.selected_component not in OBJECTS_colour_defined_separate:
        self.ui.groupBoxEllipseColour.show()
        self.__showColour(self.ui.groupBoxEllipseColour)
      else:
        self.ui.groupBoxEllipseColour.hide()

    elif shape == 'line':
      self.ui.stackedProperties.setCurrentIndex(2)
      #
      line_style = component_data["style"]
      self.ui.comboLineStyle.clear()
      for i in PEN_STYLES:
        self.ui.comboLineStyle.addItem(i)

      print("line style :", line_style)
      if line_style != M_None:
        index = self.ui.comboLineStyle.findText(line_style)
        self.ui.comboLineStyle.setCurrentIndex(index)
      #
      width = component_data["width"]
      self.ui.spinLineWidth.setValue(width)
      #
      self.current_colour = component_data["colour"]
      self.__showColour(self.ui.groupBoxLineColour)

    elif shape == 'text':
      self.ui.stackedProperties.setCurrentIndex(3)

    elif shape == 'panel':
      self.ui.stackedProperties.setCurrentIndex(4)
      #
      w = component_data["width"]
      self.ui.spinPanelWidth.setValue(w)
      h = component_data["height"]
      self.ui.spinPanelHeight.setValue(h)
      #
      self.current_colour = component_data["colour"]
      self.__showColour(self.ui.groupBoxPanelColour)

  def __colourDialog(self, ):
    r, g, b, a = self.current_colour
    colour = QtGui.QColor(r, g, b, a)
    c = self.colourDialog.getColor(colour).getRgb()
    return c  # c_.getRgb(), v

  def __showColour(self, box):
    print("colour :", self.current_colour)
    r, g, b, a = self.current_colour
    colour = QtGui.QColor(r, g, b, a)
    palette = box.palette()
    palette.setColor(QtGui.QPalette.Window, colour)
    box.setPalette(palette)
    box.update()

  def __listSwap(self, listA, listB):
    """remove item from list
    """
    k = listA.currentRow()
    item = listA.currentItem()
    #        print  R.getFncName(self),  k, item
    listA.takeItem(k)
    listB.addItem(item)
