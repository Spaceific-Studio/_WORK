# -*- coding: utf-8 -*-
# Copyright(c) 2019, Daniel Gercak
#Classes for application form for UI of Analyse module 
#analyses e.g. energy analyses...
#resource_path: C:\_WORK\PYTHON\REVIT_API\LIB\AnalyseForm.py

import sys
import os
#import __main__
#import traceback
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

#from itertools import chain, groupby
#from RevitSelection import *
#import RevitSelection as RevitSelection
#from ListUtils import *
#import ListUtils as ListUtils
from Errors import *

import clr
#import windows forms
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Drawing
from System.Drawing import Icon, Color, Point
import System.Windows.Forms as WF
from System.Drawing import *
from System.Windows.Forms import 	Application, Button, Form, Panel, ComboBox, Label, \
									TextBox, DockStyle, AnchorStyles, Screen, TreeView, \
									TreeNode, ScrollBars, TabControl, TabPage, \
									TableLayoutPanel, TableLayoutPanelGrowStyle, SizeType, \
									RowStyle, ColumnStyle \



#scriptDirectory = os.path.dirname(__main__.__file__)
scriptDirectory = os.getcwd()
#iconFilename = os.path.join(scriptDirectory, 'Eanalyse.bmp')
#icon = Icon(iconFilename)

