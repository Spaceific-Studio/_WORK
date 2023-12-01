import os.path as op
import olefile
import re

def get_rvt_file_version(rvt_file):
  if op.exists(rvt_file):
    if olefile.isOleFile(rvt_file):
      rvt_ole = olefile.OleFileIO(rvt_file)
      bfi = rvt_ole.openstream("BasicFileInfo")
      file_info = bfi.read().decode("utf-16le", "ignore")
      pattern = re.compile(r"\d{4}")
      rvt_file_version = re.search(pattern, file_info)[0]
      return rvt_file_version
    else:
      print("file does not apper to be an ole file: {}".format(rvt_file))
  else:
    print("file not found: {}".format(rvt_file))

print(get_rvt_file_version(r'P:\14W8400_Rekonstrukce_AK_VDJ_Kopanina\DSJ\09_Revit\5292_DZS_SO02_ELE_R22.rvt'))
