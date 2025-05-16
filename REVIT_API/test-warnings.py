import clr
clr.AddReference("RevitAPI")
import Autodesk
import Autodesk.Revit.DB as DB
#from Autodesk.Revit.DB import Transaction, IFailuresPreprocessor, BuiltInFailures, UV
from System.Collections.Generic import List as CList

doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView
active_lvl = active_view.GenLevel

selIds = uidoc.Selection.GetElementIds()
element = doc.GetElement(selIds[0])
print("Selected element {0} - {1} - dir(element) {2}".format(element.Id, element.Category.Name, dir(element)))
#myParams = element.GetOrderedParameters()
paramToChange = element.Parameter[DB.BuiltInParameter.FLOOR_HEIGHTABOVELEVEL_PARAM]
print("paramToChange {0}".format(paramToChange.Definition.Name))

#origin = element.GetTransform().Origin
#p1 = origin
#p2 = p1.Add(DB.XYZ(0, 0, 100))

#moveVec = toPoint.Subtract(ip_Origin)


class RoomWarningSwallower(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        fail_list = CList[FailureMessageAccessor]()
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
            roomNotEnclosed_failure_type = DB.BuiltInFailures.RoomFailures.RoomNotEnclosed
            joiningDisjoint_failure_type = DB.BuiltInFailures.JoinElementsFailures.JoiningDisjointWarn
            if failure_id == roomNotEnclosed_failure_type:
                #print("{0} with id: {1} of type: {2} removed! - {3}-{4}".format(failure_severity, failure_id.Guid, failure_id, failure_ElementIds, failure_AdditionalElementIds))
                print("{0} with id: {1} description: {2}: roomNotEnclosed_failure_type: {3} failure_id {4} id.ToSting {5} - has resolutions: {6}\n default resolution caption {7}".format( \
                                                    failure_severity, \
                                                    failure_id.Guid, \
                                                    failure_descriptionText, \
                                                    roomNotEnclosed_failure_type, \
                                                    failure_id, \
                                                    failure_id.ToString(), \
                                                    failure_has_resolutions, \
                                                    failure_default_resolution_caption))
                failure.SetCurrentResolutionType(DB.FailureResolutionType.DeleteElements)
                print("failure resolution to DeleteElements was set")
                failuresAccessor.ResolveFailure(failure)
                print("failure roomNotEnclosed was resolved")
                failuresAccessor.DeleteWarning(failure)
                print("failure warning was deleted")
            elif failure_id == joiningDisjoint_failure_type:
                print("{0} with id: {1} description: {2}: id {3} - has resolutions: {4}\n default resolution caption {5}".format( \
                                                    failure_severity, \
                                                    failure_id.Guid, \
                                                    failure_descriptionText, \
                                                    failure_id.ToString(), \
                                                    failure_has_resolutions, \
                                                    failure_default_resolution_caption))
                if failure_has_resolutions:
                    
                    #failuresAccessor.DeleteWarning(failure)
                    failure.SetCurrentResolutionType(DB.FailureResolutionType.DetachElements)
                    print("failure resolution to DetachElements was set")
                    failuresAccessor.ResolveFailure(failure)
                    print("failure joiningDisjoint was resolved")
                    failuresAccessor.DeleteWarning(failure)
                    print("failure warning was deleted")
                else:
                    failuresAccessor.DeleteWarning(failure)
        return DB.FailureProcessingResult.Continue


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