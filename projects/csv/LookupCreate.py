import os
import sys

print("file {0}".format(__file__))

myCwd = os.getcwd()
print("my cwd {0}".format(myCwd))
#path = r"b:\\12-0168-0100_Modernizace_UVZ-3_stavba\\_Revit\\Koordinace\SNIM\\EXPORT_Z_EXCELU_DO_TXT\\"
if "pydroid" in sys.prefix:
	path = r"/storage/emulated/0/_WORK/projects/csv/Lookup"
else:
    path = r"C:\DANO\_WORK\PYTHON\projects\csv\Lookup"
if "pydroid" in sys.prefix:
    savePath = r"/storage/emulated/0/_WORK/projects/csv/Lookup"
else:
    savePath = r"C:\DANO\_WORK\PYTHON\projects\csv\Lookup"

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
		self.fileName = "Uzavírací klapka EKN.csv"
		self.saveFileName = "Uzavírací klapka EKN-edited.csv"
		self.savePath = os.path.join(inSavePath, self.saveFileName)

		self.path = os.path.join(inPath, self.fileName)
		self.compileFull = True

#		self.filterTypes = [ \
#						"ZP", "ZS", "ZD", "ZO","PP", "MP", "NS", "VK", \
#						"SN", "SL", "HL", "SD", "IS", "TM", "ST", "PD", \
#						"PA", "ON", "DD", "MI", "ZA", "IT", "IH", "IA", \
#						"LP", "NL", "PL", "KV", "ZV", "TV", "OV", \
#						"PH", "OD", "VY", "MB", "SH", "SR", "SY", \
#						"SP", "SC", "PE", "RP", "VT", "TE", "OM", \
#						"NK", "VA", "PM", "SB", "CO", "CP", "FI", \
#						"ZT", "IZ", "TR", "VP", "PO", "PU", "VR", \
#						"AT", "FS", "SJ", "DZ", "SK" \
#						]

		self.rawData = self.readFile(self.path)
		#print("self.rawData len {0}\nself.dataDict {1}".format(self.rawData, self.dataDict['NS']))
		#for k,v in self.dataDict.items():
		#	print("{0} - {1}\n".format(k,v))
		
		#self.saveFile(self.savePath)
	
	def saveFile(self):
		outputStr = ""
		#firtLine
		for c, col in enumerate(self.rawData):
		    if c==0:
		        pass
		    else:
		        outputStr += ",{0}##{1}##{2}".format(col['name'], col['type'], col['units'])
		outputStr += "/n"
		#other lines
		print("self.rawData")
		print(self.rawData)
		for r, row in enumerate(self.rawData[-1]['values']):
		    for c, col in enumerate(self.rawData):
		        if c==0:
		            outputStr += ","
		        else:
		            outputStr += ",{0}".format(col["values"][r])
		        outputStr += "\n"
		print(outputStr)
		#ensure_dir(self.savePath)
		#bStr = b"{0}".format()
		#encodedStr = outputStr.encode("utf-8")
		#encodedStr = outputStr.encode("latin-1")
		#sFile = open(self.savePath) , "w", encoding='utf-16')
		#sFile.write(outputStr)
		#sFile.close()
	
	def readFile(self, inPath):
		with open(inPath) as f:
			self.dataDict = {}
			self.markDict = {}
			i=0
			previous = None
			param = None
			self.firstLine = None
			rawData = []
			for line in f:
				row = line.strip().split(',')
				
				
				if i==0:
					self.firstLine = []
					for col in row:
					    rawParam = col.split('##')
					    if len(rawParam) > 1:
					        #print(rawParam)
					        param = {"name" : rawParam[0], "type" : rawParam[1], "units" : rawParam[2] if len(rawParam)>2 else None, "values" : []}
					    else:
					        param = None
					    self.firstLine.append(param)
					rawData.append(self.firstLine)
				elif i > 0:
					for j, col in enumerate(row):
					    if isinstance(self.firstLine[j], dict):
					        self.firstLine[j]["values"].append(col) 
					    
				#rawData.append(row)
				#previous = row
				#print("{0} {1}".format(i, row))
				i +=1
			f.close()

		return rawData
			


input = InputData(path, savePath)

for k, v in enumerate(input.rawData):
    print("{0} - {1}".format(k,v))
    
input.saveFile()
