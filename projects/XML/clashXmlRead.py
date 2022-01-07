import xml.etree.ElementTree as ET
import os
from tkinter import *
from PIL import Image, ImageDraw, ImageTk
import time
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

class VerticalScrolledFrame(Frame):
	def __init__(self, parent, inClashTestDict, *args, **kwargs):
		
		Frame.__init__(self, parent, *args, **kwargs)
		#self.createWidgets()
		#self.setGlobals()
		
		#self.clashData = inClashTestDict.values()
		self.parent = parent
		self.screen_width = self.winfo_screenwidth()
		self.screen_height = self.winfo_screenheight()
		self.fHeight1 = self.screen_height*0.65
		self.fHeight2 = self.screen_height*0.3
		self.fWidth1 = self.screen_width*0.95
		
		self.dataDict = inClashTestDict
		self.vscrollbar = Scrollbar(self, orient=VERTICAL)
		self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
		self.setupCanvas()
		self.vscrollbar.config(command=self.canvas.yview)
		self.canvasHeight = self.canvas.winfo_reqheight()
		self.canvas.xview_moveto(0)
		self.canvas.yview_moveto(0)
		
		self.clashData = [x for x in [y for y in inClashTestDict.values()]]
		#Slowest update time
		self.sUTime = 0.001
		self.textVar = StringVar()
		self.timeVar = StringVar()
		self.pointerVar = StringVar()
		self.dPointerVar = StringVar()
		self.countDownVar = StringVar()
		self.moveVar = StringVar()
		self.setup()
		
		def configure_fr1(event):
			size = (self.fr1.winfo_reqwidth(), self.fr1.winfo_reqheight())
			self.canvas.config(scrollregion="0 0 %s %s" % size)
			if self.fr1.winfo_reqwidth() != self.canvas.winfo_width():
				# update the canvas's width to fit the inner frame
				self.canvas.config(width=self.fr1.winfo_reqwidth())
					
		self.fr1.bind('<Configure>', configure_fr1)
	
		def configure_canvas(event):
			if self.fr1.winfo_reqwidth() != self.canvas.winfo_width():
				# update the inner frame's width to fill the canvas
				self.canvas.itemconfigure(self.fr1_id, width=self.canvas.winfo_width())
		
		self.canvas.bind('<Configure>', configure_canvas)
		
		self.offset_y = 0
		
		def on_press(evt):
			self.offset_y = evt.y_root
		
		def on_touch_scroll(evt):
			if evt.y_root-self.offset_y<0:
				evt.delta = -1
			else:
			     evt.delta = 1
			# canvas.yview_scroll(-1*(evt.delta), 'units') # For MacOS
			self.canvas.yview_scroll( int(-1*(evt.delta/120)) , 'units') # For windows
		
		def onScrollMove(event):
			pointerYpos = event.widget.winfo_pointerxy()[1]
			self.cPointerPosY = event.widget.winfo_pointerxy()[1]
			self.deltaPointerY = self.sPointerPosY - self.cPointerPosY
			self.canvasCPosY = self.canvasSPosY + self.deltaPointerY
			self.canvas.yview_moveto(self.canvasCPosY/(self.canvasHeight*4))
			
			
			self.moveVar.set("canvasSPosY {0}, self.deltaPointerY {1} self.canvasCPosY {2}".format(self.canvasSPosY, self.deltaPointerY, self.canvasCPosY))
	
		def scrollOnPress(event):
			self.scrollSTime = time.time()
			self.canvasSPosY = self.canvas.winfo_rooty()
			self.sPointerPosY = event.widget.winfo_pointerxy()[1]
			self.pointerVar.set("pointer {0}, sPointerPosY {1}".format(event.widget.winfo_pointerxy(), self.sPointerPosY))
	
		def scrollOnRelease(event):
			self.scrollETime = time.time()
			dTime = self.scrollETime - self.scrollSTime
			self.timeVar.set("scrollDTime{0:.3f}".format(dTime))
			self.ePointerPosY = event.widget.winfo_pointerxy()[1]
			#delta of start and end pointer position
			self.dPointerPosY = self.ePointerPosY - self.sPointerPosY
			if self.dPointerPosY > 0:
				self.countDown = self.dPointerPosY - 1
			else:
				self.countDown = self.dPointerPosY + 1
			self.dPointerVar.set("dPointerPosY {0}".format(self.dPointerPosY))
			updateCanvasPosition()
			
		def updateCanvasPosition(*args):
			#currentUpdateTime
			if len(args) >1:
				print("args[0] {0}, args[1] {1}".format(args[0], args[1]))
			if self.countDown != 0:
				self.cUTime = int(abs(1/(self.countDown / self.dPointerPosY)) * self.sUTime)
			else:
				self.cUTime = self.sUTime
			if self.countDown >0:
				self.countDown -=1
				self.countDownNorm = self.countDown / self.dPointerPosY
				self.countDownVar.set("{0} norm {1:.3f}".format(self.countDown, self.countDownNorm))
				self.after(self.cUTime, updateCanvasPosition)
			elif self.countDown <0:
				self.countDown +=1
				self.countDownNorm = self.countDown / self.dPointerPosY
				self.countDownVar.set("{0} norm {1:.3f}".format(self.countDown, self.countDownNorm))
				self.canvas.yview_moveto(self.canvasCPosY)
				self.after(self.cUTime, updateCanvasPosition)
			else:
				 pass	
		
		#self.bind("<B1-Motion>", onScrollMove)
		self.bind("<Enter>", lambda _: self.bind_all('<B1-Motion>', onScrollMove), '+')
		self.bind("<Leave>", lambda _: self.unbind_all('<B1-Motion>'), '+')
		#self.bind("<ButtonPress-1>", scrollOnPress)
		self.bind("<Enter>", lambda _: self.bind_all('<ButtonPress-1>', scrollOnPress), '+')
		self.bind("<Leave>", lambda _: self.unbind_all('<ButtonPress-1>'), '+')
		self.bind("<ButtonRelease-1>", scrollOnRelease)
		#self.bind("<Enter>", lambda _: self.bind_all('<ButtonRelease-1>', scrollOnRelease), '+')
		#self.bind("<Leave>", lambda _: self.unbind_all('<ButtonRelease-1>'), '+')
		
		#self.bind("<Enter>", lambda _: self.bind_all('<Button-1>', on_press), '+')
		#self.bind("<Leave>", lambda _: self.unbind_all('<Button-1>'), '+')
		#self.bind("<Enter>", lambda _: self.bind_all('<B1-Motion>', on_touch_scroll), '+')
		#self.bind("<Leave>", lambda _: self.unbind_all('<B1-Motion>'), '+')
		
	def setup(self):
		
		#self.fr1 = Frame(self.canvas, height=self.fHeight1, width=self.fWidth1, bg='cyan')
		#self.fr1.grid(row=0, column=0, sticky=W)
		self.fr1 = Frame(self.canvas)
		self.fr1_id = self.canvas.create_window(0, 0, window=self.fr1, anchor=NW)
		
		self.lst = []
		#self.fillData()
		dataDictValues = self.dataDict.values()
		self.setupTable(len(self.clashData[0]),5)
	
	def setupCanvas(self):
		self.canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=self.vscrollbar.set)
		self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
		
	
	def setupTable(self, rCount, cCount):
		self.textVar = StringVar()
		#self.infoText = Label(self.fr1, text="textInfo", textvariable=self.textVar)
		#self.infoText.grid(row=0, column=2, sticky=NSEW)
		
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

