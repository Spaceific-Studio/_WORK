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
        self.insertedPoints = []
        self.theta = 0
        self.chkbtn1Var = IntVar(0)
        self.chkbtn1Var.trace_add("write", self.changePoint)
        self.v.set("xxxxxxxxxxxxxx")
        self.ovalX = 0.0
        self.ovalY = 0.0
        self.oval2X = 0.0
        self.oval2Y = 0.0
        self.ovalRadius = 20
        self.oval2Radius = 30
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
        self.canvas.bind("<Button-1>", self.insertPoint)
        
        self.cScrollbarY.config(command=self.canvas.yview)
        self.cScrollbarX.config(command=self.canvas.xview)
        self.updateCanvas()
        self.fr2 = Frame(self.master,width=self.fWidth2, height=self.fHeight2, bg='cyan')
        self.fr2.grid(row=2, column=0, columnspan=2, sticky=E+W)
        #Sliders setup
        
        self.slider1 = Scale(self.fr2,from_=0.0, to=self.fr1.cget("width"), orient=HORIZONTAL, length=self.fr2.cget("width")/2, width=45, resolution = 0.001, command = self.getSlider1Value, showvalue=0).grid(row=0, column=0, columnspan=2,sticky=W+N)
        self.slider2 = Scale(self.fr2,from_=0.0, to=self.fr1.cget("width"), orient=HORIZONTAL, length=self.fr2.cget("width")/2, width=45, resolution = 0.001, command = self.getSlider2Value, showvalue=0).grid(row=0, column=2, columnspan=2,sticky=W+N)
        self.slider3 = Scale(self.fr2,from_=0.0, to=self.fr1.cget("height"), orient=VERTICAL, width=45, resolution = 0.001, command = self.getSlider3Value, showvalue=0).grid(row=1, column=0,sticky=W+N+S)
        self.slider4 = Scale(self.fr2,from_=0.0, to=250, orient=VERTICAL, width=45, resolution = 0.001, command = self.getSlider4Value, showvalue=0).grid(row=1, column=0, sticky=N+S)
        self.slider5 = Scale(self.fr2,from_=0.0, to=250, orient=VERTICAL, width=45, resolution = 0.001, command = self.getSlider5Value, showvalue=0).grid(row=1, column=3, sticky=N+S)
        self.slider6 = Scale(self.fr2,from_=0.0, to=self.fr1.cget("height"), orient=VERTICAL, width=45, resolution = 0.001, command = self.getSlider6Value, showvalue=0).grid(row=1, column=3, sticky=E+N+S)
        
        #Label setup
        self.label1 = Label(self.fr2,text="xxxxxxxxxx",textvariable=self.v,wraplength=self.fWidth2, justify = LEFT).grid(row=2,column=0, columnspan=4, sticky=E+W+N+S)
        #Checkbutton setup
        self.chkButton1 = Checkbutton(self.fr2,                    text = "origin/point",                         var=self.chkbtn1Var).grid(row=3, 
                column=0,
                columnspan=4, 
                sticky = S+W+E)
        #self.chkButton1.bind('<Button-1>', self.changePoint)
        
        #self.fr2.bind('<Motion>', self.motion)
        
    def updateCanvas(self):
        self.canvas.delete("all")
        
        #oval properties
        
        ovalCenter = (self.ovalX, self.ovalY)
        oval2Center = (self.oval2X, self.oval2Y)
        tCoords = self.get2CTangent(ovalCenter, self.ovalRadius, oval2Center, self.oval2Radius)
        self.v.set("{0:3.2f} - {1:3.2f} -{2:3.2f} - {3:3.2f}\ntheta {4:3.2f}".format(tCoords[0], tCoords[1], self.arcBP1StartAngle, self.conjSegVecAngle, self.theta))
        baseOvalBBox = ((self.basePoint2[0]-self.baseRadius, self.basePoint2[1] - self.baseRadius), (self.basePoint2[0]+self.baseRadius, self.basePoint2[1] + self.baseRadius))
        ovalBbox = ((ovalCenter[0]-self.ovalRadius, ovalCenter[1]-self.ovalRadius),(ovalCenter[0]+self.ovalRadius, ovalCenter[1]+self.ovalRadius))
        oval2Bbox = ((oval2Center[0]-self.oval2Radius, oval2Center[1]-self.oval2Radius),(oval2Center[0]+self.oval2Radius, oval2Center[1]+self.oval2Radius))
        self.canvas.create_oval(ovalBbox)
        self.canvas.create_oval(oval2Bbox)
        
        self.canvas.create_arc(ovalBbox, fill="Orange", style="pieslice", start=self.arcBP2StartAngle, extent=360-self.archExtendAngle)
        self.canvas.create_arc(oval2Bbox, fill="Orange", style="pieslice", start=self.arcBP1StartAngle, extent=self.archExtendAngle)
        
        self.canvas.create_oval(baseOvalBBox, fill="Yellow")
        self.canvas.create_line([ovalCenter, oval2Center], fill="Yellow")
        self.canvas.create_line([self.basePoint1, self.bTP1], fill="Cyan")
        self.canvas.create_line([self.basePoint1, self.bTP2], fill="Red")
        self.canvas.create_line([self.tP1r[0], self.tP1r[1], self.tP2r[0], self.tP2r[1]])
        self.canvas.create_line([self.tP1l[0], self.tP1l[1], self.tP2l[0], self.tP2l[1]])
        #drawing points
        radius = 5
        ovalTP1rBBox = ((self.tP1r[0]-radius, self.tP1r[1]-radius), (self.tP1r[0]+radius, self.tP1r[1]+radius))
        ovalTP2rBBox = ((self.tP2r[0]-radius, self.tP2r[1]-radius), (self.tP2r[0]+radius, self.tP2r[1]+radius))
        self.canvas.create_oval(ovalTP1rBBox)
        self.canvas.create_oval(ovalTP2rBBox)
        ovalTP1lBBox = ((self.tP1l[0]-radius, self.tP1l[1]-radius), (self.tP1l[0]+radius, self.tP1l[1]+radius))
        ovalTP2lBBox = ((self.tP2l[0]-radius, self.tP2l[1]-radius), (self.tP2l[0]+radius, self.tP2l[1]+radius))
        self.canvas.create_oval(ovalTP1lBBox)
        self.canvas.create_oval(ovalTP2lBBox)
        
