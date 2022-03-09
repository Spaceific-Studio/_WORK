import os

print("file {0}".format(__file__))

myCwd = os.getcwd()
print("my cwd {0}".format(myCwd))
#path = r"b:\\12-0168-0100_Modernizace_UVZ-3_stavba\\_Revit\\Koordinace\SNIM\\EXPORT_Z_EXCELU_DO_TXT\\"
path = r"C:\\Users\\gercakd\\OneDrive - pvs.cz\\H\\_BIM_MANAGMENT_STUFF\\FAMILIES\\141\\_STAVEBNI\\_SNIM\SNIM_EXPORT_CSV\\"
savePath = r"C:\\Users\\gercakd\\OneDrive - pvs.cz\\H\\_BIM_MANAGMENT_STUFF\\FAMILIES\\141\\_STAVEBNI\\_SNIM\SNIM_EXPORT_CSV\\SNIM-ASSEMBLY_CODE_PLNA_VERZE\\"

def ensure_dir(file_path):
	directory = os.path.dirname(file_path) 
	if not os.path.exists(directory):
		os.makedirs(directory)		



def transpose(inList):
	returnList = [[inList[j][i] for j in range(len(inList))] for i in range(len(inList[0]))]
	return returnList

class Dic2obj(object):
	def __init__(self, dictionary):
		for key in dictionary:
			setattr(self, key, dictionary[key])

class InputData():
	#FIRST_LINE = None
	
	def __init__(self, inPath, inSavePath):
		""" if not InputData.FIRST_LINE:
			InputData.FIRST_LINE = ["Region", "Confirmed", "Deads", "Recovered","D/C %", "C/Pop%", "c7D100k ", "d7D1m ", "incC8DStd%"] """
		self.fileName = "SNIM-from_excel_txt_s_tabulatory.txt"
		self.saveFileName = "2022_03_09-SNIM-Assembly_utf-16-FULL.txt"
		self.savePath = inSavePath

		self.path = os.path.join(inPath, self.fileName)
		self.compileFull = True

		self.filterTypes = [ \
						"ZP", "ZS", "ZO","PP", "MP", "NS", "VK", \
						"SN", "SL", "SD", "IS", "TM", "ST", "PD", \
						"PA", "ON", "DD", "MI", "ZA", "IT", "IH", \
						"LP", "NL", "PL", "KV", "ZV", "TV", "OV", \
						"PH", "OD", "VY", "MB", "SH", "SR", "SY", \
						"SP", "SC", "PE", "RP", "VT", "TE", "OM", \
						"NK", "VA", "PM", "SB", "CO", "CP", "FI", \
						"ZT", "IZ", "TR", "VP", "PO", "PU", "VR", \
						"AT", "FS", "SJ" \
						]

		self.rawData = self.readFile(self.path)
		#print("self.rawData len {0}\nself.dataDict {1}".format(self.rawData, self.dataDict['NS']))
		for k,v in self.dataDict.items():
			print("{0} - {1}\n".format(k,v))
		
		self.saveFile(self.savePath)
	
	def saveFile(self, inSavePath):
		outputStr = ""
		for k,v in self.dataDict.items():
			outputStr += "{0}\t{1}\t{2}\t\n".format(k, v['Category Name'], 1)
			for tIndex, typeName in v['Types'].items():
				outputStr += "{0}{1}\t{2} - {3}\t{4}\t\n".format(k, tIndex, v['Category Name'], typeName, 2)

		ensure_dir(inSavePath)
		#bStr = b"{0}".format()
		#encodedStr = outputStr.encode("utf-8")
		#encodedStr = outputStr.encode("latin-1")
		sFile = open(os.path.join(inSavePath, self.saveFileName) , "w", encoding='utf-16')
		sFile.write(outputStr)
		sFile.close()


	def readFile(self, inPath):
		with open(inPath) as f:
			self.dataDict = {}
			self.markDict = {}
			i=0
			previous = None
			rawData = []
			for line in f:
				row = line.strip().split('\t')
				
				if i > 1:
					if not self.compileFull:
						if previous[0] in self.filterTypes:
							if row[0] == previous[0]:
								if previous[2] not in self.markDict and previous[2] != "":
									self.markDict[previous[2]] = previous[3]
								elif previous[2] not in self.markDict and previous[2] == "":
									self.markDict["01"] = "N/A"
							else:
								#print("previous[1] {0}".format(previous[1]))
								self.dataDict[previous[0]] = {}
								self.dataDict[previous[0]]['Category Name'] = previous[1]
								self.dataDict[previous[0]]['Types'] = self.markDict
								self.markDict = {}
					else:
						if row[0] == previous[0]:
							if previous[2] not in self.markDict and previous[2] != "":
								self.markDict[previous[2]] = previous[3]
							elif previous[2] not in self.markDict and previous[2] == "":
								self.markDict["01"] = "N/A"
						else:
							#print("previous[1] {0}".format(previous[1]))
							self.dataDict[previous[0]] = {}
							self.dataDict[previous[0]]['Category Name'] = previous[1]
							self.dataDict[previous[0]]['Types'] = self.markDict
							self.markDict = {}
				else:
					self.firstLine = row
				rawData.append(row)
				previous = row
				#print("{0} {1}".format(i, row))
				i +=1
			f.close()

		return rawData
			


inputJHU = InputData(path, savePath)
