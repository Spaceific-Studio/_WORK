# -*- coding: utf-8 -*-
# from log import *
from ca_func import *
# from display_func import *
import os
import Tkinter as tk
from Tkinter import *
from PIL import ImageTk
import ttk
win = tk.Tk()
resX = 51
resY = 51
layCount = 20
myHexRule = "5b025a0a224a001444044416240200005a88088e080c01310880010000004300c380c2008080900e800c8020080100002000004c0000222a0008040000008a0"
myBinRule = getBinRuleFromHex(myHexRule)
CSV_logPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/LOG/"
logReadPath = CSV_logPath + "CA2D9_" + myHexRule + "_" + str(resX) + "x" + str(resY) + ".csv"
logWritePath = CSV_logPath + "CA2D9_" + myHexRule + "_" + str(resX) + "x" + str(resY) + ".csv"
print(myHexRule)
myCaImgs = run(resX, resY, layCount, myBinRule, logWritePath, True)
print(myCaImgs)
myTkImgs = []
for i, img in enumerate(myCaImgs):
    image = ImageTk.PhotoImage(img)
    myTkImgs.append(image)



#-----------------------
#Graphics
#-----------------------

win.title("Python GUI")
#win.resizeable(0,0)
aLabel = ttk.Label(win, text=myHexRule)
aLabel.grid(column = 0, row = 1)

#Button click function
def clickMe():
    #action.configure(text="myHexRule = " + name.get())
    myHexRule = name.get()
    aLabel.configure(text="myHexRule = " + name.get())
    print (myHexRule)
#Changing our Label
ttk.Label(win, text="Enter a name").grid(column=0, row=0)

#Adding a textbox entry widget
name = tk.StringVar()
nameEntered = ttk.Entry(win, width=12, textvariable=name)
nameEntered.grid(column=0, row=0)

myButtons = []
for x, im in enumerate(myTkImgs):
    myButtons.append(ttk.Button(win, command=clickMe, image=im))
    myButtons[x].grid(column=x, row = 3)
    myButtons[x].configure(padding = 0)


action = ttk.Button(win, text="Enter a hexadecimal Rule number", command = clickMe)
action.grid(column=1, row = 0)
print (action.keys())

x_image = 'cross-on.gif'
x_image_for_button = PhotoImage(file=x_image)
action2 = ttk.Button(win, command = clickMe, image=x_image_for_button)
action2.grid(column=1, row = 2)

win.mainloop()

CSV_logPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/LOG/"
winResX = 1920
winResY = 800
resX = 51
resY = 51
layersCount = 60
writeLogFile = True
scaleFactor = 1
CAcols = winResX / resX
CAgap = 2

myHexRule = "60010000808000c889000c0010010086800012000001003200002200001000294004040000000080000149044104040800093110000210310904150094290012"
#myStrBinRule = getBinRuleFromHex(myHexRule)
#               0    5    10   15   20   25   30   35   40   45   50   55   60   65   70
#myStrBinRule = "01100000000000010000000000000000100000001000000000000000110010001000100100000000000011000000000000010000000000010000000010000110100000000000000000010010000000000000000000000001000000000011001000000000000000000010001000000000000000000001000000000000001010010100000000000100000001000000000000000000000000000000000010000000000000000000000101001001000001000100000100000100000001000000100000000000000010010011000100010000000000000000001000010000001100010000100100000100000101010000000010010100001010010000000000010010"

#myBinRule = [x for x in myStrBinRule]
#print myStrBinRule
#print myBinRule
#logReadPath = CSV_logPath + "CA2D9_" + myHexRule + "_" + str(resX) + "x" + str(resY) + ".csv"
#logWritePath = CSV_logPath + "CA2D9_" + myHexRule + "_" + str(resX) + "x" + str(resY) + ".csv"

