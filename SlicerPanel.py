import FreeCAD, Mesh
import os,sys,string
from FreeCAD import Console
from SliceVars import *
from PySide.QtGui import QMessageBox
from subprocess import call
from math import fabs

# TODO
# denity = 0 and 100 solid bottom & top layers
# save settings internally checkbox

if FreeCAD.GuiUp:
	import FreeCADGui
	from FreeCADGui import PySideUic as uic
	from PySide import QtCore, QtGui

__title__="CuraEngine Slicer Plugin"
__author__ = "cblt2l"
__url__ = "http://www.freecadweb.org"

class SlicerPanel:
	'''Slicer Settings Panel'''
	def __init__(self):
		# Get the macro directory. The qt uic form is loaded from here.
		self.macroDir = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Macro").GetString("MacroPath")

		# Load the qt uic form. It _must_ be in the macro dir
		form_class, base_class = uic.loadUiType(self.macroDir + "/Slicer.ui")
		self.formUi = form_class()
		self.form = QtGui.QWidget()
		self.formUi.setupUi(self.form)

		# Set the Default Values
		self.Vars = SliceDef()
		
		# Tab 1
		#self.initSetting(self.formUi.xxxxx, "", self.xxxx)
		#self.initMisc(self.formUi.xxxxx, "", self.xxxx)
		self.formUi.input_1_curapath.setText(self.Vars.readMisc("CuraPath"))
		self.initMisc(self.formUi.input_1_NOZDIA, "NozzleDiameter", self._nozzleDiameter)

		self.initSetting(self.formUi.input_2_FILDIA, "filamentDiameter", self._filamentDiameter)

		self.initSetting(self.formUi.input_3_POSX, "posx", self._posx)
		self.initSetting(self.formUi.input_4_POSY, "posy", self._posy)
		self.initSetting(self.formUi.input_5_POSZ, "objectSink", self._objectSink)

		self.initSetting(self.formUi.input_0_FLH, "initialLayerThickness", self._initialLayerThickness)
		self.initSetting(self.formUi.input_1_LH, "layerThickness", self._layerThickness)
		self.initSetting(self.formUi.input_2_PS, "insetCount", self._insetCount)
		self.initSetting(self.formUi.input_3_SBL, "downSkinCount", self._downSkinCount)
		self.initSetting(self.formUi.input_4_STL, "upSkinCount", self._upSkinCount)
		self.initMisc(self.formUi.input_5_DN, "InfillDensity", self._InfillDensity)
		self.initSetting(self.formUi.input_6_EF, "filamentFlow", self._filamentFlow)
		self.initSetting(self.formUi.input_1_LFR, "printSpeed", self._printSpeed)
		self.initSetting(self.formUi.input_2_RFR, "moveSpeed", self._moveSpeed)
		self.initSetting(self.formUi.input_3_IFR, "infillSpeed", self._infillSpeed)
		self.initSetting(self.formUi.input_4_FLFR, "initialLayerSpeed", self._initialLayerSpeed)
		self.initSetting(self.formUi.input_5_MLT, "minimalLayerTime", self._minimalLayerTime)

		self.initMisc(self.formUi.input_1_NT, "NozzleTemp", self._NozzleTemp)
		self.initMisc(self.formUi.input_2_BT, "BedTemp", self._BedTemp)

		# Set fan
		if not self.Vars.readMisc("FANMODE"):
			self.formUi.Group_0_EnableFan.setChecked(False)
		self.initSetting(self.formUi.input_1_MinFS, "fanSpeedMin", self._fanSpeedMin)
		self.initSetting(self.formUi.input_2_MaxFS, "fanSpeedMax", self._fanSpeedMax)
		self.formUi.slider_1_MinFS.setValue(self.Vars.readSetting("fanSpeedMin"))
		self.formUi.slider_2_MaxFS.setValue(self.Vars.readSetting("fanSpeedMax"))
		self.initSetting(self.formUi.input_1_MSAH, "fanFullOnLayerNr", self._fanFullOnLayerNr)
		# Set retract
		if not self.Vars.readMisc("RETRACTMODE"):
			self.formUi.Group_1_EnableExtruderRetract.setChecked(False)
		self.initSetting(self.formUi.input_1_ERA, "retractionAmount", self._retractionAmount)
		self.initSetting(self.formUi.input_2_ERFR, "retractionSpeed", self._retractionSpeed)
		self.initSetting(self.formUi.input_3_ERMD, "retractionMinimalDistance", self._retractionMinimalDistance)
		self.initSetting(self.formUi.input_4_ERME, "minimalExtrusionBeforeRetraction", self._minimalExtrusionBeforeRetraction)
		# Set skirt
		if not self.Vars.readMisc("SKIRTMODE"):
			self.formUi.Group_2_EnableSkirt.setChecked(False)
		self.initSetting(self.formUi.input_1_DIST, "skirtDistance", self._skirtDistance)
		self.initSetting(self.formUi.input_2_LC, "skirtLineCount", self._skirtLineCount)
		self.initSetting(self.formUi.input_3_ML, "skirtMinLength", self._skirtMinLength)
		# Set support
		if not self.Vars.readMisc("SUPPORTMODE"):
			self.formUi.Group_3_EnableSupport.setChecked(False)
		if self.Vars.readSetting("supportEverywhere"):
			self.formUi.radioButton_2_EE.setChecked(True)
		else:
			self.formUi.radioButton_1_ETB.setChecked(True)
		self.initMisc(self.formUi.input_0_SD, "SupportDensity", self._SupportDensity)
		self.initSetting(self.formUi.input_1_SXYD, "supportXYDistance", self._supportXYDistance)
		self.initSetting(self.formUi.input_2_SZD, "supportZDistance", self._supportZDistance)
		# Set raft
		if not self.Vars.readMisc("RAFTMODE"):
			self.formUi.Group_4_EnableRaft.setChecked(False)
		self.initSetting(self.formUi.input_1_RMG, "raftMargin", self._raftMargin)
		self.initSetting(self.formUi.input_2_RLS, "raftLineSpacing", self._raftLineSpacing)
		self.initSetting(self.formUi.input_3_RBT, "raftBaseThickness", self._raftBaseThickness)
		self.initSetting(self.formUi.input_4_RBLW, "raftBaseLinewidth", self._raftBaseLinewidth)
		self.initSetting(self.formUi.input_5_RIT, "raftInterfaceThickness", self._raftInterfaceThickness)
		self.initSetting(self.formUi.input_6_RILW, "raftInterfaceLinewidth", self._raftInterfaceLinewidth)
		# Tab3
		self.formUi.textEdit_startcode.append(self.Vars.readSetting("startCode"))
		self.formUi.textEdit_endcode.append(self.Vars.readSetting("endCode"))

		#Connect Signals and Slots
		# Tab 1
		#self.formUi.xxxxxxx.stateChanged.connect(self.xxxx)
		self.formUi.button_1_filediag.clicked.connect(self.chooseOutputDir)
		self.formUi.input_1_curapath.textChanged.connect(self.curaPathChange)
		# Tab 2
		self.formUi.Group_0_EnableFan.clicked.connect(self._fanMode)
		self.formUi.slider_1_MinFS.valueChanged.connect(self.formUi.input_1_MinFS.setValue)
		self.formUi.slider_2_MaxFS.valueChanged.connect(self.formUi.input_2_MaxFS.setValue)
		self.formUi.input_1_MinFS.valueChanged.connect(self.formUi.slider_1_MinFS.setValue)
		self.formUi.input_2_MaxFS.valueChanged.connect(self.formUi.slider_2_MaxFS.setValue)
		self.formUi.Group_1_EnableExtruderRetract.clicked.connect(self._retractionMode)
		self.formUi.Group_2_EnableSkirt.clicked.connect(self._skirtMode)
		self.formUi.Group_3_EnableSupport.clicked.connect(self._supportMode)
		self.formUi.radioButton_1_ETB.clicked.connect(self._supportTouchingBed)
		self.formUi.radioButton_2_EE.clicked.connect(self._supportEverywhere)
		self.formUi.Group_4_EnableRaft.clicked.connect(self._raftMode)
		# Tab 3
		self.formUi.textEdit_startcode.textChanged.connect(self._startCode)
		self.formUi.textEdit_endcode.textChanged.connect(self._endCode)
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
			self.formUi.input_1_curapath.setText(fileName)

	def curaPathChange(self, _text):
		self.Vars.writeMisc("CuraPath", _text)

	def errorBox(self, dialogText):
		msgBox = QMessageBox()
		msgBox.setText(dialogText)
		msgBox.exec_()

	def sliceParts(self, _curaBin, _stlParts):
		gcodeFile = _stlParts.replace(".stl", ".gcode")
		logFile = _stlParts.replace(".stl", ".log")
		_cmdList = self.getSettings()
		_cmdList.insert(0, _curaBin)
		_cmdList.append("-o")
		_cmdList.append(gcodeFile)
		_cmdList.append(_stlParts)
		f = open(logFile, 'w')
		f.write("#############CURA PLUGIN SETTINGS#############\n")
		for index in _cmdList:
			f.write(index + '\n')
			Console.PrintMessage(index + '\n')
		f.write("###############END CURA SETTINGS##############\n")
		retVal = call(_cmdList, stdout=f)
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
		#_tmpDic = self.Vars.settingsDict.copy()
		_tmpDic = self.Vars.exportSettings()
		# Certain parameters need to be scaled up X1000 when passed to CuraEngine
		scaleDic = dict.fromkeys(["filamentDiameter", "posx", "posy", "initialLayerThickness", "layerThickness", "extrusionWidth", "skirtDistance", "sparseInfillLineDistance",
								"supportXYDistance", "supportZDistance", "retractionAmount", "retractionAmountExtruderSwitch", "retractionMinimalDistance", 
								"minimalExtrusionBeforeRetraction", "raftMargin", "raftLineSpacing"], 1000)
		# Certain parameters are disabled in GUI and need to be set to zero
		if not self.Vars.readMisc("FANMODE"):