class MainForm(Form):
	def __init__(self, inEAnalyse):
		self.scriptDir = "\\".join(__file__.split("\\")[:-1])
		iconFilename = os.path.join(self.scriptDir, 'spaceific_64x64_sat_X9M_icon.ico')
		icon = Icon(iconFilename)
		self.EAnalyse = inEAnalyse
		self.Icon = icon		
		self.InitializeComponent()
		self.arangePanels()

		#self.Layout += self.arangePanels		
		
	def InitializeComponent(self):
		screenSize = Screen.GetWorkingArea(self)
		self.Height = screenSize.Height / 2
		self.Width = screenSize.Width / 3
		self.Text = "Energy Analyses - by Spaceific STUDIO"
		self.panelHeight = self.ClientRectangle.Height * 0.75
		self.panelWidth = self.ClientRectangle.Width / 3
		self.bgColor = Color.CadetBlue
		self.textColor = Color.White
		#self.Width = 500
		#self.Height = 200		

		# self.polysurfaceAreaLabel = Label()
		# self.polysurfaceAreaLabel.Text = "Celková plocha fasády {}".format(self.EAnalyse.myAreas)
		# self.polysurfaceAreaLabel.Width = 250
		# self.polysurfaceAreaLabel.Parent = self
		# self.polysurfaceAreaLabel.Anchor = AnchorStyles.Top
		# self.polysurfaceAreaLabel.Dock = DockStyle.Top

		self.AHTCLabel = Label()
		self.AHTCLabel.Text = "{}".format("Průměrný součinitel prostupu tepla")
		self.AHTCLabel.Width = 250
		self.AHTCLabel.Parent = self
		self.AHTCLabel.Anchor = AnchorStyles.Top
		self.AHTCLabel.Dock = DockStyle.Top

		self.submitButton = Button()
		self.submitButton.Text = 'OK'
		self.submitButton.Click += self.update
		self.submitButton.Parent = self
		self.submitButton.Anchor = AnchorStyles.Bottom
		self.submitButton.Dock = DockStyle.Bottom

		self.cancelButton = Button()
		self.cancelButton.Text = 'Cancel'
		self.cancelButton.Click += self.close
		self.cancelButton.Parent = self
		self.cancelButton.Anchor = AnchorStyles.Bottom
		self.cancelButton.Dock = DockStyle.Bottom

		self.createComponentTreeView(self.EAnalyse.quantities)

	def createComponentTreeView(self, inList):
		"""
			creates tree structure of construction with required quantities for energy analyse check
			
			inList: type list - nested list of folowing structure: 
			[object_1
				[category
					[tuple
						(	Autodesk.Revit.DB.Element,
							elementCategory type: str, 
							list[Autodesk.DesignScript.Geometry.surface, ...], 
							list[list[Autodesk.Revit.DB.Material, Autodesk.Revit.DB.Material.Name, thermalConductivity type: float], Autodesk.Revit.DB.WallType.ThermalProperties.HeatTransferCoefficient type: float] 
								or list[Autodesk.Revit.DB.Material, Autodesk.Revit.DB.RoofType.ThermalProperties.HeatTransferCoefficient type: float],
								structureWidth type: list[overalWidth type: int, list[layerWidth type: int, ..]]
							area type: float
					 	)
					]
				]
			]
		"""
		self.categoryTreeRoot = TreeView()
		objNodes = TreeNode("{0}".format("Objects"))
		for i,obj in enumerate(inList):
			objNode = TreeNode("OBJ-{0}".format(i))
			#categoryNodes = TreeNode("{0}".format("Categories"))
			for j,category in enumerate(obj):
				if (type(category) == tuple or type(category) == list) and len(category) !=0:
					if (type(category[0]) == tuple or type(category[0]) == list) and len(category[0]) !=0:
						categoryNode = TreeNode("cat {0} {1}".format(j, category[0][0].Category.Name))					
					for k, elem in enumerate(category):						
						elementNode = TreeNode("{0} - {1}".format(k, elem[0].Id if (type(elem) == tuple or type(elem) == list) and len(elem) !=0 else "-----"))
						if (type(elem) == tuple or type(elem) == list) and len(elem) !=0:
							#elementNode = TreeNode("{0}".format(k))
							try:
								materialNode = TreeNode("Materials {0} ".format(len(elem[3][0] if (type(elem[3][0]) == tuple or type(elem[3][0]) == list) and len(elem[3][0]) !=0 else "0")))
							except Exception as ex:
								materialNode = TreeNode("heee")
							#materialNode = TreeNode("Materials {0} ".format(k))
							# if (type(elem[3]) == tuple or type(elem[3]) == list) and len(elem[3]) !=0:
							# 	for materialParams in elem[3]:
							# 		paramsNode = TreeNode()
							# 		try:
							# 			materialNode.Nodes.Add("{0}-{1}".format(materialParams[0].Id if hasattr(materialParams[0], "Id") else materialParams[0], materialParams[1] if materialParams[1] else "eeeo"))
							# 			if materialParams[2]:
							# 				materialNode.Nodes.Add("lambda {0}".format(materialParams[2]))
							# 			else:
							# 				materialNode.Nodes.Add("None")
							# 				materialNode.BackColor = ModelConsistency.errColors["Err_03"][2]
							# 				elementNode.BackColor = ModelConsistency.errColors["Err_03"][1]
							# 				categoryNode.BackColor = ModelConsistency.errColors["Err_03"][0]
							# 		except Exception as ex:
							# 			materialNode.Nodes.Add("{0}-{1}".format(k, elem[1]))
									
							# 		#materialNode.Nodes.Add("lambda {0}".format(materialParams[2] if materialParams[2] else "None"))								
							# else: materialNode = TreeNode("----------")
							# try:
							# 	if item[1].__class__.__name__ != "FamilyInstance":
								#totalThickness = "Total Thickness {0}".format(elem[4][0])
							totalThickness = "Total Thickness {0}".format("miliooon")
							# 	else:
							# 		totalThickness = "Total Thickness {0}".format(elem[4])
								
							# 	if item[1].__class__.__name__ != "FamilyInstance":
							# 		htc = "Heat Transfer Coef {0}".format(len(elem[4][1]))
							# 	else:
							# 		htc = "Heat Transfer Coef must be assigned from energy analyse settings".format(len(elem[4][1]))
							htc = "Heat Transfer Coef must be assigned from energy analyse settings"

							paramNodes = [ \
											TreeNode("{0}".format(elem[1])), \
											TreeNode("Faces {0}".format(len(elem[2]))), \
											materialNode, \
											TreeNode(totalThickness), \
											TreeNode(htc) \
										]
							# except Exception as ex:
							# 	paramNodes = []
							# 	Errors.catch(ex, "createComponentTreeView() error {0} - {1}".format(k, elem[1]))				
							#paramNodesNode = TreeNode("{0} - {1} - {2} faces - {3} materials - {4} total thickness {5} layers count".format(elem[0], elem[1], len(elem[2]), len(elem[3]), elem[4][0], len(elem[4][1])))
							for l in paramNodes:
								elementNode.Nodes.Add(l)
							categoryNode.Nodes.Add(elementNode)
				#categoryNodes.Nodes.Add(categoryNode)
				else: 
					categoryNode = TreeNode("cat {0} {1}".format(j, "---"))

				objNode.Nodes.Add(categoryNode)
			objNodes.Nodes.Add(objNode)
		self.categoryTreeRoot.Nodes.Add(objNodes)
		self.categoryTreeRoot.Dock = DockStyle.Fill
		self.categoryTreeRoot.ExpandAll()
		

	def arangePanels(self):
		self.SuspendLayout()
		screenSize = Screen.GetWorkingArea(self)
		self.Height = screenSize.Height / 2
		self.Width = screenSize.Width / 2
		self.panelHeight = self.ClientRectangle.Height * 0.75
		self.panelWidth = self.ClientRectangle.Width / 3
		
		self.setupReportPanel()
		self.setupLeftPanel()
		self.setupRightPanel()
		self.setupMiddlePanel()

		self.ResumeLayout()


	def setupLeftPanel(self):
		self.leftPanel = Panel()
		#self.leftPanel.ForeColor = self.textColor
		#self.leftPanel.BackColor = self.bgColor
		self.leftPanel.BorderStyle = System.Windows.Forms.BorderStyle.None
		self.leftPanel.Width = self.panelWidth
		self.leftPanel.Height = self.panelHeight
		self.leftPanel.BackColor = Color.White
		self.leftPanel.Location = Point(0, 0)

		self.quantitiesTab = TabControl()
		self.quantitiesTab.Width = self.panelWidth
		self.quantitiesTab.Height = self.panelHeight
		self.quantitiesTab.Location = Point(0, 0)
		self.quantitiesTabPages = []
		for o, obj in enumerate(self.EAnalyse.overalAreaOfEnvelope):
			quantitiesTabPage = TabPage()
			quantitiesTabPage.Text = "OBJ_{0}".format(o)
			
