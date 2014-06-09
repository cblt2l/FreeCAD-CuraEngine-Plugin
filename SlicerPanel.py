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

import FreeCAD, Mesh
import os,sys,string
from FreeCAD import Console
from SliceVars import *
from PySide.QtGui import QMessageBox
from subprocess import call
from math import fabs

if FreeCAD.GuiUp:
	import FreeCADGui
	from FreeCADGui import PySideUic as uic
	from PySide import QtCore, QtGui
	gui = True

__title__="CuraEngine Slicer Plugin"
__author__ = "cblt2l"
__url__ = "http://www.freecadweb.org"

class SlicerPanel:
	'''Slicer Settings Panel'''
	def __init__(self):
		# Get the user's home directory.
		self.homeDir = os.path.expanduser("~")

		# Load the qt uic form. It _must_ be in ~/.FreeCAD/Mod/FreeCAD-CuraEngine-Plugin, Perhaps there is a better way...
		self.form = uic.loadUi(self.homeDir + "/.FreeCAD/Mod/FreeCAD-CuraEngine-Plugin/Slicer.ui")

		# Set the Default Values
		self.Vars = SliceDef()
		
		# Tab 1
		self.form.input_1_curapath.setText(self.Vars.readMisc("CuraPath"))
		self.initMisc(self.form.input_1_NOZDIA, "NozzleDiameter", self._nozzleDiameter)

		self.initSetting(self.form.input_2_FILDIA, "filamentDiameter", self._filamentDiameter)

		if not self.Vars.readMisc("OPPMODE"):
			self.form.Group_5_OPP.setChecked(False)
		self.initSetting(self.form.input_1_POSX, "posx", self._posx)
		self.initSetting(self.form.input_2_POSY, "posy", self._posy)
		self.initSetting(self.form.input_3_POSZ, "objectSink", self._objectSink)

		self.initSetting(self.form.input_0_FLH, "initialLayerThickness", self._initialLayerThickness)
		self.initSetting(self.form.input_1_LH, "layerThickness", self._layerThickness)
		self.initSetting(self.form.input_2_PS, "insetCount", self._insetCount)
		self.initSetting(self.form.input_3_SBL, "downSkinCount", self._downSkinCount)
		self.initSetting(self.form.input_4_STL, "upSkinCount", self._upSkinCount)
		self.initMisc(self.form.input_5_DN, "InfillDensity", self._InfillDensity)
		self.initSetting(self.form.input_6_EF, "filamentFlow", self._filamentFlow)
		self.initSetting(self.form.input_1_LFR, "printSpeed", self._printSpeed)
		# Set inset speeds here temporarily until added to GUI############################
		self.Vars.writeSetting("inset0Speed", self.Vars.readSetting("printSpeed"))
		self.Vars.writeSetting("insetXSpeed", self.Vars.readSetting("printSpeed"))
		##################################################################################
		self.initSetting(self.form.input_2_RFR, "moveSpeed", self._moveSpeed)
		self.initSetting(self.form.input_3_IFR, "infillSpeed", self._infillSpeed)
		self.initSetting(self.form.input_4_FLFR, "initialLayerSpeed", self._initialLayerSpeed)
		self.initSetting(self.form.input_5_MLT, "minimalLayerTime", self._minimalLayerTime)

		self.initMisc(self.form.input_1_NT, "NozzleTemp", self._NozzleTemp)
		self.initMisc(self.form.input_2_BT, "BedTemp", self._BedTemp)

		# Set fan
		if not self.Vars.readMisc("FANMODE"):
			self.form.Group_0_EnableFan.setChecked(False)
		self.initSetting(self.form.input_1_MinFS, "fanSpeedMin", self._fanSpeedMin)
		self.initSetting(self.form.input_2_MaxFS, "fanSpeedMax", self._fanSpeedMax)
		self.form.slider_1_MinFS.setValue(self.Vars.readSetting("fanSpeedMin"))
		self.form.slider_2_MaxFS.setValue(self.Vars.readSetting("fanSpeedMax"))
		self.initSetting(self.form.input_1_MSAH, "fanFullOnLayerNr", self._fanFullOnLayerNr)
		# Set retract
		if not self.Vars.readMisc("RETRACTMODE"):
			self.form.Group_1_EnableExtruderRetract.setChecked(False)
		self.initSetting(self.form.input_1_ERA, "retractionAmount", self._retractionAmount)
		self.initSetting(self.form.input_2_ERFR, "retractionSpeed", self._retractionSpeed)
		self.initSetting(self.form.input_3_ERMD, "retractionMinimalDistance", self._retractionMinimalDistance)
		self.initSetting(self.form.input_4_ERME, "minimalExtrusionBeforeRetraction", self._minimalExtrusionBeforeRetraction)
		if self.Vars.readSetting("enableCombing"):
			self.form.checkbox_1_EC.setChecked(True)
		else:
			self.form.checkbox_1_EC.setChecked(False)
		# Set skirt
		if not self.Vars.readMisc("SKIRTMODE"):
			self.form.Group_2_EnableSkirt.setChecked(False)
		self.initSetting(self.form.input_1_DIST, "skirtDistance", self._skirtDistance)
		self.initSetting(self.form.input_2_LC, "skirtLineCount", self._skirtLineCount)
		self.initSetting(self.form.input_3_ML, "skirtMinLength", self._skirtMinLength)
		# Set support
		if not self.Vars.readMisc("SUPPORTMODE"):
			self.form.Group_3_EnableSupport.setChecked(False)
		if self.Vars.readSetting("supportEverywhere"):
			self.form.radioButton_2_EE.setChecked(True)
		else:
			self.form.radioButton_1_ETB.setChecked(True)
		self.initMisc(self.form.input_0_SD, "SupportDensity", self._SupportDensity)
		self.initSetting(self.form.input_1_SXYD, "supportXYDistance", self._supportXYDistance)
		self.initSetting(self.form.input_2_SZD, "supportZDistance", self._supportZDistance)
		# Set raft
		if not self.Vars.readMisc("RAFTMODE"):
			self.form.Group_4_EnableRaft.setChecked(False)
		self.initSetting(self.form.input_1_RMG, "raftMargin", self._raftMargin)
		self.initSetting(self.form.input_2_RLS, "raftLineSpacing", self._raftLineSpacing)
		self.initSetting(self.form.input_3_RBT, "raftBaseThickness", self._raftBaseThickness)
		self.initSetting(self.form.input_4_RBLW, "raftBaseLinewidth", self._raftBaseLinewidth)
		self.initSetting(self.form.input_5_RIT, "raftInterfaceThickness", self._raftInterfaceThickness)
		self.initSetting(self.form.input_6_RILW, "raftInterfaceLinewidth", self._raftInterfaceLinewidth)
		# Tab3
		if self.Vars.readSetting("spiralizeMode"):
			self.form.checkbox_1_SPI.setChecked(True)
		else:
			self.form.checkbox_1_SPI.setChecked(False)
		self.form.textEdit_startcode.append(self.Vars.readSetting("startCode"))
		self.form.textEdit_endcode.append(self.Vars.readSetting("endCode"))

		#Connect Signals and Slots
		# Tab 1
		self.form.button_1_filediag.clicked.connect(self.chooseOutputDir)
		self.form.input_1_curapath.textChanged.connect(self.curaPathChange)
		self.form.button_1_ES.clicked.connect(self.exportSettingsFile)
		self.form.button_2_IS.clicked.connect(self.importSettingsFile)
		# Tab 2
		self.form.Group_0_EnableFan.clicked.connect(self._fanMode)
		self.form.slider_1_MinFS.valueChanged.connect(self.form.input_1_MinFS.setValue)
		self.form.slider_2_MaxFS.valueChanged.connect(self.form.input_2_MaxFS.setValue)
		self.form.input_1_MinFS.valueChanged.connect(self.form.slider_1_MinFS.setValue)
		self.form.input_2_MaxFS.valueChanged.connect(self.form.slider_2_MaxFS.setValue)
		self.form.Group_1_EnableExtruderRetract.clicked.connect(self._retractionMode)
		self.form.checkbox_1_EC.clicked.connect(self._enableCombing)
		self.form.Group_2_EnableSkirt.clicked.connect(self._skirtMode)
		self.form.Group_3_EnableSupport.clicked.connect(self._supportMode)
		self.form.radioButton_1_ETB.clicked.connect(self._supportTouchingBed)
		self.form.radioButton_2_EE.clicked.connect(self._supportEverywhere)
		self.form.Group_4_EnableRaft.clicked.connect(self._raftMode)
		self.form.Group_5_OPP.clicked.connect(self._oppMode)
		# Tab 3
		self.form.checkbox_1_SPI.clicked.connect(self._spiralize)
		self.form.textEdit_startcode.textChanged.connect(self._startCode)
		self.form.textEdit_endcode.textChanged.connect(self._endCode)
		##self.update()

	def accept(self):
		# Verify the active document
		actDoc = FreeCAD.ActiveDocument
		if not actDoc:
			self.errorBox("No Open Document\n")
			return False
		Console.PrintMessage("Accepted" + '\n')
		docName = actDoc.Label
		docDir = FreeCAD.ActiveDocument.FileName.replace(docName + ".fcstd", "")
		partList = FreeCADGui.Selection.getSelection()
		# Verify at least one part is selected
		if not partList:
			self.errorBox("Select at Least One Part Object")
			return False
		stlParts = docDir + docName + ".stl"
		Mesh.export(partList, stlParts)
		self.pos = self.GetXYZPos(partList)
		#Console.PrintMessage(str(self.pos) + '\n')
		retVal = self.sliceParts(self.Vars.readMisc("CuraPath"), stlParts)
		if retVal is True:
			self.errorBox("Slice Failed!\n Check log file\n" + logFile)
			return False
		else:
			return True

	def reject(self):
		FreeCADGui.Control.closeDialog()
		Console.PrintMessage("Rejected" + '\n')
		return True

	def getStandardButtons(self):
		return int(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)

	def chooseOutputDir(self):
		print "chooseOutputDir"
		Console.PrintMessage("Choose" + '\n')
		fileName, _ = QtGui.QFileDialog.getOpenFileName(None, 'Locate CuraEngine', self.Vars.readMisc("CuraPath"))
		if(fileName):
			Console.PrintMessage("Filename: " + fileName + '\n')
			self.form.input_1_curapath.setText(fileName)

	def curaPathChange(self, _text):
		self.Vars.writeMisc("CuraPath", _text)

	def exportSettingsFile(self):
		sett = self.Vars.readMisc("SettingsPath")
		fileName, _ = QtGui.QFileDialog.getSaveFileName(None, 'Save Settings File', self.Vars.readMisc("SettingsPath"))
		if(fileName):
			self.Vars.writeMisc("SettingsPath", fileName)
			self.Vars.writeSettingsFile(fileName)
			Console.PrintMessage("SettingsPath=" + self.Vars.readMisc("SettingsPath") + '\n')

	def importSettingsFile(self):
		sett= self.Vars.readMisc("SettingsPath")
		#Console.PrintMessage(sett + '\n')
		fileName, _ = QtGui.QFileDialog.getOpenFileName(None, 'Select Settings File', sett, "CuraEngine Settings File .ces (*.ces)")
		Console.PrintMessage(fileName + '\n')
		if(fileName):
			self.Vars.writeMisc("SettingsPath", fileName)
			self.Vars.importSettingsFile(fileName)
			self.errorBox("Import Complete. Please Restart Macro")

	def errorBox(self, dialogText):
		msgBox = QMessageBox()
		msgBox.setText(dialogText)
		msgBox.exec_()

	def GetXYZPos(self, partsList):
		if len(partsList) is 1:
			bb = partsList[0].Shape.BoundBox
		else:
			# Create a temporary fusion of the selected parts and get
			# the bounding box to determine the center coordinates
			f = FreeCAD.activeDocument().addObject("Part::MultiFuse","Fusion")
			f.Shapes = partsList
			# Must recompute first to get correct boundbox
			FreeCAD.ActiveDocument.recompute()
			bb = f.Shape.BoundBox
			# Delete the temp fusion
			FreeCAD.ActiveDocument.removeObject(f.Name)
		c = bb.Center
		# We want the Minimum Z height. Anything below 0 is translated to "objectSink" setting
		c.z = bb.ZMin
		#Unhide all of the selected parts that were hidden when making the fusion
		for p in partsList:
			p.ViewObject.Visibility=True
		return c

	def sliceParts(self, _curaBin, _stlParts):
		gcodeFile = _stlParts.replace(".stl", ".gcode")
		logFile = _stlParts.replace(".stl", ".log")
		_cmdList = self.getSettings()
		_cmdList.insert(0, _curaBin)
		_cmdList.insert(1, "-v")
		_cmdList.append("-o")
		_cmdList.append(gcodeFile)
		_cmdList.append(_stlParts)
		f = open(logFile, 'w')
		f.write("#############CURA PLUGIN SETTINGS#############\n")
		for index in _cmdList:
			f.write(index + '\n')
			Console.PrintMessage(index + '\n')
		f.write("###############END CURA SETTINGS##############\n")
		retVal = call(_cmdList, stderr=f)
		f.close()
		return retVal

	def initSetting(self, widget, key, handel):
		val = self.Vars.readSetting(key)
		widget.setValue(val)
		widget.valueChanged.connect(handel)

	def initMisc(self, widget, key, handel):
		val = self.Vars.readMisc(key)
		widget.setValue(val)
		widget.valueChanged.connect(handel)

	def getSettings(self):
		_cmdList = []
		_tmpDic = self.Vars.copySettings()

		# Certain parameters need to be scaled up X1000 when passed to CuraEngine
		scaleDic = dict.fromkeys(["filamentDiameter", "posx", "posy", "initialLayerThickness", "layerThickness", "extrusionWidth", "skirtDistance", "sparseInfillLineDistance",
								"supportXYDistance", "supportZDistance", "retractionAmount", "retractionAmountExtruderSwitch", "retractionMinimalDistance", 
								"minimalExtrusionBeforeRetraction", "raftMargin", "raftLineSpacing"], 1000)

		# Certain parameters are disabled in GUI and need to be set to zero
		if not self.Vars.readMisc("FANMODE"):
			_tmpDic.update(dict.fromkeys(["fanSpeedMin", "fanSpeedMax", "fanFullOnLayerNr"], 0))
		if not self.Vars.readMisc("RETRACTMODE"):
			_tmpDic.update(dict.fromkeys(["retractionAmount", "retractionSpeed", "retractionAmountExtruderSwitch", "retractionMinimalDistance",
										"minimalExtrusionBeforeRetraction", "enableCombing"], 0))
		if not self.Vars.readMisc("SKIRTMODE"):
			_tmpDic.update(dict.fromkeys(["skirtDistance", "skirtLineCount", "skirtMinLength"], 0))
		if not self.Vars.readMisc("SUPPORTMODE"):
			_tmpDic.update(dict.fromkeys(["supportEverywhere", "supportLineDistance", "supportXYDistance", "supportZDistance"], 0))
		if not self.Vars.readMisc("RAFTMODE"):
			_tmpDic.update(dict.fromkeys(["raftMargin", "raftLineSpacing", "raftBaseThickness", "raftBaseLinewidth",
										 "raftInterfaceThickness", "raftInterfaceLinewidth"], 0))

		# Add the Nozzle & Bed temps to the startcode. Idealy this should be done at postprocessing stage
		startcode = _tmpDic["startCode"]
		startcode = startcode.replace("{nozzleTemp}", str(self.Vars.readMisc("NozzleTemp")))
		startcode = startcode.replace("{bedTemp}", str(self.Vars.readMisc("BedTemp")))
		_tmpDic["startCode"] = startcode

		# Set the part placement
		if not self.Vars.readMisc("OPPMODE"):
			_tmpDic["posx"] = self.pos.x
			_tmpDic["posy"] = self.pos.y
			_tmpDic["objectSink"] = self.pos.z

		for key, val in _tmpDic.items():
			mult = scaleDic.get(key)
			if not mult:
				mult = 1
			_cmdList.append("-s")
			_cmdList.append(key + "="  + str(val * mult))
		return _cmdList

	def _setLineDistance(self, param, val):
		if param is "extrusionWidth":
			_infillden = self.Vars.readMisc("InfillDensity")
			_supportden = self.Vars.readMisc("SupportDensity")
			self.Vars.writeSetting("extrusionWidth", val)
			self.Vars.writeSetting("sparseInfillLineDistance", val * 100 / _infillden)
			self.Vars.writeSetting("supportLineDistance", val * 100 / _supportden)
		elif param is "sparseInfillLineDistance":
			_extwidth = self.Vars.readSetting("extrusionWidth")
			self.Vars.writeSetting("sparseInfillLineDistance", _extwidth * 100 / val)
		elif param is "supportLineDistance":
			_extwidth = self.Vars.readSetting("extrusionWidth")
			self.Vars.writeSetting("supportLineDistance", _extwidth * 100 / val)

	# Print setting slots
	def _nozzleDiameter(self, val):
		self.Vars.writeMisc("NozzleDiameter", val)
		self._setLineDistance("extrusionWidth", val)
	def _filamentDiameter(self, val):
		self.Vars.writeSetting("filamentDiameter", val)
	def _initialLayerThickness(self, val):
		self.Vars.writeSetting("initialLayerThickness", val)
	def _layerThickness(self, val):
		self.Vars.writeSetting("layerThickness", val)
	def _insetCount(self, val):
		self.Vars.writeSetting("insetCount", val)
	def _downSkinCount(self, val):
		self.Vars.writeSetting("downSkinCount", val)
	def _upSkinCount(self, val):
		self.Vars.writeSetting("upSkinCount", val)
	def _InfillDensity(self, val):
		self.Vars.writeMisc("InfillDensity", val)
		if val == 0:
			self.Vars.writeSetting("sparseInfillLineDistance", -1)
		#elif val == 100:
		#	self.Vars.writeSetting("sparseInfillLineDistance", 100)
		else:
			self._setLineDistance("sparseInfillLineDistance", val)
	def _filamentFlow(self, val):
		self.Vars.writeSetting("filamentFlow", val)
	# Feedrate slots
	def _printSpeed(self, val):
		self.Vars.writeSetting("printSpeed", val)
		# Set inset speeds here for now
		self.Vars.writeSetting("inset0Speed", val)
		self.Vars.writeSetting("insetXSpeed", val)
	def _moveSpeed(self, val):
		self.Vars.writeSetting("moveSpeed", val)
	def _infillSpeed(self, val):
		self.Vars.writeSetting("infillSpeed", val)
	def _initialLayerSpeed(self, val):
		self.Vars.writeSetting("initialLayerSpeed", val)
	def _minimalLayerTime(self, val):
		self.Vars.writeSetting("minimalLayerTime", val)
	# Temperature Settings
	def _NozzleTemp(self, val):
		self.Vars.writeMisc("NozzleTemp", val)
	def _BedTemp(self, val):
		self.Vars.writeMisc("BedTemp", val)
	# Fan slots
	def _fanMode(self):
		# https://bugreports.qt-project.org/browse/PYSIDE-104
		state = self.form.Group_0_EnableFan.isChecked()
		if state:
			self.Vars.writeMisc("FANMODE", True)
		else:
			self.Vars.writeMisc("FANMODE", False)
	def _fanSpeedMin(self, val):
		self.Vars.writeSetting("fanSpeedMin", val)
	def _fanSpeedMax(self, val):
		self.Vars.writeSetting("fanSpeedMax", val)
	def _fanFullOnLayerNr(self, val):
		self.Vars.writeSetting("fanFullOnLayerNr", val)
	# Retraction slots
	def _retractionMode(self):
		state = self.form.Group_1_EnableExtruderRetract.isChecked()
		if state:
			self.Vars.writeMisc("RETRACTMODE", True)
		else:
			self.Vars.writeMisc("RETRACTMODE", False)
	def _retractionAmount(self, val):
		self.Vars.writeSetting("retractionAmount", val)
	def _retractionSpeed(self, val):
		self.Vars.writeSetting("retractionSpeed", val)
	def _retractionAmountExtruderSwitch(self, val):
		self.Vars.writeSetting("retractionAmountExtruderSwitch", val)
	def _retractionMinimalDistance(self, val):
		self.Vars.writeSetting("retractionMinimalDistance", val)
	def _minimalExtrusionBeforeRetraction(self, val):
		self.Vars.writeSetting("minimalExtrusionBeforeRetraction", val)
	def _enableCombing(self):
		state = self.form.checkbox_1_EC.isChecked()
		if state:
			self.Vars.writeSetting("enableCombing", 1)
		else:
			self.Vars.writeSetting("enableCombing", 0)
	# Skirt slots
	def _skirtMode(self):
		state = self.form.Group_2_EnableSkirt.isChecked()
		if state:
			self.Vars.writeMisc("SKIRTMODE", True)
		else:
			self.Vars.writeMisc("SKIRTMODE", False)
	def _skirtDistance(self, val):
		self.Vars.writeSetting("skirtDistance", val)
	def _skirtLineCount(self, val):
		self.Vars.writeSetting("skirtLineCount", val)
	def _skirtMinLength(self, val):
		self.Vars.writeSetting("skirtMinLength", val)
	# Support slots
	def _supportMode(self):
		state = self.form.Group_3_EnableSupport.isChecked()
		if state:
			self.Vars.writeMisc("SUPPORTMODE", True)
			self.Vars.writeSetting("supportAngle", 60)
		else:
			self.Vars.writeMisc("SUPPORTMODE", False)
			self.Vars.writeSetting("supportAngle", -1)
	def _supportTouchingBed(self):
		self.Vars.writeSetting("supportEverywhere", 0)
	def _supportEverywhere(self):
		self.Vars.writeSetting("supportEverywhere", 1)
	def _SupportDensity(self, val):
		self.Vars.writeMisc("SupportDensity", val)
		if val == 0:
			self.Vars.writeSetting("supportLineDistance", -1)
		else:
			self._setLineDistance("supportLineDistance", val)
	#def _supportExtruder(self, val):
	#	self.Vars.writeSetting("supportExtruder", val)
	def _supportXYDistance(self, val):
		self.Vars.writeSetting("supportXYDistance", val)
	def _supportZDistance(self, val):
		self.Vars.writeSetting("supportZDistance", val)
	# Raft slots
	def _raftMode(self):
		state = self.form.Group_4_EnableRaft.isChecked()
		if state:
			self.Vars.writeMisc("RAFTMODE", True)
		else:
			self.Vars.writeMisc("RAFTMODE", False)
	def _raftMargin(self, val):
		self.Vars.writeSetting("raftMargin", val)
	def _raftLineSpacing(self, val):
		self.Vars.writeSetting("raftLineSpacing", val)
	def _raftBaseThickness(self, val):
		self.Vars.writeSetting("raftBaseThickness", val)
	def _raftBaseLinewidth(self, val):
		self.Vars.writeSetting("raftBaseLinewidth", val)
	def _raftInterfaceThickness(self, val):
		self.Vars.writeSetting("raftInterfaceThickness", val)
	def _raftInterfaceLinewidth(self, val):
		self.Vars.writeSetting("raftInterfaceLinewidth", val)
	# Override Part Position slots
	def _oppMode(self):
		state = self.form.Group_5_OPP.isChecked()
		if state:
			self.Vars.writeMisc("OPPMODE", True)
		else:
			self.Vars.writeMisc("OPPMODE", False)
	def _posx(self, val):
		self.Vars.writeSetting("posx", val)
	def _posy(self, val):
		self.Vars.writeSetting("posy", val)
	def _objectSink(self, val):
		self.Vars.writeSetting("objectSink", fabs(val))
	# Start/end gcode slots
	def _spiralize(self):
		state = self.form.checkbox_1_SPI.isChecked()
		if state:
			self.Vars.writeSetting("spiralizeMode", 1)
		else:
			self.Vars.writeSetting("spiralizeMode", 0)
	def _startCode(self):
		#obj = self.sender() <-- Does not work???
		txt = self.form.textEdit_startcode.toPlainText()
		self.Vars.writeSetting("startCode", txt)
	def _endCode(self):
		#obj = self.sender() <-- Does not work???
		txt = self.form.textEdit_endcode.toPlainText()
		self.Vars.writeSetting("endCode", txt)
#	def _setXYPos(self):
#		global cmdList
#		App.ActiveDocument.ActiveObject.Placement.Base.x
#		App.ActiveDocument.ActiveObject.Placement.Base.y


#panel=SlicerPanel()
#FreeCADGui.Control.showDialog(panel)
