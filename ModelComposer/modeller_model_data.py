"""
===============================================================================
 model handling module of the ModelComposer
===============================================================================
"""

__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2017. 04. 03"
__license__ = "generic module"
__version__ = "0"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from collections import OrderedDict
from copy import copy
from copy import deepcopy

import Common.common_resources as CR
from Common.common_resources import walkBreathFirstFnc
from Common.common_resources import walkDepthFirstFnc
from Common.graphics_objects import NAMES
from Common.graphics_objects import NamedNetworkDataObjects
from Common.graphics_objects import STRUCTURES_Graph_Item
from Common.treeid import Tree

ROOTID = 0


class ModelContainerError(Exception):
  def __init__(self, msg):
    print("model container error", msg)


def makeMap(givenIDs, baseID):
  return dict([(givenIDs[i], i + baseID + 1) for i in range(len(givenIDs))])


class DataError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg


# ==================================


class NodeInfo(
        dict):  # (OrderedDict): # NOTE: changed to dictionary -- OrderedDict failed to be copied (extract subtree)
  def __init__(self, name, network=None, named_network=None, node_class=CR.M_None, node_type=CR.M_None):
    # OrderedDict.__init__(self)
    dict.__init__(self)
    self["name"] = name
    self["network"] = network
    self["named_network"] = named_network
    self["class"] = node_class
    self["type"] = node_type

    if node_class == NAMES["intraface"]:
      self["transfer_constraints"] = {}  # dict hash=tokens value=list of typed tokens
      self["tokens_left"] = {}  # dict hash=tokens value=list of typed tokens
      self["tokens_right"] = {}  # dict hash=tokens value=list of typed tokens
    if node_class == NAMES["interface"]:
      pass
    else:  # TODO: should the format be the same as in the arcs -- not important -- but a canonical question
      self["tokens"] = {}  # dict hash=tokens value=list of typed tokens

    # RULE: typed tokens can only be injected in reservoirs
    if node_type == NAMES["reservoir"]:
      self["injected_typed_tokens"] = {}  # dict hash=tokens value=list of typed tokens
    # RULE: typed token conversion can only be injected in dynamic nodes
    # NOTE: this fixes a term in the ontology
    # RULE ? : think about making the event dynamic also constraint transport like a boundary
    # TODO : need for conversion and injected_conversion -- currently only injected_conversion used
    elif "dynamic" in node_type:
      self["conversions"] = {}  # dict hash=tokens value=list of active conversions
      self["injected_conversions"] = {}  # dict hash=tokens value=list of active conversions


class ArcInfo(dict):  # OrderedDict):  # NOTE: changed to dictionary -- OrderedDict failed to be copied (extract
  # subtree)
  def __init__(self, fromNodeID, toNodeID, network, named_network, mechanism, token, nature):
    # OrderedDict.__init__(self)
    dict.__init__(self)
    self["name"] = str("%s | %s" % (fromNodeID, toNodeID))
    self["source"] = fromNodeID
    self["sink"] = toNodeID
    self["token"] = token
    self["typed_tokens"] = []
    self["network"] = network
    self["named_network"] = named_network
    self["mechanism"] = mechanism
    self["nature"] = nature
    # self["type"] = arctype                   # removed

  def cleanTypedTokens(self):  # Does not work with the current implementation
    self["typed_tokens"] = []  # TODO: Remove

  def addTypedTokens(self, typed_tokens):
    self["typed_tokens"].append(typed_tokens)


class ModelGraphicsData(dict):
  def __init__(self, graphics_object, x, y, graphics_data, phase, application, state):
    super().__init__()
    self["position_x"] = x
    self["position_y"] = y
    for decoration in STRUCTURES_Graph_Item[graphics_object]:
      r, d, a, s = graphics_data.getActiveObjectRootDecorationState(phase,
                                                                    graphics_object,
                                                                    decoration,
                                                                    application, state)
      dec_x = graphics_data[phase][r][d][a][s]
      self[decoration] = {
              "position_x": dec_x["position_x"],
              "position_y": dec_x["position_y"]
              }