#									("Plocha obálky celého solidu", self.EAnalyse.overalAreaOfEnvelope[o])			
			self.quantities =	[ \
									("Plocha obálky součtem parciálních ploch", self.EAnalyse.overalAreaOfEnvelopeSurfaces[o]), \
									("Plocha obálky celého solidu", self.EAnalyse.overalAreaOfEnvelope[o]), \
									("Plocha obálky v kontaktu se vzduchem", None), \
									("Plocha obálky v kontaktu se zeminou", None), \
									("Plocha netransparetních konstrukcí", self.EAnalyse.nonTransparentConstructionArea[o]), \
									("Plocha výplní otvorů", self.EAnalyse.openingsArea[o]), \
									("Plocha lehkých obvodových plášťů", self.EAnalyse.curtainWallsArea[o]), \
									("Průměrný Součinitel Prostupu Tepla", None), \
									("Objemový koeficient A/V", None)]
			quantitiesTable = TableLayoutPanel()
			quantitiesTable.Width = self.quantitiesTab.Width
			quantitiesTable.Height = self.quantitiesTab.Height -20
			quantitiesTable.GrowStyle = TableLayoutPanelGrowStyle.AddRows
			quantitiesTable.ColumnCount = 2	

			#cWidthLabel1.Font = Font(FontFamily.CenturyGothic, 12.0, FontStyle.Bold)
			# fFamily = FontFamily()
			# fNames = fFamily.FamilyNames

			columns = []
			# for i, control in enumerate(self.quantitiesTable.Controls):
			# 	control.Width = 150 if i==0 else control.Width
			# 	control.BackColor = Color.Gray if i % 2 == 0 else Color.White
			# 	columns.append(self.quantitiesTable.GetColumn(control))
			
			

			# cWidthLabel1.Text = "len(columns) {}".format(len(columns))
			# cWidthLabel2.Text = "{}".format(len(columns))
			header = [("Veličina", "Hodnota")]
			self.quantityTableItems = header + self.quantities
			i=0		
			for item in self.quantityTableItems:
				quantityLabel = Label()
				quantityLabel.Text = "{}:".format(item[0])
				quantityLabel.Dock = DockStyle.Fill
				quantityLabel.TextAlign = ContentAlignment.MiddleLeft
				quantityLabel.Width = self.leftPanel.Width * 0.75
				quantityLabel.BackColor = Color.AliceBlue if i % 2 == 0 else Color.White
				valueLabel = Label()
				valueLabel.Text = "{}".format(item[1])
				valueLabel.Dock = DockStyle.Fill
				valueLabel.TextAlign = ContentAlignment.MiddleLeft
				valueLabel.BackColor = Color.AliceBlue if i % 2 == 0 else Color.White

				rStyle = RowStyle(SizeType.Percent, 100/(len(self.quantityTableItems)))
				quantitiesTable.RowStyles.Add(rStyle)
				
				quantitiesTable.Controls.Add(quantityLabel,0,i)
				quantitiesTable.Controls.Add(valueLabel,1,i)
				i += 1


			
				# self.leftTextBox = TextBox()
				# self.leftTextBox.Width = self.ClientRectangle.Width
				# self.leftTextBox.Height = self.ClientRectangle.Height
				# self.leftTextBox.Multiline = True
				# self.leftTextBox.ScrollBars = ScrollBars.Vertical
				# self.leftTextBox.ReadOnly = True
				# nextLine = "\r\n"
				# lineGap = "\r\n\r\n"
				# quantities = "Výpis veličin: " + lineGap
				# quantities += "Plocha obálky: " 
				# quantities += "{0}".format(None) + lineGap
				# quantities += "Plocha obálky v kontaktu se vzduchem: "
				# quantities += "{0}".format(None) + lineGap
				# quantities += "Plocha obálky v kontaktu se zeminou: "
				# quantities += "{0}".format(None) + lineGap
				# quantities += "Plocha netransparetních konstrukcí: "
				# quantities += "{0}".format(None) + lineGap
				# quantities += "Plocha výplní otvorů: "
				# quantities += "{0}".format(None) + lineGap
				# quantities += "Plocha Lehkých Obvodových Plášťů: "
				# quantities += "{0}".format(None) + lineGap + lineGap
				
				# quantities += "Průměrný Součinitel Prostupu Tepla: "
				# quantities += "{0}".format(None) + lineGap
				# quantities += "Objemový koeficient A/V: "
				# quantities += "{0}".format(None) + lineGap
				# self.leftTextBox.Text = quantities
				#self.leftPanel.Dock = DockStyle.Left
				#self.leftPanel.Anchor = (AnchorStyles.Top | AnchorStyles.Right)
				
				#self.leftPanel.Controls.Add(self.quantitiesTable)
			quantitiesTabPage.Controls.Add(quantitiesTable)
			self.quantitiesTabPages.append(quantitiesTabPage)
		#for page in self.quantitiesTabPages:
			self.quantitiesTab.Controls.Add(quantitiesTabPage)
		self.Controls.Add(self.quantitiesTab)
		

	def setupMiddlePanel(self):
		headerItemsLeft = ["Material", "Material ID", "Is Category Material", "Lambda"]
		headerItemsRight = ["Material to Use", "Overide Lambda"]
		#self.middlePanel = Panel()
		#self.middlePanel.ForeColor = self.textColor
		#self.middlePanel.BackColor = self.bgColor
		#self.middlePanel.Width = self.panelWidth
		#self.middlePanel.Height = self.panelHeight
		#self.middlePanel.Location = Point(self.panelWidth, 0)
		self.tabControl = TabControl()
		self.tabControl.Width = self.panelWidth
		self.tabControl.Height = self.panelHeight
		self.tabControl.Location = Point(self.panelWidth, 0)

		self.tabPageStructure = TabPage()
		self.tabPageStructure.Text = "Konstrukční schéma"
		self.tabPageStructure.Controls.Add(self.categoryTreeRoot)
		self.tabControl.TabPages.Add(self.tabPageStructure)

		self.tabPageMaterial = TabPage()
		self.tabPageMaterial.Text = "Mapování materiálů"		
		self.materialTable = TableLayoutPanel()
		self.materialTable.Width = self.tabPageMaterial.Width
		#self.materialTable.Height = self.tabPageMaterial.Height
		self.materialLabel = Label()
		self.materialLabel.Text = "Materiál"
		self.materialTable.GrowStyle = TableLayoutPanelGrowStyle.AddRows
		self.materialTable.ColumnCount = 5
		self.materialTable.Controls.Add(self.materialLabel,0,0)
		self.tabPageMaterial.Controls.Add(self.materialTable)
		self.tabControl.TabPages.Add(self.tabPageMaterial)

		#self.middlePanel.Dock =  DockStyle.Left
		#self.middlePanel.Controls.Add(self.categoryTreeRoot)
		#self.middlePanel.Controls.Add(self.tabControl)	
		self.Controls.Add(self.tabControl)
		

	def setupRightPanel(self):
		self.rightPanel = Panel()
		self.rightPanel.Width = self.panelWidth
		self.rightPanel.Height = self.panelHeight
		#self.rightPanel.ForeColor = self.textColor
		#self.rightPanel.BackColor = self.bgColor
		self.rightPanel.Width = self.panelWidth
		self.rightPanel.Height = self.panelHeight
		self.rightPanel.Location = Point(self.Width - self.panelWidth, 0)
		self.reportTextBox.ScrollBars = ScrollBars.Vertical
