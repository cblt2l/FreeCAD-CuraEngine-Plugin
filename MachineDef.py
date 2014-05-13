#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014                                                    *
#*   cblt2l <cblt2l@users.sourceforge.net>                                 *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

import FreeCAD
from SliceVars import *
from pivy import coin

if FreeCAD.GuiUp:
	import FreeCADGui
	from FreeCADGui import PySideUic as uic
	from PySide import QtCore, QtGui

# Temporary until settings are integrated properly
_bedx = 100
_bedy = 100
_machinex = 100
_machiney = 100
_machinez = 100
#-------------------------------------------------

def makePrintBedGrp():
#	obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","PrintBed")
	grp = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","PrintBedGroup")
	PrintBedGroup(grp)
	FreeCADGui.activeDocument().activeView().viewAxometric()
#	PrintBed(obj)
#	ViewProviderPrintBed(obj.ViewObject)


class PrintBedGroup:
	def __init__(self, grp):
		# Create objects for the printbed and print volume
		pbed = FreeCAD.ActiveDocument.addObject("App::FeaturePython","PrintBed")
		pvol = FreeCAD.ActiveDocument.addObject("App::FeaturePython","PrintVolume")
		
		# Create an object & view provider for the print bed
		PrintBed(pbed)
		ViewProviderPrintBed(pbed.ViewObject)
		
		# Create an object & view provider for the print volume
		PrintVolume(pvol)
		ViewProviderPrintVolume(pvol.ViewObject)
		
		# Add the PrintBed and PrintVolume objects to the group
		grp.addObject(pbed)
		grp.addObject(pvol)

class PrintBed:
	'The PrintBed Object'
	def __init__(self, obj):
		global _bedx, _bedy
		FreeCAD.Console.PrintMessage("Change Bed X: " + str(_bedx) + "\n")
		obj.addProperty("App::PropertyDistance", "XSize", "PrintBed", "The X Dimension of the Bed").XSize=_bedx
		obj.addProperty("App::PropertyDistance", "YSize", "PrintBed", "The Y Dimension of the Bed").YSize=_bedy
		obj.Proxy = self
		self.Type = "PrintBed"

	def onChanged(self, fp, prop):
		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

	def execute(self, fp):
		FreeCAD.Console.PrintMessage("Recompute PrintBed feature\n")

class ViewProviderPrintBed:
	'The PrintBed View Provider Object'
	def __init__(self, obj):
		obj.addProperty("App::PropertyColor","Color","PrintBed","Color of the box").Color=(1.0,0.0,0.0)
		obj.Proxy = self

	def attach(self, obj):
		"'''Setup the scene sub-graph of the view provider, this method is mandatory'''"
		self.shaded = coin.SoGroup()
		self.wireframe = coin.SoGroup()
		self.scale = coin.SoScale()
		self.color = coin.SoBaseColor()
		self.trans = coin.SoTranslation()

		self.data=coin.SoCube()
		# Top of print bed is X-Y plane
		self.trans.translation.setValue([0,0,-0.5])
		self.shaded.addChild(self.trans)
		self.shaded.addChild(self.scale)
		self.shaded.addChild(self.color)
		self.shaded.addChild(self.data)
		obj.addDisplayMode(self.shaded,"Shaded")
		style=coin.SoDrawStyle()
		style.style = coin.SoDrawStyle.LINES
		self.wireframe.addChild(style)
		self.wireframe.addChild(self.scale)
		self.wireframe.addChild(self.color)
		self.wireframe.addChild(self.data)
		obj.addDisplayMode(self.wireframe,"Wireframe")
		self.onChanged(obj,"Color")

	def updateData(self, fp, prop):
		"'''If a property of the handled feature has changed we have the chance to handle this here'''"
		# fp is the handled feature, prop is the name of the property that has changed
		x = fp.getPropertyByName("XSize").Value
		y = fp.getPropertyByName("YSize").Value
		z = 1.0
		# Set the size of the PrintBed
		self.data.width = x
		self.data.height = y
		self.data.depth = z
		
		pass

	def getDisplayModes(self,obj):
		"'''Return a list of display modes.'''"
		modes=[]
		modes.append("Shaded")
		modes.append("Wireframe")
		return modes

	def getDefaultDisplayMode(self):
		"'''Return the name of the default display mode. It must be defined in getDisplayModes.'''"
		return "Shaded"

	def setDisplayMode(self,mode):
		return mode

	def onChanged(self, vp, prop):
		"'''Here we can do something when a single property got changed'''"
		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
		if prop == "Color":
			c = vp.getPropertyByName("Color")
			self.color.rgb.setValue(c[0],c[1],c[2])

	def getIcon(self):
		return ":/icons/PartDesign_Revolution.svg"

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

