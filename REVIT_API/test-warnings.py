import clr
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *
#from Autodesk.Revit.DB import Transaction, IFailuresPreprocessor, BuiltInFailures, UV
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView
active_lvl = active_view.GenLevel

selIds = uidoc.Selection.GetElementIds()
element = doc.GetElement(selIds[0])
myParams = element.GetOrderedParameters()
paramToChange = element.Parameter[BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM]

#origin = element.GetTransform().Origin
#p1 = origin
#p2 = p1.Add(DB.XYZ(0, 0, 100))

#moveVec = toPoint.Subtract(ip_Origin)


class RoomWarningSwallower(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        fail_list = List[FailureMessageAccessor]()
        fail_acc_list = failuresAccessor.GetFailureMessages().GetEnumerator()
        print("isActive {}".format(failuresAccessor.IsActive()))
        for failure in fail_acc_list:
            failure_id = failure.GetFailureDefinitionId()
            #failure_AdditionalElementIds = list(failure.GetAdditionalElementIds())
            #failure_ElementIds = list(failure.GetFailingElementIds())
            #failure_Type = failure.GetCurrentResolutionType()
            failure_descriptionText = failure.GetDescriptionText()
            failure_has_resolutions = failure.HasResolutions()
            failure_default_resolution_caption = failure.GetDefaultResolutionCaption()
            failure_has_resolutions = failure.HasResolutions()
            failure_severity = failure.GetSeverity()
            failure_type = BuiltInFailures.RoomFailures.RoomNotEnclosed
            #if failure_id == failure_type:
            #print("{0} with id: {1} of type: {2} removed! - {3}-{4}".format(failure_severity, failure_id.Guid, failure_id, failure_ElementIds, failure_AdditionalElementIds))
            print("{0} with id: {1} description: {2}: id {3} - has resolutions: {4}\n default resolution caption {5}".format( \
                                                    failure_severity, \
                                                    failure_id.Guid, \
                                                    failure_descriptionText, \
                                                    failure_id.ToString(), \
                                                    failure_has_resolutions, \
                                                    failure_default_resolution_caption))
            failuresAccessor.DeleteWarning(failure)
        return FailureProcessingResult.Continue


# "Start" the transaction
tx = Transaction(doc, "place unenclosed room")
tx.Start()
print("baginTrans - warnings {}".format(len(doc.GetWarnings())))
options = tx.GetFailureHandlingOptions()
options.SetFailuresPreprocessor(RoomWarningSwallower())
tx.SetFailureHandlingOptions(options)

room = doc.Create.NewRoom(active_lvl, UV(0,0))
print("endTrans - warnings {}".format(len(doc.GetWarnings())))
# "End" the transaction
tx.Commit()
print("afterTrans - warnings {}".format(len(doc.GetWarnings())))

tx = Transaction(doc, "move joined element")
tx.Start()
options = tx.GetFailureHandlingOptions()
options.SetFailuresPreprocessor(RoomWarningSwallower())
tx.SetFailureHandlingOptions(options)
paramToChange.Set(-500)
tx.Commit()