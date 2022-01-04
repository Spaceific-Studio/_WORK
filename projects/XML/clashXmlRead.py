import xml.etree.ElementTree as ET
import os
from tkinter import *
from PIL import Image, ImageDraw, ImageTk
#import xmltodict

cwd = os.getcwd()
print("cwd {0}".format(cwd))
testName = "SO_03-02-ARS- MEC - hard"
fFormat = "xml"
fName = "{0}.{1}".format(testName, fFormat)
subDir1 = "clashtest"
filePath = os.path.join(cwd, subDir1)
filePath = os.path.join(filePath, fName)
imgDir = os.path.join(cwd, subDir1,"{0}_files".format(testName))
print("filePath {0}".format(filePath))
print("imgDir {0}".format(imgDir))
with open(filePath) as xmlFile:
	data = xmlFile.read().replace("\n", "")
#xmlDict = xmltodict.parse(data)
#print("xmlDict {0}".format(xmlDict))
tree = ET.parse(filePath)
root = tree.getroot()
#print("dir root {0}".format(dir(root)))
#print("root.getchildren {0}".format(root.getchildren()))
clashTestNames = []
clashTestResults = []
for clashTest in root.iter('clashtest'):
	clashTestNames.append(clashTest.attrib['name'])
	print("clashtests {0}".format(clashTestNames[-1]))
	clashResults = []
	for clashResult in clashTest.iter('clashresult'):
		clashResultAttrs = {}
		#print("clashResult {0}".format(clashResult.attrib['name']))
		clashResultObjsAttrs = []
		for clashObject in clashResult.iter('clashobject'):
			clashObjAttribNames = []
			clashObjAttribValues = []
			for clashObjAttrName in clashObject.iter('name'):
				clashObjAttribNames.append(clashObjAttrName.text)
				#print("clashObjectAttrName {0}".format(clashObjAttrName.text))
			for clashObjAttrValue in clashObject.iter('value'):
				clashObjAttribValues.append(clashObjAttrValue.text)
				#print("clashObjectAttrName {0}".format(clashObjAttrValue.text))
			zipObj = zip(clashObjAttribNames, clashObjAttribValues)
			clashObjDict = dict(zipObj)
			clashResultObjsAttrs.append(clashObjDict)
		pos3fList = [x for x in clashResult.iter('pos3f')]
		clashResultPos = pos3fList[0] if len(pos3fList) >0 else None
		posDict ={}
		xPos = clashResultPos.attrib['x']
		yPos = clashResultPos.attrib['y']
		zPos = clashResultPos.attrib['z']
		posDict ={}
		posDict['x'] = xPos
		posDict['y'] = yPos
		posDict['z'] = zPos
		clashResultAttrs['clashResultPos'] = posDict
		clashResultAttrs['clashResultName'] = clashResult.attrib['name']
		clashResultAttrs['clashResultHref'] = clashResult.attrib['href']
		clashResultAttrs['clashResultObjsAttrs'] = clashResultObjsAttrs
		#print("{0}\n\telement_1-ID {1}, item name {2}, item type {3}\n\telement_2-ID {4} item name {5}, item type {6}\n\tx:{7}\n\ty:{8}\n\tz:{9}\n\thref:{10}\n".format(clashResultAttrs['clashResultName'], clashResultAttrs['clashResultObjsAttrs'][0]['Element ID'], clashResultAttrs['clashResultObjsAttrs'][0]['Item Name'], clashResultAttrs['clashResultObjsAttrs'][0]['Item Type'], clashResultAttrs['clashResultObjsAttrs'][1]['Element ID'], clashResultAttrs['clashResultObjsAttrs'][1]['Item Name'], clashResultAttrs['clashResultObjsAttrs'][1]['Item Type'], clashResultAttrs['clashResultPos']['x'], clashResultAttrs['clashResultPos']['y'], clashResultAttrs['clashResultPos']['z'], clashResultAttrs['clashResultHref']))
		clashResults.append(clashResultAttrs)
	clashTestResults.append(clashResults)
zipObj2 = zip(clashTestNames, clashTestResults)
clashTestsDict = dict(zipObj2)

values = clashTestsDict.values()

for i, v in enumerate(values):
	pass
	#print("{0}:length{1} : ".format(v, len(v)))

