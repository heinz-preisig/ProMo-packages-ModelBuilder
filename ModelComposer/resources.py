"""
===============================================================================
 common resources for modules of the  ModelComposer Suite
===============================================================================

defines all major resources


------------------------------------------------------------------------------
 NOTE:constructStructureComponentID
 the graph component is not a class but a simple string. Reason being that it
 is easier to handle for the automaton implementation.
 Could be handled differently by defining a class with a __str__ method and
 a converting method when "loading" automaton.

 Object ID :  <structure ID>.<decoration ID>&<application-type>:<state>

 delimiters:
     O_delimiter = "."
     T_delimiter = "&"  within the application type we split with |
     S_delimiter = ":"

  application_type is now also a composite:     
     node : <nodetype>|<token>|conversion
     arc  : <arc type>|<token>|<mechanism>
     
     
  each arc and each node have a network membership

Application filters
  graphical_object level 0 - topology
  graphical object level i - adding layer i 

@changes :2017-03-24 : simple node got a network indicator
@changes : 2017-09-25 : clean up


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL"
__version__ = "5.01"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# ===============================================================================
#  resources
# ===============================================================================


import os as OS

from PyQt5 import QtGui  as Q_Gui

from Common.common_resources import M_None
from Common.resource_initialisation import DEFAULT_EXTENSION_CURSOR
from Common.resource_initialisation import DIRECTORIES

#  ToRemember: this is a little bit of a headache...needs to correspond with...

# NOTE: this defines the available actions
ACTIONS = {}
ACTIONS["topology"] = ["zoom in",
                       "add node",
                       "delete node",
                       "group nodes",
                       "explode node",
                       "begin arc",
                       "add arc",
                       "remove arc",
                       "re-direct arc",
                       "change arc",
                       "insert knot",
                       "remove knot",
                       "make a copy",
                       "insert model",
                       "reset",
                       "name node",
                       "select node",
                       ]
ACTIONS["token_topology"] = ["zoom in",
                             "inject",
                             "compute"
                             ]
ACTIONS["equation_topology"] = ["make interface",
                                "instantiate",
                                "add_equation_object",
                                "remove_equation_object",
                                "edit_representation"]


# Cursors ----------------------------------------------------------------------

class ModellerCursor(dict):
  """ origin location"""

  def __init__(self):
    hotpoints = {
            "TL": (0, 0),
            "TC": (16, 0),
            "TR": (32, 0),
            "LC": (0, 16),
            "CC": (16, 16),
            "RC": (16, 32),
            "BL": (0, 32),
            "BC": (16, 32),
            "BR": (32, 32),
            }

    c_loc = DIRECTORIES["cursor_location"]
    li = OS.listdir(c_loc)
    # print("setting up all available cursors")
    for f in li:
      pos = f[0:2]
      if pos in list(hotpoints.keys()):
        if DEFAULT_EXTENSION_CURSOR in f:
          myfile = c_loc + "/" + f
          ID = f[0:f.index(DEFAULT_EXTENSION_CURSOR)]
          pm = Q_Gui.QPixmap(myfile)
          #                    pm.setMask(pm.createHeuristicMask())
          x, y = hotpoints[pos]
          self[ID] = Q_Gui.QCursor(pm, x, y)
          # print( "set up cursor '%s'"%ID)

          # default cursors -------------------------------------------------------------
    self["forbidden"] = self["CC_forbidden"]
    self["undefined"] = self["CC_undefined"]
    self["grab"] = self["CC_grab-tongs01"]
    self["move"] = self["CC_move"]
    self[M_None] = self["CC_logo"]
    self["group_select"] = self["CC_select"]

  def getCursor(self, select):
    if select not in list(self.keys()):
      return None
    return self[select]

  def getBixMap(self, select):
    return self[select].pixmap()

  def getIcon(self, select):
    return Q_Gui.QIcon(self.getBixMap(select))

  def getAllCursorNames(self):
    return list(self.keys())


# #testing
#
if __name__ == "__main__":
  pass