"""
mainWindow = Tk()
mainWindow.grid()
mainWindow.grid_propagate(1)

app = App(mainWindow, clashTestsDict)
app.master.title("Transform app")
app.mainloop()
"""
if __name__ == "__main__":

    class SampleApp(Tk):
        def __init__(self, root, *args, **kwargs):
            #root = Tk.__init__(self, *args, **kwargs)
            Tk.__init__(self, *args, **kwargs)
            
            #self.grid()
            #self.grid_propagate(1)
            #self.screen_width = root.winfo_screenwidth()
            #self.screen_height = root.winfo_screenheight()
            #print(self.screen_height)
            self.frame = VerticalScrolledFrame(root, clashTestsDict, width=self.winfo_screenwidth(), height=500, bg ="red")
            self.frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
            #self.label = Label(self.frame, text="Shrink the window to activate the scrollbar.")
            #self.label.pack()
            """
            buttons = []
            for i in range(20):
                buttons.append(Button(self.frame.fr1, text="Button " + str(i)))
                buttons[-1].pack()
            """
	
    mainWindow = Tk()
    mainWindow.grid()
    mainWindow.grid_propagate(1)
	
    app = SampleApp(mainWindow)
    #app.grid()
    #app.grid_propagate(1)
    
    app.mainloop()

	
