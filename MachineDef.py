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

# Default Values
defaultVals = {"machinex":100, "machiney":100, "machinez":100, "offsetx":20, "offsety":20, "bedx":100, "bedy":100}
#-------------------------------------------------

def makePrintBedGrp():
#	obj = FreeCAD.ActiveDocument.addObject("App::FeaturePython","PrintBed")
	grp = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","PrintBedGroup")
	PrintBedGroup(grp)
	FreeCADGui.activeDocument().activeView().viewAxometric()
	FreeCADGui.SendMsgToActiveView("ViewFit")
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
		obj.addProperty("App::PropertyDistance", "XSize", "PrintBed", "The X Dimension of the Bed").XSize=readSetting("bedx")
		obj.addProperty("App::PropertyDistance", "YSize", "PrintBed", "The Y Dimension of the Bed").YSize=readSetting("bedy")
		obj.addProperty("App::PropertyDistance", "XOffset", "PrintBed", "The X Offset of the Bed").XOffset=readSetting("offsetx")
		obj.addProperty("App::PropertyDistance", "YOffset", "PrintBed", "The Y Offset of the Bed").YOffset=readSetting("offsety")
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
		ox = fp.getPropertyByName("XOffset").Value
		oy = fp.getPropertyByName("YOffset").Value
		# Set the size of the PrintBed
		self.data.width = x
		self.data.height = y
		self.data.depth = z
		# Translate the printbed to proper location
		self.trans.translation.setValue([(x/2)+ox, (y/2)+oy, -0.5])
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
		obj.addProperty("App::PropertyDistance", "XStroke", "Machine", "The X Axis Stroke").XStroke=readSetting("machinex")
		obj.addProperty("App::PropertyDistance", "YStroke", "Machine", "The Y Axis Stroke").YStroke=readSetting("machiney")
		obj.addProperty("App::PropertyDistance", "ZStroke", "Machine", "The Z Axis Stroke").ZStroke=readSetting("machinez")
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
		# Switch Z to proper default value
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
		# Translate box to keep corner at (0,0)
		self.trans.translation.setValue([x/2 ,y/2 , z/2])
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
		# Get the user's home directory.
		self.homeDir = os.path.expanduser("~")

		# Load the qt uic form. It _must_ be in ~/.FreeCAD/Mod/FreeCAD-CuraEngine-Plugin, Perhaps there is a better way...
		self.form = uic.loadUi(self.homeDir + "/.FreeCAD/Mod/FreeCAD-CuraEngine-Plugin/MachineDef.ui")

		self.form.doubleSpinBox_1.setValue(readSetting("machinex"))
		self.form.doubleSpinBox_2.setValue(readSetting("machiney"))
		self.form.doubleSpinBox_3.setValue(readSetting("machinez"))
		self.form.doubleSpinBox_6.setValue(readSetting("offsetx"))
		self.form.doubleSpinBox_7.setValue(readSetting("offsety"))
		self.form.doubleSpinBox_4.setValue(readSetting("bedx"))
		self.form.doubleSpinBox_5.setValue(readSetting("bedy"))

		self.form.doubleSpinBox_1.valueChanged.connect(self._machineXStroke)
		self.form.doubleSpinBox_2.valueChanged.connect(self._machineYStroke)
		self.form.doubleSpinBox_3.valueChanged.connect(self._machineZStroke)
		self.form.doubleSpinBox_6.valueChanged.connect(self._bedXOffset)
		self.form.doubleSpinBox_7.valueChanged.connect(self._bedYOffset)
		self.form.doubleSpinBox_4.valueChanged.connect(self._bedXSize)
		self.form.doubleSpinBox_5.valueChanged.connect(self._bedYSize)

	def accept(self):
		makePrintBedGrp()
		FreeCADGui.Control.closeDialog()

	def reject(self):
		FreeCADGui.Control.closeDialog()

	def getStandardButtons(self):
		return int(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)

	def _machineXStroke(self, val):
		writeSetting("machinex", val)

	def _machineYStroke(self, val):
		writeSetting("machiney", val)

	def _machineZStroke(self, val):
		writeSetting("machinez", val)

	def _bedXOffset(self, val):
		writeSetting("offsetx", val)

	def _bedYOffset(self, val):
		writeSetting("offsety", val)

	def _bedXSize(self, val):
		writeSetting("bedx", val)

	def _bedYSize(self, val):
		writeSetting("bedy", val)

def readSetting(key):
	global defaultVals
	grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/3DPrinting/MachineDef")
	val = grp.GetFloat(key, defaultVals[key])
	FreeCAD.Console.PrintMessage("Reading Key: " + key + " Value: " + str(val) + "\n")
	return val

def writeSetting(key, val):
	grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/3DPrinting/MachineDef")
	FreeCAD.Console.PrintMessage("Setting " + key + " to " + str(val) + '\n')
	grp.SetFloat(key, val)

# Run as macro
#panel=PrintBedTaskPanel()
#FreeCADGui.Control.showDialog(panel)
