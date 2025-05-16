"""
rvtver.py - read Revit version from *.rvt file

Copyright (C) 2008 by Jeremy Tammik, Autodesk Inc.

2008-09-02 initial version
2008-10-01 unicode handling added by ralf huvendiek
"""

import os, sys

"""
if 1 == len(sys.argv):
 print('usage: a.py rvtfile')
 sys.exit()

filename = sys.argv[1]
"""
filename = r"P:\14W8400_Rekonstrukce_AK_VDJ_Kopanina\DSJ\09_Revit\5292_DZS_SO02_ELE_R22.rvt"
if not os.path.exists( filename ):
 print("File '%s' does not exist." % filename)
 sys.exit()

f = open( filename, 'rb' )
data = f.read()
f.close()

s = 'Build'.encode( 'UTF-16-LE' )
i = data.find( s )

if i > 0:
 build_string = data[ i: i+40 ]
 build_string = build_string.decode( 'UTF-16-LE' )
 print("Build string found in '%s' at offset %s: %s" % (filename, i, build_string))
else:
 print('Build string not found.')