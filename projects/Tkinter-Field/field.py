import xml.etree.ElementTree as ET
import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import time
#import kiwi
#import xmltodict

cwd = os.getcwd()
print("cwd {0}".format(cwd))
#runFileDialog = True

class VerticalScrolledFrame(Frame):
	def __init__(self, parent, *args, **kwargs):
		
		Frame.__init__(self, parent, *args, **kwargs)
		#self.createWidgets()
		#self.setGlobals()
		self.parent = parent
		self.screen_width = self.winfo_screenwidth()
		self.screen_height = self.winfo_screenheight()
		self.fHeight1 = self.screen_height*0.65
		self.fHeight2 = self.screen_height*0.3
		self.fWidth1 = self.screen_width*0.95
		
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
			self.canvas.config(bg="red")
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
		"""
		def on_press(evt):
			event.widget.winfo_pointerxy()[1]
			self.pointerVar.set("deltaPointer {0}, sPointerPosY {1}".format(self.pointerPY))
		
		def on_touch_scroll(evt):
			if evt.y_root-self.offset_y<0:
				evt.delta = -1
			else:
			     evt.delta = 1
			# canvas.yview_scroll(-1*(evt.delta), 'units') # For MacOS
			self.canvas.yview_scroll( int(-1*(evt.delta/120)) , 'units') # For windows
		"""
		def scrollOnPress(event):
			self.screenTouched = True
			#pointer Y start position
			self.sPointerPosY = event.widget.winfo_pointerxy()[1]
			self.pointerVar.set(" sPointerPosY {0}".format(self.sPointerPosY))
			
		def timeUpdate(*args):
			
			self.now = time.time() - self.scrollSTime
			
			
			#if now < 20:
			#if now < 2:
				
		self.bind("<Enter>", lambda _: self.bind_all('<ButtonPress-1>', scrollOnPress), '+')
		self.bind("<Leave>", lambda _: self.unbind_all('<ButtonPress-1>'), '+')

	def setup(self):
		self.fr1 = Frame(self.canvas)
		self.fr1_id = self.canvas.create_window(0, 0, window=self.fr1, anchor=NW)
		self.lst = []
		
	def setupCanvas(self):
		self.canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=self.vscrollbar.set)
		self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
		
	
	def updateInfoText(self, event):
		self.textVar.set(event.widget.cget('text')) 
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
            self.root = root
            #self.grid()
            #self.grid_propagate(1)
            #self.screen_width = root.winfo_screenwidth()
            #self.screen_height = root.winfo_screenheight()
            #print(self.screen_height)
            self.setup()
            self.pointerX = None
            self.pointerY = None
            #self.drawGrid(10,5)
            
        def drawGrid(self, cols, rows):
        	self.npGridX = np.linspace(0,1,cols*rows, dtype=np.float32, endpoint=True).reshape((cols,rows))
        	self.npGridY = np.linspace(1,2,cols*rows, dtype=np.float32, endpoint=True).reshape((cols,rows))
        	self.npGrid = np.dstack((self.npGridX, self.npGridY))
        	#self.npGrid.reshape((cols,rows))
        	print("npGridX {0}, shape {1} np.gridY {2} shape {3}\nself.npGrid {4}\nshape {5}".format(self.npGridX, self.npGridX.shape, self.npGridY, self.npGridY.shape, self.npGrid, self.npGrid.shape))
        	#raise TypeError("print")
        
        def getGridCoords(self):
        	pass
        	
        def setup(self):
			#MAIN FRAME
            self.frame = VerticalScrolledFrame(self.root, width=self.winfo_screenwidth(), height=100, bg ="red")
            self.frame
            self.frame.pack(side=TOP, fill=BOTH, expand=TRUE)
            
            #INFO FRAME
            self.infoFrame = Frame(self.root, bg="yellow")
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

	
