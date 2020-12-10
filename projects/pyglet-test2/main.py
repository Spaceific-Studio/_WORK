from pyglet.gl import *
import PIL
from PIL import Image
from types import *

key = pyglet.window.key

class BasicButton:
    """
    Creates a basic button to pyglet.window.Window object passed as one of the args
    """
    instanceCount = 0
    

    def __init__(self, inWindow, xRes, yRes, posX, posY):

        self.createButton(inWindow, xRes, yRes, posX, posY)
    
    def createButton(self,inWindow, xRes, yRes, posX, posY):
        self.width = xRes
        self.height = yRes
        self.x = posX
        self.y = posY
        self.buttonImgPIL = PIL.Image.new("RGBA", (self.width, self.height), (0,0,0,255))
        self.mouseOverImgPIL = PIL.Image.new("RGBA", (self.width, self.height), (255,255,0,255))
        self.button2ImgPIL = PIL.Image.new("RGBA", (self.width, self.height), (255,220,200,255))
        self.buttonImg = self.PIL_to_PYG(self.buttonImgPIL)
        self.mouseOverImg = self.PIL_to_PYG(self.mouseOverImgPIL)
        self.button2Img = self.PIL_to_PYG(self.button2ImgPIL)
        self.sSbuttonImg = pyglet.sprite.Sprite(img=self.buttonImg)
        self.sMouseOverImg = pyglet.sprite.Sprite(img=self.mouseOverImg)
        self.sButton2Img = pyglet.sprite.Sprite(img=self.button2Img)
        self.sSbuttonImg.update(self.x,self.y,180.0,1,-1)
        self.window = inWindow
        self.window.push_handlers(on_mouse_motion=self.mouseOver)
        BasicButton.instanceCount += 1
        self.instanceID =  BasicButton.instanceCount
        self.window.addButton(self)
        self.window.render()

    def PIL_to_PYG(self,inImgs):
        """
        converts images from PIL to pygle by calling function convertToPYG() 
        this function determines whether input is single object or list
        """
        
        returnStuff = []
        if type(inImgs) is ListType:
            print "type of input = list"
            for i in inImgs:           
                returnStuff.append(convertToPYG(i))
            return returnStuff             
        else:
            returnStuff = self.convertToPYG(inImgs)
            return returnStuff

    def convertToPYG(self, inImg):
        """
        converts image from PIL to pygle using PIL.Image.tobytes() function
        """
        inImg.convert("RGBA")
        width = inImg.size[0]
        height = inImg.size[1]
        inImRaw = inImg.tobytes()
    #   cImRaw = inImg.convert("RGBA").tobytes("raw", "RGBA")
        inImPyg = pyglet.image.ImageData(width, height, "RGBA", inImRaw)
        return inImPyg
    
    def mouseOver(self,x, y, dx, dy):
        if x > self.x and x < self.x + self.width and y > self.y and y < self.y + self.height:
            self.sSbuttonImg = pyglet.sprite.Sprite(img=self.mouseOverImg)
            self.sSbuttonImg.update(self.x,self.y,180.0,1,-1)
            self.window.addButton(self)
            print "mouse is over!"
            return True

    def getID(self):
        return self.instanceID 
            

class main(pyglet.window.Window):
    def __init__ (self):
        super(main, self).__init__(1280,720, vsync=True, fullscreen = False)
        self.x, self.y = 0, 0

        #self.bg = Spr('background.jpg')
        self.output = pyglet.text.Label('',
                          font_size=14,
                          x=self.width//2, y=self.height//2,
                          anchor_x='center', anchor_y='center')
        self.outpuImg1 = pyglet.resource.image('ccc.jpg')
        self.outpuImg2 = pyglet.resource.image('bbb.JPG')
        self.mySprite1 = pyglet.sprite.Sprite(img=self.outpuImg1)
        self.alive = 1
        self.pressed = []
        self.key_table = {213 : 'a'}
        self.push_handlers(on_mouse_press=self.zpracuj_mys)
        self.push_handlers(on_mouse_release=self.changeImage)
        self.graphics = pyglet.graphics.draw(2, pyglet.gl.GL_POINTS, ('v2i', (10, 15, 30, 35)))
        self.rasterButtons = {}

    def on_draw(self):
        self.render()

    def zpracuj_mys(self,x, y, button, modifiers):
        self.mySprite1 = pyglet.sprite.Sprite(img=self.outpuImg2)
        self.mySprite1.update(x,y,180.0,1,-1)
        print "x = " + str(x)
        print "y = " + str(y)
        print "button = " + str(button)
        print "modifiers = " + str(modifiers)
        pass
    
    def changeImage(self,x, y, button, modifiers):
        self.mySprite1 = pyglet.sprite.Sprite(img=self.outpuImg1)
        self.mySprite1.update(x,y,180.0,1,-1)
        print "x = " + str(x)
        print "y = " + str(y)
        print "button = " + str(button)
        print "modifiers = " + str(modifiers)
        pass

    def on_close(self):
        self.alive = 0

    def on_key_release(self, symbol, modifiers):
        if symbol == key.LCTRL:
            pass # Again, here's how you modify based on Left CTRL for instance

        ## All key presses represents a integer, a=97, b=98 etc.
        ## What we do here is have a custom key_table, representing combinations.
        ## If the sum of two pressed matches to our table, we add that to our label.
        ## - If no match was found, we add the character representing each press instead. 
        ##   This way we support multiple presses but joined ones still takes priority.

        key_values = sum(self.pressed)
        if key_values in self.key_table:
            self.output.text += self.key_table[key_values]
        else:
            for i in self.pressed:
                self.output.text += chr(i)
        self.pressed = []

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE: # [ESC]
            self.alive = 0
        elif symbol == key.LCTRL:
            pass # Modify based on left control for instance
        else:
            self.pressed.append(symbol)

    def addButton(self, inButton):
        print "inButton.getID()"
        print inButton.getID()
        self.rasterButtons['' + str(inButton.getID())] = inButton
        self.render()

    def render(self):
        self.clear()
        #self.bg.draw()

        self.output.draw()
        self.mySprite1.draw()
        pyglet.graphics.draw(2, pyglet.gl.GL_POINTS, ('v3f', (10.0, 15.0, 0.0, 30.0, 35.0, 0.0)))
        for i, v in self.rasterButtons.items():
            v.sSbuttonImg.draw()
        self.flip()


    def run(self):
        while self.alive == 1:
            self.render()

            # -----------> This is key <----------
            # This is what replaces pyglet.app.run()
            # but is required for the GUI to not freeze
            #
            event = self.dispatch_events()

myWindow = main()
myButtons = []
for x in range(0,10):
    BasicButton(myWindow, 10+(x*25),10,20,20)
myWindow.run()