class App(Frame):
	def __init__(self, master, inClashTestDict):
			#attribs:
			#inClashTestDict:dict
			#input dictionary of structure
			#{
			# 'clashResultPos':dict
			# {
			#  'x':str, 'y':str, 'z': str
			# },
			# 'name':str, 'href':str,
			# 'clashResultObjsAttrs':dict
			#  {
			#   [#1-first element to clash test
			#    {'Element ID':str, 'Item Name':str, 'Item Type':str}
			#    },
			#    #2-second element to clash test
			#    {'Element ID':str, 'Item Name':str, 'Item Type':str}
			#    }
			#   ]
			#  }
			#}
		Frame.__init__(self, master, bg = "yellow", bd = 1)
		#self.createWidgets()
		#self.setGlobals()
		self.dataDict = inClashTestDict
		#self.clashData = inClashTestDict.values()
		self.master = master
		self.screen_width = master.winfo_screenwidth()
		self.screen_height = master.winfo_screenheight()
		self.fHeight1 = self.screen_height*0.65
		self.fHeight2 = self.screen_height*0.3
		self.fWidth1 = self.screen_width*0.95
		
		self.clashData = [x for x in [y for y in inClashTestDict.values()]]
		self.setup()
		
		
		
	def setup(self):
		self.fr1 = Frame(self.master, height=self.fHeight1, width=self.fWidth1, bg='yellow')
		self.fr1.grid(row=0, column=0, sticky=W)
		self.lst = []
		#self.fillData()
		dataDictValues = self.dataDict.values()
		self.setupTable(len(self.clashData[0]),5)
	
	def setupTable(self, rCount, cCount):
		self.textVar = StringVar()
		self.infoText = Label(self.fr1, text="textInfo", textvariable=self.textVar)
		self.infoText.grid(row=0, column=2, sticky=NSEW)
		
		cells ={}
		cWeight = int(100/cCount)
		results = [x for x in self.clashData[0]]
		for c in range(cCount):
			for r in range(rCount):
				
				if c == 0:
					self.fr1.columnconfigure(c,weight=1)
					self.fr1.rowconfigure(r,weight=20)
					href_t = results[r]['clashResultHref']
					href = "/".join(href_t.split("\\"))
					imgPath = os.path.join(cwd, subDir1, href)
					pilImg = Image.open(r"{0}".format(imgPath))
					pilImgR = pilImg.resize((90,90))
					img = ImageTk.PhotoImage(pilImgR)
				#self.cell = Label(self.fr1, width=30, fg='red', font=('Arial',4), text="{0},{1}".format(r,c))
					self.cell = Button(self.fr1, text="{0},{1}".format(r,c), image=img, font=('Arial',4), width=90, height=90, fg='gray')
					self.cell.imgList = []
					self.cell.imgList.append(img)
				elif c == 1:
					cText = results[r]['clashResultName']
					self.cell = Label(self.fr1, width=7, fg='black', font=('Arial',4), text="{0}".format(cText))
				elif c == 2:
					cText = results[r]['clashResultObjsAttrs'][0]['Element ID']
					self.cell = Label(self.fr1, width=7, fg='red', font=('Arial',4, 'bold'), text="{0}".format(cText))
					self.cell.bind("<ButtonRelease-1>", self.updateInfoText)
				elif c == 3:
					cText = results[r]['clashResultObjsAttrs'][1]['Element ID']
					self.cell.bind("<ButtonRelease-1>", self.updateInfoText)
					self.cell = Label(self.fr1, width=10, fg='blue', font=('Arial',4, 'bold'), text="{0}".format(cText))
				elif c == 4:
					cText = results[r]['clashResultHref']
					self.cell = Label(self.fr1, fg='grey', font=('Arial',4), text="{0}".format(cText))
					#self.cell.insert(END, self.lst[r][c])
				self.cell.grid(row=r,column=c,sticky=NSEW)
				#self.cell.bind("<ButtonRelease-1>", self.updateInfoText)
				
				cells[(r,c)] = self.cell
	
	def updateInfoText(self, event):
		self.textVar.set(event.widget.cget('text')) 
				
	def fillData(self):
		#tests = self.clashData.values()
		for i, test in enumerate(self.clashData):
			for k, v in enumerate(test):
				self.lst.append((v['clashResultName'],v))
			#self.lst.append((k, v['clashResultObjsAttrs'][0]['Element ID']))


mainWindow = Tk()
mainWindow.grid()
mainWindow.grid_propagate(1)

app = App(mainWindow, clashTestsDict)
app.master.title("Transform app")
app.mainloop()

	
