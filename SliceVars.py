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

import FreeCAD, Part
from FreeCAD import Console
import os,sys,string

__title__="CuraEngine Slicer Plugin"
__author__ = "cblt2l"
__url__ = "http://www.freecadweb.org"

class SliceDef:
	'''Variables That Describe Machine Parameters'''
	def __init__(self):
		# Get user's home dir
		homedir = os.path.expanduser("~")
		freecaddir = homedir + "/.FreeCAD/"

		# Settings that are not CuraEngine settings. These will be replaced with a GUI at some point
		self.MiscDict = {}
		#self.MiscDict.update({"XStroke":300000, "YStroke":300000, "ZStroke":120000})
		self.MiscDict.update({"NozzleTemp":185, "BedTemp":60})
		self.MiscDict.update({"NozzleDiameter":0.5})
		self.MiscDict.update({"CuraPath":"/usr/share/cura/CuraEngine"})
		self.MiscDict.update({"POSX":100, "POSY":100, "POSZ":0})
		self.MiscDict.update({"FANMODE":False, "RETRACTMODE":False, "SKIRTMODE":False, "SUPPORTMODE":False, "RAFTMODE":False})
		self.MiscDict.update({"InfillDensity":20, "SupportDensity":20})
		self.MiscDict.update({"SettingsPath":(freecaddir + "CESettings.ces")})

		# Settings that are required by CuraEngine
		self.settingsDict = {}
		self.settingsDict.update({"filamentDiameter": 3, "initialLayerThickness": 0.3,"layerThickness": 0.1, "insetCount": 2, "downSkinCount": 6, "upSkinCount": 6, 
									"sparseInfillLineDistance": 2, "filamentFlow": 100})
		# Better Way??
		#self.settingsDict.update({"extrusionWidth": self.MiscDict["NozzleDiameter"]})
		self.settingsDict.update({"extrusionWidth": .5, "posx": 100, "posy":100, "objectSink": 0})
		self.settingsDict.update({"printSpeed": 50, "moveSpeed": 200, "infillSpeed": 50, "inset0Speed": 50, "insetXSpeed": 50, "initialLayerSpeed": 20, "minimalLayerTime":5})
		self.settingsDict.update({"fanSpeedMin": 100, "fanSpeedMax": 100, "fanFullOnLayerNr": 2})
		self.settingsDict.update({"retractionAmount": 4.5, "retractionSpeed": 45, "retractionAmountExtruderSwitch": 14.5, "retractionMinimalDistance": 1.5, 
									"minimalExtrusionBeforeRetraction": 0.1, "enableCombing": 0})
		self.settingsDict.update({"skirtDistance": 6, "skirtLineCount": 1, "skirtMinLength": 0})
		self.settingsDict.update({"supportAngle": -1, "supportEverywhere": 0,"supportLineDistance": 0, "supportExtruder": -1, "supportXYDistance": 0.7, "supportZDistance": 0.15})
		self.settingsDict.update({"raftMargin": 5, "raftLineSpacing": 1, "raftBaseThickness": 0, "raftBaseLinewidth": 0, "raftInterfaceThickness": 0, "raftInterfaceLinewidth": 0})
		self.settingsDict.update({"spiralizeMode":0})
		self.settingsDict.update({"startCode": \
		"M109 S{nozzleTemp}     ;Set Nozzle Temp and Wait\n"\
		"M190 S{bedTemp}      ;Set Bed Temp and Wait\n"\
		"G21           ;metric values\n"\
		"G90           ;absolute positioning\n"\
		"G28           ;Home\n"\
		"G1 Z15.0 F300 ;move the platform down 15mm\n"\
		"G92 E0        ;zero the extruded length\n"\
		"G1 F200 E5    ;extrude 5mm of feed stock\n"\
		"G92 E0        ;zero the extruded length again\n"})
		self.settingsDict.update({"endCode": \
		"M104 S0                     ;extruder heater off\n"\
		"M140 S0                     ;heated bed heater off (if you have it)\n"\
		"G91                         ;relative positioning\n"\
		"G1 E-1 F300                    ;retract the filament a bit before lifting the nozzle, to release some of the pressure\n"\
		"G1 Z+0.5 E-5 X-20 Y-20 F9000   ;move Z up a bit and retract filament even more\n"\
		"G28 X0 Y0                      ;move X/Y to min endstops, so the head is out of the way\n"\
		"M84                         ;steppers off\n"\
		"G90                         ;absolute positioning\n"})
		##################################################################################################

		for key, val in self.MiscDict.items():
			if not self.checkSetting(key):
				self.writeMisc(key, val)
		for key, val in self.settingsDict.items():
			if not self.checkSetting(key):
				self.writeSetting(key, val)
		#Console.PrintMessage(key + " is " + str(self.checkSetting(key)) + "\n")

	def getParamType(self, param):
		if param in ["startCode","endCode","CuraPath","SettingsPath"]:
			return "string"
		else:
			return "float"

	def checkSetting(self, key):
		grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CuraEngine")
		pt = self.getParamType(key)
		# Check to see if setting has been set in grp
		if pt is "string":
			return grp.GetString(key, "~~~~~") != "~~~~~"
		if pt is "float":
			return grp.GetFloat(key,-1e200) != -1e200

	def readSetting(self, key):
		grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CuraEngine")
		pt = self.getParamType(key)
		if pt is "string":
			return grp.GetString(key, self.settingsDict[key])
		elif pt is "float":
			return grp.GetFloat(key, self.settingsDict[key])

	def writeSetting(self, key, val):
		grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CuraEngine")
		pt = self.getParamType(key)
		if pt is "string":
			grp.SetString(key, val)
		elif pt is "float":
			grp.SetFloat(key, val)
		Console.PrintMessage("Setting " + key + " to " + str(val) + '\n')

	def readMisc(self, key):
		grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CuraEngine")
		pt = self.getParamType(key)
		if pt is "string":
			return grp.GetString(key, self.MiscDict[key])
		elif pt is "float":
			return grp.GetFloat(key, self.MiscDict[key])

	def writeMisc(self, key, val):
		grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CuraEngine")
		pt = self.getParamType(key)
		if pt is "string":
			grp.SetString(key, val)
		elif pt is "float":
			grp.SetFloat(key, val)
		Console.PrintMessage("Setting " + key + " to " + str(val) + '\n')

	def copySettings(self):
		tmpDic = {}
		for key in self.settingsDict:
			tmpDic[key] = self.readSetting(key)
		return tmpDic

	def copyMisc(self):
		tmpDic = {}
		for key in self.MiscDict:
			tmpDic[key] = self.readMisc(key)
		return tmpDic

	def writeSettingsFile(self, filename):
		grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CuraEngine")
		grp.Export(filename)


	def importSettingsFile(self, filename):
		grp = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/CuraEngine")
		grp.Import(filename)

