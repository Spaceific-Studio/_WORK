# Povolit podporu Python a načíst knihovnu DesignScript
import clr
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel

ex = Excel.ApplicationClass()   
ex.Visible = True
ex.DisplayAlerts = False 


#workbook = ex.Workbooks.Open('D:/DANO/_WORK_ARCHIV/BIM_MANAGMENT_STUFF/ENERG_ANALYZY/read_write_data-test_file.xlsx')
workbook = ex.Workbooks.Open('D:/DANO/_WORK_ARCHIV/BIM_MANAGMENT_STUFF/ENERG_ANALYZY/nkn_v_3-29.xlsx')
ws = workbook.Worksheets[11]
wsCount = workbook.Worksheets.Count
#rows = ws.Rows[1]
cell = ws.Range["A3"]
cellText = cell.Value2
#rows = ws.Rows[1].Value2[0,0]
typBudovyRange = ws.Range["B120", "B129"]
popisKonstrukceRange = ws.Range["G106", "G131"]
#tabText = tabRange.Address[False, False]
typyBudovy = typBudovyRange.Value2
popisKonstrukce = popisKonstrukceRange.value2
#listTabText = ",".join(["{}".format(x) for x in tabText])
# Vstupní údaje k tomuto uzlu budou uloženy jako seznam proměnných IN.
dataEnteringNode = IN

# Umístit kód pod tento řádek

# Přiřaďte výstup k proměnné OUT.
OUT = (wsCount, typyBudovy, popisKonstrukce)