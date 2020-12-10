import Autodesk.Revit.DB as DB
param_ID = DB.ElementId(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM)

param_provider = DB.ParameterValueProvider(param_ID)

print (param_provider.GetDoubleValue(el))