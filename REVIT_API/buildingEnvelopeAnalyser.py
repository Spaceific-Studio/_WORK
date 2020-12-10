import sys
import time
#import traceback
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
sys.path.append(pyt_path)
sys.path.append(lib_path)

from itertools import chain, groupby
from RevitSelection import *
import RevitSelection as RevitSelection
from ListUtils import *
import ListUtils as ListUtils
from Errors import *
from SpaceOrganize import *

import clr
# Import Element wrapper extension methods
clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
# Import geometry conversion extension methods
clr.ImportExtensions(Revit.GeometryConversion)

#import windows forms
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Drawing
import System.Windows.Forms as WF
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument

clr.AddReference("System")
from System.Collections.Generic import List as Clist
from System.Collections.Generic import IEnumerable as iEnum
from System import Guid as Guid

# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB
#import Autodesk.Revit.DB as DB

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI.Selection import *

#clr.AddReference('DSCoreNodes')
#from DSCore import List, Solid

clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

def getBuildInParams(inElement):
	builtInParams = System.Enum.GetValues(DB.BuiltInParameter)
	#builtInNames = System.Enum.GetType(BuiltInParameter)
	bips = []
	for bip in builtInParams:
		parameter = inElement.get_Parameter(bip)
		if parameter != None:
			bips.append(bip)
	return bips

TransactionManager.Instance.EnsureInTransaction(doc)
trans = DB.SubTransaction(doc)

analyser = DB.Analysis.BuildingEnvelopeAnalyzer.Create(doc, Autodesk.Revit.DB.Analysis.BuildingEnvelopeAnalyzerOptions())
elements = analyser.GetBoundingElements()
hostElementIds = [x.HostElementId for x in list(elements)]
IdsCol = Clist[Autodesk.Revit.DB.ElementId](hostElementIds)
hostElements = [doc.GetElement(x.HostElementId) for x in list(elements)]

linkedElementIds = [x.LinkedElementId for x in list(elements)]
trans.Start()
try:
	EAmodelOptions = DB.Analysis.EnergyAnalysisDetailModelOptions()
except Exception as ex:
	Errors.catch(ex, "didn't get EAmodel")
trans.Commit()
TransactionManager.Instance.TransactionTaskDone()
EAmodelOptions.EnergyModelType = DB.Analysis.EnergyModelType.BuildingElement
EAmodelOptions.ExportMullions = True
EAmodelOptions.IncludeShadingSurfaces = True
EAmodelOptions.SimplifyCurtainSystems = True
EAmodelOptions.Tier =  DB.Analysis.EnergyAnalysisDetailModelTier.FirstLevelBoundaries
analModel = DB.Analysis.EnergyAnalysisDetailModel.Create(doc, EAmodelOptions)
myOutput = analModel.GetMaterialIds(False)
prInfo = doc.ProjectInformation.Parameters
parameters = []
for params in prInfo:
	if params.__class__.__name__ == "ParameterSet":
		for iterator in params.ForwardIterator():
			parameters.append(iterator)
	elif params.__class__.__name__ == "Parameter":
		if params.Definition.Name == "Energy Settings":
			EnergySettings = params.AsValueString()
			#EnergySettingsElement = doc.GetElement(EnergySettings)
			#parameter = DB.ParameterValueProvider(params.Definition.ParameterGroup)
			parameters.append((params.Definition.Name, params.HasValue, DB.LabelUtils.GetLabelFor(params.Definition.ParameterGroup)))
		parameters.append(params.Definition.Name)
param_ID = DB.ElementId(DB.BuiltInParameter.RBS_CONSTRUCTION_SET_PARAM)
enSettingsElement = DB.FilteredElementCollector(doc).OfClass(DB.Analysis.EnergyDataSettings).ToElements()
enSettingsElementBIPS = getBuildInParams(enSettingsElement[0])
param_ID = DB.ElementId(DB.BuiltInParameter.ENERGY_ANALYSIS_BUILDING_OPERATING_SCHEDULE)
EABOS = DB.ParameterValueProvider(param_ID).GetIntegerValue(enSettingsElement[0])
Errors.catchVar(EABOS, "EABOS")
Errors.catchVar(enSettingsElementBIPS, "enSettingsElementBIPS")
Errors.catchVar(enSettingsElement[0].AnalysisType, "enSettingsElement.Category")
Errors.catchVar([(x.Definition.Name, x.Definition.ParameterGroup, x.Definition.Name, x.Definition.ParameterType, x.Definition.UnitType, x.StorageType, x.Element, x.HasValue, x.Id, x.IsReadOnly, x.UserModifiable) for x in enSettingsElement[0].GetOrderedParameters()], "enSettingsElement")
#Errors.catchVar(DB.ParameterValueProvider(param_ID).GetStringValue(enSettingsElement), "RBS_CONSTRUCTION_SET_PARAM")
Errors.catchVar(parameters,"parameters")
#buildingConstructionSet = doc.GetElement(enSettingsElement[0].GetBuildingConstructionSetElementId(doc))
#buildingConstructionParameters = buildingConstructionSet.GetOrderedParameters()
#construction = buildingConstructionSet.GetConstructions(DB.ConstructionType.ExteriorWall)
#analConstrLookUpTableParamId = DB.ElementId(DB.BuiltInParameter.ANALYTIC_CONSTRUCTION_LOOKUP_TABLE)
#Errors.catchVar(doc.GetElement(buildingConstructionSet), "buildingConstructionSet")
#Errors.catchVar(buildingConstructionParameters, "buildingConstructionParameters")
if Errors.hasError():
 	OUT = Errors.report
elif Errors.hasContent():
	OUT = Errors.getConntainerContent()
else:
	OUT = myOutput