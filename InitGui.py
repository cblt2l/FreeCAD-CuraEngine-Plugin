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

class TDPrinting ( Workbench ):
	"Workbench for 3D Printers"
	Icon = """
			/* XPM */
			static const char *test_icon[]={
			"16 16 2 1",
			"a c #000000",
			". c None",
			"................",
			"..############..",
			"..############..",
			"..###......###..",
			"..###......###..",
			"..###......###..",
			"..############..",
			"..############..",
			"..####..........",
			"..####..........",
			"..####..........",
			"..####..........",
			"..####..........",
			"..####..........",
			"................",
			"................"};
			"""
	MenuText = "3D Printing"
	ToolTip = "Workbench for 3D Printing"

        def GetClassName(self):
               return "Gui::PythonWorkbench"

	def Initialize(self):
		#import myModule1, myModule2
		import Commands
		list = ["createMachineDef", "sliceCuraEngine"]
		self.appendToolbar("3D Printing", list)
		self.appendMenu("3D Printing", list)
		self.appendCommandbar("PyModuleCommands",list)
		Log ("Loading MyModule... done\n")

	def Activated(self):
               # do something here if needed...
		Msg ("MyWorkbench.Activated()\n")

	def Deactivated(self):
               # do something here if needed...
		Msg ("MyWorkbench.Deactivated()\n")

FreeCADGui.addWorkbench(TDPrinting)
