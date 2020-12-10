from Autodesk.Revit.DB import *
import clr
from Autodesk.Revit.UI.Selection import Selection as UISelection
from Autodesk.Revit.UI import UIApplication

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles

class MainForm(Form):
	def __init__(self):
		self.InitializeComponent()
	def InitializeComponent(self):
		self.Text = "Filter elements by parameter name and value"
		self.Width = 500
		self.Height = 200

		self.paramaterValueTB = TextBox()
		self.paramaterValueTB.Text = "Enter value"
		#self.paramaterValueTB.Location = Point(5, 55)
		self.paramaterValueTB.Width = 150
		self.paramaterValueTB.Parent = self
		self.paramaterValueTB.Anchor = AnchorStyles.Top
		self.paramaterValueTB.Dock = DockStyle.Top		

		self.parameterCB = ComboBox()
		self.parameterCB.Width = 150
		self.parameterCB.Parent = self
		self.parameterCB.Anchor = AnchorStyles.Top
		self.parameterCB.Dock = DockStyle.Top
		self.parameterCB.Items.AddRange(selectedParameters)
		self.parameterCB.SelectionChangeCommitted += self.OnChanged
		
		self.parameterCBLabel = Label()
		self.parameterCBLabel.Text = "Select parameter"
		self.parameterCBLabel.Width = 250
		self.parameterCBLabel.Parent = self
		self.parameterCBLabel.Anchor = AnchorStyles.Top
		self.parameterCBLabel.Dock = DockStyle.Top
		
		self.label = Label()
		self.label.Text = "You must select objects first"
		self.label.Width = 250
		self.label.Parent = self
		self.label.Anchor = AnchorStyles.Top
		self.label.Dock = DockStyle.Top

		# self.paramaterNameTB = TextBox()
		# self.paramaterNameTB.Text = "Enter parameter Name"
		# #self.paramaterNameTB.Location = Point(5, 30)
		# self.paramaterNameTB.Width = 150
		# self.paramaterNameTB.Dock = DockStyle.Top

		self.submitButton = Button()
		self.submitButton.Text = 'Submit'
		self.submitButton.Location = Point(25, 125)
		self.submitButton.Click += self.update
		self.submitButton.Parent = self
		self.submitButton.Anchor = AnchorStyles.Bottom
		self.submitButton.Dock = DockStyle.Bottom

		self.closeButton = Button()
		self.closeButton.Text = 'Close'
		self.closeButton.Click += self.close
		self.closeButton.Parent = self
		self.closeButton.Anchor = AnchorStyles.Bottom
		self.closeButton.Dock = DockStyle.Bottom

		self.AcceptButton = self.submitButton
		self.CancelButton = self.closeButton

		# self.Controls.Add(self.label)
		# self.Controls.Add(self.parameterCBLabel)
		# self.Controls.Add(self.paramaterNameTB)
		# self.Controls.Add(self.paramaterValueTB)
		# self.Controls.Add(self.submitButton)


	def update(self, sender, event):
		self.label.Text = self.paramaterValueTB.Text
		
		myParameterName = self.parameterCB.SelectedItem
		myParameterValue = self.paramaterValueTB.Text
		selectedElementsIds = filterByCustomParameterValue(selection, myParameterName, myParameterValue)
		myCollection = Clist[ElementId](selectedElementsIds)
		lMyCollection = list(myCollection)
		print("\nYou selected: {0}".format(myParameterName))
		print("With value: {0}\n".format(myParameterValue))
		print ("selectedItems length - {0}".format(len(selectedElementsIds)))
		t = Transaction(doc, "Filter elements by parameter name and value")
		#transaction Start
		t.Start()
		selection.Clear()
		__revit__.ActiveUIDocument.Selection.SetElementIds(myCollection)
		#uidoc.ShowElements(myCollection)
		#transaction commit
		t.Commit()
		#close the form window		

	def close(self, sender, event):
		self.Close()
	def OnChanged(self, sender, event):
		self.label.Text = sender.Text

#clr.AddReference("RevitServices")
#import RevitServices
#from RevitServices.Persistance import DocumentManager

from System.Collections.Generic import List as Clist

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

#input("zadaj nazov parametru: \n")
#  Creating collector instance and collecting all the walls from the model
wall_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

# Iterate over wall and collect Volume data
total_volume = 0.0

# Get all properties of wall
# for element in selection:
# 	param_set = element.GetOrderedParameters()
# 	for param in list(param_set):
# 		print ("ParamName - {name}; value - {value}; hasValue - {hasValue}; ParameterType - {parameterType} unitType - {unitType}" \
# 				.format( \
# 						name=param.Definition.Name, \
# 						parameterType = param.Definition.ParameterType, \
# 						value = param.AsValueString(), \
# 						hasValue = param.HasValue, \
# 						unitType=param.Definition.UnitType \
# 						) \
# 			  )
# 	print ("-----------")
def getElementaAndCategory(inSelection):
	returnCategories = []
	returnElements = []
	for el in inSelection:
		elementCategory = el.Category.Name
		if elementCategory not in returnCategories:
			returnCategories.append(elementCategory)
			returnElements.append(el)
	returnTuple = (tuple(returnElements), tuple(returnCategories))
	return returnTuple

def getParametersByCategories(inTuple):
	returnParameters = []
	for el in inTuple[0]:
		param_set = el.GetOrderedParameters()
 		for param in list(param_set):
			paramName = param.Definition.Name
			if paramName not in returnParameters:
				returnParameters.append(paramName)
	listSorted = sorted(returnParameters)
	return tuple(listSorted)
	
def filterByCustomParameterValue(inSelection, parameterName, parameterValue):
	returnSelection = []
	for element in inSelection:
		param_set = element.GetOrderedParameters()
		for parameter in param_set:
			if parameter.HasValue and parameter.Definition.Name == parameterName and parameterValue == parameter.AsValueString():
				print("this elementID has correct value - {0}".format(element.Id))
				returnSelection.append(element.Id)
	return returnSelection

elementCategories = getElementaAndCategory(selection)
selectedParameters = getParametersByCategories(elementCategories)
#print (dir(MainForm))

#run input form
Application.EnableVisualStyles()
myDialogWindow = MainForm()
Application.Run(myDialogWindow)




#print __revit__.ActiveUIDocument.Selection.GetElementIds()