class PrintVolume:
	'The StrokeLimit Object'
	def __init__(self, obj):
		global _machinex, _machiney, _machinez
		
		obj.addProperty("App::PropertyDistance", "XStroke", "Machine", "The X Axis Stroke").XStroke=_machinex
		obj.addProperty("App::PropertyDistance", "YStroke", "Machine", "The Y Axis Stroke").YStroke=_machiney
		obj.addProperty("App::PropertyDistance", "ZStroke", "Machine", "The Z Axis Stroke").ZStroke=_machinez
		obj.Proxy = self
		self.Type = "Machine"

	def onChanged(self, fp, prop):
		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")

	def execute(self, fp):
		FreeCAD.Console.PrintMessage("Recompute Machine feature\n")

class ViewProviderPrintVolume:
	'The StrokeLimit View Provider Object'
	def __init__(self, obj):
		#obj.addProperty("App::PropertyColor","Color","Machine","Color of the box").Color=(1.0,0.0,0.0)
		obj.Proxy = self

	def attach(self, obj):
		"'''Setup the scene sub-graph of the view provider, this method is mandatory'''"
		self.wireframe = coin.SoGroup()
		self.scale = coin.SoScale()
#		self.color = coin.SoBaseColor()
		self.trans = coin.SoTranslation()

		self.data=coin.SoCube()
		self.trans.translation.setValue([0,0,100])
		self.wireframe.addChild(self.trans)
		style=coin.SoDrawStyle()
		style.style = coin.SoDrawStyle.LINES
		self.wireframe.addChild(style)
		self.wireframe.addChild(self.scale)
#		self.wireframe.addChild(self.color)
		self.wireframe.addChild(self.data)
		obj.addDisplayMode(self.wireframe,"Wireframe")

	def updateData(self, fp, prop):
		"'''If a property of the handled feature has changed we have the chance to handle this here'''"
		# fp is the handled feature, prop is the name of the property that has changed
		x = fp.getPropertyByName("XStroke").Value
		y = fp.getPropertyByName("YStroke").Value
		z = fp.getPropertyByName("ZStroke").Value
		self.trans.translation.setValue([0,0,z/2])
		self.data.width = x
		self.data.height = y
		self.data.depth = z
		pass

	def getDisplayModes(self,obj):
		"'''Return a list of display modes.'''"
		modes=[]
		modes.append("Wireframe")
		return modes

	def getDefaultDisplayMode(self):
		"'''Return the name of the default display mode. It must be defined in getDisplayModes.'''"
		return "Wireframe"

	def setDisplayMode(self,mode):
		return mode

	def onChanged(self, vp, prop):
		"'''Here we can do something when a single property got changed'''"
		FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
#		if prop == "Color":
#			c = vp.getPropertyByName("Color")
#			self.color.rgb.setValue(c[0],c[1],c[2])

	def getIcon(self):
		return ":/icons/PartDesign_Revolution.svg"

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

class PrintBedTaskPanel:
	def __init__(self):
		# temporary settings mechanism
		global _machinex, _machiney, _machinez, _bedx, _bedy

		# Get the macro directory. The qt uic form is loaded from here.
		self.macroDir = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").GetString("MacroPath")

		# Load the qt uic form. It _must_ be in the macro dir
		form_class, base_class = uic.loadUiType(self.macroDir + "/MachineDef.ui")
		self.formUi = form_class()
		self.form = QtGui.QWidget()
		self.formUi.setupUi(self.form)

		self.formUi.spinBox_1.setValue(_machinex)
		self.formUi.spinBox_2.setValue(_machiney)
		self.formUi.spinBox_3.setValue(_machinez)
		self.formUi.spinBox_4.setValue(_bedx)
		self.formUi.spinBox_5.setValue(_bedy)

		self.formUi.spinBox_1.valueChanged.connect(self._machineXStroke)
		self.formUi.spinBox_2.valueChanged.connect(self._machineYStroke)
		self.formUi.spinBox_3.valueChanged.connect(self._machineZStroke)
		self.formUi.spinBox_4.valueChanged.connect(self._bedXSize)
		self.formUi.spinBox_5.valueChanged.connect(self._bedYSize)

	def accept(self):
		makePrintBedGrp()
		FreeCADGui.Control.closeDialog()

	def reject(self):
		FreeCADGui.Control.closeDialog()

	def getStandardButtons(self):
		return int(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)

	def _machineXStroke(self, val):
		global _machinex
		_machinex = val
		FreeCAD.Console.PrintMessage("Change Machine X: " + str(val) + "\n")

	def _machineYStroke(self, val):
		global _machiney
		_machiney = val
		FreeCAD.Console.PrintMessage("Change Machine Y: " + str(val) + "\n")

	def _machineZStroke(self, val):
		global _machinez
		_machinez = val
		FreeCAD.Console.PrintMessage("Change Machine Y: " + str(val) + "\n")

	def _bedXSize(self, val):
		global _bedx
		_bedx = val
		FreeCAD.Console.PrintMessage("Change Bed X: " + str(val) + "\n")

	def _bedYSize(self, val):
		global _bedy
		_bedy = val
		FreeCAD.Console.PrintMessage("Change Bed Y: " + str(val) + "\n")



# Run as macro
panel=PrintBedTaskPanel()
FreeCADGui.Control.showDialog(panel)
