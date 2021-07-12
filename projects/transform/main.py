import math
from tkinter import *
from PIL import Image, ImageDraw, ImageTk
import numpy as np
import sys
import os
#import subprocess
#import re
import platform

def pushButton(event):
    label1.config(text="{0}".format(event.widget.cget("text")))
    
def pushToCanvas(inCanvas, inObj):
    if isinstance(inObj, Image):
        img = PhotoImage(inObj)
        inCanvas.create_image(0,0, image = img)
    elif isinstance(inObj, list):
        inCanvas.create_line(inObj)
        
imgPath =r"/storage/emulated/0/_WORK/projects/transform/data/"
imgFileName = "screen.jpg"
img = Image.new(mode="RGB", size=(200,200))
imgSavePath = os.path.join(imgPath, imgFileName)
img2FileName = "download_20200830_124806.jpg"
img2OpenPath = os.path.join(imgPath, img2FileName)
img2 = Image.open(os.path.join(imgPath, img2FileName))
#img2.save(os.path.join(imgPath,"ss.jpg"))

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = "yellow", bd = 1)
        #self.createWidgets()
        #self.setGlobals()
        self.master = master
        self.screen_width = master.winfo_screenwidth()
        self.screen_height = master.winfo_screenheight()
        self.fHeight1 = self.screen_height*0.65
        self.fHeight2 = self.screen_height*0.3
        self.fWidth1 = self.screen_width*0.95
        self.fWidth2 = self.screen_width
        self.currentAngle = 0.0
        self.setup()
        
    def setup(self):
        self.v = StringVar()
        self.chkbtn1Var = IntVar(0)
        self.chkbtn1Var.trace_add("write", self.changePoint)
        self.v.set("xxxxxxxxxxxxxx")
        self.ovalX = 0.0
        self.ovalY = 0.0
        #self.master.bind('<Motion>', self.motion)
        self.fr1 = Frame(self.master, height=self.fHeight1, width=self.fWidth1, bg='yellow')
        self.fr1.grid(row=0, column=0, sticky=W)
        self.cScrollbarY = Scrollbar(self.master, orient=VERTICAL)
        self.cScrollbarY.grid(row=0, column=1, sticky=W+E+S+N)
        self.cScrollbarX = Scrollbar(self.master, orient=HORIZONTAL)
        self.cScrollbarX.grid(row=1, column=0, sticky=N+W+E)
        self.canvas = Canvas(self.fr1, bg = "gray", width = self.fWidth1, height = self.fHeight1, yscrollcommand=self.cScrollbarY.set, xscrollcommand=self.cScrollbarX.set)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.imageList = []
        self.canvas.place (x= 0, y=0)
        self.cScrollbarY.config(command=self.canvas.yview)
        self.cScrollbarX.config(command=self.canvas.xview)
        self.updateCanvas()
        self.fr2 = Frame(self.master,width=self.fWidth2, height=self.fHeight2, bg='cyan')
        self.fr2.grid(row=2, column=0, columnspan=2, sticky=E+W)
        #Sliders setup
        self.slider1 = Scale(self.fr2,from_=0.0, to=math.pi*2, orient=VERTICAL, width=45, resolution = 0.001, command = self.getSlider1Value, showvalue=0).grid(row=1, column=0, sticky=W+N+S)
        self.slider2 = Scale(self.fr2,from_=0.0, to=self.fr1.cget("width"), orient=HORIZONTAL, length=self.fr2.cget("width"), width=45, resolution = 0.001, command = self.getSlider2Value, showvalue=0).grid(row=0, column=0, columnspan=3,sticky=W+N)
        self.slider3 = Scale(self.fr2,from_=0.0, to=self.fr1.cget("height"), orient=VERTICAL, width=45, resolution = 0.001, command = self.getSlider3Value, showvalue=0).grid(row=1, column=2,sticky=E+N+S)
        #Label setup
        self.label1 = Label(self.fr2,text="xxxxxxxxxx",textvariable=self.v,wraplength=self.fWidth2, justify = LEFT).grid(row=1,column=1, sticky=E+W+N+S)
        #Checkbutton setup
        self.chkButton1 = Checkbutton(self.fr2,                    text = "origin/point",                         var=self.chkbtn1Var).grid(row=2, 
                column=0,
                columnspan=2, 
                sticky = S+W)
        #self.chkButton1.bind('<Button-1>', self.changePoint)
        
        #self.fr2.bind('<Motion>', self.motion)
        
    def updateCanvas(self):
        self.canvas.delete("all")
        #self.canvas.create_line([(50,10),(100,100)])
        #img2FileName = "download_20200830_124806.jpg"
        #img2OpenPath = os.path.join(imgPath, img2FileName)
        #img2 = Image.open(os.path.join(imgPath, img2FileName))
        #rImg = img2.resize((100,100))
        #tkImg = ImageTk.PhotoImage(img2)
        #self.canvas.create_image(100, 100 ,image = tkImg, anchor = NW)
        #self.canvas.imageList.append(tkImg)
        
        #oval properties
        ovalCenter = (self.ovalX, self.ovalY)
        ovalRadius = 10
        ovalBbox = ((ovalCenter[0]-ovalRadius, ovalCenter[1]-ovalRadius),(ovalCenter[0]+ovalRadius, ovalCenter[1]+ovalRadius))
        self.canvas.create_oval(ovalBbox)
        #oval2 properties
        oval2InitCoord = (-10,-50)
        currentRotPoint = oval2InitCoord if self.chkbtn1Var.get() ==1 else ovalCenter
        oval2RotCoords = self.rotAtPoint((0,0), np.deg2rad(self.currentAngle), currentRotPoint)
        
        oval2Bbox = ((oval2RotCoords[0]-ovalRadius, oval2RotCoords[1]-ovalRadius),(oval2RotCoords[0]+ovalRadius, oval2RotCoords[1]+ovalRadius))
        
        self.canvas.create_oval(oval2Bbox, fill="Orange")
        length = 300
        vec1 = (300, 0)
        vec1Np = np.asarray(vec1, dtype = np. float32)
        vec1Norm = np.linalg.norm(vec1Np)
        vec1Unit = vec1Np / vec1Norm
        vec2 = (0, 190)
        vec2Np = np.asarray(vec2, dtype = np. float32)
        vec2Norm = np.linalg.norm(vec2Np)
        vec2Unit = vec2Np / vec2Norm        
        vec1DotVec2 = vec1Unit.dot(vec2Unit)
        vec2DotVec1 = vec2Unit.dot(vec1Unit)
        self.v.set("oval2rotCoords {0}\nchkbtn1Var {1}\nvec1Norm {2}\nvec1Unit {3}\nvec2Norm {4}\nvec2Unit {5}\nvec1DotVec2 {6}\nvec2DotVec1 {7}".format(oval2RotCoords, self.chkbtn1Var.get(), vec1Norm, vec1Unit, vec2Norm, vec2Unit, vec1DotVec2, vec2DotVec1))
        self.canvas.create_line([(0,0),(vec1[0],vec1[1])], fill = "Green")
        self.canvas.create_line([(0,0),(vec2[0],vec2[1])], fill = "Cyan")
        
        self.canvas.create_line([(0,0),(vec1[0] * vec1DotVec2, vec1[1] *vec1DotVec2)], fill = "Orange")
        
        
        #vec1rtd = self.rotVecOrigin(vec1,10)
        #vec2rtd = self.rotVecOrigin(vec1,-10)
        #self.v.set("vec1 = ({0:.2f},{1:.2f})\nvec1rtd = ({2:.2f},{3:.2f})\ndeg {4:.2f}\nrad {5:.2f}\nX = {6:.2f}\nY = {7:.2f}".format(vec1[0], vec1[1], vec1rtd[0], vec1rtd[1], self.currentAngle, np.deg2rad(self.currentAngle), self.ovalX, self.ovalY))
        
        #self.canvas.create_line([(0,0),(vec1rtd[0],vec1rtd[1])], fill="Red")
        #self.canvas.create_line([(0,0),(vec2rtd[0],vec2rtd[1])], fill="Blue")
        
    def pushButton(self, event):
        self.label1.config(text="{0}".format(event.widget.cget("text")))
        
    def getSlider1Value(self, event):
        self.currentAngle = np.rad2deg(float(event))
        #self.v.set("current angle {0} type {1}".format(self.currentAngle, type(self.currentAngle)))
        self.updateCanvas()
    
    def getSlider2Value(self, event):
        self.ovalX = float(event)
        self.updateCanvas()
    
    def getSlider3Value(self, event):
        self.ovalY = float(event)
        self.updateCanvas()
        
    def rotAtPoint(self, inPoint, inRad, inCenterPoint):
        inPointNp = np.asarray(inPoint, dtype=np.float32)
        inCenterPointNp = np.asarray(inCenterPoint, dtype=np.float32)
        delta = inPointNp - inCenterPointNp
        self.v.set("delta {0}".format(delta))
        #deltaMx = [(delta[0], 0), \
        #           (0, delta[1])]
        #deltaMx = [(delta[0], 0), \
        #           (0, delta[1])]
        #deltaNpMx = np.asarray(deltaMx, dtype=np.float32)
        inCenterPointNp = np.asarray(inCenterPoint, dtype=np.float32)
        moveCenterMx = [(inCenterPoint[0], 0),\
                        (0, inCenterPoint[1])]
        moveCenterNpMx = np.asarray(moveCenterMx, dtype = np.float32)
        rotMx = [(math.cos(inRad), -math.sin(inRad)), \
                 (math.sin(inRad), math.cos(inRad))]
        rotNpMx = np.asarray(rotMx, dtype=np.float32)
        #return deltaNpMx.dot(rotNpMx) + moveCenterNpMx
        return delta.dot(rotNpMx) + inCenterPointNp
        #return delta
        
        
            
    def rotVecOrigin(self, inVec, inDegrees):
        vecNp = np.asarray(inVec, dtype=np.float32)
        thetaRad = np.deg2rad(inDegrees)
        self.v.set(self.v.get() + "\nthetaDegrees = {0}\nthetaRad = {1}".format(inDegrees, thetaRad))
        rotMx = [(math.cos(thetaRad), -math.sin(thetaRad)), \
                 (math.sin(thetaRad), math.cos(thetaRad))]
        rotNpMx = np.asarray(rotMx, dtype=np.float32)
        print("rotNpMx {0} shape {1}".format(rotNpMx, rotNpMx.shape))
        return vecNp.dot(rotNpMx)
    
    def changePoint(self, *args, **kwargs):
        self.updateCanvas()
        print("self.chkbtn1Var {0}".format(self.chkbtn1Var))
        
    
    def motion(self,event):
        x, y = event.x, event.y
        #print('{}, {}'.format(x, y))
        self.v.set('{}, {}'.format(x, y))
        
mainWindow = Tk()
mainWindow.grid()
mainWindow.grid_propagate(1)

app = App(mainWindow)
app.master.title("Transform app")
app.mainloop()

#oSystemName = os.uname()[0]
#osNodeName = os.uname()[1]
#osRelease = os.uname()[2]
#osVersion = os.uname()[3]
#osMachine = os.uname()[4]
#print("oSystemName = {0}\nosNodeName = {1}\nosRelease = {2}\nosVersion {3}\nosMachine = {4}".format(oSystemName, osNodeName, osRelease, osVersion, osMachine))
#print("os.uname() {0}".format(os.uname()))
#print("platform.system() {0}".format(platform.system()))
#print("platform Linux") if platform.system() == "Linux" else print("noPlatforName")
