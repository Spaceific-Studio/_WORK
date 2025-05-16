import pyglet
from PIL import Image, ImageDraw, ImageFont, ImageColor
from types import *

def PIL_to_PYG(inImgs):
    returnStuff = []
    if type(inImgs) is ListType:
        print "type of input = list"
        for i in inImgs:           
            returnStuff.append(convertToPYG(i))
        return returnStuff             
    else:
        returnStuff = convertToPYG(inImgs)
        return returnStuff


def convertToPYG(inImg):
    inImg.convert("RGBA")
    width = inImg.size[0]
    height = inImg.size[1]
    inImRaw = inImg.tobytes()
 #   cImRaw = inImg.convert("RGBA").tobytes("raw", "RGBA")
    inImPyg = pyglet.image.ImageData(width, height, "RGBA", inImRaw)
    return inImPyg
