#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 main window implementation of the ModelComposer
===============================================================================

Main program controlling the graphical interface for the model construction.

Note: This implementation does not allow for several tokens with typed tokens.
Note: It only works with one set of typed tokens per network.

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import copy
import os as os
#
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from Common.automata_objects import GRAPH_EDITOR_STATES
from Common.common_resources import askForModelFileGivenOntologyLocation  # askForModelFile,
from Common.common_resources import CONVERSION_SEPARATOR
from Common.common_resources import getOntologyName
from Common.common_resources import M_None
from Common.graphics_objects import getGraphData
from Common.ontology_container import OntologyContainer
from Common.qt_resources import cleanLayout
from Common.qt_resources import ModellerRadioButton
from Common.radio_selector_impl import RadioSelector
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.save_file_impl import SaveFileDialog
from Common.ui_string_dialog_impl import UI_String
from ModelBuilder.ModelComposer.modeller_commander import Commander
from ModelBuilder.ModelComposer.modeller_logger_impl import Logger
from ModelBuilder.ModelComposer.modeller_mainwindow import Ui_MainWindow
from OntologyBuilder.TypedTokenEditor.editor_typed_token_impl import TypedTokenData

LEFT = QtCore.Qt.LeftDockWidgetArea
RIGHT = QtCore.Qt.RightDockWidgetArea

SPACING = 20

EDITOR_PHASES = list(GRAPH_EDITOR_STATES.keys())

DEBUG = {}
DEBUG["load data"] = False

REDIRECT_ERROR = False
REDIRECT_STDOUT = False


def debugPrint(source, what):
  print(source, ": ", what)


class Stream(QtCore.QObject):
  newText = QtCore.pyqtSignal(str)

  def write(self, text):
    self.newText.emit(str(text))
    self.flush()

  def flush(self):
    pass


class ErrorMessage():
  def __init__(self, media, msg):
    media(msg)


