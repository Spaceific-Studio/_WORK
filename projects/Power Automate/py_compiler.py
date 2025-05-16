from posixpath import dirname
from py_compile import compile as pc
import sys
import os
#from py_compile import compile as pcompile
dirName = r"C:\DANO\_WORK\PYTHON\projects\Power Automate"
fileName = "save_file_test.py"
try:
    #pc(r"C:\DANO\_WORK\PYTHON\projects\Power Automate\save_file_test.py")
    pc(os.path.join(dirName, fileName))
    print('Compiling OK of file {1}\{2}'.format(sys.exc_info, dirName, fileName))
except Exception as ex:
    print('Compile error in py_compiler.py: {0}'.format(sys.exc_info()))