#		if not self.formUi.Group_0_EnableFan.isChecked():
			_tmpDic.update(dict.fromkeys(["fanSpeedMin", "fanSpeedMax", "fanFullOnLayerNr"], 0))
		if not self.Vars.readMisc("RETRACTMODE"):
			_tmpDic.update(dict.fromkeys(["retractionAmount", "retractionSpeed", "retractionAmountExtruderSwitch", "retractionMinimalDistance",
										"minimalExtrusionBeforeRetraction"], 0))
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

		for key, val in _tmpDic.items():
		#for key in _tmpDic:
			#val = self.Vars.readSetting(key)
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
	def _posx(self, val):
		self.Vars.writeSetting("posx", val)
	def _posy(self, val):
		self.Vars.writeSetting("posy", val)
	def _objectSink(self, val):
		self.Vars.writeSetting("objectSink", fabs(val))
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
		state = self.formUi.Group_0_EnableFan.isChecked()
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
		state = self.formUi.Group_1_EnableExtruderRetract.isChecked()
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
	# Skirt slots
	def _skirtMode(self):
		state = self.formUi.Group_2_EnableSkirt.isChecked()
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
		state = self.formUi.Group_3_EnableSupport.isChecked()
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
		state = self.formUi.Group_4_EnableRaft.isChecked()
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
	# Start/end gcode slots
	def _startCode(self):
		#obj = self.sender() <-- Does not work???
		txt = self.formUi.textEdit_startcode.toPlainText()
		self.Vars.writeSetting("startCode", txt)
	def _endCode(self):
		#obj = self.sender() <-- Does not work???
		txt = self.formUi.textEdit_endcode.toPlainText()
		self.Vars.writeSetting("endCode", txt)
#	def _setXYPos(self):
#		global cmdList
#		App.ActiveDocument.ActiveObject.Placement.Base.x
#		App.ActiveDocument.ActiveObject.Placement.Base.y


panel=SlicerPanel()
FreeCADGui.Control.showDialog(panel)
