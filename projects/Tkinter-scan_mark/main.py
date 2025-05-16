# -*- coding: utf-8 -*- 
from tkinter import *
import tkinter as tk

class Viewer(Frame):
    def __init__(self, master,x=600,y=200, onLeft=None, onRight=None, **kwargs):
        self.root=master
        self.xsize=x
        self.ysize=y
        self.onLeft=onLeft
        self.onRight=onRight
        self.ratio=100.
        Frame.__init__(self, master,width=x,height=y, **kwargs)
        self.canvas = Canvas(self, width=x, height=y, background="white")
        self.xsb = Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.ysb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        self.canvas.configure(scrollregion=(0,0,x,y))

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.bind("<Button-1>", self.clickL)
        self.canvas.bind("<Button-3>", self.clickR)

        # This is what enables using the mouse:
        self.canvas.bind("<ButtonPress-1>", self.move_start)
        self.canvas.bind("<B1-Motion>", self.move_move)
        #linux scroll
        self.canvas.bind("<Button-4>", self.zoomerP)
        self.canvas.bind("<Button-5>", self.zoomerM)

        self.canvas.bind_all("<Prior>", self.zoomerP)
        self.canvas.bind_all("<Next>", self.zoomerM)
        self.canvas.bind_all("E", self.zoomExtens)
        #windows scroll
        self.canvas.bind_all("<MouseWheel>",self.zoomer)

    def reset(self):
        pass

    def set_title(self, title):
        self.root.title( title)

    #move
    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)
        return True
    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        return True

    #windows zoom
    def zoomer(self,event):
        if (event.delta > 0):
            self.ratio *= 1.1
        elif (event.delta < 0):
            self.ratio *= 0.9
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))

    def zoomExtens(self, *args):
        x0,y0,x1,y1 = self.canvas.bbox("all")
        xlen=x1-x0
        ylen=y1-y0
        height=self.canvas.winfo_height()
        width=self.canvas.winfo_width()
        unfit=min(width/float(xlen), height/float(ylen))
        self.ratio*=unfit
        self.redraw()
        #
        """"
        if xlen and ylen:
            self ratio*=
            self.canvas.scale("all", xlen/2., ylen/2., float(self.xsize)/xlen, float(self.ysize)/ylen)
            self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        """
    #linux zoom
    def zoomerP(self,event):
        self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
    def zoomerM(self,event):
        self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
    def pose2p(self, pose):
        x,y=pose[:2]
        return int(x*self.ratio), -int(y*self.ratio)

    def line2p(self, line):
        if type(line[0]) in (float, int):
            line=zip(line[::2],line[1::2])
        return map(self.pose2p, line)
    def p2m(self, x, y):
        return x/self.ratio, -y/self.ratio
    def create_line(self, coords, **kwargs):
        return self.canvas.create_line(self.line2p(coords), **kwargs)
    def create_polygon(self, coords, **kwargs):
        return self.canvas.create_polygon(self.line2p(coords), **kwargs)
    def delete(self, object):
        self.canvas.delete(object)

    def clickL(self, event):
        if self.onLeft:
            x,y=self.p2m(int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y)))
            self.onLeft(x,y)
        return True

    def clickR(self, event):
        if self.onRight:
            x,y=self.p2m(int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y)))
            self.onRight(x,y)
        return True

if __name__ == '__main__':
	mainWindow = Tk()
	mainWindow.grid()
	mainWindow.grid_propagate(1)
	app = Viewer(mainWindow)
	app.master.title("scan_mark")
	app.mainloop()
    #my_gui=Viewer()	
    #my_gui.mainloop()