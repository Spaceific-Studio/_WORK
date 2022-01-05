# -*- coding: utf-8 -*- 
from tkinter import *
import tkinter as tk
import time
from PIL import Image, ImageTk
import os

class TapScreen(Tk):
	
	def __init__(self):
		Tk.__init__(self)
		self.scrollBarWidth = 50
		self.screenWidth = self.winfo_screenwidth() - self.scrollBarWidth
		self.screenHeight = 1400
		self.setup()
		
		
		
	
	def setup(self):
		#CANVAS
		self.sTime = time.time()
		print("cwd {0}".format(os.getcwd()))
		imgPath = r"/storage/emulated/0/_WORK/projects/XML/clashtest/SO_03-02-ARS- MEC - hard_files/cd000002.jpg"
		img = Image.open(imgPath)
		rImg = img.resize((800,800))
		tkImg = ImageTk.PhotoImage(rImg)
		
		#Slowest update time
		self.sUTime = 0.5
		self.canvas = Canvas(self, width=self.screenWidth, height=self.screenHeight, bg="pink")
		self.canvas.grid(row=0, column=0, sticky=EW)
		self.canvas.imageList = []
		#self.canvas.bind("<Enter>", self.on_touch_scroll)
		#self.canvas.bind("<Leave>", self.on_touch_scroll)
		#self.bind("<B1-Motion>", self.updateInfoText)
		self.bind("<ButtonPress-1>", self.scrollOnPress)
		self.bind("<ButtonRelease-1>", self.scrollOnRelease)
		self.bind("<B1-Motion>", self.onScrollMove)
		self.canvas.create_line(0,0,50,50)
		self.canvas.create_image(500,500, image=tkImg)
		self.canvas.imageList.append(tkImg)
		self.canvasHeight = self.canvas.winfo_reqheight()
		self.canvas.xview_moveto(0)
		self.canvas.yview_moveto(0)
		#self.canvas.config( yscrollcommand=self.updateCanvasPosition)
		
		
		#INFOFRAME
		self.infoFrame = Frame(self, width=self.screenWidth, height=300, bg="beige")
		self.infoFrame.grid(row=1, column=0, sticky=EW)
		
		#INFOLABEL
		self.textVar = StringVar()
		self.infoLabel = Label(self.infoFrame, textvariable=self.textVar, text="textinfo", font=('Arial',10))
		self.infoLabel.grid(row=0, column=0, sticky=EW)
		
		#TIMELABEL
		self.timeVar = StringVar()
		self.timeVar.set("1")
		self.timeLabel = Label(self.infoFrame, textvariable=self.timeVar, text="time", font=('Arial',10))
		self.timeLabel.grid(row=1, column=0, sticky=EW)
		
		#POINTERLABEL
		self.pointerVar = StringVar()
		self.pointerVar.set(0)
		self.pointerLabel = Label(self.infoFrame, textvariable=self.pointerVar, text="pointer", font=('Arial',10))
		self.pointerLabel.grid(row=2, column=0, sticky=EW)
		
		#DELTAPOINTERLABEL
		self.dPointerVar = StringVar()
		self.dPointerVar.set("delta")
		self.dPointerLabel = Label(self.infoFrame, textvariable=self.dPointerVar, text="dPointer", font=('Arial',10))
		self.dPointerLabel.grid(row=3, column=0, sticky=EW)
		
		#COUNTDOWNLABEL
		self.countDownVar = StringVar()
		self.countDownVar.set("countDown")
		self.countDownLabel = Label(self.infoFrame, textvariable=self.countDownVar, text="countDown", font=('Arial',10))
		self.countDownLabel.grid(row=4, column=0, sticky=EW)
		
		#MOVELABEL
		self.moveVar = StringVar()
		self.moveVar.set("moveCoords")
		self.moveLabel = Label(self.infoFrame, textvariable=self.moveVar, text="move", font=('Arial',10))
		self.moveLabel.grid(row=5, column=0, sticky=EW)
		
		#self.updateClock()
	def onScrollMove(self, event):
		pointerYpos = event.widget.winfo_pointerxy()[1]
		self.cPointerPosY = event.widget.winfo_pointerxy()[1]
		self.deltaPointerY = self.cPointerPosY - self.sPointerPosY
		self.canvasCPosY = self.canvasSPosY + self.deltaPointerY
		self.canvas.yview_moveto(self.canvasCPosY/self.canvasHeight)
		self.moveVar.set("canvasSPosY {0}, self.deltaPointerY {1} self.canvasCPosY {2}".format(self.canvasSPosY, self.deltaPointerY, self.canvasCPosY))
		
	def scrollOnPress(self, event):
		self.scrollSTime = time.time()
		self.canvasSPosY = self.canvas.winfo_rooty()
		self.sPointerPosY = event.widget.winfo_pointerxy()[1]
		self.pointerVar.set("pointer {0}, sPointerPosY {1}".format(event.widget.winfo_pointerxy(), self.sPointerPosY))
		
	def scrollOnRelease(self, event):
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
		self.updateCanvasPosition()
		
	def updateCanvasPosition(self, *args):
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
			self.after(self.cUTime, self.updateCanvasPosition)
		elif self.countDown <0:
			self.countDown +=1
			self.countDownNorm = self.countDown / self.dPointerPosY
			self.countDownVar.set("{0} norm {1:.3f}".format(self.countDown, self.countDownNorm))
			self.canvas.yview_moveto(self.canvasCPosY)
			self.after(self.cUTime, self.updateCanvasPosition)
		else:
			 pass
			 		
	def on_touch_scroll(self, event):
		yPosOld = event.y_root
		self.canvas.xview_moveto(10)
		self.canvas.yview_moveto(50)
		myDelta = event.delta
		self.textVar.set("{0}".format(yPosOld))
		
	def updateClock(self):
		timeNow = time.time()
		dTime = timeNow - self.sTime
		self.timeVar.set("{0:.3f}".format(dTime))
		self.after(50, self.updateClock)
		
	def updateInfoText(self, event):
		if not hasattr(self, "c"):
			self.c = 1
		else:
			self.c = self.c +1
		self.textVar.set("{0}".format(self.c))
		self.canvas.xview_moveto(100)
		self.canvas.yview_moveto(self.c)
			
if __name__ == '__main__':
	#mainWindow = Tk()
	#mainWindow.grid()
	#mainWindow.grid_propagate(1)
	#app = zoomer(mainWindow)
	#app.master.title("zoom app")
	#app.mainloop()
    my_gui=TapScreen()	
    my_gui.mainloop()