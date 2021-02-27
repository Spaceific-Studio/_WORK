# Import the math module to convert user input degrees to radians.
import math

# Get a list of all user selected objects in the Revit Document.
selection = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]

# Definitions
def rotateSelectedElement(degrees_to_rotate):
    from Autodesk.Revit.UI.Selection import ObjectType

    #define the active Revit application and document
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument

    #define a transaction variable and describe the transaction
    t = Transaction(doc, 'This is my new transaction')

    # Convert the user input from degrees to radians.
    converted_value = float(degrees_to_rotate) * (math.pi / 180.0)

    # Begin new transaction
    t.Start()

    # Get the first selected element from the current Revit doc.
    el = selection[0].Id

    # Get the element from the selected element reference
    el_ID = doc.GetElement(el)      

    # Get the Bounding Box of the selected element.
    el_bb = el_ID.get_BoundingBox(doc.ActiveView)

    # Get the min and max values of the elements bounding box.
    el_bb_max = el_bb.Max
    el_bb_min = el_bb.Min

    # Get the center of the selected elements bounding box.
    el_bb_center = (el_bb_max + el_bb_min) / 2

    #Create a line to use as a vector using the center location of the bounding box.
    p1 = XYZ(el_bb_center[0], el_bb_center[1], 0)
    p2 = XYZ(el_bb_center[0], el_bb_center[1], 1)
    myLine = Line.CreateBound(p1, p2)

    # Rotate the selected element.
    ElementTransformUtils.RotateElement(doc, el, myLine, converted_value)

    # Close the transaction
    t.Commit()


# Execute    
# Add the desired degrees to rotate by as an argument for rotateSelectedElement()
rotateSelectedElement(45)