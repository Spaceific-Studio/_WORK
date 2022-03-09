import xml.etree.ElementTree as ET
import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import time
#import kiwi
#import xmltodict

cwd = os.getcwd()
print("cwd {0}".format(cwd))
#runFileDialog = True
runFileDialog = False
haveFileName = False
if runFileDialog:
	fileDialogWindow = Tk()
	#print("dir Tk {0}".				format(dir(fileDialogWindow)))
	#raise TypeError("Tk.winfo.height {0}".format(fileDialogWindow.winfo.height))
	fileDialogWindow.configure(height=900)
	fileDialogWindow.file_name = filedialog.askopenfile(initialdir=cwd, title="Open clash xml file", filetypes=(("xml files", "*.xml"), ("all files", "*.*")))
	print("Selected file: {0}".format(fileDialogWindow.file_name.name))
	try:
		fdFName = fileDialogWindow.file_name.name
		testName = fdFName.split("/")[-1].split(".")[0]
		fFormat = fdFName.split("/")[-1].split(".")[1]
		haveFileName = True
		fileDialogWindow.destroy()
	except Exception as ex:
		haveFileName = False
elif not haveFileName:
	testName = "SO_03-02-ARS- MEC - hard"
	fFormat = "xml"
#raise TypeError("fdName {0}.{1}".format(testName, fFormat))
#testName = "SO_03-02-ARS- MEC - hard"
#fFormat = "xml"
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
		self.canvasCPosY = self.canvas.winfo_y()
		self.accel = 0.8
		self.fps = 30
		self.idle = int(1000/self.fps)
		
		self.clashData = [x for x in [y for y in inClashTestDict.values()]]
		#Slowest update time
		self.sUTime = 0.001
		self.textVar = StringVar()
		self.timeVar = StringVar()
		self.pointerVar = StringVar()
		self.dPointerVar = StringVar()
		self.canvasSPosYVar =  StringVar()
		self.countDownVar = StringVar()
		self.moveVar = StringVar()
		self.speedVar = StringVar()
		self.posDevVar = StringVar()
		
		self.setup()
		
		
		def configure_fr1(event):
			size = (self.fr1.winfo_reqwidth(), self.fr1.winfo_reqheight())
			self.canvas.config(scrollregion="0 0 %s %s" % size)
			self.canvas.config(bg="black")
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
		
		def timeUpdate(*args):
			
			self.now = time.time() - self.scrollSTime
			
			
			#if now < 20:
			#if now < 2:
			if self.cScrollSpeed > 20 and not self.screenTouched:
				updateCanvasPosition()
				self.scrollLoop = self.after(self.idle, timeUpdate)
			elif not self.screenTouched:
				updateCanvasPosition()
			elif hasattr(self, "scrollLoop"):
				self.after_cancel(self.scrollLoop)
		
		def onScrollMove(event):
			pointerYpos = event.widget.winfo_pointerxy()[1]
			self.cPointerPosY = event.widget.winfo_pointerxy()[1]
			self.dPointerPosY = self.cPointerPosY - self.pPointerPosY
			self.cMoveTime = time.time()
			self.dMoveTime =  self.cMoveTime - self.pMoveTime
			self.deltaPointerY = self.cPointerPosY - self.sPointerPosY
			#if not hasattr(self, "canvasCPosY"):
			#self.canvasCPosY = self.vscrollbar.get()[0]*(self.fr1.winfo_reqheight() + self.deltaPointerY)
			#else:
			self.canvasCPosY = self.canvasSPosY - self.deltaPointerY
			"""	
			if self.canvasSPosY + self.deltaPointerY >= 0 or self.canvasSPosY + self.deltaPointerY <= self.fr1.winfo_reqheight() - self.canvasHeight:
				self.canvasCPosY = self.canvasSPosY + self.deltaPointerY
				self.canvas.yview_moveto(self.canvasCPosY/(self.fr1.winfo_reqheight()))
			"""
			#self.moveVar.set("canvasSPosY {0}, self.deltaPointerY {1} self.canvasCPosY {2}".format(self.canvasSPosY, self.deltaPointerY, self.canvasCPosY))
			#self.moveVar.set("self.canvasCPosY {0:.2f}, fr1.reqheight {1} self.canvasCPosY {2}".format(self.canvasCPosY, self.fr1.winfo_reqheight() - self.canvas.winfo_reqheight(), self.canvasCPosY))
			
			self.pMoveTime = self.cMoveTime
			self.cScrollSpeed = self.dPointerPosY/self.dMoveTime
			self.pointerVar.set("deltaPointer {0}, sPointerPosY {1}".format(self.deltaPointerY, self.sPointerPosY))
			
			self.pPointerPosY = self.cPointerPosY
			#updateCanvasPosition()
			self.speedVar.set("dPPosY {0:.2f}, dMTime {1:.2f} scrollSpeed {2:.2f}".format(self.dPointerPosY, self.dMoveTime, self.cScrollSpeed))
			
			
	
		def scrollOnPress(event):
			self.screenTouched = True
			if hasattr(self, "scrollLoop"):
				self.after_cancel(self.scrollLoop)
			self.scrollSTime = time.time()
			#pointer Y start position
			self.sPointerPosY = event.widget.winfo_pointerxy()[1]
			#pointer Y current position
			self.cPointerPosY = event.widget.winfo_pointerxy()[1]
			#pointer Y prev position
			self.pPointerPosY = event.widget.winfo_pointerxy()[1]
			#pointer Y difference between current and prev event position
			self.dPointerPosY = 0
			#time of previous event
			self.pMoveTime = time.time()
			#time difference between previous and current event
			self.dMoveTime = 0
			#pointer Y current position
			#canvas Y start position
			self.canvasSPosY = self.canvas.winfo_y()
			#canvas Y release position
			self.canvasCPosY = self.canvasSPosY
			#canvas Y release position
			if not hasattr(self, "canvasRPosY"):
				self.canvasRPosY = 0
			#if not hasattr(self, "canvasCPosY"):
				#self.canvasCPosY =  self.vscrollbar.get()[0]*(self.fr1.winfo_reqheight() + self.deltaPointerY)
			#else:
				#self.canvasCPosY = self.canvasSPosY + self.deltaPointerY
			#self.canvasSPosY = self.canvas.winfo_y()
			#self.canvasSPosY = self.canvasCPosY
			#self.focus_set()
			#self.canvasSPosY = self.vscrollbar.get()[0]*(self.fr1.winfo_reqheight() - self.winfo_screenheight())
			#self.canvasSPosYVar.set("cCpPosY {0} cSPosY {1} cRpPosY{2}".format(event.widget.winfo_pointerxy(), self.canvas.winfo_y(), self.canvasRPosY))
			
			#self.pointerVar.set("pointer {0}, sPointerPosY {1}".format(event.widget.winfo_pointerxy(), self.sPointerPosY))
	
		def scrollOnRelease(event):
			self.screenTouched = False
			if not hasattr(self, "cScrollSpeed"):
				self.cScrollSpeed = 0
			self.scrollETime = time.time()
			dTime = self.scrollETime - self.scrollSTime
			self.canvasRPosY = self.canvasCPosY
			#if not hasattr(self, "canvasCPosY"):
				#self.canvasCPosY = self.vscrollbar.get()[0]*(self.fr1.winfo_reqheight())
			#self.cPointerPosY = event.widget.winfo_pointerxy()[1]
			self.timeVar.set("scrollDTime{0:.3f}".format(dTime))
			#self.canvasSPosYVar.set("cCrPosY {0} cSPosY {1} cRrPosY{2}".format(self.canvasCPosY, self.canvas.winfo_y(), self.canvasRPosY))
			#self.after_cancel(self.scrollLoop)
			#self.speedVar.set("dPPosY {0:.2f}, dMTime {1:.2f} scrollSpeed {2:.2f}".format(self.dPointerPosY, self.dMoveTime, self.cScrollSpeed))
			#self.canvas.yview_moveto(self.canvasCPosY/(self.fr1.winfo_reqheight()*4))
			#self.cScrollSpeed = 500
			timeUpdate()
			
			#updateCanvasPosition()
			
		def updateCanvasPosition(*args):
			#currentUpdateTime
			if len(args) >0:
				event = args[0]
				#print("args[0] {0}, args[1] {1}".format(args[0], args[1]))
			if not self.screenTouched:
				self.cScrollSpeed *= self.accel
				self.canvasCPosY += self.cScrollSpeed
			else:
				pass
			#self.speedVar.set("dPPosY {0:.2f}, dMTime {1:.2f} scrollSpeed {2:.2f}".format(self.dPointerPosY, self.dMoveTime, self.cScrollSpeed))
			#self.timeVar.set("now {0:.3f}".format(self.now if hasattr(self, "now") else 0))
			#if not hasattr(self, "canvasCPosY"):
				#self.canvasCPosY = self.vscrollbar.get()[0]*(self.fr1.winfo_reqheight() + self.cScrollSpeed)
			#else:
			
			self.moveVar.set("CPosY {0:.2f}, fr1.reqheight {1} sb.get() {2}".format(self.canvasCPosY, self.fr1.winfo_reqheight() - self.canvas.winfo_reqheight(), self.vscrollbar.get()[0]*self.fr1.winfo_reqheight()))
			
			self.canvas.yview_moveto(self.canvasCPosY/(self.fr1.winfo_reqheight()))
			
			vsbPosYNorm = self.vscrollbar.get()[0]
			vsbPosY = vsbPosYNorm * self.fr1.winfo_reqheight()
			#self.vscrollbar.get()[0]*(self.fr1.winfo_reqheight() - self.winfo_screenheight())
			posDev = self.canvasCPosY - vsbPosY
			self.posDevVar.set("vsbYNorm {0:.3f} vsbY {1:.3f} pDev{2:.3f}".format(vsbPosYNorm, vsbPosY, posDev))
			
			#self.canvasSPosYVar.set("cCuPosY {0} cSPosY {1} cRuPosY{2}".format(self.canvasCPosY, self.canvas.winfo_y(), self.canvasRPosY))
				#self.after(self.cUTime, updateCanvasPosition)
			#else:
				 #pass	
		
		#self.bind("<B1-Motion>", onScrollMove)
		#self.bind('<Enter>', lambda _: self.bind_all('<ButtonPress-1>', timeUpdate), '+')
		self.bind("<Enter>", lambda _: self.bind_all('<ButtonPress-1>', scrollOnPress), '+')
		self.bind("<Leave>", lambda _: self.unbind_all('<ButtonPress-1>'), '+')
		#self.bind('<Map>', timeUpdate, '+')
		self.bind("<Enter>", lambda _: self.bind_all('<B1-Motion>', onScrollMove), '+')
		#self.bind("<Enter>", lambda _: self.bind('<B1-Motion>', onScrollMove), '+')
		self.bind("<Leave>", lambda _: self.unbind_all('<B1-Motion>'), '+')
		#self.bind("<Leave>", lambda _: self.unbind('<B1-Motion>'), '+')
		#self.bind("<ButtonPress-1>", scrollOnPress)
		#self.bind("<Enter>", lambda _: self.bind_all('<ButtonPress-1>', scrollOnPress), '+')
		#self.bind("<Enter>", lambda _: self.bind_all('<ButtonPress-1>', scrollOnPress), '+')
		
		
		#self.bind("<Leave>", lambda _: self.unbind_all('<ButtonPress-1>'), '+')
		#self.bind("<Leave>", lambda _: self.unbind('<ButtonPress-1>'), '+')
		#self.bind("<Enter>", lambda _: self.bind_all('<ButtonPress-1>', scrollOnPress), '+')
		#self.bind("<Leave>", lambda _: self.unbind_all('<ButtonPress-1>'), '+')
		#self.bind("<ButtonRelease-1>", scrollOnRelease)
		self.bind("<Enter>", lambda _: self.bind_all('<ButtonRelease-1>', scrollOnRelease), '+')
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
		bgCol = "orange"
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
					self.cell = Button(self.fr1, text="{0},{1}".format(r,c), image=img, font=('Arial',4), width=90, height=90, bg=bgCol, fg='gray')
					self.cell.imgList = []
					self.cell.imgList.append(img)
				elif c == 1:
					cText = results[r]['clashResultName']
					self.cell = Label(self.fr1, width=7, fg='white', font=('Arial',4), bg=bgCol, text="{0}".format(cText))
				elif c == 2:
					cText = results[r]['clashResultObjsAttrs'][0]['Element ID']
					self.cell = Label(self.fr1, width=7, bg=bgCol, fg='red', font=('Arial',4, 'bold'), text="{0}".format(cText))
					self.cell.bind("<ButtonRelease-1>", self.updateInfoText)
				elif c == 3:
					cText = results[r]['clashResultObjsAttrs'][1]['Element ID']
					self.cell.bind("<ButtonRelease-1>", self.updateInfoText)
					self.cell = Label(self.fr1, width=10, bg=bgCol, fg='green', font=('Arial',4, 'bold'), text="{0}".format(cText))
				elif c == 4:
					cText = results[r]['clashResultHref']
					self.cell = Label(self.fr1, bg=bgCol, fg='grey', font=('Arial',4), text="{0}".format(cText))
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
            
            #MAIN FRAME
            self.frame = VerticalScrolledFrame(root, clashTestsDict, width=self.winfo_screenwidth(), height=100, bg ="red")
            self.frame.pack(side=TOP, fill=BOTH, expand=TRUE)
            
            #INFO FRAME
            self.infoFrame = Frame(root, bg="yellow")
            self.infoFrame.pack(side=BOTTOM, fill=BOTH, expand=TRUE)
            
            #canvasSPosY LABEL
            self.cCPosYLabel = Label(self.infoFrame, textvariable=self.frame.canvasSPosYVar, text="Shrink the window to activate the scrollbar.")
            self.cCPosYLabel.pack(side=TOP)
            #POINTER LABEL
            self.pointerLabel = Label(self.infoFrame, textvariable=self.frame.pointerVar, text="Shrink the window to activate the scrollbar.")
            self.pointerLabel.pack(side=TOP)
            #DeltaPOINTER LABEL
            self.dPointerLabel = Label(self.infoFrame, textvariable=self.frame.dPointerVar, text="Shrink the window to activate the scrollbar.")
            self.dPointerLabel.pack(side=TOP)
            #MOVE LABEL
            self.moveLabel = Label(self.infoFrame, textvariable=self.frame.moveVar, text="Shrink the window to activate the scrollbar.")
            self.moveLabel.pack(side=TOP)
            #TIME LABEL
            self.timeLabel = Label(self.infoFrame, textvariable=self.frame.timeVar, text="Shrink the window to activate the scrollbar.")
            self.timeLabel.pack(side=TOP)
            #SPEED LABEL
            self.speedLabel = Label(self.infoFrame, textvariable=self.frame.speedVar, text="Shrink the window to activate the scrollbar.")
            self.speedLabel.pack(side=TOP)
            #Position deviation LABEL
            self.posDevLabel = Label(self.infoFrame, textvariable=self.frame.posDevVar, text="Shrink the window to activate the scrollbar.")
            self.posDevLabel.pack(side=TOP)
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

	
