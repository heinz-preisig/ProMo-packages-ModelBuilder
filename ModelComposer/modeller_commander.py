#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
  commander for ModelComposer
===============================================================================
  main switch board of Process Modeller


__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL"
__version__ = "5.01"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

"""

import copy
import os
from collections import OrderedDict

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import Common.common_resources as CR
import Common.resource_initialisation as RI
import ModelBuilder.ModelComposer.resources             as R
from Common.automata_objects import GRAPH_EDITOR_STATES
# from Common.automata_objects import STATES               # TODO: What's this?
from Common.common_resources import askForModelFileGivenOntologyLocation
from Common.common_resources import NODE_COMPONENT_SEPARATOR
from Common.graphics_objects import INTERFACE
from Common.graphics_objects import INTRAFACE
from Common.graphics_objects import LOCATION_PARAMETERS
from Common.graphics_objects import NAMES
from Common.graphics_objects import OBJECTS_with_state
from Common.graphics_objects import STATES  # TODO: Bug or real?
from Common.graphics_objects import TOOLTIP_TEMPLATES
from Common.qt_resources import BUTTON_NAMES
from Common.ui_string_dialog_impl import UI_String
from ModelBuilder.ModelComposer.modeller_graphcomponents import Arc_Edge
from ModelBuilder.ModelComposer.modeller_graphcomponents import Knot
from ModelBuilder.ModelComposer.modeller_graphcomponents import Node
from ModelBuilder.ModelComposer.modeller_graphcomponents import NodeView
from ModelBuilder.ModelComposer.modeller_model_data import ModelContainer
from ModelBuilder.ModelComposer.modeller_model_data import ModelGraphicsData
from ModelBuilder.ModelComposer.modeller_model_data import ROOTID

EDITOR_PHASES = list(GRAPH_EDITOR_STATES.keys())


# global methods --------------------------------------------------------------

def debugPrint(source, what):
  print(source, ": ", what)


class Commander(QtCore.QObject):
  """
  main switch board
  """

  def __init__(self, mainWin):
    """
    connect the main mainWin containing the main GUI
    @param mainWin: main GUI window
    """

    QtCore.QObject.__init__(self)
    self.main = mainWin
    self.showMouseActions = mainWin.showMouseAction
    self.cursors = R.ModellerCursor()
    self.intraconnections_dictionary = self.main.ontology.intraconnection_network_dictionary
    self.interconnections_dictionary = self.main.ontology.interconnection_network_dictionary

    # graphics view
    self.scene = None
    self.view = None

    #  interface behaviour
    self.__loadAutomata()

    # model container - start with a root node
    self.current_ID_node_or_arc = ROOTID  # str(ROOTID)  # nodeID    #HAP: ID string to integer
    self.model_container = ModelContainer(self.main.networks, self.main.ontology)

    # initial commander state
    self.state_nodes = {}
    self.state_arcs = {}
    self.current_application = R.M_None
    self.step = 0  # event counter
    self.resetGroups()
    self.arc_group = []
    self.library_model_name = ""  # current library model file name
    self.schnipsel_file = None
    self.modified = False

    # handling connections - arcs
    self.selected_arcID = None
    self.arcSourceID = None
    self.end_to_move = None  # "source" or "sink" to be moved
    self.editor_phase = self.main.editor_phase  # EDITOR_PHASES[0]  # "topology"

    # RULE: default editor phase is the first in the list
    self.editor_state = GRAPH_EDITOR_STATES[self.editor_phase][0]
    self.current_object_state = STATES[self.editor_phase]["nodes"][0]
    self.current_application = R.M_None

    # connect graphics data
    self.graphics_data = self.main.graphics_DATA

    rootID = ROOTID  # str(ROOTID)           #HAP: ID string to integer
    self.state_nodes[rootID] = STATES[self.editor_phase]["nodes"][0]
    self.__makeViewAndScene(rootID)
    self.currently_viewed_node = rootID

    self.string_dialog = UI_String("new node name", "node name")
    self.string_dialog.accepted.connect(self.__changeName)

  def __loadAutomata(self):
    automata = CR.getData(self.main.automata_working_file_spec)
    self.mouse_automata = automata["mouse"]
    self.key_automata = automata["key"]

    self.inverse_key_automata = {}

    for phase in self.key_automata:
      self.inverse_key_automata[phase] = {}
      for key in self.key_automata[phase]:
        state = self.key_automata[phase][key]["state"]
        self.inverse_key_automata[phase][state] = key

  # interface to graphics  ------------------------------------------------------

  def processGUIEvent(self, event_type, item, pressed, position=None):
    """
    executes automata dependent on event type
     - dummy event (event on dummy item) : do nothing
     - keyboard : keyboard automaton
     - GUI : no automaton yet
     - mouse : mouse automaton
    @param event_type:  in {keyboard, GUI, mouse}
    @param item:        graphics item on which event occurred
    @param pressed:     what mouse button was pressed
    @param position:    at what position
    """

    # print("  item : ", item, item.__class__, "ShapePannel" in str(item.__class__) )

    #  TODO: circumvent problems after deleting objects and changing editor mode via GUI control interface
    if "ShapePannel" in str(item.__class__):
      self.recover_item = item

    self.current_ID_node_or_arc = item.getGraphObjectID()  # graphics_root_object

    self.main.writeStatus("")

    #
    # RULE selecting a primitive node or arc implies changing network
    # try:  # circumvent problems after deleting objects and changing editor mode via GUI control interface
    graphics_root_object = item.parent.graphics_root_object
    state = self.getGraphObjectState(graphics_root_object)
    if graphics_root_object == NAMES["node"]:
      network = self.model_container["nodes"][self.current_ID_node_or_arc]["network"]
      named_network = self.model_container["nodes"][self.current_ID_node_or_arc]["named_network"]
      # print("node simple network:", network)
      if network in self.main.networks:
        self.main.setNetwork(network, named_network)
    if graphics_root_object == NAMES["connection"]:
      network = self.model_container["arcs"][self.current_ID_node_or_arc]["network"]
      named_network = self.model_container["arcs"][self.current_ID_node_or_arc]["named_network"]
      # print("node simple network:", network)
      if network in self.main.networks:
        self.main.setNetwork(network, named_network)
    # except:
    #   item = self.recover_item
    #   self.current_ID_node_or_arc = item.getGraphObjectID()
    #   graphics_root_object = None
    #   state = None

    self.current_object_state = state

    self.current_item = item  # broadcast item

    # ======== keyboard

    if event_type in ["keyboard", "controlboard"]:
      # print("updateGraph", "key event", pressed, list(self.key_automata[self.editor_phase].keys()))
      if pressed not in list(self.key_automata[self.editor_phase].keys()):
        print(">>>> commander -- key %s not recognised" % pressed)
        # print("updateGraph", "key event", pressed, "not in ", list(self.key_automata[self.editor_phase].keys()))
        return

      next_state = self.key_automata[self.editor_phase][pressed]["state"]
      action = self.key_automata[self.editor_phase][pressed]["output"]

      if event_type == "keyboard":  # break dead lock with setting only for keyboard 'controlboard' couples to here
        self.main.setKeyAutomatonState(pressed)

      # ======================================================================
      # # RULE: change of editor state is always applied on the panel
      # for i in self.scene.items():
      #   if NAMES["panel"] in dir(i):
      #     if (i.graphics_root_object == NAMES["panel"]):
      #       if (i.decoration == NAMES["root"]):
      #         item = i
      # ======================================================================

    # ========= GUI
    elif event_type == "GUI":
      action = "zoom in"
      next_state = "-"

    # ======== mouse
    elif event_type == "mouse":
      # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.
      if self.editor_phase in ["topology", "token_topology", "equation_topology"]:
        #
        # RULE: topology automaton operates on root object type and state independent of the network
        graphics_root_object = item.parent.graphics_root_object
        decoration = item.decoration
        application = item.application
        object_str = self.getObjectStr(application, decoration, graphics_root_object, state)

        mouse_automaton = self.mouse_automata[self.editor_phase]

        if object_str not in mouse_automaton[self.editor_state].keys():
          print("process event -- object %s not active" % object_str)
          print("              -- keys %s", mouse_automaton.keys())
          return
        else:
          event = BUTTON_NAMES[pressed]
          next_state = mouse_automaton[self.editor_state][object_str][event]["state"]
          action = mouse_automaton[self.editor_state][object_str][event]["output"]

          if next_state != "-":
            if next_state in list(self.inverse_key_automata[self.editor_phase].keys()):
              this_key = self.inverse_key_automata[self.editor_phase][next_state]
              self.main.setKeyAutomatonState(this_key)

          self.__reportEvent(state, next_state, action, object_str, event)


    # ============ error
    else:
      print("updateGraph",
            "commander.processGUIEvent: event handling error")

    if next_state != "-":
      self.editor_state = next_state

    pars = {
            "nodeID": item.parent.ID,
            "action": action,
            "object": item.decoration,
            "pos"   : position,
            "file"  : "-",
            "failed": False,
            }
    if graphics_root_object == NAMES["connection"]:
      pars["arc"] = item.parent.getArcID()

    pars = self.__c00_executeCommand(pars)

    return pars

  def getGraphObjectState(self, graphics_root_object):
    # print("getGraphObjectState  object ", graphics_root_object, self.current_ID_node_or_arc)
    if graphics_root_object in OBJECTS_with_state:
      if graphics_root_object in [NAMES["node"], NAMES["intraface"], NAMES["interface"]]:
        state = self.state_nodes[self.current_ID_node_or_arc]
      elif graphics_root_object == NAMES["connection"]:
        state = self.state_arcs[self.current_ID_node_or_arc]
      else:
        state = R.M_None
    else:
      state = R.M_None
    self.current_object_state = state
    return state

  def processMainEvent(self, pars):
    """
    processes events generated by the main window,
    the main interface component
    @param pars:
    for list see __c00_executeCommand
    @user: main window
    """
    self.__c00_executeCommand(pars)

  def getTheCursor(self, graphics_root_object, decoration, application, state):
    object_str = self.getObjectStr(application, decoration, graphics_root_object, state)

    if object_str not in self.mouse_automata[self.editor_phase][self.editor_state]:
      cursor = "undefined"
      actionR = ""
      actionL = ""
    else:
      cursor = self.mouse_automata[self.editor_phase][self.editor_state][object_str]["cursor"]
      actionL = self.mouse_automata[self.editor_phase][self.editor_state][object_str]["left"]["output"]
      actionR = self.mouse_automata[self.editor_phase][self.editor_state][object_str]["right"]["output"]

    self.showMouseActions(graphics_root_object, decoration, self.cursors.getBixMap(cursor), actionL, actionR)

    return self.cursors[cursor]

  def getObjectStr(self, application, decoration, graphics_root_object, state):
    r, d, a, s = self.graphics_data.getActiveObjectRootDecorationState(self.editor_phase,
                                                                       graphics_root_object,
                                                                       decoration,
                                                                       application,
                                                                       state)
    object_str = str((r, d, s))
    return object_str

    # GUI and model interface -----------------------------------------------------

  def makeThisCurrentNode(self, nodeID):
    """
    opens, if not yet open, and puts node window on top
    @param nodeID: node ID
    """
    pars = {}
    pars["nodeID"] = nodeID
    pars["action"] = "zoom in"
    self.__c00_executeCommand(pars)

  # internal methods and model interface ---------------------------------------

  # internal methods -----------------------------------------------------------

  def __c00_executeCommand(self, pars):
    """
    Command handling
    @param pars: dictionary
    - "action" : action to be taken
    - "nodeID" : node ID
    - "object" : selected graph object
    - "pos"    : position
    - "file"   : file identifier
    - "arc"    : arc ID
    - "network": network name
    - "state"  : state inforation for injection for example
    """

    action = pars["action"]

    # self.stateIndicator(self.editor_state)
    if action == "None":
      res = {"failed": False}
    elif action == "-":
      res = {"failed": False}
    elif action == "zoom in":
      res = self.__c01_makeThisCurrentNode(pars["nodeID"])
    elif action == "add node":
      res = self.__c02_addNode(pars["pos"])
    elif action == "delete node":
      res = self.__c03_deleteNode(pars["nodeID"])
    elif action == "group nodes":
      res = self.__c04_groupNodes(pars["pos"])
    elif action == "explode node":
      res = self.__c05_explodeNode(pars["nodeID"])
    elif action == "begin arc":
      res = self.__c06_beginArc(pars["nodeID"])
    elif action == "add arc":
      res = self.__c07_addTheArc(pars["nodeID"])
    elif action == "remove arc":
      res = self.__c08_removeArc(pars["arc"])
    elif action == "re-direct arc":
      res = self.__c09_reconnectArc(pars["object"])
    elif action == "change arc":
      res = self.__c10_changeArc(pars["nodeID"])
    elif action == "insert knot":
      res = self.__c11_insertKnot()
    elif action == "remove knot":
      res = self.__c12_removeKnot()
    elif action == "make a copy":
      res = self.__c13_makeCopy(pars["nodeID"])
    elif action == "load from file":
      res = self.__c14_insertModelFromFile(pars["file"])
    elif action == "reset":
      res = self.__c15_reset()
    elif action == "name node":
      res = self.__c16_editName(pars["nodeID"])
    elif action == "library file":
      res = self.__c21_setCurrentLibFile(pars["file"])
    elif action == "map&save model":
      res = self.__c22_mapAndSaveModel(self.model_container, pars["file"])
    elif action == "save model":
      res = self.__c23_saveData(self.model_container, pars["file"])
    elif action == "insert model":
      res = self.__c25_insertSchnipsel(pars["pos"])
    elif action == "shift editor phase":
      res = self.__c26_shiftEditorPhase(pars["phase"])
    elif action == "select node":
      res = self.__c27_selectIntrafaceNode(pars["nodeID"])
    elif action == "inject":
      res = self.__c28_injectTypedTokensOrConversions(pars["nodeID"])
    elif action == "compute token distribution":
      res = self.__c31_computeTypedTokenDomains()
    else:
      action = "-"
      res = {"failed": False}

    if res["failed"]:
      return

    if action in ["new model", "map&save model", "save model", "make a copy"]:
      self.modified = False
    elif action in ["add node", "delete node", "group nodes",
                    "explode node", "add arc", "remove arc",
                    "insert knot", "remove knot",
                    "insert model"]:
      self.modified = True  # TODO: handling of the modified to be completed
    self.main.markModifiedModel(self.modified)

    par_dic = res.copy()  # copy results into par list
    par_dic["viewed node"] = self.current_ID_node_or_arc

    return res

  def __c02_addNode(self, pos, network=None):
    """
    command: add node
    @param pos: position  QtPoint
    @return: dictionary
            "new node":           newnodeID,
            "network":            network
            "arc closed":         arcs_closed,
            "arc open at sink":   arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":             False
    """

    x, y = pos.x(), pos.y()

    if not network:
      # if not self.main.current_network:
      #   return {
      #         "failed"  : True
      #         }
      network = self.main.current_network  # default
      named_network = self.main.current_named_network

      node_type = self.main.selected_node_type[self.main.current_network]
      node_class = NAMES["node"]

      node_characteristics, app = node_type.split(NODE_COMPONENT_SEPARATOR)
    else:
      node_class = NAMES["branch"]
      node_type = NAMES["branch"]
      named_network = NAMES["branch"]
      node_characteristics = ""

    features = self.applyNodeDefinitionRules(node_characteristics)

    state = STATES[self.editor_phase]["nodes"][0]
    decoration_positions = ModelGraphicsData(node_class,
                                             x, y,  # this sets the initial position
                                             self.graphics_data,
                                             self.editor_phase,
                                             node_type,
                                             state)

    newnodeID = self.model_container.addChild(self.current_ID_node_or_arc,
                                              decoration_positions,
                                              network,
                                              named_network,
                                              node_class,
                                              node_type,
                                              features=features)
    self.state_nodes[newnodeID] = STATES[self.editor_phase]["nodes"][0]

    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "new node": newnodeID,
            "failed"  : False
            }

  def __addBoundaryNode(self, pos, boundary, network, named_connection_network):
    """
    command: add node
    @param pos: position  QtPoint
    @return: dictionary
            "new node":           newnodeID,
            "network":            network
            "arc closed":         arcs_closed,
            "arc open at sink":   arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":             False
    """

    x, y = pos.x(), pos.y()

    # network = self.main.current_network

    # named_network = self.main.named_network_dictionary[network]

    # RULE: node type for boundary is constraint to event dynamic

    if boundary == NAMES["intraface"]:
      application = self.main.ontology.list_intra_node_objects[0]
      features = self.applyNodeDefinitionRules("intraface")
    elif boundary == NAMES["interface"]:
      application = self.main.ontology.list_inter_node_objects[0]
      features = self.applyNodeDefinitionRules("interface")
    else:
      print("fatal error no such boundary: ", boundary)

    node_class = boundary

    state = STATES[self.editor_phase]["nodes"][0]
    decoration_positions = ModelGraphicsData(node_class,
                                             x, y,  # this sets the initial position
                                             self.graphics_data,
                                             self.editor_phase,
                                             application,
                                             state)

    newnodeID = self.model_container.addChild(self.current_ID_node_or_arc,
                                              decoration_positions,
                                              network,
                                              named_connection_network,
                                              node_class,
                                              application,
                                              features=features)
    self.state_nodes[newnodeID] = STATES[self.editor_phase]["nodes"][0]

    self.__redrawScene(self.current_ID_node_or_arc)
    # self.dialog.addNode(newnodeID, self.current_ID_node_or_arc)

    return {
            "new node": newnodeID,
            "failed"  : False
            }

  def __c03_deleteNode(self, nodeID):
    """
    command: remove node nodeID
    @param nodeID: node ID
    @return: dictionary
            "deleted nodes": deleted_nodes,
            "deleted arcs":  deleted_arcs,
            "changed arcs":  changed_arcs,
            "failed": False
    """

    del_nodes = self.model_container.deleteNode(nodeID)

    print("deleting node %s on scene %s" % (nodeID, self.currently_viewed_node))

    for n in reversed(del_nodes):
      # self.dialog.removeNode(n)
      try:
        del self.state_nodes[n]
      except:
        pass

    self.redrawCurrentScene()

    return {"failed": False}

  def __c04_groupNodes(self, pos):
    """
    command: grouping and moving of nodes dependent on the event node
    if the event node is where the group is located, the group is "grouped"
    if the event node is another node, the group is moved.

    @note: The moving cannot be done to
    - any member (including subtrees) of the group
    - to a node which has an arc to a member of the group

    @param pos: position on where to locate the new node when grouping

    @return: dictionary
            "old node":   old_node,
            "new node":    nodeID,
            "moved nodes": moved_nodes,
            "failed":      False
    """
    #  groups if event node is the same as target node
    if not self.node_group:
      res = {}
      res["failed"] = True
      return res

    nodeGroupIDS = []
    for n in self.node_group:
      nodeGroupIDS.append(n.ID)

    arcGroupIDs = []
    for a in self.arc_group:
      arcGroupIDs.append(a.ID)

    # print("group - node group IDs:", nodeGroupIDS)

    pars = self.__c02_addNode(pos, network="composite")
    newNodeID = pars["new node"]
    self.model_container.groupNodes(newNodeID, nodeGroupIDS)
    for n in nodeGroupIDS:
      self.state_nodes[n] = STATES[self.editor_phase]["nodes"][0]

    for a in arcGroupIDs:
      self.state_arcs[a] = STATES[self.editor_phase]["arcs"][0]

    # clear selection
    self.resetGroups()
    # for ID in nodeGroupIDS:
    # self.dialog.moveNode(ID, newNodeID)

    self.model_container["nodes"][newNodeID]["class"] = NAMES["branch"]
    self.model_container["nodes"][newNodeID]["type"] = NAMES["branch"]

    parentID = self.model_container["ID_tree"].getImmediateParent(newNodeID)
    self.__redrawScene(parentID)

    return {
            "failed": False
            }

  def __c05_explodeNode(self, nodeID):
    """
    command: explode a node, inverse of grouping
    @param nodeID: node ID
    @return: dictionary
            "exploded node" : nodeID,
            "moved nodes"   : set,
            "failed": False
    """
    #  explode node

    parentID = self.model_container.explodeNode(nodeID)

    self.__redrawScene(parentID)

    return {
            "exploded node": nodeID,
            "failed"       : False
            }

  def __c01_makeThisCurrentNode(self, nodeID):
    """
    Command: flip page and show current node
    report nodes arcs etc
    @param nodeID: node ID
    @return: dictionary
            "viewed node": nodeID,
            "failed":      False
    """
    #        print "__c09_makeThisCurrentNode", ">__c09_makeThisCurrentNode>", nodeID

    # self.__resetNodeStatesAndSelectedArc()
    self.__redrawScene(nodeID)

    return {
            "viewed node": nodeID,
            "failed"     : False
            }

  def __c06_beginArc(self, nodeID):
    """
    begin generating an arc. Marks a node as begin point for arc.
    @param nodeID: node ID
    @return: dictionary
            "selected source": nodeID,
            "failed":          False
    """
    #  start an arc
    self.state_nodes[nodeID] = "selected"
    nw = self.main.current_network
    # token = copy.copy(self.main.selected_token[self.main.editor_phase][nw])
    # mechanism = copy.copy(self.main.selected_transfer_mechanism[nw][token])
    # nature = copy.copy(self.main.selected_arc_nature[nw][token])
    token = self.main.selected_token[self.main.editor_phase][nw]
    mechanism = self.main.selected_transfer_mechanism[nw][token]
    nature = self.main.selected_arc_nature[nw][token]
    self.arcSourceID = nodeID  # keep for inserting boundary
    self.selected_arc_specs = (token, mechanism, nature)
    self.current_ID_node_or_arc = self.model_container["ID_tree"].getImmediateParent(nodeID)

    self.selected_intraface_node = None
    # self.__ruleNodeAccessTopologyAcrossNetworks()
    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "selected source": nodeID,
            "failed"         : False
            }

  def __c07_addTheArc(self, toNodeID):
    """
    Command: add arc from marked node to "toNodeID" node completes what started with begin arc
    @param toNodeID: destination node ID
    @return: dictionary
            "added arc":  arcID,
            "source node": self.selected_node.getNodeID(),
            "sink node":   toNodeID,
            "failed":      False
    """
    #  this affects all pannels where the arc shows

    insert_intraface = False
    insert_interface = False
    connection_network = None

    if self.model_container["nodes"][self.arcSourceID]["class"] not in [NAMES["intraface"], NAMES["interface"]]:
      source_network = self.model_container["nodes"][self.arcSourceID][NAMES["network"]]
      sink_network = self.model_container["nodes"][toNodeID][NAMES["network"]]
      source_named_network = self.model_container["nodes"][self.arcSourceID][NAMES["named_network"]]
      sink_named_network = self.model_container["nodes"][toNodeID][NAMES["named_network"]]
      # print("__c11_addTheArc", " from network %s to network %s"%(source_network,sink_network))

      # introducing boundary
      # RULE s :
      # RULE: - boundary can only be introduced automatically, not manually  --> automaton
      # RULE: - both sides of the boundaries are in-arcs  --> controlled here
      # RULE: - only two arcs allowed one from each side
      cnw = CR.TEMPLATE_CONNECTION_NETWORK % (source_network, sink_network)
      cnwi = CR.TEMPLATE_CONNECTION_NETWORK % (sink_network, source_network)
      named_connection_network = CR.TEMPLATE_CONNECTION_NETWORK % (source_named_network, sink_named_network)
      if source_network != sink_network:  # two different networks
        # Constructionsite : first determine if it is an intra or an inter face
        # Constructionsite : split source and sink and then build decision on it.
        if cnw in self.intraconnections_dictionary:
          connection_network = cnw
          insert_intraface = True
        elif cnwi in self.intraconnections_dictionary:
          connection_network = cnwi
          insert_intraface = True
        elif cnw in self.interconnections_dictionary:
          connection_network = cnw
          insert_interface = True
        elif cnwi in self.interconnections_dictionary:
          connection_network = cnwi
          insert_interface = True
      # RULE: - intraface if the two named networkds are not the same.
      else:
        if source_named_network != sink_named_network:
          connection_network = cnw
          insert_intraface = True

    token = self.main.selected_token[self.main.editor_phase][source_network]
    if insert_intraface or insert_interface:
      if insert_intraface:
        # Rule : mechanism left must be equal to the mechanism right
        mech_left = self.main.selected_transfer_mechanism[source_network][token]
        mech_right = self.main.selected_transfer_mechanism[sink_network][token]
        if mech_left != mech_right:
          # Rule: if they are not the same then we set the right one equal to the left
          # self.__resetNodeStatesAndSelectedArc()
          # self.redrawCurrentScene()
          # self.main.writeStatus("the mechanisms on both sides must be the same")
          # return {"failed": True}

          mechanisms = sorted(self.main.arcInfoDictionary[sink_network][token].keys())
          index = mechanisms.index(mech_left)
          self.main.setSelectorChecked("mechanism", "mechanism", index)
          self.main.writeStatus("the mechanism on the right has be set idential to the mechanism on the left")

        nature_left = self.main.selected_arc_nature[source_network][token]
        nature_right = self.main.selected_arc_nature[sink_network][token]

        # Rule: nature left must be equal to the mechanism right
        if nature_left != nature_right:
          self.__resetNodeStatesAndSelectedArc()
          self.__c15_reset()
          self.main.writeStatus("the nature of the transfer on both sides must be the same")
          return {"failed": True}

      # seems all is ok so go ahead and put the intraface

      parent_nodeID_source = self.model_container["ID_tree"].getImmediateParent(self.arcSourceID)
      x_source = self.model_container["scenes"][parent_nodeID_source]["nodes"][self.arcSourceID]["position_x"]
      y_source = self.model_container["scenes"][parent_nodeID_source]["nodes"][self.arcSourceID]["position_y"]

      parent_nodeID_sink = self.model_container["ID_tree"].getImmediateParent(toNodeID)
      x_sink = self.model_container["scenes"][parent_nodeID_sink]["nodes"][toNodeID]["position_x"]
      y_sink = self.model_container["scenes"][parent_nodeID_sink]["nodes"][toNodeID]["position_y"]
      x_mid = x_sink + (x_source - x_sink) / 2
      y_mid = y_sink + (y_source - y_sink) / 2
      pos = QtCore.QPoint(x_mid, y_mid)

      if insert_intraface:
        if self.selected_intraface_node == None:
          self.current_ID_node_or_arc = parent_nodeID_source  # insert on source side
          pars = self.__addBoundaryNode(pos, NAMES["intraface"], connection_network, named_connection_network)
          newnodeID = pars["new node"]
        else:
          newnodeID = self.selected_intraface_node
      else:
        self.current_ID_node_or_arc = parent_nodeID_source  # insert on source side
        pars = self.__addBoundaryNode(pos, NAMES["interface"], connection_network, named_connection_network)
        newnodeID = pars["new node"]

      if insert_intraface:
        # RULE: mechanisms are dependent on network
        # thus only the source is known at this point and the sink one must be done manually.
        token, mechanism, arctype = self.selected_arc_specs
        named_network = self.model_container["nodes"][self.arcSourceID]["named_network"]
        arcID, views_with_arc = self.model_container.addArc(self.arcSourceID, newnodeID,
                                                            source_network,
                                                            named_network,
                                                            mechanism,
                                                            token,
                                                            arctype)
        self.model_container["nodes"][newnodeID]["transfer_constraints"][token] = []  # used in colouring
        named_network = self.model_container["nodes"][toNodeID]["named_network"]
        arcID, views_with_arc = self.model_container.addArc(newnodeID, toNodeID,
                                                            sink_network,
                                                            named_network,
                                                            mechanism,
                                                            token,
                                                            arctype)
      elif insert_interface:
        # RULE: interfaces are connected from reading state information writing property
        # rule = self.main.ontology.rules["interface-connections"]
        interface = self.main.ontology.interfaces[connection_network]
        token = interface["token"]
        mechanism = interface["mechanism"]
        arctype = interface["nature"]
        named_network = self.model_container["nodes"][self.arcSourceID]["named_network"]
        arcID, views_with_arc = self.model_container.addArc(self.arcSourceID, newnodeID,
                                                            source_network,
                                                            named_network,
                                                            mechanism,
                                                            token,
                                                            arctype)

        named_network = self.model_container["nodes"][toNodeID]["named_network"]
        arcID, views_with_arc = self.model_container.addArc(newnodeID, toNodeID,
                                                            sink_network,
                                                            named_network,
                                                            mechanism,
                                                            token,
                                                            arctype)

    else:
      named_network = self.model_container["nodes"][toNodeID]["named_network"]
      arcID, views_with_arc = self.model_container.addArc(self.arcSourceID, toNodeID,
                                                          self.main.current_network,
                                                          named_network,
                                                          self.main.selected_transfer_mechanism[
                                                            self.main.current_network][token],
                                                          self.main.selected_token[self.main.editor_phase][
                                                            self.main.current_network],
                                                          self.main.selected_arc_nature[self.main.current_network][
                                                            token])

    self.state_nodes[self.arcSourceID] = STATES[self.editor_phase]["arcs"][0]
    self.arcSourceID = None

    self.clearSelectedNodes()
    self.clearBlockedNodes()

    self.current_ID_node_or_arc = self.model_container["ID_tree"].getImmediateParent(toNodeID)
    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "added arc": arcID,
            "sink node": toNodeID,
            "failed"   : False
            }

  def __c11_insertKnot(self):
    """
    Command: insert knot into edge pointed to
    @postcondition: self.current_item.parentItem() must be an edge
    @return: dictionary
            "arc" : arcID,
            "failed" : False
    """

    #  insert knot in the middle
    edge = self.current_item.parent
    arcID = edge.arcID

    nodeA = edge.source
    nodeB = edge.dest
    # print("inser knot source dest:", nodeA.graphics_root_object,  nodeB.graphics_root_object)
    #
    middlePoint = edge.getMidPoint()
    position = middlePoint.x(), middlePoint.y()

    sourcePoint = nodeA.pos()
    s_x = sourcePoint.x()
    s_y = sourcePoint.y()
    destPoint = nodeB.pos()
    d_x = destPoint.x()
    d_y = destPoint.y()

    knot_list = self.model_container["scenes"][self.currently_viewed_node]["arcs"][arcID]
    # print("node list", knot_list)
    if len(knot_list) > 0:
      if nodeA.graphics_root_object == NAMES["elbow"]:
        if nodeB.graphics_root_object == NAMES["elbow"]:
          indexA = knot_list.index((s_x, s_y))
          indexB = knot_list.index((d_x, d_y))
        else:
          indexA = knot_list.index((s_x, s_y))
          indexB = -1
      else:
        if nodeB.graphics_root_object == NAMES["elbow"]:
          indexA = -1
          indexB = knot_list.index((d_x, d_y))

    else:
      indexA = -1
      indexB = -1

    # print("indices ", indexA, indexB)

    self.model_container.insertKnot(self.currently_viewed_node, arcID, indexA, indexB, position)

    self.redrawCurrentScene()

    return {
            "arc"   : arcID,
            "failed": False
            }

  def __c08_removeArc(self, arcID):
    """
    Command: remove specified arc
    @param arcID: arc ID
    @return: dictionary
            "arc" : arcID,
            "failed": False
    """
    #  remove the identified arc
    #        print "__c14_removeArc", "remove arc ", arcID
    # check if this an arc that connects to an intraface or an interface
    arcs_to_delete = [arcID]

    # rule: delete both related arcs that are connected to an intraface
    intraface_interface_possibly_to_delete = None
    for node in self.model_container["nodes"]:
      if self.model_container["nodes"][node]["class"] == NAMES["intraface"]:
        arcs = self.model_container.getArcsConnectedToNode(node)
        if arcID in arcs:
          print("delete found an intraface")
          token1 = self.model_container["arcs"][arcID]["token"]
          mech1 = self.model_container["arcs"][arcID]["mechanism"]
          nature1 = self.model_container["arcs"][arcID]["nature"]
          for arcID2 in arcs:
            if arcID != arcID2:
              token2 = self.model_container["arcs"][arcID2]["token"]
              mech2 = self.model_container["arcs"][arcID2]["mechanism"]
              nature2 = self.model_container["arcs"][arcID2]["nature"]
              if (token1 == token2) and (mech1 == mech2) and (nature1 == nature2):
                arcs_to_delete.append(arcID2)
                intraface_interface_possibly_to_delete = node
      elif self.model_container["nodes"][node]["class"] == NAMES["interface"]:
        arcs = self.model_container.getArcsConnectedToNode(node)
        if arcID in arcs:
          print("delete found an interface")
          arcs_to_delete = arcs
          intraface_interface_possibly_to_delete = node

    # TODO: once a node has no arcs, it has no tokens thus the affected nodes need to be updated
    for arc in arcs_to_delete:
      self.model_container.deleteArc(arc)
      print("remove arc ", arc, " from ", self.currently_viewed_node)
      del self.state_arcs[arc]

    if intraface_interface_possibly_to_delete:
      arcs = self.model_container.getArcsConnectedToNode(intraface_interface_possibly_to_delete)
      if len(arcs) == 0:
        self.__c03_deleteNode(intraface_interface_possibly_to_delete)
      else:
        self.redrawCurrentScene()
    else:
      self.redrawCurrentScene()
    return {
            "arc"   : arcID,
            "failed": False
            }

  def __c12_removeKnot(self):
    """
    Command: remove knot
    @postcondition: self.current_item.parentItem() must be a knot
    @return: dictionary
            "arc": arcID,
            "failed": False
    """
    knot = self.current_item.parent
    self.model_container.removeKnot(self.currently_viewed_node, knot.arcID,
                                    knot.pos().x(), knot.pos().y())
    self.redrawCurrentScene()

    return {
            "arc"   : knot.arcID,
            "failed": False
            }

  def __c09_reconnectArc(self, pointer_object_name):
    """
    Command: starts reconnecting an existing arc
    @param pointer_object_name: is a end-pointer on the edge
    @return: dictionary
            "arc" :        self.selected_arcID,
            "target node": S_ID,
            "failed":      False
    """
    #  each edge =section of an arc between two knots, is direction sensitive
    #  it is the node closer to which knot one points to
    #  that is being selected, that is if it is not an open arc

    # todo: one cn now reconnect to another network -- must be disabled

    item = self.current_item
    self.selected_arcID = item.parent.getArcID()
    self.state_arcs[self.selected_arcID] = "selected"

    if NAMES["tail"] in pointer_object_name:
      self.end_to_move = "source"
      node_to_block = (self.model_container["arcs"][self.selected_arcID]["sink"])  # str(self.model_container[
      # "arcs"][self.selected_arcID]["sink"]) #HAP: str --> int
    elif NAMES["head"] in pointer_object_name:
      self.end_to_move = "sink"
      node_to_block = (self.model_container["arcs"][self.selected_arcID]["source"])  # str(self.model_container[
      # "arcs"][self.selected_arcID]["source"]) #HAP: str --> int

    self.state_nodes[node_to_block] = "selected"

    self.__resetNodeStatesAndSelectedArc()
    self.redrawCurrentScene()

    return {
            # "target node": S_ID,
            "failed": False
            }

  def __c10_changeArc(self, C_ID):
    """
    Command: change specified arc
    @param C_ID: new node"s ID where specified end of the arc is
                re-connected
    @postcondition: self.selected_arcID must contain an arc object's ID
    @return: dictionary
            "arc":               self.selected_arcID,
            "old source & sink": (old_source, old_sink),
            "new source & sink": (fromNode, toNode),
            "failed":            False
    """
    #  changing arc
    #  requires an
    #  - new nodeID: C_ID
    #  - arcID which was identified before being in self.selected_arcID
    #  - information if it is the source or the sink to be changed

    self.model_container.changeArc(self.selected_arcID,
                                   self.end_to_move,
                                   C_ID)

    self.state_arcs[self.selected_arcID] = STATES[self.editor_phase]["arcs"][0]
    nodeID = self.model_container["ID_tree"].getImmediateParent(C_ID)

    self.__resetNodeStatesAndSelectedArc()  # revokes isolation of the current network
    self.__redrawScene(nodeID)

    return {
            "failed": False
            }

  def __c13_makeCopy(self, nodeID):
    """
    Command: make a copy of the subtree with the root nodeID
    @param nodeID: node ID of subtree's root
    @return: combined dictionaries
           containing: from model
                "root":     root,
                "node map": node_map,
                "arc map":  arc_map
            and __c22:
                "saved file": f,
                "failed": False
            and
                "new root" : nodeID
    """

    # get schnipsel name -- rule: new or used
    schnipsel_name_to_be_saved, new_model = askForModelFileGivenOntologyLocation(self.main.ontology_name,
                                                                                 left_icon="reject",
                                                                                 left_tooltip="reject",
                                                                                 right_icon="accept",
                                                                                 right_tooltip="accept", )

    container = self.model_container.extractSubtree(nodeID)
    schnipsel_file = os.path.join(self.main.model_library_location, schnipsel_name_to_be_saved)
    f = schnipsel_file + RI.EXTENSION_GRAPH_DATA
    container.write(f)
    self.main.writeStatus("saved schnipsel to %s" % schnipsel_name_to_be_saved)
    self.schnipsel_file = schnipsel_file
    self.main.setSchnipsel(schnipsel_name_to_be_saved)

    res_dic = {}
    res_dic["new root"] = nodeID
    res_dic["failed"] = False

    return res_dic  # result from saving

  def __c14_insertModelFromFile(self, model_file):
    """
    Command: insert a model
    @return: dictionary
            "inserted nodes": nodes_on_root,
            "inserted arcs":  arcs,
            "node map":       node_map,
            "arc map":        arc_map,
            "arc closed": arcs_closed,
            "arc open at sink": arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":         False,
    """
    #  insert file as shown in main window

    if not model_file:
      self.main.writeStatus("no model defined")
      return

    f = model_file  # + RI.EXTENSION_GRAPH_DATA
    # print(model_file)
    self.model_container.makeFromFile(f)
    self.main.named_network_dictionary = self.model_container["named_networks"]
    self.main.makeNamedNetworkBrushes()

    self.model_container.updateTokensInAllDomains()
    self.model_container.updateTypedTokensInAllDomains()

    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "failed": False,
            }

  def __c15_reset(self):
    """
    Command: reset from current operation
        - de-select selected nodes and arcs
        - deletes group
    @return: dictionary
            "failed": False
    """

    self.__resetNodeStatesAndSelectedArc()

    self.redrawCurrentScene()
    self.editor_state = GRAPH_EDITOR_STATES[self.editor_phase][0]

    return {"failed": False}

  def __c16_editName(self, nodeID):
    # NOTE: breaks the strict command design would need to be changed to receive a name from the protocol or
    # NOTE: an empty name then asking one for live change
    name = self.model_container["nodes"][nodeID]["name"]
    if name == "default":
      name = nodeID
    self.string_dialog.show()
    self.string_dialog.setText(name)

    return {"failed": False}

  def __c21_setCurrentLibFile(self, schnipsel_file):
    """
    Command: set current schnipsel_file name
    @param name: schnipsel_file
    @return: dictionary
            "failed":       False
    """
    self.schnipsel_file = schnipsel_file
    return {
            "failed": False
            }

  def __c22_mapAndSaveModel(self, model, f):  # TODO this is obsolete model is always mapped just save maps!
    """
    Command: map and save model.
    This remaps the whole model tree starting with root being 0 consecutive
    renumbering the nodes.
    @param model: model object
    @param f: file name
    @return: dictionary
           containing: from model
                "root":     root,
                "node map": node_map,
                "arc map":  arc_map
            and :
                "saved file": f,
                "failed": False
    """

    self.__c23_saveData(model, f)

    # f_ = f + RI.EXTENSION_GRAPH_DATA
    # print("__c22_mapAndSaveModel", "__map and save model in commander to file :", f_)
    # node_map = self.model_container.write(f_)

    return {"failed": False}  # res_dic

  def __c23_saveData(self, model, f):
    """
    Command: save data on file f
    @param model: model object
    @param f: file name
    @return: dictionary
            "saved file": f,
            "failed": False
    """
    #
    # print("debugging -- library model name: ", self.library_model_name)
    # print("debugging -- model container   : ", self.model_container)
    ff = os.path.basename(f)
    name, ext = os.path.splitext(ff)
    dir = os.path.dirname(f)
    f_flat = os.path.join(dir, "%s_flat%s" % (name, ext))

    node_map = self.model_container.write(f)
    self.model_container.makeAndWriteFlatTopology(f_flat)

    mapped_currently_viewed_node = node_map[int(self.currently_viewed_node)]
    self.currently_viewed_node = (mapped_currently_viewed_node)  # str(mapped_currently_viewed_node) #HAP: str --> int
    self.__redrawScene(self.currently_viewed_node)
    # print("debugging -- __c23_saveData",
    #       "--------- currently node viewed : %s ---> %s" % (self.currently_viewed_node, mapped_currently_viewed_node))
    # print("debugging -- __c23_saveData", "--------- saved graph file:", f)
    return {
            "saved file": f,
            "failed"    : False
            }

  def __c25_insertSchnipsel(self, position):
    """
    Command: insert a model
    @return: dictionary
            "inserted nodes": nodes_on_root,
            "inserted arcs":  arcs,
            "node map":       node_map,
            "arc map":        arc_map,
            "arc closed": arcs_closed,
            "arc open at sink": arcs_open_at_sink,
            "arc open at source": arcs_open_at_source,
            "failed":         False,
            "library file":   self.library_model_name
    """
    #  insert file as shown in main window

    if not self.schnipsel_file:
      self.main.writeStatus("no schnipsel defined")
      return {"failed": True}

    f = self.schnipsel_file
    if not os.path.exists(f):
      self.main.writeStatus("no such file %s" % f)
      return {"failed": True}

    tree, node_map, arc_map, node_offset, parent_ID = \
      self.model_container.addFromFile(f, self.current_ID_node_or_arc,
                                       position,
                                       self.graphics_data,
                                       self.editor_phase)

    self.__redrawScene(self.current_ID_node_or_arc)

    return {
            "failed"      : False,
            "library file": self.library_model_name
            }

  def __c27_selectIntrafaceNode(self, nodeID):
    """
    selects and unselects
    :param nodeID: node ID as string
    :return:
    """
    print("debugging -- selecting node")
    node_type = self.model_container["nodes"][nodeID]["class"]
    if node_type in [NAMES["node"]]:
      self.node_group.add(nodeID)
      self.state_nodes[nodeID] = "selected"
    if node_type in [NAMES["intraface"]]:
      self.selected_intraface_node = nodeID
      self.node_group.add(nodeID)
      self.state_nodes[nodeID] = "selected"
    if node_type in [NAMES["panel"]]:
      self.__resetNodeStatesAndSelectedArc()

    ancestors = self.model_container["ID_tree"].getAncestors(nodeID)
    self.__redrawScene(ancestors[0])

    return {"failed": False}

  def __c28_injectTypedTokensOrConversions(self, nodeID):
    self.node_group.add(nodeID)
    select = self.main.state_inject_or_constrain_or_convert
    if select == "inject":
      self.main.injectTypedTokens()
    elif select == "convert":
      self.main.injectConversions()
    elif select == "constrain":
      self.main.injectTypedTokenTransferConstraints()
    return {"failed": False}

  def __c31_computeTypedTokenDomains(self):

    print("__c31_computeTypedTokenDomains -- not yet implemented")
    return {"failed": False}

  def __setName(self, node, name):
    if name == CR.DEFAULT:
      name = str(node.ID)
    for i in list(node.getItemList().keys()):
      if "name" == i:
        node.modifyComponentAppearance(i, ("setText", name))
        nodeID = node.ID
        try:
          self.dialog.changeNodeName(nodeID, name)  # note: interface is not always up-to-date
        except:
          pass

  def __makeViewAndScene(self, nodeID):
    self.__setupScene(nodeID)
    self.__setupView(nodeID)
    self.__putEnvironment(nodeID)

  def __changeName(self, name):  # connected to c16_editName
    nodeID = self.current_ID_node_or_arc
    self.model_container["nodes"][nodeID]["name"] = name

    self.__redrawScene(self.currently_viewed_node)

  def __resetNodeStatesAndSelectedArc(self):
    self.arcSourceID = None
    for n in self.state_nodes:
      self.state_nodes[n] = STATES[self.editor_phase]["nodes"][0]
    for a in self.state_arcs:
      if self.state_arcs[a] == "selected":
        self.state_arcs[a] = STATES[self.editor_phase]["arcs"][0]
    self.resetGroups()
    self.clearSelectedNodes()
    self.selected_intraface_node = None

  def __reportEvent(self, state, next_state, action, item_type, event):
    """
    report mouse event in logging view
    @param state:      current state of automaton
    @param next_state: next state
    @param action:     action to be taken
    @param item_type:  item type
    @param event:      event
    """
    """
    """
    s = ("\n" + str(self.step) + \
         "- state: " + state + \
         "\t- next_state: " + next_state + \
         "\n" + str(self.step) + \
         "- object: " + item_type + \
         "\t- event: " + event + \
         "\n" + str(self.step) + \
         "\t- action: " + action)
    self.main.logger.onUpdateStandardOutput(s)
    pass

  def __drawNode(self, x, y, ID, graphics_root_object, application):
    node = Node(ID, graphics_root_object, application, x, y, self.scene, self.view, self)
    # print("draw node %s indicators %s " % (ID, indicator))
    if graphics_root_object == NAMES["node"]:  # only add to simple nodes
      if (graphics_root_object not in [INTRAFACE, INTERFACE]) or ():
        indicator = self.__makeIndicators(ID)
        for i in indicator:
          name = indicator[i]["name"]
          type = indicator[i]["type"]
          x = indicator[i]["position_x"]
          y = indicator[i]["position_y"]
          rgba_colour = indicator[i]["colour"]
          if type == NAMES["indicator token"]:
            node.addIndicatorDot(name, x, y, rgba_colour)
          else:
            node.addIndicatorText(name, x, y, indicator[i]["label"])

    if graphics_root_object in [NAMES["node"], NAMES["reservoir"]]:
      # add tool tip
      data = self.model_container["nodes"][ID]
      s = "<nobr> <b> node: <b> </nobr><br/>"
      for d in data:
        s += "<nobr> %s -- %s </nobr><br/>"%(d, data[d])
      # s = TOOLTIP_TEMPLATES["nodes"] % (
      #         data["network"],
      #         data["named_network"],
      #         data["type"],
      #         data["tokens"])
      # if "conversions" in data:
      #   s.join("<br>%s" % data["conversions"])
      print("debugging -- tool tip:", s)
      node.setToolTip(s)

    if graphics_root_object == NAMES["intraface"]:
      # add tool tip
      data = self.model_container["nodes"][ID]
      s = "<nobr> <b> intraface: <b> </nobr><br/>"
      for d in data:
        s += "<nobr> %s -- %s </nobr><br/>"%(d, data[d])
      # s = TOOLTIP_TEMPLATES["intraface"] % (data["network"],
      #                                       data["named_network"],
      #                                       data["type"],
      #                                       data["tokens_left"],
      #                                       data["tokens_right"]
      #                                       )

      node.setToolTip(s)

    self.scene.addItem(node)
    name = str(self.model_container["nodes"][ID][NAMES["name"]])  # Note: in a new model this is an integer 0
    if name == "0":
      name = self.main.model_name
    self.__setName(node, name)
    return node

  def __drawArc(self, arcID, fromNode, toNode):
    # if self.editor_phase == "token_topology":
    #   print("debugging -- draw arc")
    arc = Arc_Edge(arcID,
                   fromNode, toNode,
                   self.scene,
                   self.view,
                   self)

    data = self.model_container["arcs"][arcID]
    s = "<nobr> <b> arc: <b> </nobr><br/>"
    for d in data:
      s += "<nobr> %s -- %s </nobr><br/>" % (d, data[d])

    # s = TOOLTIP_TEMPLATES["arc"] % (data["network"],
    #                                 data["named_network"],
    #                                 data["mechanism"],
    #                                 data["nature"],
    #                                 data["token"],
    #                                 data["typed_tokens"],
    #                                 )
    arc.setToolTip(s)

    self.scene.addItem(arc)

    return

  def __setupView(self, nodeID):
    """
    set up a new view for node nodeID
    @param nodeID: node ID
    """

    del self.view

    v = self.main.ui.graphicsView
    scene = self.scene
    v.setScene(scene)
    v.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
    v.setRenderHint(QtGui.QPainter.Antialiasing)
    v.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
    v.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
    v.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
    self.view = v
    scene.update()
    self.view.update()

  def __putEnvironment(self, nodeID):
    """
    put the environment on node nodeID
    The graphical representation of the environment is generated every time it is not stored in the
    data file. Thus the location of the ancestors and siblings is autogenerated
    in contrast to the location of the child nodes. Their location is being stored in the model file.

    This will enable to re-size the view dynamically.

    @param nodeID: node ID
    """
    # for the generation of the environment get first the geometry from the base graphical data generator

    root_data = self.graphics_data.getData(self.editor_phase, NAMES["panel"],
                                           NAMES["root"], self.current_application, R.M_None)
    ancestors_panel_data = self.graphics_data.getData(self.editor_phase, NAMES["panel"],
                                                      NAMES["left panel"], self.current_application, R.M_None)
    width_anchestors_panel = ancestors_panel_data["width"]
    siblings_pannel_data = self.graphics_data.getData(self.editor_phase, NAMES["panel"],
                                                      NAMES["right panel"], self.current_application, R.M_None)
    width_siblings_panel = siblings_pannel_data["width"]

    # set size of panels
    width_view = self.main.ui.graphicsView.width()
    height_view = self.main.ui.graphicsView.height()

    x_view = self.view.rect().x()
    y_view = self.view.rect().y()

    x = x_view - width_view / 2 - 5  # transformation and adjustment for frame
    y = y_view - height_view / 2 - 5

    MARGIN_X = 0
    MARGIN_Y = 0

    w_root = width_view - width_anchestors_panel - width_siblings_panel - 2 * MARGIN_X
    x_root = x + width_anchestors_panel + MARGIN_X
    h_root = height_view - 2 * MARGIN_Y
    y_root = y + MARGIN_Y

    root_data["position_x"] = x_root
    root_data["position_y"] = y_root
    root_data["width"] = w_root
    root_data["height"] = h_root
    ancestors_panel_data["position_x"] = x
    ancestors_panel_data["position_y"] = y
    ancestors_panel_data["height"] = h_root
    siblings_pannel_data["position_x"] = x + width_view - width_siblings_panel
    siblings_pannel_data["position_y"] = y
    siblings_pannel_data["height"] = h_root
    self.view.offset = QtCore.QPoint(x, y)  # transformation of rubber band

    #  setup environment
    ancestors = self.model_container["ID_tree"].getAncestors(nodeID)
    siblings = self.model_container["ID_tree"].getSiblings(nodeID)

    if nodeID not in self.state_nodes:
      self.state_nodes[nodeID] = STATES[self.editor_phase]["nodes"][0]
    env = NodeView(nodeID, self)
    self.scene.addItem(env)

    dy_connector = LOCATION_PARAMETERS["connector_offset"]
    dy_ancestor = LOCATION_PARAMETERS["ancestor_offset"]
    dy_sibling = LOCATION_PARAMETERS["sibling_offset"]
    x_ancestors = x + width_anchestors_panel
    y_ancestors = - height_view / 2 + dy_ancestor
    self.__addAncestors(nodeID, ancestors, x_ancestors, y_ancestors)
    x_siblings = + width_view / 2 - width_siblings_panel
    y_siblings = - height_view / 2 + dy_sibling
    self.__addSiblings(nodeID, siblings, x_siblings, y_siblings)
    x_connector = 0
    y_connector = - height_view / 2 + dy_connector
    self.__drawNode(x_connector, y_connector, nodeID, NAMES["connector"], self.current_application)

  def __addAncestors(self, nodeID, ancestors, x_o, y_o):
    counter = 0
    h = LOCATION_PARAMETERS["ancestor_spacing"]  # 50

    for i in reversed(ancestors):
      y = y_o + 25 + counter * h
      node = self.__drawNode(x_o, y, i, NAMES["parent"], self.current_application)

      data = self.model_container["nodes"][i]
      s = TOOLTIP_TEMPLATES["ancestor"] % data["name"]
      node.setToolTip(s)
      counter = counter + 1

  def __addSiblings(self, nodeID, siblings, x_o, y_o):
    counter = 0

    h = LOCATION_PARAMETERS["sibling_spacing"]  # h = 50
    for i in siblings:
      y = y_o + 25 + counter * h
      node = self.__drawNode(x_o, y, i, NAMES["sibling"], self.current_application)
      data = self.model_container["nodes"][i]
      s = TOOLTIP_TEMPLATES["sibling"] % data["name"]
      node.setToolTip(s)
      counter = counter + 1
      counter = counter + 1

  def __setupScene(self, nodeID):
    """
    set up a scene for node nodeID
    @param nodeID: node ID
    """

    del self.scene

    scene_width = self.main.ui.graphicsView.width()
    scene_height = self.main.ui.graphicsView.height()

    adjust = 10
    scene = QtWidgets.QGraphicsScene(self.main)  # tie on to main widget
    scene.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)  # TODO check which one works better
    scene.setItemIndexMethod(QtWidgets.QGraphicsScene.BspTreeIndex)
    scene.setSceneRect(float(-scene_width / 2.0), -float(scene_height / 2.0),
                       float(scene_width - adjust), float(scene_height - adjust))
    self.scene = scene

  def __delScene(self, nodeID):
    """
    delete a scene
    @param nodeID: node ID
    """
    self.scene = None
    pass

  def __getObjectFromScene(self, scene_object, sceneID, OID):
    # for O in self.scenes[sceneID].items():
    for O in self.scene.items():
      StrO = str(O.__class__)
      t = StrO.split(".")[-1]  # get last bit
      tt = t.split("'")[0]  # remove '>
      if scene_object == tt:
        if O.ID == OID:
          return O
    return None

  def __makeIndicators(self, ID):
    indicator = OrderedDict()
    tokens = self.model_container.getTokensInNode(ID)
    if not tokens:
      return indicator

    pos = {}
    x_ = LOCATION_PARAMETERS["token_indicators"]["x"]
    y_ = LOCATION_PARAMETERS["token_indicators"]["y"]
    dx = LOCATION_PARAMETERS["token_indicators"]["dx"]
    dy = LOCATION_PARAMETERS["token_indicators"]["dy"]

    for token in tokens:
      pos[token] = (x_, y_)
      x_ = x_ + dx
      y_ = y_ + dy

    # print("make indicators ", self.main.typedTokens[self.main.current_network])
    for token in self.model_container["nodes"][ID]["tokens"]:
      # RULE: interface tokens are not shown
      if token in self.main.ontology.tokens:

        name = token
        # NOTE: if you get an error here then you need to add a token colour above
        colour = self.main.TOKENS[token]['colour']  # rgba_colour[token]
        x, y = pos[token]
        # print("set tokens token %s, x: %s, y: %s" % (token, x, y))
        indicator[name] = {
                "name"      : name,
                "position_x": x,
                "position_y": y,
                "colour"    : colour,
                "type"      : NAMES["indicator token"]
                }

        typed_tokens = self.model_container["nodes"][ID]["tokens"][token]
        y_t = copy.copy(y) - 25
        for typed_token in typed_tokens:
          name = "%s-%s" % (token, typed_token)
          colour = self.main.TOKENS[token]['colour']
          y_t = y_t - 15
          indicator[name] = {
                  "name"      : name,
                  "position_x": x - 10,
                  "position_y": y_t,
                  "colour"    : colour,
                  "type"      : NAMES["indicator typed token"],
                  "label"     : typed_token
                  }
          pass

    # print("indicator definition:", indicator)
    return indicator

  def __redrawScene(self, nodeID, debug=False):
    """
    redraw a scene
    @param nodeID: node ID
    """

    # print("begin redraw scene")
    self.currently_viewed_node = nodeID
    self.__makeViewAndScene(nodeID)

    if debug:
      print("start redraw node ", nodeID)

    self.applyControlAccessRules()

    # nodes
    children = self.model_container["ID_tree"].getChildren(nodeID)
    for child in children:
      graph_object_class = self.model_container["nodes"][child]["class"]
      application = self.model_container["nodes"][child]["type"]
      self.__drawNode(0, 0, child, graph_object_class, application)

    # arcs
    arcs_on_scene = list(self.model_container["scenes"][nodeID]["arcs"].keys())
    for arcID in arcs_on_scene:
      if arcID not in self.state_arcs:
        self.state_arcs[arcID] = STATES[self.editor_phase]["arcs"][0]

      fromNodeID = self.model_container["arcs"][arcID]["source"]  # str(self.model_container["arcs"][arcID][
      # "source"]) #HAP: str --> int
      toNodeID = self.model_container["arcs"][arcID][
        "sink"]  # str(self.model_container["arcs"][arcID]["sink"])   #HAP: str --> int
      nodes_IDs = self.model_container["ID_tree"].getNodes()

      if fromNodeID not in nodes_IDs:
        self.state_arcs[arcID] = "open"
      else:
        if self.model_container["ID_tree"].getChildren(fromNodeID) != []:
          self.state_arcs[arcID] = "open"
      if toNodeID not in nodes_IDs:
        self.state_arcs[arcID] = "open"
      else:
        if self.model_container["ID_tree"].getChildren(toNodeID) != []:
          self.state_arcs[arcID] = "open"

      subarc = self.model_container.getArcOnNodeScene(arcID)
      sourceID, sinkID = subarc[nodeID]
      fromNode = self.__getObjectFromScene("Node", nodeID, sourceID)
      toNode = self.__getObjectFromScene("Node", nodeID, sinkID)

      no_knots = len(self.model_container["scenes"][nodeID]["arcs"][arcID])
      if no_knots != 0:
        last_knot = None
        fNode = fromNode
        for k in range(no_knots):
          (x, y) = self.model_container["scenes"][nodeID]["arcs"][arcID][k]
          knot = Knot(k, arcID, x, y, self.scene, self.view, self)  # current_view_object, self)
          # print("redraw -- adding knot")
          # self.scene.addItem(knot)
          data = self.model_container["arcs"][arcID]
          s = '<b> %s - %s <b><br>%s <br>%s <br>%s - %s ' % (data["network"],
                                                             data["named_network"],
                                                             data["mechanism"],
                                                             data["nature"],
                                                             data["token"],
                                                             data["typed_tokens"],
                                                             )
          knot.setToolTip(s)

          # collision check for knots only
          for i in self.scene.items():
            if (knot.collidesWithItem(i)):
              # print("collision:", i.graphics_root_object)
              if i.graphics_root_object in [NAMES["intraface"],
                                            NAMES["interface"],
                                            NAMES["branch"],
                                            NAMES["node"],
                                            NAMES["elbow"],
                                            NAMES["connector"]]:
                print("collision execute avoidance:", i.graphics_root_object)
                x_ = knot.x()
                y_ = knot.y()
                width = knot.boundingRect().width()
                x = x_ + width
                y = y_ + width
                knot.setY(y)
                knot.setX(x)

                self.model_container.updateKnotPosition(self.currently_viewed_node, arcID,
                                                        k,
                                                        x, y)

          self.scene.addItem(knot)
          if k > 0:
            fNode = last_knot
          tNode = knot
          self.__drawArc(arcID, fNode, tNode)
          last_knot = knot
        self.__drawArc(arcID, last_knot, toNode)

      else:
        self.__drawArc(arcID, fromNode, toNode)

  def __ruleNodeAccessTopologyAcrossNetworks(self):
    viewed_node = self.currently_viewed_node

    children = self.model_container["ID_tree"].getChildren(viewed_node)

    for child in children:  # set the default when not defined
      if child not in self.state_nodes:
        self.state_nodes[child] = STATES[self.editor_phase]["nodes"][
          0]  # RULE: the first in the list is the default usually "enabled"  # default is enabled

    self.clearBlockedNodes()

    # RULE: Boundary -> only one connection per token for the respective network

    for node in children:
      # network_node = self.model_container["nodes"][node][NAMES["network"]]
      node_class = self.model_container["nodes"][node]["class"]
      if node_class == NAMES["intraface"]:
        arcs_connected_to_node = self.model_container.getArcsConnectedToNode(node)
        # print("intraface %s , connected arcs %s -- token %s" % (node, arcs_connected_to_node, token))

        # if token is in the intraface - allow for only two connections

        if self.state_nodes[node] == "selected":
          return  # when connecting it comes through here twice so this is the second time

        intraface_node = self.model_container["nodes"][node][NAMES["network"]]
        network_left, network_right = intraface_node.split(CR.CONNECTION_NETWORK_SEPARATOR)  # NETWORK_SEPARATOR)
        # network_tokens_left = self.main.tokens_on_networks[network_left]["type"]
        tokens = set()
        left = set(self.model_container["nodes"][node]["tokens_left"].keys())
        right = set(self.model_container["nodes"][node]["tokens_right"].keys())
        tokens = left.union(right)

        # are there existing connections ?
        arc_IDs = list(self.model_container["arcs"].keys())
        mech_left = self.main.selected_transfer_mechanism[network_left]
        mech_right = self.main.selected_transfer_mechanism[network_right]
        if arc_IDs:
          for arc in arc_IDs:
            mechanism = self.model_container["arcs"][arc]["mechanism"]
          if mech_left != mech_right:
            # error is handled in adding the arcs when going through an intraface
            # print(">>>>>>>>>>>>>>>>> error -- the two mechanisms must be the same" ,"mechanisms left and right:",
            # mech_left, mech_right)
            pass
          else:
            if self.main.selected_token[self.main.editor_phase][network_left] in tokens:
              if mech_left != mechanism:
                self.state_nodes[node] = "enabled"
              else:
                self.state_nodes[node] = "blocked"
            else:
              self.state_nodes[node] = "enabled"

  def __ruleNodeAccessInNetworkOnly(self):
    nodeID = (self.model_container["arcs"][self.selected_arcID][self.end_to_move])  # str(self.model_container[
    # "arcs"][self.selected_arcID][self.end_to_move]) #HAP:str --> int

    source_network = self.model_container["nodes"][nodeID][NAMES["network"]]
    children = self.model_container["ID_tree"].getChildren(self.currently_viewed_node)

    for child in children:
      network = self.model_container["nodes"][child][NAMES["network"]]
      if self.state_nodes[child] != "selected":
        if network != source_network:
          self.state_nodes[child] = "blocked"
        else:
          self.state_nodes[child] = "enabled"  # default is enabled

  def __ruleNodeAccessTypedTokensInject(self):
    print("debugging -- token control inject rule")

    #
    # RULE: only constant systems can receive tokens in a given network
    # RULE: do not block the selected nodes but only if token is in present
    # SOMETHING IS FISHY here

    children = self.model_container["ID_tree"].getChildren(self.currently_viewed_node)
    tokens = self.main.tokens_on_networks[self.main.current_network]
    for child in children:  # set the default (initialisation, import etc.)
      if child not in self.state_nodes:
        self.state_nodes[child] = "blocked"  # default is blocked
    for node in children:
      self.__enableNodeOnRule(node, "nodes_allowing_token_injection")
      # if self.state_nodes[node] != "selected":
      #   self.state_nodes[node] = "blocked"
      #   network = self.main.current_network
      #   named_network = self.model_container["nodes"][node]["named_network"]
      #   if named_network == self.main.current_named_network:  # self.main.current_network:
      #     if "constant" in self.model_container["nodes"][node]["type"]:
      #       for token in tokens:
      #         if token in self.main.nw_token_typedtoken_dict[network].keys():
      #           if token in self.model_container["nodes"][node]["tokens"]:
      #             self.state_nodes[node] = "enabled"

    # self.setDefaultEditorState()

  def __ruleNodeAccessTypedTokensConvert(self):
    # RULE: only simple nodes in a given network
    # RULE: do not block the selected nodes

    children = self.model_container["ID_tree"].getChildren(self.currently_viewed_node)

    # for child in children:  # set the default (initialisation, import etc.)
    #   if child not in self.state_nodes:
    #     self.state_nodes[child] = "blocked"  # default is blocked

    for node in children:
      self.__enableNodeOnRule(node,"nodes_allowing_token_conversion")

  def __enableNodeOnRule(self, node, rule):
    self.state_nodes[node] = "blocked"    # default is blocked
    network = self.model_container["nodes"][node]["network"]
    if network == self.main.current_network:
      node_data = self.model_container["nodes"][node]
      node_type = node_data["type"]
      if NODE_COMPONENT_SEPARATOR in node_type:
        node_component, app = node_type.split(NODE_COMPONENT_SEPARATOR)
      else:
        node_component = node_type
      if node_component in self.main.ontology.rules[rule]:
        self.state_nodes[node] = "enabled"

  def __ruleNodeAccessTypedTokensConstrain(self):
    #
    # RULE: transfer constraints - only for boundaries with equal token on either side
    # RULE: do not block the selected nodes

    children = self.model_container["ID_tree"].getChildren(self.currently_viewed_node)

    # for child in children:  # set the default (initialisation, import etc.)
    #   if child not in self.state_nodes:
    #     self.state_nodes[child] = "blocked"  # default is blocked

    for node in children:
      if self.state_nodes[node] != "selected":
        self.state_nodes[node] = "blocked"
        if NAMES["intraface"] == self.model_container["nodes"][node]["class"]:  # TODO:  token is the key -- must only
          #  be one

          if (self.model_container["nodes"][node]["tokens_left"].keys() == \
                  self.model_container["nodes"][node]["tokens_right"].keys()) or \
            (self.main.selected_token[self.main.editor_phase][self.main.current_network] in \
                    self.model_container["nodes"][node]["tokens_left"].keys()):
              self.state_nodes[node] = "enabled"
    pass

  def __ruleNodeAccessUndetermined(self):
    #
    # RULE: if the state is not known, then everything is blocked

    children = self.model_container["ID_tree"].getChildren(self.currently_viewed_node)

    for node in children:
      self.state_nodes[node] = "blocked"
    pass

  def __clearNodes(self, fromwhat):
    children = self.model_container["ID_tree"].getChildren(self.currently_viewed_node)

    for node in children:
      if self.state_nodes[node] == fromwhat:
        self.state_nodes[node] = STATES[self.main.current_network]["nodes"][0]  # "enabled"

  def resetGroups(self):
    self.node_group = set()
    self.knot_group = set()
    # self.__checkNodeGroup()

  def setDefaultEditorState(self):
    self.editor_state = GRAPH_EDITOR_STATES[self.editor_phase][0]  # RULE: first state in the list is default
    for event in self.key_automata[self.editor_phase]:
      if self.editor_state == self.key_automata[self.editor_phase][event]["state"]:
        self.main.setKeyAutomatonState(event)

  def resetNodeStates(self):  # RULE: the first in the list is the default usually "enabled"  # default is enabled
    viewed_node = self.currently_viewed_node
    children = self.model_container["ID_tree"].getChildren(viewed_node)
    for child in children:  # set the default (initialisation, import etc.)
      self.state_nodes[child] = STATES[self.editor_phase]["nodes"][0]
    return

  def applyNodeDefinitionRules(self, nodetype):
    # if "has_tokens" in features:
    #   self["tokens"] = {}  # dict hash=tokens value=list of typed tokens
    # if "has_conversion" in features:
    #   self["conversions"] = {}  # dict hash=tokens value=list of active conversions
    # if "intraface" in features:
    #   self["tokens_right"] = {}  # dict hash=tokens value=list of typed tokens
    #   self["tokens_left"] = {}  # dict hash=tokens value=list of typed tokens
    #   self["transfer_constraints"] = {}  # dict hash=tokens value=list of typed tokens
    # if "accepts_inject_of_typed_tokens" in features:
    #   self["injected_typed_tokens"] = {}  # dict hash=tokens value=list of typed tokens

    features = set()
    for rule in list(self.main.ontology.rules.keys()):
      if rule == "nodes_allowing_token_injection":
        if nodetype in self.main.ontology.rules[rule]:
          features.add("has_tokens")
          features.add("accepts_inject_of_typed_tokens")
      if rule == "nodes_allowing_token_conversion":
        if nodetype in self.main.ontology.rules[rule]:
          features.add("has_tokens")
          features.add("has_conversion")
      if rule == "nodes_allowing_token_transfer":
        if nodetype in self.main.ontology.rules[rule]:
          features.add("has_tokens")
          features.add("intraface")

    return sorted(features)

  def applyControlAccessRules(self):
    phase = self.editor_phase
    state = self.editor_state
    network = self.main.current_network
    named_network = self.main.current_named_network

    print("debugging -- access rules editor phase & state :", phase, state)
    print("debugging -- access rules editor network & named network :", network, named_network)

    # token_control = self.main.control_tools.index
    # typed_token_control = self.main.control_typed_tokens.index

    if phase == EDITOR_PHASES[0]:
      if state == "re-connect_arc":
        self.__ruleNodeAccessInNetworkOnly()
      # elif state == "insert":
      #   return
      else:
        self.__ruleNodeAccessTopologyAcrossNetworks()
    elif phase == EDITOR_PHASES[1]:
      select = self.main.state_inject_or_constrain_or_convert
      if select == "inject":
        self.__ruleNodeAccessTypedTokensInject()
      elif select == "convert":
        self.__ruleNodeAccessTypedTokensConvert()
      elif select == "constrain":
        self.__ruleNodeAccessTypedTokensConstrain()
      else:
        self.__ruleNodeAccessUndetermined()

  def redrawCurrentScene(self):
    # print("redraw scene initialising", self.initialising)
    if self.main.initialising:
      return
    # if "currently_viewed_node" not in dir(self):
    #   return
    self.__redrawScene(self.currently_viewed_node)

  def clearBlockedNodes(self):
    self.__clearNodes("blocked")

  def clearSelectedNodes(self):
    self.__clearNodes("selected")

  def blockNodesInNetworkInViewedNode(self, network):
    for node in self.model_container["scenes"]:
      if network == self.model_container["nodes"]:
        self.state_nodes[node] = "blocked"

  def setPanelAsCurrentItem(self):
    self.current_item = None
    for i in self.scene.items():
      if (i.graphics_root_object == NAMES["panel"]):
        if "decoration" in dir(i):
          if (i.decoration == NAMES["root"]):
            self.current_item = i
            # print("----- setting current item to panel")
    return self.current_item
