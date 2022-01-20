"""
===============================================================================
 logger module of the ModelComposer
===============================================================================

produces output streams for standard output and error output
produces output on request on the structure of the model

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL"
__version__ = "5.01"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ModelBuilder.ModelComposer.modeller_logger import Ui_LoggerForm



class Logger(QtWidgets.QWidget):

  def __init__(self, model_container, parent):

    QtWidgets.QWidget.__init__(self)
    self.ui = Ui_LoggerForm()
    self.ui.setupUi(self)
    self.model_container = model_container
    self.commander = parent.commander

  def home(self):
    self.std_outbox = self.ui.std_outbox  # this is the QtGui.QTextEdit()
    self.std_outbox.moveCursor(QtGui.QTextCursor.Start)
    self.std_outbox.ensureCursorVisible()
    self.std_outbox.setLineWrapColumnOrWidth(500)
    self.std_outbox.setLineWrapMode(QtWidgets.QTextEdit.FixedPixelWidth)

    self.err_outbox = self.ui.err_outbox  # this is the QtWidgets.QTextEdit()
    self.err_outbox.moveCursor(QtGui.QTextCursor.Start)
    self.err_outbox.ensureCursorVisible()
    self.err_outbox.setLineWrapColumnOrWidth(500)
    self.err_outbox.setLineWrapMode(QtWidgets.QTextEdit.FixedPixelWidth)

  def onUpdateStandardOutput(self, text):
    cursor = self.std_outbox.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.insertText(text)
    self.std_outbox.setTextCursor(cursor)
    self.std_outbox.ensureCursorVisible()

  def onUpdateErrorOutput(self, text):
    cursor = self.err_outbox.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.insertText(text)
    self.err_outbox.setTextCursor(cursor)
    self.err_outbox.ensureCursorVisible()

  @QtCore.pyqtSlot()  # signal with no arguments
  def on_pushPrintTree_clicked(self):

    self.ui.Logger.append("\n-----------------\nTree \n-----------------")
    tree = self.model_container["ID_tree"]
    for n in tree:
      s = "node %s : %s" % (n, tree[n])
      self.ui.Logger.append(s)

  @QtCore.pyqtSlot()  # signal with no arguments
  def on_pushPrintNodes_clicked(self):
    self.ui.Logger.append("\n-----------------\nNodes \n-----------------")
    if self.commander.node_group:
      nodes = {}
      for node in self.commander.node_group:
        try:
          nodes[node.ID] = self.model_container["nodes"][node.ID]
        except:
          print("pushPrintNodes: something goes wrong")
    else:
      nodes = self.model_container["nodes"]

    for node in sorted(nodes.keys()):
      s = "node %s : " % node
      self.ui.Logger.append(s)
      for item in nodes[node]:
        s = "   -- %s : %s " % (item, nodes[node][item])
        self.ui.Logger.append(s)
      # try:
      #   s = "   -+ %s : %s " % ("state", self.state_nodes[node])
      # except:
      #   pass

  @QtCore.pyqtSlot()  # signal with no arguments
  def on_pushPrintArcs_clicked(self):
    self.ui.Logger.append("\n-----------------\nArcs \n-----------------")
    arcs = self.model_container["arcs"]
    for id in sorted(arcs):
      s = "%s :: %s --> %s   +   %s" % (id, arcs[id]["source"], arcs[id]["sink"], arcs[id]["token"])
      self.ui.Logger.append(s)

  @QtCore.pyqtSlot()  # signal with no arguments
  def on_pushPrintScenes_clicked(self):
    self.ui.Logger.append("\n-----------------\nScenes \n-----------------")
    scenes = self.model_container["scenes"]
    for id in sorted(scenes):
      nodes = scenes[id]["nodes"]
      arcs = scenes[id]["arcs"]
      for nn in nodes:
        s = "scene nodes %s - %s  , %s" % (id, nn, nodes[nn])
        self.ui.Logger.append(s)
      for a in arcs:
        s = "scene arcs %s - %s  , %s" % (id, a, arcs[a])
        self.ui.Logger.append(s)

  @QtCore.pyqtSlot()  # signal with no arguments
  def on_pushClearWindow_clicked(self):
    self.ui.Logger.clear()

  @QtCore.pyqtSlot()  # signal with no arguments
  def on_pushClearOutputBox_clicked(self):
    self.ui.outbox.clear()
