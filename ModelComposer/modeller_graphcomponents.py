"""
===============================================================================
  graphic elements for ModelComposer
===============================================================================

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

from Common.common_resources import M_None
from Common.graphics_objects import IndicatorDot
from Common.graphics_objects import LAYERS
from Common.graphics_objects import LOCATION_PARAMETERS
from Common.graphics_objects import NAMES
from Common.graphics_objects import NODES, ARCS
from Common.graphics_objects import OBJECTS_arcs_with_states
from Common.graphics_objects import OBJECTS_changing_position
from Common.graphics_objects import OBJECTS_nodes_with_states
from Common.graphics_objects import OBJECTS_not_move
from Common.graphics_objects import OBJECTS_with_application
from Common.graphics_objects import OBJECTS_with_state
from Common.graphics_objects import STRUCTURES_Graph_Item, DECORATIONS_with_state, DECORATIONS_with_application
from Common.qt_resources import KEYS
from Common.qt_resources import PRESET_COLOURS


def debugPrint(source, what):
  print(source, ': ', what)


MOUSE_PRESS_DELAY_MOVE = 75
ORIGIN = QtCore.QPointF(0, 0)
GRID = 10


class ComponentError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg


# root components --------------------------------------------------------------


class R_Item(QtWidgets.QGraphicsItem):

  def __init__(self, strID, graphics_root_object, scene, view, commander):
    QtWidgets.QGraphicsItem.__init__(self)
    self.scene = scene
    self.view = view
    self.commander = commander
    self.ID = strID
    self.graphics_root_object = graphics_root_object

    self.items = {}
    decorations = STRUCTURES_Graph_Item[self.graphics_root_object]
    for decoration in decorations:
      self.items[decoration] = self.addItem(decoration)
      self.items[decoration].position = self.items[decoration].pos()
      self.items[decoration].setParentItem(self)

  def boundingRect(self):
    return self.childrenBoundingRect()

  def addItem(self, decoration):
    shape = STRUCTURES_Graph_Item[self.graphics_root_object][decoration]

    # get shape
    phase = self.commander.editor_phase
    if self.graphics_root_object == NAMES["elbow"]:
      shape_data = self.commander.graphics_data.getData(phase, NAMES["elbow"],
                                                        decoration, M_None, M_None)
      obj_str = str([phase, NAMES["elbow"], decoration, M_None, M_None])
      x = 0  # no relative offset
      y = 0
    else:
      # if self.graphics_root_object in NODES + [NAMES["panel"]]:
      #   state = self.commander.state_nodes[self.ID]
      #   if self.graphics_root_object in OBJECTS_with_application:
      #     application = self.commander.model_container["nodes"][self.ID]["type"]
      #   else:
      #     application = M_None
      state = M_None
      application = M_None

      if self.graphics_root_object in NODES + [NAMES["panel"]]:
        if self.graphics_root_object in OBJECTS_with_state:
          if decoration in DECORATIONS_with_state:
            state = self.commander.state_nodes[self.ID]
        if self.graphics_root_object in OBJECTS_with_application:
          if decoration in DECORATIONS_with_application:
            application = self.commander.model_container.getNodeApplication(self.ID)

      elif self.graphics_root_object == NAMES["connection"]:
        if decoration in DECORATIONS_with_state:
          state = self.commander.state_arcs[(self.ID)]
        if self.graphics_root_object in OBJECTS_with_application:
          application = M_None
          if decoration in DECORATIONS_with_application:
            application = self.commander.model_container.getArcApplication(self.ID)
      else:
        raise ComponentError(" no such class of components :%s" % self.graphics_root_object)
      r, d, a, s = \
        self.commander.main.graphics_DATA.getActiveObjectRootDecorationState(
                phase,
                self.graphics_root_object,
                decoration,
                application,
                state)  # filter
      pass
      if decoration == "network":
        obj_str = self.commander.model_container["nodes"][self.ID]["network"]

      elif decoration == "named_network":
        obj_str = self.commander.model_container["nodes"][self.ID]["named_network"]
      else:
        obj_str = str([phase, r, d, a, s])

      if s == "selected":
        print("debugging -- R_Item obj string", obj_str)

      shape_data = self.commander.graphics_data.getData(phase, self.graphics_root_object,
                                                        decoration, application, state)
      if shape_data["movable"]:
        application_graphical_data = self.commander.model_container.getNodeGraphicsData(self.ID)
        x = application_graphical_data[decoration]["position_x"]
        y = application_graphical_data[decoration]["position_y"]
      else:
        x = shape_data["position_x"]
        y = shape_data["position_y"]

    # print("addItem - decorator, shape", decoration, shape)
    if shape == 'panel':
      brush = self.commander.main.BRUSHES[obj_str]
      item = ShapePannel(x, y, decoration, brush, shape_data, self)
    elif shape == 'text':
      # brush = self.commander.main.BRUSHES[obj_str]
      item = ShapeText(x, y, decoration, self)
    elif shape in ['ellipse']:  # , 'dir_indicator', 'prop_indicator']:
      brush = self.commander.main.BRUSHES[obj_str]
      item = ShapeEllipse(x, y, decoration, brush, shape_data, self)
    elif shape in ['line']:
      pen = self.commander.main.PENS[obj_str]
      item = ShapeLine(decoration, pen, shape_data, self)
    else:
      item = None
      print('addItem', 'error: no such item type :', shape)

    item.o_type = shape

    return item

  def addIndicatorDot(self, name, x, y, rgba_colour):
    r, g, b, a = rgba_colour
    brush = QtGui.QBrush(QtGui.QColor(r, g, b, a))

    shape_data = IndicatorDot()

    self.items[name] = ShapeEllipse(x, y, NAMES["indicator token"], brush, shape_data, self)
    self.items[name].position = self.items[name].pos()
    self.items[name].setParentItem(self)
    self.items[name].setAcceptHoverEvents(True)

  def addIndicatorText(self, name, x, y, text):
    item = ShapeText(x, y, NAMES["indicator typed token"], self)
    item.position = item.pos()
    item.setParentItem(self)
    item.setAcceptHoverEvents(True)
    item.setText(text)

    self.items[name] = item

  def getItemList(self):
    return self.items

  def removeItem(self, item):
    self.scene.removeItem(item)
    del item

  def modifyComponentAppearance(self, dec_ID, method_params):
    """
    in: decorationID, (method, params)
    supported methods:
        setText
        hide
        show
    """
    method, params = method_params
    item = self.items[dec_ID]

    if method == 'setText':
      item.setText(str(params))  # HAP: ID string to integer
      item.show()
    elif method == 'hide':
      item.hide()
    elif method == 'show':
      item.show()


class R_Node(R_Item):  # root component
  """
  node's root properties and methods
  """

  def __init__(self, strID, graphics_root_object, application, x, y, scene, view, commander):
    self._scene = scene
    self.view = view
    self.application = application

    self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

    if graphics_root_object == NAMES["elbow"]:
      self.network = None
    else:
      self.network = commander.model_container["nodes"][strID]["network"]

    if graphics_root_object in OBJECTS_changing_position:
      if graphics_root_object != NAMES["elbow"]:
        application_graphical_data = commander.model_container.getNodeGraphicsData(strID)
        x = application_graphical_data["position_x"]
        y = application_graphical_data["position_y"]

    R_Item.__init__(self, strID, graphics_root_object, scene, view, commander)
    self.__inList = []  # inlist
    self.__outList = []  # outlist

    self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
    self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
    self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

    p = QtCore.QPointF(x, y)  # puts it into its place
    self.setPos(p)

  def boundingRect(self):
    return self.childrenBoundingRect()

  def itemChange(self, change, value):
    if change == QtWidgets.QGraphicsItem.ItemPositionChange:
      for edge in self.__inList:
        sourcePoint, destPoint = edge.arcCoord()
        self.__prepareEdgeDrawing(destPoint, edge, sourcePoint)
      for edge in self.__outList:
        sourcePoint, destPoint = edge.arcCoord()
        self.__prepareEdgeDrawing(destPoint, edge, sourcePoint)

    return QtWidgets.QGraphicsItem.itemChange(self, change, value)

  # def getID(self):
  #   return self.ID

  def addInEdge(self, edge):
    self.__inList.append(edge)
    sourcePoint, destPoint = edge.arcCoord()
    self.__prepareEdgeDrawing(destPoint, edge, sourcePoint)

  def addOutEdge(self, edge):
    self.__outList.append(edge)
    sourcePoint, destPoint = edge.arcCoord()
    self.__prepareEdgeDrawing(destPoint, edge, sourcePoint)

  @staticmethod
  def __prepareEdgeDrawing(destPoint, edge, sourcePoint):
    edge.items[NAMES["root"]].prepare(sourcePoint, destPoint)
    edge.items[NAMES["tail"]].prepare(sourcePoint)
    edge.items[NAMES["head"]].prepare(destPoint)

  def removeInEdge(self, edge):
    i = self.__inList.index(edge)
    del self.__inList[i]

  def removeOutEdge(self, edge):
    i = self.__outList.index(edge)
    del self.__outList[i]

  def getInList(self):
    return self.__inList

  def getOutList(self):
    return self.__outList

  def removeMe(self):
    scene = self._scene
    scene.removeItem(self)
    del self


class G_Item(QtWidgets.QGraphicsItem):
  def __init__(self, parent, decoration):
    #  ToRemember: it seems that the object must be movable in order to
    #  ToRemember: in order to accept hover vents.
    #  one can also make it selectable, but that leads to problems with
    #  having to unselect also after the operation.

    QtWidgets.QGraphicsItem.__init__(self)

    self._scene = parent.commander.scene
    self.view = parent.commander.view  # current_view_object
    self.parent = parent
    self.graphics_root_object = parent.graphics_root_object
    self.decoration = decoration
    self.commander = parent.commander
    self.n_group = False
    self.k_group = False
    self.moved_decoration = False
    self.rubber = None


    self.rubber_active = False
    self.mark_grouped = False

    yellow = PRESET_COLOURS["yellow"]
    self.rubber_select_brush = QtGui.QBrush(QtGui.QColor(yellow))

    # control application of the node classes
    if self.graphics_root_object in OBJECTS_with_application:
      if self.graphics_root_object == NAMES["connection"]:
        self.application = parent.commander.model_container.getArcApplication(parent.ID)
      else:  # this are primitive nodes
        self.application = parent.commander.model_container.getNodeApplication(parent.ID)
        # ["nodes"][parent.ID]["type"]
    else:
      self.application = M_None

    self.shape_data = getShapeData(self.graphics_root_object, decoration, parent)  # moving uses it !

    self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
    self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)
    self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
    try:
      self.setAcceptHoverEvents(True)
    except:
      print("debugging -- set hover event error")
      pass
    # c = R.ModellerCursor()
    self.move_cursor = self.commander.cursors.getCursor('grab')
    self.moved_root = False

    self.setFocus(QtCore.Qt.MouseFocusReason)
    self.view.viewport().setFocus(QtCore.Qt.MouseFocusReason)
    self.setMyCursor()

    self.mousePressDelayTimerMove = QtCore.QTimer()  # timer to control delay

    self.mousePressDelayTimerMove.timeout.connect(self.__mousePressDelayTimerMoveEvent)

  def mousePressEvent(self, event):
    self.moved_root = False
    self.moved_decoration = False
    self.rubber_active = False

    base_obj = self.parent
    node_group = self.commander.node_group
    knot_group = self.commander.knot_group

    if base_obj in node_group:
      # print("mouse press event found parent")
      self.n_group = True
    else:
      self.n_group = False
      # print("mouse press event did not find parent", self.parent)
      # print(" node group:", node_group)

    if base_obj in knot_group:
      self.k_group = True
    else:
      self.k_group = False

    if NAMES["panel"] not in self.parent.graphics_root_object:
      self.mousePressDelayTimerMove.start(MOUSE_PRESS_DELAY_MOVE)

      QtWidgets.QGraphicsItem.mousePressEvent(self, event)

  def __mousePressDelayTimerMoveEvent(self):
    #  handles time event of "mousePressDelayTimerMove"
    # print( 'mousePressDelayTimerEvent')
    self.mousePressDelayTimerMove.stop()
    # RULE: don't move connections and conectors via mouse
    if self.graphics_root_object not in OBJECTS_changing_position:
      return
    self.setCursor(self.move_cursor)

  def mouseReleaseEvent(self, event):
    if self.mousePressDelayTimerMove.isActive():
      self.mousePressDelayTimerMove.stop()
    self.setMyCursor()

    node_group = self.commander.node_group
    knot_group = self.commander.knot_group

    if self.moved_root:
      self.moved_root = False
      if (node_group == set() and knot_group == set()):  # or \
        # ((self.parentItem not in node_group) and (self.parentItem() not in knot_group)):
        # if (node_group == set() and knot_group == set()) or \
        #         ((self.parentItem not in node_group) and (self.parentItem() not in knot_group)):
        # TODO: seems this never happens -- should it ? == did see it once for 0 ???
        # print("posintion: ", dir(self.parent))
        x = self.parentItem().x()
        y = self.parentItem().y()
        # grid = 10
        # x = grid * round(float(self.parentItem().x()) / grid)
        # y = grid * round(float(self.parentItem().y()) / grid)

        print("moving node: {} to position ({},{}) ".format(self.parent.ID, x, y))
        if self.graphics_root_object == NAMES["elbow"]:
          self.commander.model_container.updateKnotPosition(self.commander.currently_viewed_node,
                                                            self.parent.arcID,
                                                            self.parent.ID,
                                                            x, y)
        else:
          self.commander.model_container.updateNodePosition(self.parent.ID, x, y)
      else:
        for n in self.commander.node_group:
          x = n.x()
          y = n.y()
          self.commander.model_container.updateNodePosition(n.ID, x, y)
        pass
        for k in self.commander.knot_group:
          x = k.x()
          y = k.y()

          self.commander.model_container.updateKnotPosition(self.commander.currently_viewed_node,
                                                            k.arcID,
                                                            k.ID,
                                                            x, y)
      return

    elif self.moved_decoration:
      self.moved_decoration = False
      x = self.x()
      y = self.y()
      self.commander.model_container.updateDecorationPosition(self.parentItem().ID, self.decoration, x, y)

    elif self.rubber_active:
      self.__formGroups()
    else:
      self.parent.commander.processGUIEvent('mouse', self, event.button(),
                                            event.pos())

  def __formGroups(self):
    added_new = False  # used to delete group
    nodes = [NAMES["node"], NAMES["interface"], NAMES["intraface"], NAMES["branch"]]
    offset = self.view.offset
    x_o = offset.x()
    y_o = offset.y()
    a = self._scene.items()
    for i in a:
      t = i.graphics_root_object
      # print(" rubber root ? :",i )
      if (t in nodes) or (t == NAMES["elbow"]) or (t == NAMES["connection"]):
        x_r = self.rubber.x() + x_o
        y_r = self.rubber.y() + y_o
        w = self.rubber.rect().width()
        h = self.rubber.rect().height()
        rect = QtCore.QRectF(x_r, y_r, w, h)

        # i_x = i.pos().x()
        # i_y = i.pos().y()

        # if (x_r < i_x < x_r + w) and (y_r < i_y < y_r + h):  # rect.contains(i.pos()):
        if rect.contains(i.pos()):
          StrO = str(i.__class__)
          t = StrO.split('.')[-1]  # get last bit
          tt = t.split("'")[0]  # remove '>
          if "ID" in dir(i):  # check if it is root object
            if tt == "Node":
              # print("rubber adding node", i, i.ID)
              for item in i.items:
                i.items[item].mark_grouped = True
                added_new = True
              self.commander.node_group.add(i)
            elif tt == "Knot":
              added_new = True
              # print(r"rubber adding knot", i.arcID)
              for item in i.items:
                i.items[item].mark_grouped = True
                added_new = True
              self.commander.knot_group.add(i)

        self.view.viewport().repaint()
        self.rubber.hide()

    if not added_new:
      for node in self.commander.node_group:
        for item in node.items:
          node.items[item].mark_grouped = False
      for knot in self.commander.knot_group:
        for item in knot.items:
          knot.items[item].mark_grouped = False
      self.view.viewport().repaint()

      self.rubber_active = False
      self.rubber.hide()

      self.commander.resetGroups()

      # NOTE do not flip page changes addresses

  def keyPressEvent(self, event):
    super(G_Item, self).keyPressEvent(event)
    # print(">>>> key press event")
    key_pressed = event.key()
    key = KEYS[key_pressed]
    self.commander.processGUIEvent('keyboard', self, key)
    self.setMyCursor()

  # def cannotMoveRelative(self):
  #   return self.decoration in R.G_OBJECTS_no_rel_move

  def mouseMoveEvent(self, event):
    # print("mouse move")
    #  do rubber
    if self.graphics_root_object == NAMES["panel"]:
      if self.decoration == NAMES["root"]:
        if not self.rubber_active:
          self.rubber_active = True
          view = self.view
          offset = self.view.offset
          self.moved_root = False
          self.rubber = Rubber(view, event.pos(), offset)
        else:
          self.moved_root = False
          self.rubber.mouseMoveEvent(event)
          return

    if self.graphics_root_object not in OBJECTS_changing_position:
      return

    # do moves
    else:
      if self.decoration in OBJECTS_not_move:
        return
      if self.decoration == "root":
        x = self.__gridding(event.pos().x())
        y = self.__gridding(event.pos().y())
      else:
        x = event.pos().x()
        y = event.pos().y()

      dx = event.lastPos().x() - x
      dy = event.lastPos().y() - y

      if not self.n_group and not self.k_group:
        # print("mouse move event ")
        if not self.shape_data["movable"]:
          # print("move parent")
          self.moved_root = True
          self.moved_decoration = False
          self.parentItem().moveBy(-dx, -dy)
          return

        else:
          self.moved_root = False
          self.moved_decoration = True
          # print("move self")
          self.moveBy(-dx, -dy)
          return

      else:
        # print("moving group :", self.commander.node_group)
        self.moved_root = True
        node_group = self.commander.node_group
        knot_group = self.commander.knot_group
        for n in node_group:
          # print("moving node :", n, dx, dy)
          n.moved = True
          n.moveBy(-dx, -dy)

        for k in knot_group:
          k.moved = True
          # print("moving knot :", k, dx, dy)
          k.moveBy(-dx, -dy)

  def __gridding(self,z):
    g_z = GRID * round(z/GRID)
    return g_z

  def hoverEnterEvent(self, event):
    # print('hoverEnterEvent - mouse enter event', self.graphics_root_object, self.decoration)

    self.setFocus(QtCore.Qt.MouseFocusReason)
    self.view.viewport().setFocus(QtCore.Qt.MouseFocusReason)
    self.view.viewport().update()
    self.setMyCursor()

  def hoverLeaveEvent(self, event):
    # print("hover leave", self.graphics_root_object)
    self.clearFocus()
    self.view.viewport().update()
    #  NOTE: DO NOT clear focus on viewport....
    pass

  def hoverMoveEvent(self, event):
    self.update()
    pass

  # def enterEvent(self, event):
  #   self.setFocus(QtCore.Qt.MouseFocusReason)
  #   self.parent.view.viewport().setFocus(QtCore.Qt.MouseFocusReason)
  #   self.__mousePressDelayTimerMoveEvent().stop()

  def setMyCursor(self):
    state = self.getGraphObjectState()
    cursor = self.parent.commander.getTheCursor(self.graphics_root_object,
                                                self.decoration, self.application, state)
    if (self.graphics_root_object == "node_simple") and (self.decoration == "root"):
      # print("setCursor :", self.parent.graphics_root_object, self.decoration)
      cursor = self.parent.commander.getTheCursor(self.graphics_root_object,
                                                self.decoration, self.application, state)
    self.setCursor(cursor)

  def getGraphObjectState(self):
    ID = self.parent.ID
    # print("getGraphObjectState  object ", self.graphics_root_object, ID)
    if self.graphics_root_object in OBJECTS_with_state:
      if self.graphics_root_object in OBJECTS_nodes_with_states:
        state = self.commander.state_nodes[ID]
      elif self.graphics_root_object == OBJECTS_arcs_with_states:
        state = self.commander.state_arcs[ID]
      else:
        state = M_None
    else:
      state = M_None
    return state

  def getGraphObjectID(self):
    return self.parent.ID


# shapes -----------------------------------------------------------------------

def getShapeData(graphics_root_object, graph_object, parent):

  if graphics_root_object in NODES + [NAMES["panel"]]:  # [NAMES["node"], NAMES["panel"]]:
    application = parent.commander.model_container.getNodeApplication(parent.ID)  # ["nodes"][parent.ID]["type"]
    state = parent.commander.state_nodes[parent.ID]
  elif graphics_root_object == NAMES["connection"]:
    application = parent.commander.model_container.getArcApplication(parent.ID)
    # print("get shape >>> application:", application)
    state = parent.commander.state_arcs[parent.ID]
  elif graphics_root_object == NAMES["elbow"]:
    # print("getShapeData knot")
    application = M_None
    state = parent.commander.state_arcs[parent.arcID]

  phase = parent.commander.editor_phase
  shape_data = parent.commander.graphics_data.getData(phase, parent.graphics_root_object,
                                                      graph_object, application, state)

  # print("getShapeData - shape_data: ",shape_data )
  return shape_data


class ShapePannel(QtWidgets.QGraphicsRectItem, G_Item):
  def __init__(self, x, y, decoration, brush, shape_data, parent):
    w = shape_data["width"]
    h = shape_data["height"]
    self.brush = brush

    QtWidgets.QGraphicsRectItem.__init__(self, x, y, w, h)  # must be before G_item ini
    G_Item.__init__(self, parent, decoration)
    self.size = QtCore.QRectF(x, y, w, h)
    self.setRect(self.size)
    self.setAcceptHoverEvents(True)
    self.setVisible(True)
    self.setBrush(brush)
    z = LAYERS[shape_data["layer"]]
    self.setZValue(z)

  def boundingRect(self):
    return self.size

  def paint(self, painter, option, widget):
    if self.mark_grouped:
      # print(">>>>>pane repaint")
      painter.setBrush(self.rubber_select_brush)
    else:
      painter.setBrush(self.brush)
    painter.drawRect(self.size)
    pass


class ShapeEllipse(QtWidgets.QGraphicsEllipseItem, G_Item):
  def __init__(self, x, y, decoration, brush, shape_data, parent):
    G_Item.__init__(self, parent, decoration)
    # if decoration == "named_network":
    #   print("debugging -- got a named network")

    self.shape_data = shape_data
    self.brush = brush

    w = shape_data["width"]
    h = shape_data["height"]
    z = LAYERS[shape_data["layer"]]

    QtWidgets.QGraphicsEllipseItem.__init__(self, x, y, w, h)
    G_Item.__init__(self, parent, decoration)
    self.size = QtCore.QRectF(x, y, w, h)
    # self.offset = x, y

    if self.decoration in ["property", "indicator"]:
      print("ellipse ", self.decoration, x, y, w, h)

    self.setPos(x - w / 2, y - h / 2)
    self.setRect(self.size)
    self.setZValue(z)

    self.locPoint = None

  def boundingRect(self):
    return self.size

  def prepare(self, locPoint):
    self.locPoint = locPoint
    self.prepareGeometryChange()

  def paint(self, painter, option, widget):
    if self.mark_grouped:
      # print(">>>>>ellipse repaint")
      painter.setBrush(self.rubber_select_brush)
    else:
      painter.setBrush(self.brush)
    width = self.size.width()
    height = self.size.height()

    # painter.drawEllipse(0, 0, width, height)

    if self.decoration in [NAMES["tail"], NAMES["head"]]:
      # print("ellipse  head tails")
      x = self.locPoint.x() - width / 2
      y = self.locPoint.y() - height / 2
      painter.drawEllipse(0, 0, width, height)
      self.setPos(x, y)
    else:
      x = self.pos().x() + width / 2  # self.offset[0] - width / 2
      y = self.pos().y() + height / 2  # self.offset[1] - height / 2
      painter.drawEllipse(x, y, width, height)
      # if self.decoration in ["property", "indicator"]:
      #   print("painting ", self.decoration, x,y, width, height)#, self.offset)


class ShapeLine(QtWidgets.QGraphicsLineItem, G_Item):
  def __init__(self, decoration, pen, shape_data, parent):
    QtWidgets.QGraphicsLineItem.__init__(self)
    G_Item.__init__(self, parent, decoration)

    # if self.commander.editor_phase == "token_topology":
    #   print("debugging -- define line")

    self.pen = pen

    z = LAYERS[shape_data["layer"]]
    self.setZValue(z)

    self.sourcePoint = QtCore.QPointF()
    self.destPoint = QtCore.QPointF()

    head_data = getShapeData(parent.graphics_root_object, NAMES["head"], parent)
    tail_data = getShapeData(parent.graphics_root_object, NAMES["tail"], parent)
    head_width = head_data["width"]
    head_height = head_data["height"]
    tail_width = tail_data["width"]
    tail_height = tail_data["height"]

    self.header_offset = QtCore.QPointF(head_height / 2, head_width / 2)
    self.tail_offset = QtCore.QPointF(tail_height / 2, tail_width / 2)
    self.extra = 10

  def boundingRect(self):  # essential for moving arc
    return \
      QtCore.QRectF(self.sourcePoint,
                    QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                  self.destPoint.y() - self.sourcePoint.y())
                    ).normalized().adjusted(-self.extra, -self.extra,
                                            self.extra, self.extra)

  def prepare(self, sourcePoint, destPoint):
    self.sourcePoint = sourcePoint
    self.destPoint = destPoint
    self.prepareGeometryChange()

  def paint(self, painter, option, widget):
    line = QtCore.QLineF(self.sourcePoint, self.destPoint)

    if line.length() == 0.0:
      return

    painter.setPen(self.pen)
    painter.drawLine(line)


class ShapeText(QtWidgets.QGraphicsSimpleTextItem, G_Item):
  def __init__(self, x, y, decoration, parent):
    QtWidgets.QGraphicsSimpleTextItem.__init__(self)
    G_Item.__init__(self, parent, decoration)

    shape_data = getShapeData(parent.graphics_root_object, decoration, parent)
    self.shape_data = shape_data

    z = LAYERS[shape_data["layer"]]
    self.setZValue(z)
    self.setText('text')
    self.setAcceptHoverEvents(True)
    self.setPos(x - 5, y - 5)
    self.show()


# viewed components ------------------------------------------------------------

class NodeView(R_Item):
  """
  implements the node pannel:
  left a pannel for the ancestors
  right a pannel for the siblings
  """

  def __init__(self, ID, commander):
    scene = commander.view  # [ID]
    view = commander.scene  # s[ID]
    self.graphics_root_object = NAMES["panel"]
    R_Item.__init__(self, ID, NAMES["panel"], scene, view, commander)

  # def getOrigins(self):
  #   return (self.anc_origin, self.sib_origin)

  #
  def paint(self, painter, option, widget):
    #  NOTE: eliminate " QGraphicsItem.paint() is abstract and must be overridden"
    pass


class Rubber(QtWidgets.QRubberBand):
  def __init__(self, view, origin, offset):
    QtWidgets.QRubberBand.__init__(self, QtWidgets.QRubberBand.Rectangle, view)
    self.offset = offset
    self.origin = origin.toPoint() - self.offset

  def mouseMoveEvent(self, event):
    posit = event.pos().toPoint() - self.offset
    origin = self.origin
    rec = QtCore.QRect(origin, posit).normalized()
    self.setGeometry(rec)
    self.show()


# main components
class Node(R_Node):
  """
  implements node, determines shape
  in:
      canvas, x,y, ID, type, node_structure
      x,y : position
      ID: unique numerical ID
      type: what class of node
      node_structure: graphics_objects
  """

  def __init__(self, strID, graphics_root_object, application, x, y, scene, view, commander):
    QtWidgets.QGraphicsItem.__init__(self)
    # print("Node -- graphics_root_object", graphics_root_object)
    self.graphics_root_object = graphics_root_object
    R_Node.__init__(self, strID, graphics_root_object, application, x, y, scene, view, commander)

  def getNodeID(self):
    return self.ID

  def paint(self, painter, option, widget):
    # NOTE: eliminate " QGraphicsItem.paint() is abstract and must be overridden"
    pass


class Knot(R_Node):
  """
  implements node, determines shape
  in:
      canvas, x,y, ID, type, node_structure
      x,y : position
      ID: unique numerical knotID
      type: what class of node
      node_structure: see graphics_objects
  """

  def __init__(self, knotID, arcID, x, y, scene, view, commander):
    QtWidgets.QGraphicsItem.__init__(self)
    self.graphics_root_object = NAMES["elbow"]
    self.arcID = arcID
    R_Node.__init__(self, knotID, NAMES["elbow"], M_None, x, y, scene, view, commander)

  def paint(self, painter, option, widget):
    # NOTE: eliminate " QGraphicsItem.paint() is abstract and must be overridden"
    pass

  def getKnotID(self):
    return self.ID

  def getArcID(self):
    return self.arcID  # self.arcID


class Arc_Edge(R_Item):
  """
  implements edge on an arc (from node|knot to knot|node)
  in:
      source node
      sink node
      canvas
      arcID
      edge_structure
  """

  def __init__(self, arcID, sourceNode, destNode, scene, view, commander):
    QtWidgets.QGraphicsItem.__init__(self, None)
    self.scene = scene
    self.view = view
    R_Item.__init__(self, arcID, NAMES["connection"], scene, view, commander)

    self.arcID = arcID
    self.graphics_root_object = NAMES["connection"]
    self.now_open = False

    self.source = sourceNode
    self.dest = destNode
    self.source.addOutEdge(self)
    self.dest.addInEdge(self)
    self.setAcceptHoverEvents(True)
    # self.arc_type = self.commander.model_container["arcs"][arcID]["type"]

  def updateMe(self):
    self.state = self.commander.state_arcs[self.arcID]
    # print("update me")
    for i in self.items:
      self.items[i].update()

  def paint(self, painter, option, widget):
    #  NOTE: eliminate " QGraphicsItem.paint() is abstract and must be overridden"
    #        print 'paint edge'
    pass

  def getArcID(self):
    return self.arcID

  def removeMe(self):
    self.source.removeOutEdge(self)
    self.dest.removeInEdge(self)
    self.scene.removeItem(self)
    del self

  def arcCoord(self):
    S = self.source
    D = self.dest
    p = ORIGIN
    source = self.mapFromItem(S, p)
    dest = self.mapFromItem(D, p)
    line = QtCore.QLineF(source, dest)
    S_rect = S.items["root"].boundingRect()
    D_rect = D.items["root"].boundingRect()
    f = LOCATION_PARAMETERS["arc_node_gap_factor"]  # factor makes a gap to the outer rim of root decorator
    S_w = S_rect.width() * f
    S_h = S_rect.height() * f
    D_w = D_rect.width() * f
    D_h = D_rect.height() * f
    l = line.length()
    dx = line.dx()
    dy = line.dy()
    source_Offset = QtCore.QPointF(S_w / l * dx, S_h / l * dy)
    dest_Offset = QtCore.QPointF(D_w / l * dx, D_h / l * dy)
    sourcePoint = source + source_Offset
    destPoint = dest - dest_Offset
    return sourcePoint, destPoint

  def getMidPoint(self):
    sourcePoint = self.source.pos()
    destPoint = self.dest.pos()
    middlePoint = sourcePoint + (destPoint - sourcePoint) / 2.0
    return middlePoint

  def printMe(self):
    print('edge %s' % self)