#		self.rightPanel.Dock = DockStyle.Left
#		self.rightPanel.Anchor = AnchorStyles.Right
		self.rightPanel.Controls.Add(self.AHTCLabel)
		self.rightPanel.Controls.Add(self.cancelButton)
		self.rightPanel.Controls.Add(self.submitButton)
		#self.rightPanel.Anchor = AnchorStyles.Right
		self.Controls.Add(self.rightPanel)
	
	def setupReportPanel(self):
		self.reportPanel = Panel()
		#self.reportPanel.ForeColor = self.textColor
		#self.reportPanel.BackColor = self.bgColor
		self.reportPanel.Width = self.ClientRectangle.Width
		self.reportPanel.Height = self.ClientRectangle.Height * 0.1
		self.reportPanel.Location = Point(0, self.ClientRectangle.Height - self.reportPanel.Height)
#		self.reportPanel.Dock = DockStyle.Left
#		self.reportPanel.Anchor = AnchorStyles.Right

		self.reportTextBox = TextBox()
		self.reportTextBox.Width = self.ClientRectangle.Width
		self.reportTextBox.Height = self.ClientRectangle.Height * 0.1
		self.reportTextBox.Multiline = True
		self.reportTextBox.ScrollBars = ScrollBars.Vertical
		self.reportTextBox.ReadOnly = True
		self.reportPanel.Controls.Add(self.reportTextBox)
		if ModelConsistency.hasError:
			reportText = ""
			for error in ModelConsistency.report:
				reportText += "{0} - {1} for these elements: (".format(error, ModelConsistency.errTypes[error])
				if len(ModelConsistency.ID_stack[error]) > 0:
					for elId in ModelConsistency.ID_stack[error]:
						reportText += "{}, ".format(elId)
				reportText += ")\n\n"
			self.reportTextBox.Text = reportText
		self.reportTextBox.Text += "{}".format(",".join(str(self.EAnalyse.modelMaterials)))
		#self.reportPanel.Anchor = AnchorStyles.Right
		self.Controls.Add(self.reportPanel)

	def createMappingTable(self, inList):
		pass

	def runScripts(self):
		pass

	def update(self, sender, event):
		self.runScripts()
		#self.Close()

	def close(self, sender, event):
		self.Close()
	def OnChanged(self, sender, event):
		self.label.Text = sender.Text


# def Unwrap(item, *args):
# 	return UnwrapElement(item)