class MainWindowImpl(QtWidgets.QMainWindow):
  def __init__(self):
    QtWidgets.QMainWindow.__init__(self)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    self.move(QtCore.QPoint(0, 0))

    self.initialising = True
    self.writeStatus(" initialising")
    self.editor_phase = EDITOR_PHASES[0]

    # interface details
    self.__setupSignals()
    self.button_logic = self.__setupButtonLogics()
    # self.__setupButtonWithIcons()
    self.__buttonLogics("start")
    self.ui.labelOntology.hide()
    self.ui.labelModel.hide()
    self.ui.labelSchnipsel.hide()

    # first get ontology
    ontology_name = getOntologyName(task="task_model_composer")
    self.ontology_name = copy.copy(ontology_name)
    self.ui.labelOntology.setText(ontology_name)
    self.ui.labelOntology.show()

    # TODO: remove automata_working_file_spec from automation definition program -- needs carefule consideration
    self.model_library_location = DIRECTORIES["model_library_location"] % ontology_name
    self.automata_working_file_spec = FILES["automata_file_spec"] % ontology_name
    self.typed_token_file_spec = FILES["typed_token_file"] % ontology_name

    new_model = None
    if not os.path.exists(self.typed_token_file_spec):
      print("no typed token file ")
      sys.exit()

    # now ask for model
    self.model_name = ""
    while self.model_name in [""]:
      self.model_name, new_model = askForModelFileGivenOntologyLocation(self.model_library_location, alternative=True)
      if self.model_name in [None, "exit"]:
        sys.exit(0)

    # model file and schnipsel file without extension
    self.__display_model_name(self.model_name)
    self.model_file = os.path.join(self.model_library_location,
                                   self.model_name)  # NOTE: extension is added when writing
    self.model_location = DIRECTORIES["model_location"] % (ontology_name, self.model_name)
    self.model_file = FILES["model_file"] % (ontology_name, self.model_name)
    # print(self.model_file)
    self.schnipsel_name = None
    self.schnipsel_file = None

    # attach ontology
    ontology = OntologyContainer(ontology_name)
    self.ontology = ontology
    self.networks = ontology.leave_networks_list

    self.tokens_on_networks = ontology.tokens_on_networks
    self.tokens = ontology.tokens
    self.nodeTypes = ontology.node_types_in_networks
    self.arcApplications = ontology.arc_types_in_leave_networks_list_coded
    self.arcInfoDictionary = ontology.arc_info_dictionary
    # self.typedTokens = ontology.typed_tokens_on_networks
    self.nw_token_typedtoken_dict = ontology.token_typedtoken_on_networks
    self.typed_tokens_data = TypedTokenData(file=self.typed_token_file_spec)
    # self.networks = ontology.leave_networks_list      tuplicated
    self.converting_tokens = ontology.converting_tokens

    self.connection_networks = {}
    self.connection_networks.update(ontology.interconnection_network_dictionary)  # intRA
    self.connection_networks.update(ontology.intraconnection_network_dictionary)  # intER

    self.NETWORK, self.TOKENS, self.graphics_DATA, self.state_colours = getGraphData(self.networks, self.connection_networks,
                                                                 ontology.node_type_list,
                                                                 ontology.arc_type_list, self.tokens,
                                                                 FILES["graph_resource_file_spec"] % ontology_name)
    if DEBUG["load data"]:
      print("node types :", self.nodeTypes)
      print("init - tokens:", self.tokens_on_networks)
      print("arc types :", self.arcApplications)
      print("typed tokens :", self.typedTokens)
      print("typed tokens data :", self.typed_tokens_data)
      print("arc all_arc_applications :", ontology.arc_type_list)
      print("arc types", ontology.arc_type_list)

    # make painting tools
    self.PENS, self.BRUSHES = self.graphics_DATA.makeBrushesAndPens()
    NETWORK_BRUSHES = self.NETWORK.makeBrushes()
    self.BRUSHES.update(NETWORK_BRUSHES)
    self.ui.groupNamed_NetworkColour.setAutoFillBackground(True)


    self.colourDialog = QtWidgets.QColorDialog()

    for i in range(0, 16):  # reset all custom colours first to white
      colour = QtGui.QColor(255, 255, 255)  # .rgba()
      self.colourDialog.setCustomColor(i, colour)

    count = 0
    tokens = sorted(self.TOKENS.keys())
    for token in tokens:
      print(token, ' : ', count)
      r, g, b, a = self.TOKENS[token]["colour"]
      colour = QtGui.QColor(r, g, b, a)  # .rgba()
      self.colourDialog.setCustomColor(count, colour)
      count += 2  # makes it the first row
    colour_select = QtGui.QColor(255, 255, 0)  # .rgba()
    self.colourDialog.setCustomColor(1, colour_select)
    colour_open = QtGui.QColor(0, 255, 255)  # .rgba()
    self.colourDialog.setCustomColor(3, colour_open)
    colour_uni_directional = QtGui.QColor(85, 85, 85)  # .rgba()
    self.colourDialog.setCustomColor(5, colour_uni_directional)
    colour_bi_directional = QtGui.QColor(170, 170, 170)  # .rgba()
    self.colourDialog.setCustomColor(7, colour_bi_directional)
    colour_distributed = QtGui.QColor(225, 225, 225)  # .rgba()
    self.colourDialog.setCustomColor(9, colour_distributed)



    # intialising

    self.previous_network = None  # keep track of main tool states
    self.current_network = None  # needed by commander

    # keep for re-use once defined
    self.selected_node_type = {nw: self.nodeTypes[nw][0] for nw in self.networks}  # per network
    self.selected_token = {editor_phase: {nw: 0 for nw in self.networks} for editor_phase in EDITOR_PHASES}
    self.selected_transfer_mechanism = {nw: {token: 0 for token in self.arcInfoDictionary[nw]} for nw in self.networks}
    self.selected_arc_nature = {nw: {token: 0 for token in self.arcInfoDictionary[nw]} for nw in self.networks}
    # self.selected_connection_application = {}

    # for short-time use only
    self.selected_set_typed_tokens = set()
    self.selected_set_coversions = set()
    self.selected_set_constraints = set()
    self.state_inject_or_constrain_or_convert = None
    self.current_named_network = None

    self.editor_phase = EDITOR_PHASES[0]
    self.cursors = {}

    # TODO: one could save the selected xx in a file and load if file exists to start where one stopped.

    # attach commander
    # self.current_network = None  # defines attribute for commander's use later
    self.commander = Commander(self)  # attach commander

    if new_model:
      # self.named_network_dictionary = {nw: self.commander.model_container["named_networks"][nw][0] for nw in
      #                                  self.networks}
      self.named_network_dictionary = self.commander.model_container["named_networks"]

      # for nw in self.networks:
      #   self.named_network_dictionary[nw] = {nw : self.NETWORK[nw]["colour"]}

    self.radio_selectors = {}

    if not new_model:
      self.insertModelFromFile(self.model_name)
      # self.named_network_dictionary = {}
      # for nw in self.commander.model_container["named_networks"]:
      #   self.named_network_dictionary[nw] = self.commander.model_container["named_networks"][nw][0]

    self.__setupInterface()
    item = self.commander.setPanelAsCurrentItem()  # this sets the initial item to the panel

    self.initialising = False

  def __display_model_name(self, model_name):
    self.ui.labelModel.setText(model_name)
    self.ui.labelModel.show()

  def __setupInterface(self):
    self.__setupModellerApl()
    self.__makeMainToolPage()
    self.__buttonLogics("pushNewModel")

  def __setupButtonLogics(self):
    l_0 = {}  # "actionOntology"}
    l_1 = ["pushExit",
           "pushSaveAs",
           "pushSchnipsel",
           ]
    l_2 = l_1 + ["pushSave"]

    e = {
            "start"           : l_2,
            "pushExit"        : [],
            "pushNewModel"    : l_2,
            "pushLoadFromFile": l_2,
            "pushSave"        : l_2,
            "pushSaveAs"      : l_2,
            }
    return e

  def __setupSignals(self):
    #  connect signals
    u = self.ui
    b = {
            "pushExit"     : [u.pushExit, self.pushExit],
            "pushSave"     : [u.pushSave, self.pushSave],
            "pushSaveAs"   : [u.pushSaveAs, self.saveAs],
            "pushSchnipsel": [u.pushSchnipsel, self.showSchnipselPopWindow],
            }
    self.buttons = {}
    for i in b:
      # self.connect(b[i][0], QtCore.pyqtSignal("clicked()"), b[i][1])
      self.buttons[i] = b[i][0]

  def on_pushExit_pressed(self):
    print(">>>> exiting")

  def __setupModellerApl(self):
    """
    set up modeller application
    - logger
    - tabify logger and control page
    - key automaton
    """

    # self.ui. Logger.setReadOnly(1)  # setup logger window
    self.logger = Logger(self.commander.model_container, self)
    self.ui.dockWidgetLogger.setWidget(self.logger)  # still needs to be connected to the model container

    self.ui.dockWidgetLogger.show()

    self.logger.home()
    if REDIRECT_STDOUT:
      sys.stdout = Stream(newText=self.logger.onUpdateStandardOutput)
    if REDIRECT_ERROR:
      sys.stderr = Stream(newText=self.logger.onUpdateErrorOutput)

    # print("setting up application")

    self.tabifyDockWidget(self.ui.dockWidgetMain, self.ui.dockWidgetLogger)
    self.ui.dockWidgetMain.raise_()

    self.__setupKeyAutomatonIndicator()
    self.__shiftKeyAutomaton(EDITOR_PHASES[0])

  def __setupKeyAutomatonIndicator(self):
    self.radio = {}
    for phase in EDITOR_PHASES:
      self.radio[phase] = {}
      keys = list(self.commander.key_automata[phase].keys())
      for k in keys:
        state = self.commander.key_automata[phase][k]["state"]
        label = str("%s - %s" % (k, state))
        l = label.replace("Key_", "")
        l = l.replace("Escape", "Esc")
        # print("make radio %s - key %s" %(l,k))
        r = ModellerRadioButton(M_None, M_None, k, l, autoexclusive=True)
        # r.setDisabled(True)
        self.radio[phase][k] = r

        # Note: key simulation through radio buttons
        self.radio[phase][k].radio_signal.connect(self.__keyAutomatonSignal)

      if keys != []:  # Note: fully functioning in 5.01
        k = keys[0]
        self.radio[phase][k].setChecked(True)

  def __keyAutomatonSignal(self, token_class, token, strID, value):
    if value == True:
      item = self.commander.setPanelAsCurrentItem()
      self.commander.processGUIEvent("controlboard", item, strID)

  def __shiftKeyAutomaton(self, phase):
    # print("shifting key automaton")
    cleanLayout(self.ui.formKeyAutomaton)
    count = 0
    for k in sorted(self.radio[phase]):
      radio = self.radio[phase][k]
      self.ui.formKeyAutomaton.setWidget(count, QtWidgets.QFormLayout.LabelRole, radio)
      count += 1

    if self.initialising: self.commander.setDefaultEditorState()  # NOTE: only place being used -- caused a lot of
    # problems when using it rules

  def __mapAndSave(self):
    """
    renumber nodes
    """
    # pars = {
    #   "action": "map&save model",
    #   "file": self.model_file
    #   }
    pars = {
            "nodeID": None,
            "action": "map&save model",
            "object": None,
            "pos"   : None,
            "file"  : self.model_file
            }
    self.commander.processMainEvent(pars)

  def __buttonLogics(self, state):
    """
    Defines button logic
    @param state: program state
    """
    for i in self.buttons:
      self.buttons[i].setEnabled(0)
    for b in self.button_logic[state]:
      self.buttons[b].setEnabled(1)

  # =============== make tool pages

  def __makeMainToolPage(self):
    # add editor phase toggle button
    # self.editor_phase_button = ToggleButton(EDITOR_PHASES[0], EDITOR_PHASES[1])
    # self.ui.layoutEditorPhase.addWidget(self.editor_phase_button)
    # self.editor_phase_button.hide()
    # self.editor_phase_button.changed.connect(self.setEditorPhase)

    enabled_editor_phases = ["topology"]

    # RULE: all open arcs must be closed before token topology is enabled

    open_arcs = self.commander.model_container.checkforOpenArcs()
    if len(open_arcs) == 0:
      enabled_editor_phases.append("token_topology")
    #
    # # RULE: no rule for the equation topology as yet
    # enabled_editor_phases.append(("equation_topology"))
    # self.ui.comboEditorPhase.addItems(enabled_editor_phases)

    self.__clearLayout(self.ui.layoutNetworks)
    self.radio_selectors["networks"] = self.__makeAndAddSelector("networks",
                                                                 self.networks,
                                                                 self.radioReceiverNetworks,
                                                                 len(self.networks) - 1,
                                                                 self.ui.layoutNetworks)

    # RULE: no rule for the equation topology as yet
    enabled_editor_phases.append(("equation_topology"))
    self.ui.comboEditorPhase.addItems(enabled_editor_phases)

  def __makeInteractionToolPage(self):
    self.state_inject_or_constrain_or_convert = None  # reset state of the interaction tool box
    self.__clearLayout(self.ui.layoutInteractiveWidgetTop)
    self.__clearLayout(self.ui.layoutInteractiveWidgetBottom)
    nw = self.current_network
    if self.editor_phase == EDITOR_PHASES[0]:
      index = self.selected_node_type[nw]
      self.radio_selectors["nodes"] = self.__makeAndAddSelector("nodes", self.nodeTypes[nw], self.radioReceiverNode,
                                                                index,
                                                                self.ui.layoutInteractiveWidgetTop)
    else:
      tokens = sorted(self.arcInfoDictionary[nw].keys())
      s_tokens = []
      for token in tokens:
        nature = list(self.ontology.ontology_tree[nw]["structure"]["arc"][token].keys())
        if "auto" not in nature:
          s_tokens.append(token)

      if s_tokens:
        index = self.selected_token[self.editor_phase][nw]
        self.radio_selectors["node_token"] = self.__makeAndAddSelector("token", s_tokens, self.radioReceiverNodeToken,
                                                                       index,
                                                                       self.ui.layoutInteractiveWidgetTop)

  def __clearLayout(self, layout):
    while layout.count():
      child = layout.takeAt(0)
      if child.widget() is not None:
        child.widget().deleteLater()
      elif child.layout() is not None:
        self.__clearLayout(child.layout())

  def __removeWidgetFromLayoutTopDown(self, layout, no):
    n = layout.count()
    for cnt in reversed(range(no, n)):
      widget = layout.takeAt(cnt).widget()
      if widget is not None:
        widget.deleteLater()

  def __trimLayout(self, no, layout):
    if layout.count() >= no:
      self.__removeWidgetFromLayoutTopDown(layout, no)

  def __makeAndAddSelector(self, group_name, what, receiver, index, layout, autoexclusive=True):
    radio_selector = RadioSelector()
    list_of_choices = []
    counter = 0
    layout.addWidget(radio_selector)
    for item in what:
      list_of_choices.append((str(counter), item, receiver))
      counter += 1
    radio_selector.addListOfChoices(group_name, list_of_choices, index, autoexclusive=autoexclusive)
    return radio_selector

  def __selectColour(self, where):

    if not self.current_named_network:
      self.current_named_network = self.current_network
    colour_ = self.named_network_dictionary[self.current_network][self.current_named_network]["colour"]
    colour = self.__colourDialog(colour_)
    self.__changeData("colour", colour)
    self.__showColour(where, colour)
    return

  def __showColour(self, box, colour):
    print("colour :", colour)
    r, g, b, a = colour
    colour = QtGui.QColor(r, g, b, a)
    palette = box.palette()
    palette.setColor(QtGui.QPalette.Window, colour)
    box.setPalette(palette)
    box.update()

  def __colourDialog(self, colour):
    print("debugging -- ask for colour ", colour)
    r, g, b, a = colour
    colour = QtGui.QColor(r, g, b, a)
    # colourDialog = QtWidgets.QColorDialog(self)
    c = self.colourDialog.getColor(colour).getRgb()
    # del colourDialog


    # c = QtWidgets.QColorDialog(self).getColor(colour, parent=None)
    # col = c.getRgb()
    return c  # c_.getRgb(), v

  def __changeData(self, what, value):
    print("debugging -- change :", what, value)
  # action handling
  # -------------------------------------------------------------

  #  //////////////////////////////////////////////////////////////////////////

  def setNetwork(self, nw, named_network):
    """
    network changer all interface components that are parametrised with the network, are to be updated
    """
    # print("setting nework from commander")
    self.current_network = nw
    # self.named_network_dictionary[nw] = named_network
    index = self.networks.index(nw)
    self.radio_selectors["networks"].check("networks", index)
    index = self.commander.model_container["named_networks"][nw].index(named_network)
    self.radio_selectors["named_networks"].check("named_networks", index)

  @QtCore.pyqtSlot(str)
  def on_comboEditorPhase_currentIndexChanged(self, phase):
    self.writeStatus("phase :%s" % phase)
    self.setEditorPhase(phase)
    pass

  def radioReceiverNetworks(self, token_class, token, token_string, toggle):
    # print("maybe asked to change network from %s to %s"%(self.current_network, token_string))
    if toggle:
      # print("do change nework from radio button from %s to %s"%(self.current_network, token_string))
      # self.editor_phase_button.show()
      self.current_network = token_string
      #
      # TODO: add radio_selectors for named nodes
      # self.__makeInteractionToolPage()

      self.__trimLayout(1, self.ui.layoutNetworks)
      named_networks = self.commander.model_container["named_networks"][self.current_network]
      if not self.current_named_network:
        self.current_named_network= self.current_network
      _dummy = len(self.named_network_dictionary[self.current_network].keys())-1
      self.radio_selectors["named_networks"] = self.__makeAndAddSelector("named_networks",
                                                                         named_networks,
                                                                         self.radioReceiverNamedNetworks,
                                                                         _dummy,
                                                                         self.ui.layoutNetworks)
      self.commander.redrawCurrentScene()

  def radioReceiverNamedNetworks(self, token_class, token, token_string, toggle):
    if toggle:
      # self.named_network_dictionary[self.current_network][token_string} = []
      print("debugging -- token string:", token_string)
      self.old_named_network_name = token_string
      self.__makeInteractionToolPage()
      # self.__makeInteractionToolPage()

  def radioReceiverNode(self, token_class, token, token_string, toggle):
    nw = self.current_network
    self.__trimLayout(1, self.ui.layoutInteractiveWidgetBottom)
    self.selected_node_type[nw] = token_string
    tokens = sorted(self.arcInfoDictionary[nw].keys())
    s_token = self.selected_token[self.editor_phase][nw]
    s_tokens = []
    for token in tokens:
      nature = list(self.ontology.ontology_tree[nw]["structure"]["arc"][token].keys())
      if "auto" not in nature:
        s_tokens.append(token)
    if s_tokens:
      self.radio_selectors["arc_token"] = self.__makeAndAddSelector("token", s_tokens, self.radioReceiverArcToken,
                                                                    s_token,
                                                                    self.ui.layoutInteractiveWidgetBottom)

  def radioReceiverArcToken(self, token_class, token, token_string, toggle):
    if toggle:
      # print("radioReceiverArcToken: reciever class %s, radio token %s. token_string %s"
      # % (token_class, token, token_string))

      self.__trimLayout(1, self.ui.layoutInteractiveWidgetBottom)
      nw = self.current_network
      self.selected_token[self.editor_phase][nw] = token_string
      s_token = self.selected_token[self.editor_phase][nw]
      mechanisms = sorted(self.arcInfoDictionary[nw][s_token].keys())
      index = self.selected_transfer_mechanism[self.current_network][s_token]
      self.radio_selectors["mechanism"] = self.__makeAndAddSelector("mechanism", mechanisms,
                                                                    self.radioReceiverArcMechanism, index,
                                                                    self.ui.layoutInteractiveWidgetBottom)

  def radioReceiverArcMechanism(self, token_class, token, mechanism, toggle):
    if toggle:
      # print("radioReceiverArcMechanism: reciever class %s, radio token %s. token_string %s" % (token_class, token,
      # token_string))

      self.__trimLayout(2, self.ui.layoutInteractiveWidgetBottom)
      nw = self.current_network
      s_token = self.selected_token[self.editor_phase][nw]
      self.selected_transfer_mechanism[nw][s_token] = mechanism
      distributions = self.arcInfoDictionary[nw][s_token][mechanism]
      nature = self.selected_arc_nature[self.current_network][s_token]
      self.radio_selectors["nature"] = self.__makeAndAddSelector("nature", distributions,
                                                                 self.radioReceiverArcDistribution, nature,
                                                                 self.ui.layoutInteractiveWidgetBottom)

  def radioReceiverArcDistribution(self, token_class, token, token_string, toggle):
    if toggle:
      # print("radioReceiverArcDistribution: reciever class %s, radio token %s. token_string %s" % (
      # token_class, token, token_string))
      nw = self.current_network
      s_token = self.selected_token[self.editor_phase][nw]
      self.selected_arc_nature[nw][s_token] = token_string

  def radioReceiverNodeToken(self, token_class, token, token_string, toggle):
    if toggle:
      # print("radioReceiverNodeToken: reciever class %s, radio token %s. token_string %s" % (
      # token_class, token, token_string))
      # self.current_token = token_string
      nw = self.current_network
      self.selected_token[self.editor_phase][nw] = token_string
      self.__clearLayout(self.ui.layoutInteractiveWidgetBottom)  # trimLay(1,)
      ask = []
      if token_string in self.ontology.token_typedtoken_on_networks[nw].keys():
        # self.__clearLayout(self.ui.layoutInteractiveWidgetTop) #__trimLayout(1, )
        nature = list(
                self.ontology.ontology_tree[nw]["structure"]["arc"][self.selected_token[self.editor_phase][nw]].keys())

        if "auto" not in nature:
          typed_tokens = self.nw_token_typedtoken_dict[nw][token_string]
          # OPS!
          if typed_tokens:
            items_to_inject = self.typed_tokens_data[typed_tokens[0]]["instances"]
            ask.extend(["inject", "constrain"])
            if len(items_to_inject) > 0:
              # there is something to inject and constrain
              self.items_to_inject = items_to_inject
            items_to_convert = self.typed_tokens_data[typed_tokens[0]]["conversions"]
            if len(items_to_convert) > 0:
              self.items_to_convert = items_to_convert
              ask.append("convert")
              self.radio_selectors["typed token"] = \
                self.__makeAndAddSelector("typed token", ask, self.radioReceiverTypedTokenTool, -1,
                                          self.ui.layoutInteractiveWidgetBottom)
        else:
          self.__clearLayout(self.ui.layoutInteractiveWidgetBottom)

        self.writeStatus("")
      else:
        self.__clearLayout(self.ui.layoutInteractiveWidgetBottom)
        self.writeStatus("no typed tokens for this token : %s" % token_string)

  def radioReceiverTypedTokenTool(self, token_class, token, token_string, toggle):
    if toggle:
      self.__trimLayout(1, self.ui.layoutInteractiveWidgetBottom)
      print(
              "radioReceiverTypedTokenTool: reciever class -%s-, radio token -%s-.,token_string -%s-, "
              "self.items_to_inject -%s-"
              % (token_class, token, token_string, self.items_to_inject))
      self.state_inject_or_constrain_or_convert = token_string
      self.commander.redrawCurrentScene()  # may have changed since last
      if token_string in ["inject", "constrain"]:
        self.radio_selectors[token_string] = self.__makeAndAddSelector(token_string, self.items_to_inject,
                                                                       self.radioReceiverTypedTokenInject, -1,
                                                                       self.ui.layoutInteractiveWidgetBottom,
                                                                       autoexclusive=False)
      elif token_string == "convert":
        items = []
        for item in self.items_to_convert:
          items.append("%s %s %s" % (item["reactants"], CONVERSION_SEPARATOR, item["products"]))

        self.radio_selectors["convert"] = self.__makeAndAddSelector("convert", items,
                                                                    self.radioReceiverTypedTokenToConvert, -1,
                                                                    self.ui.layoutInteractiveWidgetBottom,
                                                                    autoexclusive=False)
        pass

  def radioReceiverTypedTokenInject(self, token_class, token, token_string, toggle):
    pass

  def radioReceiverTypedTokenToConvert(self, token_class, token, token_string, toggle):
    # if toggle:
    #   # print("radioReceiverTypedTokenToConvert: reciever class %s, radio token %s. token_string %s"
    #   #       % (token_class, token, token_string))
    #   self.selected_set_coversions.add(token_string)
    #   # print("radioReceiverTypedTokenToConvert typed token convertion set", self.selected_set_coversions)
    # else:
    #   if token_string in self.selected_set_typed_tokens:
    #    self.selected_set_typed_tokens.remove(token_string)
    pass

  def on_toolNamed_NetworkColour_pressed(self):
    print("debugging -- tool clicked")
    where = self.ui.groupNamed_NetworkColour
    return self.__selectColour(where)

  def showSchnipselPopWindow(self):
    """
    ask for and define schnipsel model name
    """
    self.schnipsel_name, new_model = askForModelFileGivenOntologyLocation(self.model_library_location,
                                                                          alternative=False, exit=None)

    if self.schnipsel_name in ["exit", "", None]: return

    self.ui.labelSchnipsel.setText(self.schnipsel_name)
    self.ui.labelSchnipsel.show()

    self.schnipsel_file = FILES["model_file"] % (self.ontology_name, self.schnipsel_name)
    self.__buttonLogics("pushLoadFromFile")
    pars = {
            "nodeID": None,
            "action": "library file",
            "object": None,
            "pos"   : None,
            "file"  : self.schnipsel_file
            }
    self.commander.processMainEvent(pars)

  def save_topology_png(self, file_name):
    outfile = os.path.join(file_name, 'figures', 'topo.png')
    p = QtWidgets.QPixmap.grabWindow(self.ui.graphicsView.winId())
    p.save(outfile)

  def insertModelFromFile(self, model_name):
    """
    takes a model from a file and inserts it into new empty model
    Note this actually insert a model
    """
    # print("stop")

    pars = {
            "nodeID": None,
            "action": "load from file",
            "object": None,
            "pos"   : None,
            "file"  : self.model_file
            }
    self.commander.processMainEvent(pars)

  def injectTypedTokens(self):
    token = self.selected_token[self.editor_phase][self.current_network]  # current_token
    list_typed_tokens = self.radio_selectors["inject"].getListOfCheckedLabelInGroup("inject")
    # print("inject typed tokens ", list_typed_tokens, "into ", self.commander.node_group, "token:", token)

    self.commander.model_container.injectListInToNodes(self.commander.node_group,
                                                       token,
                                                       list_typed_tokens,
                                                       "injected_typed_tokens")
    self.computeTypedTokenDistribution(token)
    self.commander.clearSelectedNodes()
    self.commander.redrawCurrentScene()
    self.radio_selectors["inject"].uncheckGroup("inject")
    self.selected_set_typed_tokens = set()
    self.commander.resetGroups()
    pass

  def computeTypedTokenDistribution(self, token):
    for node in self.commander.node_group:
      domain = self.commander.model_container.isInDomain(node, token)
      if domain:
        self.commander.model_container.computeTypedTokenDistribution(token, domain)
      else:
        self.writeStatus("no domain present")

  def injectConversions(self):
    token = self.selected_token[self.editor_phase][self.current_network]
    # list_conversions = deepcopy(list(self.selected_set_coversions))
    list_conversions = self.radio_selectors["convert"].getListOfCheckedLabelInGroup("convert")
    print("inject conversions ", list_conversions)
    self.radio_selectors["convert"].uncheckGroup("convert")

    self.commander.model_container.injectListInToNodes(self.commander.node_group,
                                                       token,
                                                       list_conversions,
                                                       "injected_conversions")
    # todo: this fails if there is no domain
    self.computeTypedTokenDistribution(token)
    self.commander.clearSelectedNodes()
    self.commander.redrawCurrentScene()
    self.commander.resetGroups()

  def injectTypedTokenTransferConstraints(self):
    token = self.selected_token[self.editor_phase][self.current_network]
    # list_typed_tokens = deepcopy(list(self.selected_set_typed_tokens))
    list_typed_tokens = self.radio_selectors["constrain"].getListOfCheckedLabelInGroup("constrain")
    # print("inject constraints ", list_typed_tokens)
    self.radio_selectors["constrain"].uncheckGroup("constrain")

    self.commander.model_container.injectListInToNodes(self.commander.node_group,
                                                       token,
                                                       list_typed_tokens,
                                                       "transfer_constraints")
    self.computeTypedTokenDistribution(token)
    self.commander.clearSelectedNodes()
    self.commander.redrawCurrentScene()
    self.commander.resetGroups()

  def __resetTypedTokensRadio(self, radio_block):
    for group in radio_block.getGroups():
      radio_block.uncheckGroup(group)

  def on_pushAddNamedNetwork_pressed(self):

    named_networks = self.commander.model_container["named_networks"][self.current_network]
    current_name = self.named_network_dictionary[self.current_network]
    ui = UI_String("edit named network", "give new name", limiting_list=named_networks)
    ui.exec_()

    new_name = ui.getText()
    if new_name:
      named_networks.append(new_name)
      self.radioReceiverNetworks(None, None, self.current_network, True)

  def on_pushEditNamedNetwork_pressed(self):

    named_networks = self.commander.model_container["named_networks"][self.current_network]
    old_name = self.old_named_network_name
    ui = UI_String("edit named network", old_name, limiting_list=named_networks)
    ui.exec_()

    new_name = ui.getText()
    if new_name:
      # index = named_networks[self.current_network].index(old_name)
      # named_networks[index] = new_name
      self.commander.model_container.renameNamedNetwork(self.current_network, old_name, new_name)
      value = self.named_network_dictionary[self.current_network][old_name]
      self.named_network_dictionary[self.current_network][new_name] = value
      del self.named_network_dictionary[self.current_network][old_name]
      self.current_named_network=new_name
      self.radioReceiverNetworks(None, None, self.current_network, True)

  def on_pushDeleteNamedNetwork_pressed(self):
    self.writeStatus("deleting named network is not yet implemented")

  def saveAs(self, *args):
    """
    ask for model file and then map and save it
    """
    self.model_name, new_name = askForModelFileGivenOntologyLocation(self.model_library_location, alternative=True)
    if not self.model_name:
      return
    # folder =
    self.model_location = DIRECTORIES["model_location"] % (self.ontology_name, self.model_name)
    print(self.model_location)
    if not os.path.exists(self.model_location):
      os.mkdir(self.model_location)
    self.model_file = FILES["model_file"] % (self.ontology_name, self.model_name)
    self.__mapAndSave()
    self.__buttonLogics("pushSaveAs")
    self.__display_model_name(self.model_name)
    self.writeStatus("saving to file %s" % self.model_name)

  def pushSave(self):
    """
    save current file
    """
    self.writeStatus("saving to file %s" % self.model_name)
    print(">>> saving to file :", self.model_file)

    # folder =
    if not os.path.exists(self.model_location):
      os.mkdir(self.model_location)

    pars = {
            "nodeID": None,
            "action": "save model",
            "object": None,
            "pos"   : None,
            "file"  : self.model_file
            }
    # print(self.model_name)
    # print(self.model_file)
    # self.save_topology_png(self.model_file)
    self.commander.processMainEvent(pars)
    # self.__buttonLogics("pushReset")

  def pushReset(self):
    # self.commander.flipPage(str(0))
    # self.__buttonLogics("pushReset")
    pars = {
            "action": "reset"
            }
    self.commander.processMainEvent(pars)

  def pushExit(self, *args):
    # if self.commander.modified:
    w = SaveFileDialog()
    w.answer.connect(self.__controlExit)
    w.exec_()
    debugPrint("actionExit", "closing")

  def __controlExit(self, response):
    print(" exit response ", response)
    if response == "save":
      self.pushSave()
    elif response in ["ignore", "exit"]:
      self.exit()
    elif response == "cancel":
      pass
    else:
      pass

  def exit(self):
    self.close()

  # used also by commander
  # ------------------------------------------------------

  def setEditorPhase(self, phase):
    # RULE: allow change only if there are no open arcs
    open_arcs = self.commander.model_container.checkforOpenArcs()

    if len(open_arcs) != 0:
      msg_box = QtWidgets.QMessageBox()
      msg_box.setText("there are open arcs - close them ! %s" % open_arcs)
      msg_box.exec_()
      self.setEditorPhase("topology")
      return {
              "failed": True
              }
    else:
      # RULE: all arcs must be closed before the token domain can be computed
      if self.current_network:
        D = self.commander.model_container.computeTokenDomains(self.tokens_on_networks[self.current_network])
        print("identified token domains: ", D)

    # self.editor_phase = phase

    self.commander.editor_phase = phase
    self.commander.setDefaultEditorState()
    # self.redrawCurrentScene()

    self.editor_phase = phase
    self.__makeInteractionToolPage()
    self.__shiftKeyAutomaton(phase)
    self.commander.redrawCurrentScene()
    # pars = {"action": "shift editor phase",
    #         "phase" : phase}
    # self.commander.processMainEvent(pars)

  def setSchnipsel(self, schnipsel_name):
    self.schnipsel_name = schnipsel_name
    self.schnipsel_file = os.path.join(self.model_library_location, self.schnipsel_name)
    self.ui.labelSchnipsel.setText(self.schnipsel_name)
    self.ui.labelSchnipsel.show()

  def setKeyAutomatonState(self, event):
    self.interface_set = True
    phase = self.commander.editor_phase
    for r in self.radio[phase]:
      self.radio[phase][r].setChecked(False)
    self.radio[phase][event].setChecked(True)

  def showMouseAction(self, item, decoration, cursor, actionLeft, actionRight):
    if cursor != "leave":
      if cursor not in list(self.cursors.keys()):
        bitMap = QtGui.QPixmap(32, 32)
        bitMap.fill(QtCore.Qt.black)
        bitMap.setMask(cursor.mask())
        self.cursors[cursor] = cursor
      self.ui.pixmapCursor.setPixmap(self.cursors[cursor])
    else:
      self.ui.pixmapCursor.setPixmap(self.image0)
    try:
      s = (str(item))  # + ":" + decoration + ":" + self.commander.current_object_state)
      self.ui.labelObject.setText(s)
    except:
      pass
    self.ui.labelLeft.setText((str(actionLeft)))
    self.ui.labelRight.setText((str(actionRight)))

  def markModifiedModel(self, state):
    if state:
      r, g, b = 0, 255, 255
    else:
      r, g, b = 255, 255, 255

    self.ui.labelModel.setStyleSheet("QLabel { background-color: rgb(%s,%s,%s) }" % (r, g, b))

  # Logger ================================================================

  def writeStatus(self, status):
    self.ui.textStatus.clear()
    self.ui.textStatus.setPlainText(status)

# ------------------------------------------------------------------------------
