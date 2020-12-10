# -*- coding: utf-8 -*-
import pyglet
from pyglet_gui.theme import Theme
from pyglet_gui.gui import Label
from pyglet_gui.manager import Manager
from pyglet_gui.buttons import Button
from log import *
from ca_func import *
from display_func import *
import os
import Tkinter as tk


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
myStrBinRule = getBinRuleFromHex(myHexRule)
#               0    5    10   15   20   25   30   35   40   45   50   55   60   65   70
myStrBinRule = "01100000000000010000000000000000100000001000000000000000110010001000100100000000000011000000000000010000000000010000000010000110100000000000000000010010000000000000000000000001000000000011001000000000000000000010001000000000000000000001000000000000001010010100000000000100000001000000000000000000000000000000000010000000000000000000000101001001000001000100000100000100000001000000100000000000000010010011000100010000000000000000001000010000001100010000100100000100000101010000000010010100001010010000000000010010"

myBinRule = [x for x in myStrBinRule]
print myStrBinRule
print myBinRule
logReadPath = CSV_logPath + "CA2D9_" + myHexRule + "_" + str(resX) + "x" + str(resY) + ".csv"
logWritePath = CSV_logPath + "CA2D9_" + myHexRule + "_" + str(resX) + "x" + str(resY) + ".csv"
#myCA = run(resX, resY, layersCount, myBinRule, logWritePath, writeLogFile)
#print "myCA"
#print myCA
#myPygCA = PIL_to_PYG(myCA)
#print "myPygCA"
#crossOnPIL = Image.open("cross-on.png")
#crossOffPIL = Image.open("cross-off.png")
#crossOnImg = PIL_to_PYG(crossOnPIL)
#crossOffImg =  PIL_to_PYG(crossOffPIL)
#print myPygCA
#myLogData = readCSV_Log(logReadPath)
#inspArraySequence = getInspArraySeqence(9)
##cIm = getCross(myStrBinRule, inspArraySequence, 2, myLogData)
#print cIm
#cIm.convert("RGBA")
#width = cIm.size[0]
#height = cIm.size[1]
#cImRaw = cIm.tobytes()
#cImPyg = pyglet.image.ImageData(width, height, 'RGBA', cImRaw)

def callback(is_pressed):
    print('Button was pressed to state', is_pressed)

button = Button('Hello world', on_press=callback)

batch = pyglet.graphics.Batch()
theme = Theme({"font": "Lucida Grande",
               "font_size": 12,
               "text_color": [255, 255, 255, 255],
               "gui_color": [255, 150, 64, 255],
               "button": {
                   "down": {
                       "image": {
                           "source": "cross-on.png",
                           "frame": [8, 6, 2, 2],
                           "padding": [18, 18, 8, 6]
                       },
                       "text_color": [255, 255, 255, 255]
                   },
                   "up": {
                       "image": {
                           "source": "cross-off.png",
                           "frame": [6, 5, 6, 3],
                           "padding": [18, 18, 8, 6]
                       }
                   }
               }
              }, resources_path='theme/')

window = pyglet.window.Window(winResX, winResY, resizable=True, vsync=True)
Manager(button, window=window, theme=theme, batch=batch)
help()
pyglet_gui.core.Viewer.set_position(20,20)
pyglet.app.run()

#imageOff = pyglet.resource.image("C:\\_WORK\\PYTHON\\projects\\pyglet_gui-test\\cross-off.png")
#imageOn = pyglet.resource.image("C:\\_WORK\\PYTHON\\projects\\pyglet_gui-test\\cross-on.png")
# myKeys = {"jano":2, "peto":3, "duri":4}
# print "type(myKeys):"
# print type(myKeys)
# myList = [15,85,156,1561,1561,1]
# print "type(myList):"
# print type(myList)
# for k, v in myKeys.items():
#     print "key = " + str(k)
#     print "value = " + str(v)
# for k, v in enumerate(myList):
#     print "key = " + str(k)
#     print "value = " + str(v)
#label = Label('Hello world')
# def callback(is_pressed):
#     print('Button was pressed to state', is_pressed)
#button = Button('Hello world', on_press=callback)

# theme = Theme({"font": "Arial",
#                "font_size": 15,
#                "text_color": [255, 255, 255, 255]}, resources_path='')

# print "type(window)"
# print type(window)
# batch = pyglet.graphics.Batch()

#Manager(button, window=window, theme=theme, batch=batch)

# def zpracuj_mys(x, y, button, modifiers):
#     print "x = " + str(x)
#     print "y = " + str(y)
#     print "button = " + str(button)
#     print "modifiers = " + str(modifiers)
#  #   Manager(label, window=window, theme=theme, batch=batch)
#     CAimgPointer = int(remap(x, 0, winResX, 0, len(myPygCA)))
#     print "CAimgPointer - " + str(CAimgPointer) 
#     sprite3 = pyglet.sprite.Sprite(img=myPygCA[3])
#     print "myPygCA[" + str(CAimgPointer) + "]"
#     print myPygCA[CAimgPointer]
#     sprite3.update(0, winResY, 180.0,2,-1)
#     sprite3.draw()
#     myPygCA[CAimgPointer].blit(0, 0)
#     pass

# window.push_handlers(on_mouse_press=zpracuj_mys)
# help(pyglet)
# @window.event
# def on_draw():
#     window.clear()
# #    batch.draw()
#     iW = cImPyg.width
#     iH = cImPyg.height
#     label = Label('Width of image = ' + str(iW))

#     sprite2 = pyglet.sprite.Sprite(img=cImPyg)
#     sprite2.update(0,winResY,180.0,0.3,-1)
#     sprite2.draw()
#     # myPygCA[20].blit(0, 0)
    
#     for i, im in enumerate(myPygCA):
#          iW = im.width
#          iH = im.height
#          sprite = pyglet.sprite.Sprite(img=im)
#          CAposX = (iW * (i % CAcols)) + ((i % CAcols) * CAgap)
#          CAposY = iH * (i/CAcols)
# #         print "CAposX = " + str(CAposX)
# #         print "CAposY = " + str(CAposY)
# #         print "i = " + str(i)
#          sprite.update(CAposX, winResY - 200 + iH, 180.0,2,-1)
         
# #         im.blit(iW*i+i*gap, 0)
#          sprite.draw()


#pyglet.app.run()