class ModelContainer(dict):
  def __init__(self, networks):

    self.networks = networks

    self["ID_tree"] = Tree(ROOTID)  # StrTree(str(ROOTID))    #HAP: ID string to integer

    self["named_networks"] = NamedNetworkDataObjects(networks)

    # global nodes
    #               the_hash  : nodeID
    #               value : name
    self["nodes"] = {}
    self["domains"] = {}

    # global arcs
    #               the_hash: arcID
    #               value: arc dictionary [name, [fromNodeID, toNodeID]]
    self["arcs"] = {}
    self.arcID = 0
    self["scenes"] = {}

    rootID = ROOTID  # str(ROOTID)   #HAP: ID string to integer
    self["nodes"][rootID] = NodeInfo(rootID)
    self.__newScene(rootID)

  def __newScene(self, nodeID):
    self["scenes"][nodeID] = {}
    self["scenes"][nodeID]["nodes"] = {}
    self["scenes"][nodeID]["arcs"] = {}

  def addChild(self, parentNodeID, decoration_positions, network, named_network, node_class, nodetype):

    childNodeID = self["ID_tree"].addChild(parentNodeID)

    self["nodes"][childNodeID] = NodeInfo(CR.DEFAULT, network=network, named_network=named_network,
                                          node_class=node_class, node_type=nodetype)
    self.__newScene(childNodeID)
    self["scenes"][parentNodeID]["nodes"][childNodeID] = decoration_positions
    self["nodes"][childNodeID]["network"] = network
    self["nodes"][parentNodeID]["class"] = NAMES["branch"]
    self["nodes"][parentNodeID]["type"] = NAMES["branch"]

    return childNodeID

  def updateNodePosition(self, nodeID, x, y):

    parent_nodeID = self["ID_tree"].getImmediateParent(nodeID)
    self["scenes"][parent_nodeID]["nodes"][nodeID]["position_x"] = x
    self["scenes"][parent_nodeID]["nodes"][nodeID]["position_y"] = y

  def updateDecorationPosition(self, nodeID, decoration, x, y):

    parent_nodeID = self["ID_tree"].getImmediateParent(nodeID)
    self["scenes"][parent_nodeID]["nodes"][nodeID][decoration]["position_x"] = x
    self["scenes"][parent_nodeID]["nodes"][nodeID][decoration]["position_y"] = y

  def updateKnot(self, sceneID, arcID, knotIndex, position):
    self["scenes"][sceneID]["arcs"][arcID][knotIndex] = position

  def setDecoratorPosition(self, sceneID, nodeID, decorator, position):
    self["scenes"][sceneID]["nodes"][nodeID][decorator] = position

  def renameNode(self, nodeID, name):
    self["nodes"][nodeID]["name"] = name

  def deleteNode(self, nodeID):

    # del_nodes = [nodeID]
    # del_nodes.extend(list(self["ID_tree"].walkDepthFirst(nodeID)))

    del_nodes = walkDepthFirstFnc(self["ID_tree"], nodeID)

    print("delete nodes -  nodes ", del_nodes)

    arcs = set()
    for scene in del_nodes:
      for k in list(self["scenes"][scene]["arcs"].keys()):
        arcs.add(k)
    #
    # # print("delete arcs %s "%(arcs))
    del_arcs = []
    redo_arcs_source = []
    redo_arcs_sink = []
    for arc in arcs:
      if self["arcs"][arc]["source"] in del_nodes:
        if self["arcs"][arc]["sink"] in del_nodes:
          del_arcs.append(arc)
          self.deleteArc(arc)
        else:
          redo_arcs_sink.append(arc)
          self.deleteArc(arc)
      else:
        redo_arcs_source.append(arc)
        self.deleteArc(arc)
    #
    # print("delete arcs %s " % del_arcs)
    # print("redo arcs   sink %s " % redo_arcs_sink)
    # print("redo arcs   source %s " % redo_arcs_source)

    # TODO: this did not work. Problem is the knots thus we delete for the time being. See above
    # for arc in redo_arcs_sink:
    #   self.openThisArc(arc, del_nodes, "sink")
    #
    # for arc in redo_arcs_source:
    #   self.openThisArc(arc, del_nodes, "source")

    siblings = self["ID_tree"].getSiblings(nodeID)
    for scene in siblings:
      for n in self["scenes"][scene]['nodes']:
        if n in del_nodes:
          del self["scenes"][scene]['nodes'][n]

    for node in reversed(del_nodes):
      # print("remove ", node)

      del self["scenes"][node]
      parentID = self["ID_tree"].getImmediateParent(node)
      del self["scenes"][parentID]["nodes"][node]
      del self["nodes"][node]
      self["ID_tree"].removeID(node)

    return del_nodes  # , del_arcs # , changed_arcs

  def deleteArc(self, arcID):

    # keep for handling tokens
    token = self["arcs"][arcID]["token"]
    source = self["arcs"][arcID]["source"]  # str(self["arcs"][arcID]["source"]) #HAP str --> int
    sink = self["arcs"][arcID]["sink"]  # str(self["arcs"][arcID]["sink"]) #HAP str --> int
    network = self["arcs"][arcID]["network"]

    # remove arc
    subarcs = self.getArcOnNodeScene(arcID)
    for scene in subarcs:
      del self["scenes"][scene]["arcs"][arcID]
    del self["arcs"][arcID]

    # handle tokens
    for node in [source, sink]:
      self.fixTokensInNode(node, token)
      # tokens = self.getTokensInNode(node)
      # if token not in tokens:
      #   self["nodes"][node][tokens].remove(token)

  def renameNamedNetwork(self, network, old_name, new_name):
    for node in self["nodes"]:
      if self["nodes"][node]["named_network"] == old_name:
        self["nodes"][node]["named_network"] = new_name

    for arc in self["arcs"]:
      if self["arcs"][arc]["named_network"] == old_name:
        self["arcs"][arc]["named_network"] = new_name

    print("model -- rename named domain")

  def getArcsInAndOutOfNode(self, nodeID):
    arcs_out = []
    arcs_in = []
    for arc in self["arcs"]:
      source = self["arcs"][arc]["source"]  # str(self["arcs"][arc]["source"]) # HAP: str --> int
      sink = self["arcs"][arc]["sink"]  # str(self["arcs"][arc]["sink"])  #HAP: str --> int
      if nodeID == source:
        arcs_out.append(arc)
      elif nodeID == sink:
        arcs_in.append(arc)
    return arcs_out, arcs_in

  def getArcsConnectedToNode(self, nodeID):
    arcs = []
    arcs_out, arcs_in = self.getArcsInAndOutOfNode(nodeID)
    arcs.extend(arcs_out)
    arcs.extend(arcs_in)
    return arcs

  def getCommonIntrafaceNode(self, sourceNodeID, sinkNodeID):
    common_intraface = []
    source_arc_out, source_arc_in = self.getArcsInAndOutOfNode(sourceNodeID)
    sink_arc_out, sink_arc_in = self.getArcsInAndOutOfNode(sinkNodeID)
    for arc_so in source_arc_out:
      sink = self["arcs"][arc_so]["sink"]
      for arc_si in sink_arc_in:
        source = self["arcs"][arc_si]["source"]
        if sink == source:
          if self["nodes"][sink]["class"] == NAMES["intraface"]:  # self["nodes"][str(sink)]["type"] == NAMES[
            # "intraface"]: # HAP:str --> int
            common_intraface.append(sink)
    for arc_so in source_arc_in:  # can go the opposite direction
      sink = self["arcs"][arc_so]["source"]
      for arc_si in sink_arc_out:
        source = self["arcs"][arc_si]["sink"]
        if sink == source:
          if self["nodes"][sink]["class"] == NAMES[
            "intraface"]:  # self["nodes"][str(sink)]["type"] == NAMES["intraface"]: #HAP: str --> int
            common_intraface.append(sink)

    return common_intraface

  def getTokensInNode(self, nodeID):

    arcs = self.getArcsConnectedToNode(nodeID)
    tokens = set()
    for arc in arcs:
      tokens.add(self["arcs"][arc]["token"])

    return list(tokens)

  def getNodeApplication(self, nodeID):
    try:
      application = self["nodes"][nodeID]["type"]
    except:
      print("problem")
    return application

  def getArcApplication(self, arcID):
    transferred_token = self["arcs"][arcID]["token"]
    transfer_mechanism = self["arcs"][arcID]["mechanism"]
    transfer_nature = self["arcs"][arcID]["nature"]
    application = CR.TEMPLATE_ARC_APPLICATION % (transferred_token, transfer_mechanism, transfer_nature)
    return application

  def fixTokensInNode(self, nodeID, token):

    # token = self["arcs"][arcID]["token"]
    tokens = self.getTokensInNode(nodeID)
    # node_type = self["nodes"][nodeID]["type"]
    # if node_type == NAMES["intraface"]:
    #   left_network, right_network = self["nodes"][nodeID]["network"].split(CR.CONNECTION_NETWORK_SEPARATOR)
    if tokens == []:
      return
    if token not in tokens:
      # del self["nodes"][nodeID]["tokens"][token]
      try:
        del self["nodes"][nodeID]["tokens"][token]
      except:
        print(">>> warning >>> issues with fixing tokens in node %s with tokens %s trying to delete token %s" % (
                nodeID, tokens, token))

  def addArc(self, fromNodeID, toNodeID, network, named_network, mechanism, token, nature):

    # TODO: one could consider to insert a knot in the middle on each affected scene

    arcsIDList = list(self["arcs"].keys())
    if arcsIDList == []:
      self.arcID = 0
    else:
      self.arcID = max(arcsIDList) + 1
      # arcsIDs = []
      # [arcsIDs.append(a) for a in arcsIDList]
      # self.arcID = max(arcsIDs) + 1
    arcID = self.arcID  # str(self.arcID)   #HAP:  str -- int
    self["arcs"][arcID] = ArcInfo(fromNodeID, toNodeID, network, named_network, mechanism, token, nature)
    subarcsIDs = self.getArcOnNodeScene(arcID)
    nodes_with_arcIDs = list(subarcsIDs.keys())

    for nodeID in subarcsIDs:
      self["scenes"][nodeID]["arcs"][arcID] = []

    for node in [fromNodeID, toNodeID]:
      # print("- add token ", node, token, network)
      self.addToken(node, token, network)

    return arcID, nodes_with_arcIDs

  def addToken(self, nodeID, token, network):
    if self["nodes"][nodeID]["class"] == NAMES["interface"]:
      return

    if self["nodes"][nodeID]["class"] == NAMES["intraface"]:
      self.addTypedTokensToIntraface(nodeID, token, [], network)
    self["nodes"][nodeID]["tokens"][token] = []

  def addTypedTokensToIntraface(self, nodeID, token, typed_tokens, network):

    network_left, network_right = self.__getBoundaryNetworks(nodeID)
    if network == network_left:
      self["nodes"][nodeID]["tokens_left"][token] = typed_tokens
    else:
      self["nodes"][nodeID]["tokens_right"][token] = typed_tokens

  def addTypedTokenTransferConstraintsToBoundary(self, nodeID, token, typed_tokens, network):
    #
    # RULE: this applies to boundaries only with left & right network be identical
    network_left, network_right = self.__getBoundaryNetworks(nodeID)
    assert network_left == network_right

    pass

  def __getBoundaryNetworks(self, nodeID):
    return self["nodes"][nodeID]["network"].split(CR.CONNECTION_NETWORK_SEPARATOR)

  def getArcOnNodeScene(self, arcID):

    fromNodeID = self["arcs"][arcID]["source"]
    toNodeID = self["arcs"][arcID]["sink"]
    fromNodeID = fromNodeID  # str(fromNodeID)   #HAP: str --> int
    toNodeID = toNodeID  # str(toNodeID)          #HAP: str --> int
    fromPathID = [fromNodeID] + self["ID_tree"].getAncestors(fromNodeID)
    toPathID = [toNodeID] + self["ID_tree"].getAncestors(toNodeID)
    common_ancestorID = self["ID_tree"].getFirstCommonNode(fromNodeID, toNodeID)
    # print("fromNode, fromPath", [fromNodeID],'   ', [fromPathID])
    # print("toNode, toPath",[toNodeID], '    ', [toPathID])
    # print("common_ancestor",  [common_ancestorID])
    from_index = fromPathID.index(common_ancestorID)
    to_index = toPathID.index(common_ancestorID)
    from_remainderIDs = fromPathID[0:from_index]
    to_remainderIDs = toPathID[0:to_index]

    # print("from_remainder ", from_remainderIDs)
    # print("to_remainder ",to_remainderIDs)
    _nodes_with_arcIDs = from_remainderIDs + \
                         to_remainderIDs + \
                         [common_ancestorID]
    _nodes_with_arcIDs.remove(fromNodeID)
    _nodes_with_arcIDs.remove(toNodeID)
    nodes_with_arcIDs = list(set(_nodes_with_arcIDs))
    subarcsIDs = OrderedDict()
    for node in nodes_with_arcIDs:
      subarcsIDs[node] = [None, None]
      children = self["ID_tree"].getChildren(node)
      siblings = self["ID_tree"].getSiblings(node)
      ancestors = self["ID_tree"].getAncestors(node)
      N = children + siblings + ancestors + [node]
      l = fromPathID
      r = toPathID
      for nl in N:
        s = False
        kl = 0
        while ((not s) and (kl < len(l))):
          if l[kl] == nl:
            subarcsIDs[node][0] = nl
            s = True
          kl += 1
        if s:
          break
      for nr in N:
        t = False
        kr = 0
        while ((not t) and (kr < len(r))):
          if (r[kr] == nr):
            subarcsIDs[node][1] = nr
            # print(".......",node,  subarcsIDs[node])
            t = True
          kr += 1
        if t:
          break

    # this one is very tricky indeed
    if fromNodeID == common_ancestorID:
      subarcsIDs[fromNodeID] = fromNodeID, toPathID[0]
    else:
      subarcsIDs[fromNodeID] = fromNodeID, common_ancestorID
    if common_ancestorID == toNodeID:
      subarcsIDs[toNodeID] = fromNodeID[0], toNodeID
    else:
      subarcsIDs[toNodeID] = common_ancestorID, toNodeID
    # print('subarcs', subarcsIDs)
    return subarcsIDs

  def changeArc(self, arcID, end_to_move, movedNodeID):

    # TODO changing arcs must adhere to the rules of networks - it does not
    # TODO some obsolete code ?

    old_subarcs = self.getArcOnNodeScene(arcID)

    tokens_to_transfer = deepcopy(self["arcs"][arcID]["token"])
    typed_tokens_to_transfer = deepcopy(self["arcs"][arcID]["typed_tokens"])

    if end_to_move == 'source':
      disconnected_node = self["arcs"][arcID]["source"]  # str(self["arcs"][arcID]["source"]) #HAP str --> int
      self["arcs"][arcID]["source"] = movedNodeID
    elif end_to_move == 'sink':
      disconnected_node = self["arcs"][arcID]["sink"]  # str(self["arcs"][arcID]["sink"])  #HAP: str --> int
      self["arcs"][arcID]["sink"] = int(movedNodeID)

    # FIX: typed tokens are not transferred and combined needs fixing
    self["nodes"][movedNodeID]["tokens"][tokens_to_transfer] = typed_tokens_to_transfer

    subarcs = self.getArcOnNodeScene(arcID)

    # delete those subarcs that are not in the new list
    deleted_subarcs = []
    for nodeID in old_subarcs:
      if nodeID not in subarcs:
        del self["scenes"][nodeID]["arcs"][arcID]
        deleted_subarcs.append(nodeID)

    # add those subarcs thar are not in old list:
    added_subarcs = []
    for nodeID in subarcs:
      if nodeID not in old_subarcs:
        self["scenes"][nodeID]["arcs"][arcID] = []
        added_subarcs.append(nodeID)

    # handle tokens
    token = self["arcs"][arcID]["token"]
    network = self["arcs"][arcID]["network"]
    self.fixTokensInNode(disconnected_node, token)

    return

  def openThisArc(self, arcID, del_nodes, where):
    node_to_change = self["arcs"][arcID][where]
    parentID = self["ID_tree"].getImmediateParent(node_to_change)
    while parentID in del_nodes:
      node_to_change = parentID
      parentID = self["ID_tree"].getImmediateParent(node_to_change)
    self["arcs"][arcID][where] = parentID

    source = self["arcs"][arcID]["source"]
    sink = self["arcs"][arcID]["sink"]
    print("openThisArc source, sink:", source, sink)
    subarcs = self.getArcOnNodeScene(arcID)
    print("openThisArc subarcs", subarcs)

  def insertKnot(self, nodeID, arcID, indexA, indexB, position):
    cA = (indexA == -1)
    cB = (indexB == -1)
    if cA and cB:
      self["scenes"][nodeID]["arcs"][arcID] = [position]
    elif cA and not cB:
      self["scenes"][nodeID]["arcs"][arcID].insert(0, position)
    elif not cA and cB:
      self["scenes"][nodeID]["arcs"][arcID].append(position)
    elif not cA and not cB:
      if indexA < indexB:
        self["scenes"][nodeID]["arcs"][arcID].insert(indexB, position)
      else:
        self["scenes"][nodeID]["arcs"][arcID].insert(indexA, position)

  def removeKnot(self, nodeID, arcID, x, y):
    knot_data = self["scenes"][nodeID]["arcs"][arcID]
    knot_data.remove([x, y])

  def updateKnotPosition(self, nodeID, arc_ID, index, x, y):
    knot_list = self["scenes"][nodeID]["arcs"][arc_ID]
    knot_list[index] = (x, y)

  def mapMe(self):

    data = self
    node_map = self["ID_tree"].mapMe()
    arcIDs = list(data["arcs"].keys())
    no_arcIDs = len(arcIDs)
    arcID_map = dict([(arcIDs[i], i) for i in
                      range(no_arcIDs)])  # dict([(arcIDs[i], str(i)) for i in range(no_arcIDs)]) #HAP: str --> int

    odata = OrderedDict()
    for the_hash in data:
      odata[the_hash] = OrderedDict()

    for node in data["nodes"]:
      nodeID = node_map[node]  # str(node_map[int(node)])     #HAP: str --> int
      odata["nodes"][nodeID] = data["nodes"][node]

    for scene in data["scenes"]:
      scene_node_ID = node_map[scene]  # str(node_map[int(scene)]) #HAP: str --> int
      odata["scenes"][scene_node_ID] = OrderedDict()
      odata["scenes"][scene_node_ID]["nodes"] = OrderedDict()
      odata["scenes"][scene_node_ID]["arcs"] = OrderedDict()

      for nodeID in data["scenes"][scene]["nodes"]:  # knots are not saved only position --> see below
        onode_ID = node_map[nodeID]  # str(node_map[int(nodeID)])  #HAP: str--> int
        odata["scenes"][scene_node_ID]["nodes"][onode_ID] = data["scenes"][scene]["nodes"][nodeID]

      for arc in data["scenes"][scene]["arcs"]:
        a = arcID_map[arc]
        b = data["scenes"][scene]["arcs"][arc]
        odata["scenes"][scene_node_ID]["arcs"][arcID_map[arc]] = b

    for arcID in data["arcs"]:
      odata["arcs"][arcID_map[arcID]] = data["arcs"][arcID]
      arc_source_ID = data["arcs"][arcID]["source"]
      arc_sink_ID = data["arcs"][arcID]["sink"]
      mapped_arc_source_ID = node_map[arc_source_ID]
      mapped_arc_sink_ID = node_map[arc_sink_ID]
      odata["arcs"][arcID_map[arcID]]["source"] = mapped_arc_source_ID
      odata["arcs"][arcID_map[arcID]]["sink"] = mapped_arc_sink_ID

    odata["named_networks"] = data["named_networks"]

    for i in self:
      if i != "ID_tree":
        del self[i]
        self[i] = odata[i]

    return node_map

  def getInternalandExternalArcs(self, nodeID):

    external_arcs = []
    internal_arcs = []

    nodeIDs = self["ID_tree"].walkBreadthFirst(nodeID)
    nodeIDs = []  # convert to integers
    [nodeIDs.append(i) for i in nodeIDs]

    arcs = self["arcs"]
    for arc in arcs:
      if (arcs[arc]["source"] in nodeIDs) and (arcs[arc]["sink"] in nodeIDs):
        internal_arcs.append(arc)
      elif (arcs[arc]["source"] in nodeIDs) or (arcs[arc]["sink"] in nodeIDs):
        external_arcs.append(arc)

    print("external_arc :", external_arcs)
    print("internal_arcs:", internal_arcs)
    return external_arcs, internal_arcs

  def extractSubtree(self, nodeID):

    container = ModelContainer()

    # TODO: external arcs may be connected to dummy inputs/outputs or the relative root ???

    external_arcs, internal_arcs = self.getInternalandExternalArcs(nodeID)

    tree, node_map = self["ID_tree"].getSubTree(nodeID)

    no_arcIDs = len(internal_arcs)
    arcID_map = dict([(internal_arcs[i], (i)) for i in range(no_arcIDs)])  # dict([(internal_arcs[i], str(i)) for i
    # in range(no_arcIDs)]) #HAP: str --> int

    container["ID_tree"] = tree

    for node in node_map:
      c_node = node_map[node]
      container["nodes"][c_node] = deepcopy(self["nodes"][node])
      container.__newScene(c_node)

    for node in node_map:
      c_node = node_map[node]
      for n in node_map:
        if n in self["scenes"][node]["nodes"]:
          c_n = node_map[n]
          # b = self["scenes"][node]["nodes"][n].copy()
          container["scenes"][c_node]["nodes"][c_n] = deepcopy(self["scenes"][node]["nodes"][n])
      for arc in internal_arcs:
        if arc in self["scenes"][node]["arcs"]:
          c_arc = arcID_map[arc]
          # c = self["scenes"][node]["arcs"][arc].copy()
          container["scenes"][c_node]["arcs"][c_arc] = deepcopy(self["scenes"][node]["arcs"][arc])

    for arc in internal_arcs:
      c_arc = arcID_map[arc]
      container["arcs"][c_arc] = deepcopy(self["arcs"][arc])
      # source = node_map[str(self["arcs"][arc]["source"])]    #HAP: str --> int
      source = node_map[self["arcs"][arc]["source"]]  # HAP: str -->int
      sink = node_map[self["arcs"][arc]["sink"]]
      container["arcs"][c_arc]["source"] = source
      container["arcs"][c_arc]["sink"] = sink

    container.printMe()

    return container

  def printMe(self):
    self.printTree()
    self.printNodes()
    self.printArcs()

  def printArcs(self):
    print('\narcs', '\n -----------------')
    arcs = self["arcs"]
    for id in sorted(arcs):
      print('\nARC : %s  , %s' % (id, arcs[id]))

  def printNodes(self):
    print("\nnodes", '\n -----------------')
    scenes = self["scenes"]
    for id in sorted(scenes):
      nodes = scenes[id]["nodes"]
      arcs = scenes[id]["arcs"]
      for nn in nodes:
        print("scene nodes %s - %s  , %s" % (id, nn, nodes[nn]))
      for a in arcs:
        print("scene arcs %s - %s  , %s" % (id, a, arcs[a]))

  def printTree(self):
    print("\ntree", '\n -----------------')
    tree = self["ID_tree"].ID_tree
    for n in tree:
      print("node %s : %s" % (n, tree[n]))

  def write(self, f):

    # TODO: DONE mapping could be done on reading instead of writing. Solves problem of intermediate writing -->
    #  makeFromFile
    node_map = self.mapMe()

    a = deepcopy(self["ID_tree"])
    self["ID_tree"] = self["ID_tree"].toJson()  # self["ID_tree"].ID_tree.toJson()   #HAP: str --> int
    # del self["ID_tree"]

    CR.putData(self, f, indent=2)

    # del self["ID_tree"]
    self["ID_tree"] = a

    return node_map

  def getAndFixData(self, f):
    """
    Json does not allow for integer hashes. Thus all those need to be changed into integers after reading.
    :param f:
    :return:
    """
    data = CR.getData(f)
    new_data = deepcopy(data)
    tofix = ["ID_tree", "arcs", "nodes", "scenes"]
    # tofix = ["arcs", "nodes", "scenes"]
    for d in tofix:
      for i in data[d]:
        i_i = int(i)
        if d != "scenes":
          new_data[d].pop(i)
        new_data[d][i_i] = data[d][i]

    # this is not elegant, but there seems to be a python problem if one does it more elegantly
    d = "scenes"
    for i in list(data[d].keys()):
      i_i = int(i)
      for ii in list(data[d][i]["arcs"].keys()):
        new_data[d][i_i]["arcs"][int(ii)] = data[d][i]["arcs"][ii]
        d_ = new_data[d][i_i]["arcs"].pop(ii)
      for ii in list(data[d][i]["nodes"].keys()):
        new_data[d][i_i]["nodes"][int(ii)] = data[d][i]["nodes"][ii]
        d_ = new_data[d][i_i]["nodes"].pop(ii)
      del new_data[d][i]

    # print("got here")
    return new_data

  def makeFromFile(self, f):
    data = self.getAndFixData(f)
    tree = Tree(0)
    tree.fromJson(data["ID_tree"])
    tree.imposeIDTree(tree)
    self["ID_tree"] = tree
    del data["ID_tree"]
    for the_hash in data:
      if the_hash == "named_networks":
        self["named_networks"] = NamedNetworkDataObjects(self.networks)
        self["named_networks"].updateWithData(data["named_networks"])
      else:
        self[the_hash] = data[the_hash]
    print(" -------- ")

  def addFromFile(self, f, parentID, position, graphics_data, editor_phase):

    data = self.getAndFixData(f)  # CR.getData(f)
    if not data:
      return

    # offset first
    node_offset = self["ID_tree"].currentID + 1
    arc_offset = len(self["arcs"])

    arcIDs = list(data["arcs"].keys())
    no_arcIDs = len(arcIDs)
    # arcID_map = dict([(arcIDs[i], str(i + arc_offset)) for i in range(no_arcIDs)])    #HAP: str --> int
    arcID_map = dict([(arcIDs[i], (i + arc_offset)) for i in range(no_arcIDs)])

    # make proper ID tree from json format
    tree = Tree(0)
    tree.fromJson(data["ID_tree"])  # has string(int) as the_hash needs changing to int
    node_map = tree.mapMe(offset=node_offset)
    # strhashedtree = tree.toJson()

    # offset graph data
    odata = OrderedDict()
    for the_hash in data:
      odata[the_hash] = OrderedDict()
    del odata["ID_tree"]

    for node in data["nodes"]:
      nodeID = node_map[int(node)]  # str(node_map[int(node)])                 #HAP: str --> int
      odata["nodes"][nodeID] = data["nodes"][node]

    for scene in sorted(data["ID_tree"].keys()):
      scene_node_ID = node_map[int(scene)]  # str(node_map[int(scene)]) # HAP: str --> int
      odata["scenes"][scene_node_ID] = {}
      odata["scenes"][scene_node_ID]["nodes"] = {}
      odata["scenes"][scene_node_ID]["class"] = {}
      odata["scenes"][scene_node_ID]["arcs"] = {}

      for nodeID in data["scenes"][scene]["nodes"]:  # knots are not saved only position --> see below
        onode_ID = node_map[int(nodeID)]  # str(node_map[int(nodeID)])  # HAP: str--> int
        odata["scenes"][scene_node_ID]["nodes"][onode_ID] = data["scenes"][scene]["nodes"][nodeID]

      for arc in data["scenes"][scene]["arcs"]:
        # a = arcID_map[arc]
        b = data["scenes"][scene]["arcs"][arc]
        odata["scenes"][scene_node_ID]["arcs"][arcID_map[arc]] = b

    for arcID in data["arcs"]:
      arc_source_ID = data["arcs"][arcID]["source"]
      arc_sink_ID = data["arcs"][arcID]["sink"]
      mapped_arc_source_ID = node_map[arc_source_ID]
      mapped_arc_sink_ID = node_map[arc_sink_ID]
      network = data["arcs"][arcID]["network"]
      named_network = data["arcs"][arcID]["named_network"]
      mechanism = data["arcs"][arcID]["mechanism"]
      token = data["arcs"][arcID]["token"]
      nature = data["arcs"][arcID]["nature"]
      odata["arcs"][arcID_map[arcID]] = ArcInfo(mapped_arc_source_ID, mapped_arc_sink_ID, network,
                                                named_network,
                                                mechanism, token, nature)

    for the_hash in self:
      if the_hash == "ID_tree":
        self["ID_tree"].addMappedTree(tree, parentID)
      elif the_hash == "named_networks":
        for nw in self["named_networks"]:
          s = set(self["named_networks"][nw])
          ds = set(data["named_networks"][nw])
          us = s.union(ds)
          ls = list(us)
          print("named networks ", nw, "--", s, ds, ls)
          self["named_networks"][nw] = ls
      else:
        self[the_hash].update(odata[the_hash])

    # pos = [position.x(), position.y()]
    # self["nodes"][str(node_offset)]["name"] = CR.DEFAULT                #HAP: str --> int
    # self["nodes"][str(node_offset)]["type"] = NAMES["branch"]          #HAP: str --> int
    self["nodes"][node_offset]["name"] = CR.DEFAULT
    self["nodes"][node_offset]["type"] = NAMES["branch"]
    # self["scenes"][parentID]["nodes"][str(node_offset)] = ModelGraphicsData(NAMES["branch"],     #HAP: str --> int
    #                                                                            position.x(),
    #                                                                            position.y(),
    #                                                                            graphics_data,
    #                                                                            editor_phase,
    #                                                                            CR.M_None,
    #                                                                            'normal')
    self["scenes"][parentID]["nodes"][node_offset] = ModelGraphicsData(NAMES["branch"],
                                                                       position.x(),
                                                                       position.y(),
                                                                       graphics_data,
                                                                       editor_phase,
                                                                       CR.M_None,
                                                                       'normal')
    #   def __init__(self, graphics_object, x, y, graphics_data, phase, application, state):
    # [pos, R.STRUCTURES[R.S_NODE_COMPOSITE]]

    return tree, node_map, arcID_map, node_offset, parentID

  def explodeNode(self, nodeID):

    parentID = self["ID_tree"].getImmediateParent(nodeID)

    # tree move children to parent
    children = self["ID_tree"].getChildren(nodeID)
    for child in children:
      # print("move: ", child)
      self["ID_tree"].moveID(child, parentID)
      self["scenes"][parentID]["nodes"][child] = self["scenes"][nodeID]["nodes"][child]

    for arc in self["scenes"][nodeID]["arcs"]:  # top_arc:
      self["scenes"][parentID]["arcs"][arc] = self["scenes"][nodeID]["arcs"][arc]

    for scene in children:
      # print("fix scene: ", child)
      nodes = list(self["scenes"][scene]["nodes"].keys())
      for node in nodes:
        if node == nodeID:
          del self["scenes"][scene]["nodes"][node]

    # NOTE: delete node does too much in terms of connections - simple version enough
    del self["nodes"][nodeID]
    del self["scenes"][nodeID]
    del self["scenes"][parentID]["nodes"][nodeID]
    self["ID_tree"].removeID(nodeID)

    return parentID

  def groupNodes(self, newNodeID, nodeGroupIDS):

    nodeID = self["ID_tree"].getImmediateParent(newNodeID)

    # children = self["ID_tree"].getChildren(nodeID)
    for node in nodeGroupIDS:
      # print("move: ", child)
      self["ID_tree"].moveID(node, newNodeID)
      self["scenes"][newNodeID]["nodes"][node] = self["scenes"][nodeID]["nodes"][node]
      del self["scenes"][nodeID]["nodes"][node]

    arcs = list(self["scenes"][nodeID]["arcs"].keys())
    nodes_in_branch = []
    iter = walkBreathFirstFnc(self["ID_tree"], newNodeID)
    for n in iter:  # self["ID_tree"].walkBreadthFirst(newNodeID):
      nodes_in_branch.append(n)
    nodes_in_branch.remove(newNodeID)

    external = []
    internal = []
    for arc in arcs:  # top_arc:
      # self["scenes"][newNodeID]["arcs"][arc] = self["scenes"][nodeID]["arcs"][arc]
      # source = str(self["arcs"][arc]["source"])               # HAP: str --> int
      # sink = str(self["arcs"][arc]["sink"])
      source = self["arcs"][arc]["source"]
      sink = self["arcs"][arc]["sink"]
      if (source in nodes_in_branch) and (sink in nodes_in_branch):
        internal.append(arc)
      elif (source not in nodes_in_branch) and (sink in nodes_in_branch):
        external.append(arc)
      elif (source in nodes_in_branch) and (sink not in nodes_in_branch):
        external.append((arc))
      else:
        # print("arc %s is not connected to this branch %s"%(arc, newNodeID))
        pass

    for arc in internal:  # these need transferring they only show on the new view
      self["scenes"][newNodeID]["arcs"][arc] = deepcopy(self["scenes"][nodeID]["arcs"][arc])
      del self["scenes"][nodeID]["arcs"][arc]

    for arc in external:  # these need copying as they show on both views
      self["scenes"][newNodeID]["arcs"][arc] = deepcopy(self["scenes"][nodeID]["arcs"][arc])

    for scene in nodeGroupIDS:
      # print("fix scene: ", child)
      nodes = list(self["scenes"][scene]["nodes"].keys())
      for node in nodes:
        if node == nodeID:
          del self["scenes"][scene]["nodes"][node]

    pass

  def getNodeGraphicsData(self, nodeID):
    parent_nodeID = self["ID_tree"].getImmediateParent(nodeID)
    return self["scenes"][parent_nodeID]["nodes"][nodeID]

  def checkforOpenArcs(self):

    # check for arcs to be open:
    leave_nodes_IDs = self["ID_tree"].getAllLeaveNodes()
    open_arcs = set()
    for arc in self["arcs"]:
      if (self["arcs"][arc]["source"] not in leave_nodes_IDs) or \
              (self["arcs"][arc]["sink"] not in leave_nodes_IDs):
        open_arcs.add(arc)
    return open_arcs

  # def existArcThroughInterface(self, source_nodeID, sink_nodeID):
  #
  #   to_nodes = []

  def injectListInToNodes(self, node_group, token, list, where):
    print('list: ', list, "to where ", where)
    for node in node_group:
      print('node directory for node %s' % node, self["nodes"][node].keys())
      # print("inject tokens ", node_group, token, list, self["nodes"][node])
      self["nodes"][node][where][token] = list

  def putTypedTokens(self, node_group, token, list_typed_tokens):
    for node in node_group:
      self["nodes"][node]["tokens"][token] = list_typed_tokens

  # def injectTypedTokenConversion(self, node_group, token, list_typed_tokens_conversions):
  #   for node in node_group:
  #     self["nodes"][node]["injected_conversion"][token] = list_typed_tokens_conversions
  #
  #
  # def injectTypedTokenTransferConstraints(self, node_group, token, list_typed_tokens_costraints):
  #   for node in node_group:
  #     self["nodes"][node]["transfer_constraints"][token] = list_typed_tokens_costraints

  def getAllLeaveNodesInNetworksAndApplication(self):
    leave_nodes = self["ID_tree"].getAllLeaveNodes()

    typed_nodes = {}
    for node in leave_nodes:
      nw = self["nodes"][node]["network"]
      node_type = self["nodes"][node]["type"]
      if nw not in typed_nodes:
        typed_nodes[nw] = {}
      if node_type not in typed_nodes[nw]:
        typed_nodes[nw][node_type] = []
      typed_nodes[nw][node_type].append(node)

    return typed_nodes

  def getArcsWithToken(self, arcs, token):

    # NOTE: an token can be present in more than one network
    # all_arcs = self["arcs"]
    arcs_with_token = []
    for a in arcs:
      if self["arcs"][a]["token"] == token:
        arcs_with_token.append(a)
    return arcs_with_token

  def computeTokenIncidenceMatrix(self, arcs, token):
    arcs_with_token = self.getArcsWithToken(arcs, token)
    I = {}
    for arc in arcs_with_token:
      source_node = self["arcs"][arc]["source"]
      sink_node = self["arcs"][arc]["sink"]
      for node in [source_node, sink_node]:
        if node not in list(I.keys()):
          I[node] = []
        I[node].append(arc)
    return I

  def computeTokenAdjacencyMatrix(self, domain, token):
    arcs_with_token = self.getArcsWithToken(self["arcs"], token)
    A = {}
    for arc in arcs_with_token:
      arc_data = self["arcs"][arc]
      source_node = arc_data["source"]
      sink_node = arc_data["sink"]
      if (source_node in domain) and (sink_node in domain):
        # type = arc_data["type"]

        if source_node not in A:
          A[source_node] = []
        A[source_node].append(sink_node)

        # if "bi-directional" == type:
        if sink_node not in A:
          A[sink_node] = []
        A[sink_node].append(source_node)
    print("adjacency matrix :", A)
    return A

  def computeTokenDomain(self, node, I, D, V):
    arcs_in_node = I[node]
    m = node
    for arc in arcs_in_node:
      if arc not in V:
        V.add(arc)
        D.append(node)
        source = self["arcs"][arc]["source"]
        sink = self["arcs"][arc]["sink"]
        _m = [source, sink]
        _m.remove(node)
        m = _m[0]
        if m not in D:
          D, m = self.computeTokenDomain(m, I, D, V)
          if m:
            D.append(m)

    D = list(set(D))
    return D, m

  def computeTokenDomains(self, tokens):
    D = {}
    arcs = list(self["arcs"].keys())
    for token in tokens:
      V = set()
      I = self.computeTokenIncidenceMatrix(arcs, token)
      if I != {}:
        count = 0
        N = []
        D[token] = {}
        nodes = list(I.keys())
        for node in nodes:
          if node not in N:
            D[token][count] = []
            D[token][count], m = self.computeTokenDomain(node, I, D[token][count], V)
            N.extend(D[token][count])
            count += 1
      else:
        D[token] = {}
    self["domains"] = D
    return D

  def isInDomain(self, node, token):

    for no in self["domains"][token]:
      if node in self["domains"][token][no]:
        # Note: node must only be in one domain for a given token !
        return self["domains"][token][no]

    return None

  def isOfType(self, node, type):
    return type == self["nodes"][node]["type"]

  def computeTypedTokenDistribution(self, token, domain):
    # print(" >>>>>>>>>>>>  clearing domain ", domain, token)
    arcs_in_domain = set()
    conversions = {}
    for node in domain:
      conversions[node] = set()
      node_class = self["nodes"][node]["class"]
      # print(" >>>>>>>>>>>>  clearing node ", node, node_class)
      # clean up first
      if NAMES["intraface"] == node_class:
        self["nodes"][node]["tokens_left"][token] = []
        self["nodes"][node]["tokens_right"][token] = []
      else:
        self["nodes"][node]["tokens"][token] = []
      connected_arcs = self.getArcsConnectedToNode(node)
      for arc in connected_arcs:
        if self["arcs"][arc]["token"] == token:  # Not resetting token
          arcs_in_domain.add(arc)

    adj_matrix = self.computeTokenAdjacencyMatrix(domain, token)
    for node in domain:
      node_type = self["nodes"][node]["type"]
      if NAMES["reservoir"] == node_type:
        if token in self["nodes"][node]["injected_typed_tokens"]:
          for typed_token in self["nodes"][node]["injected_typed_tokens"][token]:
            network = self["nodes"][node]["network"]
            self.colourBranch(network, node, token, typed_token, adj_matrix, conversions)

    for node in domain:
      if self["nodes"][node]["class"] == NAMES["node"]:
        arcs = self.getArcsConnectedToNode(node)
        for arc in arcs:
          token = self["arcs"][arc]["token"]
          source = self["arcs"][arc]["source"]
          sink = self["arcs"][arc]["sink"]
          if self["nodes"][source]["class"] == NAMES["node"]:
            node_ = source
          else:
            if self["nodes"][sink]["type"] == NAMES["node"]:
              node_ = sink
            else:
              raise DataError(">>>> cannot find a simple node")
              sys.exit()
          typed_tokens = copy(self["nodes"][node_]["tokens"][token])  # !!! copy
          self["arcs"][arc]["typed_tokens"] = typed_tokens

    # for arc in arcs_in_domain:              # Happens after reaction injections
    #   self["arcs"][arc]["typed_tokens"] = []                      # First clean
    #   # self["arcs"][arc].cleanTypedTokens()                        # First clean
    #   source = str(self['arcs'][arc]['source'])
    #   sink = str(self['arcs'][arc]['sink'])
    #   if self["nodes"][source]["type"] == NAMES["intraface"]:
    #     typed_tokens_source = set(self["nodes"][source]["tokens_left"][token])
    #   else:
    #     typed_tokens_source = set(self["nodes"][source]["tokens"][token])
    #   if self["nodes"][sink]["type"] == NAMES["intraface"]:
    #     typed_tokens_sink = set(self["nodes"][sink]["tokens_right"][token])
    #   else:
    #     typed_tokens_sink = set(self["nodes"][sink]["tokens"][token])
    #   # Updating the arcs with typed tokens
    #   self["arcs"][arc]["typed_tokens"] = sorted(list(typed_tokens_source
    #                                                   | typed_tokens_sink))
    #   # DOES NOT WORK WITH CURRENT IMPLEMENTATION:
    #   # self["arcs"][arc].addTypedTokens(sorted(list(typed_tokens_source
    #   #                                                 | typed_tokens_sink))
    #   # TODO: Check sequence of typed tokens

  def colourBranch(self, network, node, token, typed_token, adj_matrix, conversions):
    node_data = self["nodes"][node]
    # boundaries have two sides
    boundary = NAMES["intraface"] == node_data["class"]
    if boundary:
      left_network, right_network = node_data["network"].split(CR.CONNECTION_NETWORK_SEPARATOR)
      left = left_network == network
      right = right_network == network
      if left:
        typed_tokens = node_data["tokens_left"][token]
      elif right:
        typed_tokens = node_data["tokens_right"][token]
    else:
      typed_tokens = self["nodes"][node]["tokens"][token]
    # continue if typed token is not present or stop iteration
    if typed_token not in typed_tokens:
      typed_tokens.append(typed_token)
      if "dynamic" in node_data["type"]:
        if token in node_data["injected_conversions"]:  # in the sequence it may not yet be defined, patience
          for conversion in node_data["injected_conversions"][token]:
            E, P = conversion.split(CR.CONVERSION_SEPARATOR)
            Elist = eval(E)
            Plist = eval(P)
            Es_set = set(Elist)
            typed_token_set = set(typed_tokens)
            if Es_set.issubset(typed_token_set):  # reaction takes place
              conversions[node].add(conversion)
              for ss in Plist:
                self.colourBranch(network, node, token, ss, adj_matrix, conversions)
      if node in adj_matrix:
        for node_alt in adj_matrix[node]:
          if boundary:
            # TODO: one could add the token here as it may be empty before one comes here or as currently when
            # defining the boundary
            if typed_token not in node_data["transfer_constraints"][token]:
              if left:
                next_network = right_network
              else:
                next_network = left_network

              self.colourBranch(next_network, node_alt, token, typed_token, adj_matrix, conversions)
            else:
              pass  # do not continue -- no transfer of this typed token

          else:
            next_network = network
            self.colourBranch(next_network, node_alt, token, typed_token, adj_matrix, conversions)