#        for point in self.insertedPoints:
#            ovalBBox = ((point[0]-radius, point[1]-radius), (point[0]+radius, point[1]+radius))
#            self.canvas.create_oval(ovalBBox)
#            #drawing line - point to oval center
#            #self.canvas.create_line([(point[0],point[1]),(self.ovalX, self.ovalY)], fill = "Orange")
#            #drawing tangent lines to oval
#            p2r = self.getTangentPoint(point, (self.ovalX, self.ovalY), self.ovalRadius)
#            p2l = self.getTangentPoint(point, (self.ovalX, self.ovalY), self.ovalRadius, left=True)
#            if p2r:
#                self.canvas.create_line([point,p2r], fill = "Cyan")
#            if p2l:
#                self.canvas.create_line([point,p2l], fill = "Yellow")

    def insertPoint(self,event):
        text = self.v.get()
        xCoord = event.x
        yCoord = event.y
        self.insertedPoints.append((xCoord, yCoord))
        text = ""
        for i, point in enumerate(self.insertedPoints):
            if i > len(self.insertedPoints)-4:
                text += "{0}, {1}\n".format(point[0], point[1])
                
        text += "len(self.insertedPoints) {0}\n".format(len(self.insertedPoints))
        self.v.set(text)
        
        self.updateCanvas()
        
    
    def pushButton(self, event):
        self.label1.config(text="{0}".format(event.widget.cget("text")))
        
    def getSlider4Value(self, event):
        self.ovalRadius = float(event)
        #self.v.set("current angle {0} type {1}".format(self.currentAngle, type(self.currentAngle)))
        self.updateCanvas()
    
    def getSlider1Value(self, event):
        self.ovalX = float(event)
        self.updateCanvas()
    
    def getSlider3Value(self, event):
        self.ovalY = float(event)
        self.updateCanvas()
    
    def getSlider2Value(self, event):
        self.oval2X = float(event)
        self.updateCanvas()
    
    def getSlider5Value(self, event):
        self.oval2Radius = float(event)
        #self.v.set("current angle {0} type {1}".format(self.currentAngle, type(self.currentAngle)))
        self.updateCanvas()
    
    def getSlider6Value(self, event):
        self.oval2Y = float(event)
        self.updateCanvas()
        
        
    def get2CTangent(self, inCP1, inR1, inCP2, inR2):
        if inR1 > inR2:
            #conjunction segment of 2 centers
            self.conjSegVec = (inCP1[0] - inCP2[0], inCP1[1] - inCP2[1])
            #center point with smaler diameter
            self.basePoint1 = inCP2
            #center point with bigger diameter
            self.basePoint2 = inCP1
            #circle with smaller diameter
            self.radius1 = inR2
            #circle with bigger diameter
            self.radius2 = inR1
            #radius of base circle (inR1 - inR2) the yellow one
            self.baseRadius = inR1 - inR2
        else:
            self.conjSegVec = (inCP2[0] - inCP1[0], inCP2[1] - inCP1[1])
            self.basePoint1 = inCP1
            self.basePoint2 = inCP2
            self.radius1 = inR1
            self.radius2 = inR2
            #radius of base circle (inR2 - inR1)
            self.baseRadius = inR2 - inR1
        bP1Np = np.asarray(self.basePoint1, dtype = np. float32)
        bP2Np = np.asarray(self.basePoint2, dtype = np. float32)
        bPSubtracted = np.subtract(bP1Np, bP2Np)
        bpNorm = np.linalg.norm(bPSubtracted)
        
        # if length between center points is heigher then R1 + R2
        #if bpNorm > inR1 + inR2:
        if bpNorm + self.radius1 > self.radius2:
            self.conjSegVecNp = np.asarray(self.conjSegVec, dtype = np.float32)
            self.conjSegVecNorm = np.linalg.norm(self.conjSegVecNp)
            self.conjSegVecUnit = np.multiply(self.conjSegVecNp, 1/self.conjSegVecNorm)
            # base Tangent Point1
            self.bTP1 =self.getTangentPoint(self.basePoint1, self.basePoint2, self.baseRadius, left = False)
            bTP1Np = np.asarray(self.bTP1, dtype = np. float32)
            self.tP1rVec = np.subtract( bTP1Np, bP2Np)
            self.tP1rNorm = np.linalg.norm(self.tP1rVec)
            self.tP1rUnit = np.multiply(self.tP1rVec, 1/self.tP1rNorm)
            self.tP1r = np.add(self.basePoint2,np.multiply(self.tP1rUnit, self.radius2))
            self.tP2r = np.add(self.basePoint1,np.multiply(self.tP1rUnit, self.radius1))
            # base Tangent Point2
            self.bTP2 =self.getTangentPoint(self.basePoint1, self.basePoint2, self.baseRadius, left = True)
            bTP2Np = np.asarray(self.bTP2, dtype = np. float32)
            self.tP1lVec = np.subtract( bTP2Np, bP2Np)
            self.tP1lNorm = np.linalg.norm(self.tP1lVec)
            self.tP1lUnit = np.multiply(self.tP1lVec, 1/self.tP1lNorm)
            self.tP1l = np.add(self.basePoint2,np.multiply(self.tP1lUnit, self.radius2))
            self.tP2l = np.add(self.basePoint1,np.multiply(self.tP1lUnit, self.radius1))
            xAxis = np.asarray((1,0), dtype = np.float32)
            if self.conjSegVecUnit[1] > 0:
                self.conjSegVecAngle = np.rad2deg(math.acos(xAxis.dot(self.conjSegVecUnit)))
            else:
                self.conjSegVecAngle = 360 - np.rad2deg(math.acos(xAxis.dot(self.conjSegVecUnit)))
            self.theta =180 - np.rad2deg(math.acos(self.conjSegVecUnit.dot(self.tP1rUnit))) if inR1 > inR2 else np.rad2deg(math.acos(self.conjSegVecUnit.dot(self.tP1rUnit)))
            self.thetaBP2 = np.rad2deg(math.acos(self.conjSegVecUnit.dot(self.tP1rUnit))) if inR1 > inR2 else np.rad2deg(math.acos(self.conjSegVecUnit.dot(self.tP1rUnit)))
            self.archExtendAngle = self.theta*2
            
            self.arcBP1StartAngle = 180 - self.conjSegVecAngle - self.theta if inR1 > inR2 else -self.conjSegVecAngle - self.theta
            self.arcBP2StartAngle = -self.conjSegVecAngle - self.thetaBP2 if inR1 > inR2 else  360 -self.conjSegVecAngle + self.thetaBP2
            
        else:
            self.bTP1 = self.basePoint2
            self.bTP2 = self.basePoint2
            self.tP1r = self.basePoint2
            self.tP2r = self.basePoint1
            self.tP1l = self.basePoint2
            self.tP2l = self.basePoint1
            self.arcBP1StartAngle = 0
            self.arcBP2StartAngle = 0
            self.conjSegVecAngle = 0
            self.archExtendAngle =0
            self.theta = 0
            
            
        
        return self.conjSegVec
        
    def getTangentPoint(self,inP1, inCP, inRadius, **kwargs):
        left = kwargs["left"] if "left" in kwargs else False
        #vec1 = (inCP[0] - inP1[0], inCP[1] - inP1[1])
        #vec1Np = np.asarray(vec1, dtype = np. float32)
        p1Np = np.asarray(inP1, dtype = np. float32)
        cpNp= np.asarray(inCP, dtype = np. float32)
        vec1Np = np.subtract(cpNp, p1Np)
        vec1Norm = np.linalg.norm(vec1Np)
        if float(vec1Norm > inRadius):
            vec1Unit = vec1Np / vec1Norm
            vec2Norm = math.sqrt((vec1Norm**2) - (inRadius**2))
            alpha = np.rad2deg(math.acos(vec2Norm/vec1Norm))
            rotVec = self.rotVecOrigin(vec1Unit, alpha if left else -alpha)
            #xAxis = np.asarray((1,0), dtype = np. float32)
            #vec1UnitAngle = np.rad2deg(math.acos(vec1Unit.dot(xAxis)))
            #vec2UnitAngle = np.rad2deg(math.acos(rotVec.dot(xAxis)))
            rotVecNorm = np.add(np.multiply(rotVec, vec2Norm), p1Np)
            p2 = (rotVecNorm[0], rotVecNorm[1])
            #checkRot = np.rad2deg(math.acos(vec1Np.dot(rotVec)))
            #return (vec2Norm/vec1Norm, np.rad2deg(math.acos(vec2Norm/vec1Norm)))
            return p2
            #return (alpha, vec1UnitAngle,vec2UnitAngle)
        else:
            return None
        
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
        #self.v.set(self.v.get() + "\nthetaDegrees = {0}\nthetaRad = {1}".format(inDegrees, thetaRad))
        rotMx = [(math.cos(thetaRad), -math.sin(thetaRad)), \
                 (math.sin(thetaRad), math.cos(thetaRad))]
        rotNpMx = np.asarray(rotMx, dtype=np.float32)
        #print("rotNpMx {0} shape {1}".format(rotNpMx, rotNpMx.shape))
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
