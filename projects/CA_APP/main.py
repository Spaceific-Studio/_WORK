import tkinter as tk 
from tkinter import *
from ca_func import *
from PIL import ImageTk, Image, ImageDraw
#import ttk
import types
from numpy import base_repr

mainWindow = Tk()
mainWindow.grid()
mainWindow.grid_propagate(1)

class MatrixButton(tk.Button):
    INSTANCE_NUM = 0
    def __init__(self, *args, **kwargs):
#        print ("len(*args)")
#        print (len(args))
#        print (args[1][0])
#        print (MatrixButton.INSTANCE_NUM)
        tk.Button.__init__(self, *args[0:1], **kwargs)
        self.value = 0         
        self.ID = self.INSTANCE_NUM
        MatrixButton.INSTANCE_NUM += 1
#        self.imgON = ImageTk.PhotoImage(args[1])
#        print ("self.imgON")
#        print (args[1][1])
#        args[1][1].save(r"C:/testPix3b.png")
#        args[1][0].save(r"C:/testPix3a.png")
        self.imgs = [args[1][0], args[1][1]]
#        print ("self.imgs-assigned")
        
    def switchValue(self):
        if self.value == 0:
            self.setValue(1)
        elif self.value == 1:
            self.setValue(0)
        self.configure(bg = "red")
        
    def selectionOff(self):
        self.configure(bg = "Gray80")
        self.setImage()

    def setImage(self, *args):
        if len(args) !=0:
            self.imgs = args[0]
            #print ("MatrixButton->setImage()->self.imgs was set to {0} and {1}".format(args[0][0], args[0][1]))
        self.config(image = self.imgs[self.value])

    def reset(self):
        self.configure()

    def setValue(self, inValue):
        self.value = inValue
        self.setImage()
    def getValue(self):
        return self.value
    def getID(self):
        return self.ID

class InitialMatrixButton(MatrixButton):
    INSTANCE_NUM = 0
    def __init__(self, *args, **kwargs):
        MatrixButton.__init__(self, *args, **kwargs)
        self.ID = self.INSTANCE_NUM
        InitialMatrixButton.INSTANCE_NUM += 1

class CaAPP(tk.Frame):
    HEX_RULE = "" 
    BIN_RULE = ""
    INT_RULE = ""
    ALPHA_NUM_RULE = ""
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg = "yellow", bd = 1)
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.createWidgets()
        self.setGlobals()
        self.caResX = 51
        self.caResY = 51
        self.setPaths()
        self.rbVar = tk.IntVar()
        self.rbVar.set(0)
        self.imRbVar = tk.IntVar()
        self.imRbVar.set(0)
        self.ruleStrVar = tk.StringVar()
        self.myLogData = readCSV_Log(self.logReadPath)
        self.getMatrixImgs()
        self.width = 1920
        self.height = 1000
        self.bgColor = "Gray16"
        self.text1Color = "white"
        self.text2Color = "Gray60"
 #       self.config(height = 800)
        master.geometry("" + str(self.width) + "x" + str(self.height))
        master.resizable(1, 1)
        self.pack(fill=BOTH, expand=1)
        self.matrixButtonsToChange = []         
        self.currentRow = 0
        self.grid(sticky=N+S+E+W)
        self.intialMatrixWidth = 25
        
        self.cols = 89 - self.intialMatrixWidth
#        self.createWidgets()
        #self.createMenu()
        self.createInspectorMatrixFrame()                
        self.caLayCount = 30
        self.caCols = 20
        self.caCanvasXscale = 1.0
        self.caCanvasYscale = 1.0
        self.caCanvasScaleInc = 0.1
        self.create_CA_Canvas()
        self.initButtonSize = 13
        self.createInitialImageCanvas()
        
        self.initialMatrixToChange = [] 
        self.initialImageMatrix = self.createInitialImageMatrix()
        self.createMenuBar()
        
        self.updateCanvas()
        
    def createWidgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def getMatrixImgs(self):
        myLogData = readCSV_Log(self.logReadPath)
        hexRuleON = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        binRuleON = getBinRuleFromHex(hexRuleON)
        PILimagesON = getCrossImgs(binRuleON, getInspArraySeqence(9), 2, myLogData)
        hexRuleOFF = "0"
        binRuleOFF = getBinRuleFromHex(hexRuleOFF)
        PILimagesOFF = getCrossImgs(binRuleOFF, getInspArraySeqence(9), 2, myLogData)
        print ("PIL images created")
        self.matrixButtonImgs = []
        for i, img in enumerate(PILimagesON):
#            imageON = ImageTk.PhotoImage(img)
#            imageOFF = ImageTk.PhotoImage(PILimagesOFF[i])
            self.matrixButtonImgs.append([PILimagesOFF[i], img])
        # print (self.matrixButtonImgs)
        # print ("matrixButtonImgs created")

    def updateMatrixButtons(self):
        for i, w in enumerate(self.matrixButtons):
            w.setValue(int(self.BIN_RULE[i]))
            w.setImage(self.matrixButtonImgs[i])
            

    def updateInspMatrixImgs(self):        
        #print ("myLogData from path: {0} was loaded".format(myLogDataPath))
        self.myNewInspMatrixImgs = self.matrixButtonImgs
        myCaimage = self.caIMGs[5]
        rImage = self.caPILimgs[5].resize((200,200))
        self.resizedImage = ImageTk.PhotoImage(rImage)
        for i, img in enumerate(self.myNewInspMatrixImgs):
            self.myImg = img[0]
            self.caCanvas.create_image(i*50, 0 ,image = self.myImg, anchor = tk.NW)
        #print (myCaimage)
        self.testButton = tk.Button(self.caCanvas, image = myCaimage)
        self.caCanvas.create_image(100, 0 ,image = self.resizedImage, anchor = tk.NW)
        self.testButton.grid()
        #self.buttonFrame = tk.Frame(self.caCanvas, width = 100, height = 20, bd = 0)
        #self.buttonFrame.grid(sticky = N+S+E+W)
        #self.caCanvas.create_image(0, 0 , image = myCaimage, anchor = tk.NW)
        #self.caCanvas.create_window(0,0, height = 100, width = 100)

    def getLogData():
        return self.myLogData

    def setGlobals(self):
        CaAPP.HEX_RULE = "24a0e880a0208000020480004000000084a08408a080000000482800800000010018800000000000290808002000000028000208400200011044000000000012" 
        intRule = int(CaAPP.HEX_RULE,16)
        self.ruleStrVar = CaAPP.HEX_RULE
        CaAPP.ALPHA_NUM_RULE = base_repr(intRule, base=36)
        # print ("setGlobals - CaAPP.HEX_RULE")
        # print (CaAPP.HEX_RULE)
        CaAPP.BIN_RULE = getBinRuleFromHex(CaAPP.HEX_RULE)
        
        # print ("setGlobals - CaAPP.BIN_RULE")
        # print (CaAPP.BIN_RULE)
        # print (type(CaAPP.BIN_RULE))
        CaAPP.INT_RULE = intRule
        # print ("setGlobals - CaAPP.INT_RULE")
        # print (CaAPP.INT_RULE)
    
    def updateBINrule(self, inBinRule):
        CaAPP.BIN_RULE = inBinRule
    #    print ("updateBINrule() - inBinRule" + str(int(inBinRule,2)))
    #    print ("updateBINrule() - BIN_RULE" + str(int(CaAPP.BIN_RULE,2)))
        CaAPP.INT_RULE = int(CaAPP.BIN_RULE,2)
        CaAPP.ALPHA_NUM_RULE = base_repr(CaAPP.INT_RULE, base=36)
        CaAPP.HEX_RULE = "{0:x}".format(CaAPP.INT_RULE)
        
    def updateHEXrule(self, inHexRule):
        CaAPP.HEX_RULE = inHexRule        
        CaAPP.BIN_RULE = getBinRuleFromHex(CaAPP.HEX_RULE)        
        CaAPP.INT_RULE = int(CaAPP.BIN_RULE,2)
        CaAPP.ALPHA_NUM_RULE = base_repr(CaAPP.INT_RULE, base=36)
        self.ruleStrVar = CaAPP.ALPHA_NUM_RULE
    
    def updateANUMrule(self, inNumRule):
        CaAPP.ALPHA_NUM_RULE = inNumRule        
        self.ruleStrVar = inNumRule
        CaAPP.INT_RULE = int(inNumRule,36)  
        CaAPP.HEX_RULE = "{:x}".format(CaAPP.INT_RULE)
        CaAPP.BIN_RULE = getBinRuleFromHex(CaAPP.HEX_RULE)
        
    def setPaths(self):
        self.CSV_logPath = r"C:DANO/_WORK/DATA/PYTHON/CELULAR_AUTOMAT-2D/LOG/"
        self.saveCAimagesPath = r"C:/DANO/_WORK/DATA/PYTHON/CELULAR_AUTOMAT-2D/RNDCA2D9-sequence/interesting/"
        #self.logReadPath = self.CSV_logPath + "CA2D9_" + self.HEX_RULE + "_" + str(self.caResX) + "x" + str(self.caResY) + ".csv"
        self.logReadPath = self.getLOGpath(CaAPP.HEX_RULE)

    def getLOGpath(self,inFileName):        
        returnPath = self.CSV_logPath + "CA2D9_" + inFileName + "_" + str(self.caResX) + "x" + str(self.caResY) + ".csv"
        return returnPath

    def generateCAimgs(self):
        self.caPILimgs = runWithLayer(self.createInitialImage(), self.caResX, self.caResY, self.caLayCount, CaAPP.BIN_RULE, self.logReadPath, True)
        self.caIMGs = []
        for img in self.caPILimgs:
            self.caIMGs.append(ImageTk.PhotoImage(img))

    # def createWidgets(self):
    #     self.quitButton = tk.Button(self, text = "Quit", command = self.quit)
    #     self.quitButton.grid(columnspan = self.cols)
    
    #  def setBINRuleByHEX(self, inHex):
    # #    print ("setBINRuleByHEX - inHex")
    # #    print (inHex)
    #     self.BIN_RULE = getBinRuleFromHex(inHex)
    #     pass
    
    def addMatrixSelection(self, udalost):
        #self.BIN_RULE[inPosition] = self.switchValue(self.BIN_RULE[inPosition])
        udalost.widget.switchValue()
        if udalost.widget.ID in self.matrixButtonsToChange:
            self.matrixButtonsToChange.remove(udalost.widget.ID)
            udalost.widget.selectionOff()
            
        else:
            self.matrixButtonsToChange.append(udalost.widget.ID)
    #        print ("Added to matrixButtonsToChange " + str(udalost.widget.ID))
    #    print (self.matrixButtonsToChange)
    #    print ("hodnota value")
    #    print (udalost.widget.value)
    #    print ("MatrixButton ID")
    #    print (udalost.widget.ID)

    def addInitialMatrixSelection(self, udalost):
        myButton = udalost.widget
        myConf = myButton.config()
        stateValues = myConf['state']
        stateValue = stateValues[len(stateValues)-1]
        print ('stateValue of button {0} = {1}'.format(myButton.ID, stateValue))
#        print (stateValue)
        if stateValue != "disabled":
            udalost.widget.switchValue()
            self.updateInitialImageMatrix(udalost.widget.getID(), udalost.widget.getValue())
            print ("mozes kludne")

        else:
            print ("nene nezmenis hodnotu")
            pass
    #    self.initialMatrixButtons

    def createInitialImageMatrix(self):
        returnArray = []
        for i in self.initialMatrixButtons:
            returnArray.append(i.getValue())
        return returnArray

    def updateInitialImageMatrix(self, inIndex, inValue):
        self.initialImageMatrix[inIndex] = inValue
        print ("initialImageMatrix")
        print (self.initialImageMatrix)
    
    def createInitialImage(self):
        img = Image.new("RGBA",(self.caResX,self.caResY), (0,0,0,255))
        if self.rbVar.get() == 0:
            img = createFirstLayerFromScratch(self.caResX, self.caResY)
        else:
            returnPixCoords = []
            for i, v in enumerate(self.initialImageMatrix):
                if v == 1:
                    returnPixCoords.append(get2DpixCoords(i, self.intialMatrixWidth))
            imgI = Image.new("RGBA",(self.intialMatrixWidth,self.intialMatrixWidth), (0,0,0,255))
            imgID = ImageDraw.Draw(imgI)
            imgID.point(returnPixCoords, (255, 255, 255,255))
            #img.paste(imgI, (int((abs((self.intialMatrixWidth-self.caResX)/2), int((abs(self.intialMatrixWidth-self.caResY)/2)))))
            img.paste(imgI, (int(self.caResX/2 - self.intialMatrixWidth/2), int(self.caResY/2 - self.intialMatrixWidth/2)))
        #img.save(r"H:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/pasteTest.png")
        print ("pasteTest.png saved")
        print ('self.rbVar - {}'.format(self.rbVar.get()))
        return img

    def updateRule(self, udalost):
#        updatedRule = self.switchRuleValues(self.BIN_RULE)
    #    print ("self.INT_RULE")
    #    print (self.INT_RULE)
        print ("len(self.matrixButtonsToChange)")
        print (len(self.matrixButtonsToChange))
        print ("udalost.widget.cget(text)")
        print (udalost.widget.cget('text'))
        self.caLayCount = int(self.caLayCountSB.get())
        if udalost.widget.cget('text') == 'Change Rule':
            self.updateANUMrule(self.ruleEntry.get())
        else:
            if len(self.matrixButtonsToChange) != 0:
                print ("len(self.matrixButtonsToChange)")
                print (len(self.matrixButtonsToChange))
                updatedRule = self.getNewRule()
                self.updateBINrule(updatedRule)
            else:
                updatedRule = self.ruleEntry.get()
                self.updateANUMrule(updatedRule)

        self.setPaths()
        print ("Path to LOG file was updated to : {0}".format(self.logReadPath))
        self.generateCAimgs()
        self.getMatrixImgs()
        #self.updateInspMatrixImgs()        
        self.updateMatrixButtons()
        if len(self.matrixButtonsToChange) != 0:            
    #        self.createInspectorMatrixFrame()
            for i in self.matrixButtonsToChange: 
                self.matrixButtons[i].selectionOff()
                self.matrixButtons[i].setImage()
        elif udalost.widget.cget('text') == 'Change by entry Rule':            
            for i, w in enumerate(self.matrixButtons):
                w.setValue(int(CaAPP.BIN_RULE[i]))
        self.matrixButtonsToChange = []
        
        self.label2.configure(text = "BIN RULE: " + CaAPP.BIN_RULE)
        self.label3.configure(text = "INT RULE: " + str(CaAPP.INT_RULE))
       
        ruleEntryText = self.ruleEntry.get()     
        print (ruleEntryText)
        self.ruleEntry.delete(0, len(ruleEntryText))    
        self.ruleEntry.insert(0,CaAPP.ALPHA_NUM_RULE)
        self.updateCanvas()
        self.initialImageMatrix = self.createInitialImageMatrix()
        self.createInitialImage()
        #    print ("self.INT_RULE")
        #    print (self.INT_RULE)

    def updateCanvas(self):        
        self.caCanvas.delete("all")
        yOffset = 50
        rImage = self.caPILimgs[8].resize((200, 200))
        self.resizedImage = ImageTk.PhotoImage(rImage)
        myCaimage = self.caIMGs[5]
        self.pImage = self.caIMGs[0]
        self.caIMGs = []
        for i, image in enumerate(self.caPILimgs):
            imgXsize = image.size[0]
            #print ("imgXSize = {0}, resized = {1}".format(imgXsize, int(imgXsize * self.caCanvasXscale)))
            #print (self.caCanvasXscale)
            imgYsize = image.size[1]
            rImage = image.resize((int(imgXsize * self.caCanvasXscale), int(imgYsize * self.caCanvasYscale)))
            self.resizedCAImage = ImageTk.PhotoImage(rImage)
            self.caIMGs.append(self.resizedCAImage)
            self.caCanvas.create_image((i % self.caCols) * self.resizedCAImage.width(), (i / self.caCols) * self.resizedCAImage.height(), image = self.caIMGs[i], anchor = tk.NW)
            
        #     #imgXsize = image.size[0]
        #     #imgYsize = image.size[1]
        #     #resImg = image.resize((int(imgXsize * self.caCanvasXscale), int(imgYsize * self.caCanvasYscale)), Image.ANTIALIAS)
        #     self.resImg = self.caPILimgs[i].resize((int(self.caCanvasXscale), int(self.caCanvasYscale)))
        #     #pImage = ImageTk.PhotoImage(image)
        #     self.pImage = ImageTk.PhotoImage(self.resImg)
        #     print ("photoImage width - {w} - height {h}".format(w = self.pImage.width(), h = self.pImage.height()))
        #     print (self.pImage)
        #     #self.caCanvas.create_image((i % self.caCols)*self.pImage.width(), yOffset + ((i / self.caCols) * self.pImage.height()) , image = self.pImage, anchor = tk.NW)


    def caCanvasZoom(self, udalost):
        print (udalost.delta)
        if udalost.delta>0: print ("ZOOM IN!")
        elif udalost.delta<0: print ("ZOOM OUT!")
    
    def caCanvasGrab(self, udalost):
        self._y = udalost.y
        self._x = udalost.x
    
    def caCanvasDrag(self, udalost):
        if (self._y-udalost.y < 0): self.caCanvas.yview("scroll",-1,"units")
        elif (self._y-udalost.y > 0): self.caCanvas.yview("scroll",1,"units")
        if (self._x-udalost.x < 0): self.caCanvas.xview("scroll",-1,"units")
        elif (self._x-udalost.x > 0): self.caCanvas.xview("scroll",1,"units")
        self._x = udalost.x
        self._y = udalost.y
    
    def updateCaLaycountSB(self, udalost):        
        self.caLayCount = int(udalost.widget.get())
        print (type(self.caLayCount))
        print (self.caLayCount)
        print ("self.caLayCount was updated")
        print (int(udalost.widget.winfo_geometry().split("x")[0]))

    def zoomIn(self, udalost):
        #self.caCanvas.delete("all")
        self.caCanvasXscale += self.caCanvasScaleInc
        self.caCanvasYscale += self.caCanvasScaleInc
        print ("zoomIn->self.caCanvasXscale = " + str(self.caCanvasXscale))
        self.caCanvas.scale("all", 0, 0, 1 + self.caCanvasScaleInc, 1 + self.caCanvasScaleInc)
        self.updateCanvas()
        #self.updateCanvas()
    
    def zoomOut(self, udalost):
        #self.caCanvas.delete("all")
        self.caCanvasXscale =  max(self.caCanvasXscale - self.caCanvasScaleInc, 1)
        self.caCanvasYscale = max(self.caCanvasYscale - self.caCanvasScaleInc, 1)
        self.caCanvas.scale("all", 0,0, 1 - self.caCanvasScaleInc, 1 - self.caCanvasScaleInc)
        self.updateCanvas()
        #updateCanvas()

    def getNewRule(self):
        returnRule = ""
        for i in self.matrixButtons:
            returnRule += str(i.value)
    #    print ("getNewRule() - returnRule" + str(int(returnRule,2)))
    #    print ("getNewRule() - BIN_RULE" + str(int(self.BIN_RULE,2)))
        return returnRule

    def switchRuleValues(self, inRule):
        
        if type(inRule) is types.StringType:
            returnRule = ""
    #        print ("type = StringType")
            for i, v in enumerate(inRule):
                if i in self.matrixButtonsToChange:
                    if v=="0":
                        returnRule += "1"
                    elif v == "1":
                        returnRule += "0"
                else:
                    returnRule += v
            return returnRule
                
        elif type(inRule) is types.ListType:
            returnRule = inRule
            returnStrRule = ""
    #        print ("type = ListType")
            for j in self.matrixButtonsToChange:
                returnRule[j] = (inRule[j]-1) * (-1)
            returnStrRule.join(returnRule)
            return returnStrRule
    
    def getIntFromInitialImg(self):
        binVal = ""
        sPos = 0
        ePos = 0
        zeroSpos = False
        for i, w in enumerate(self.initialMatrixButtons):
            binVal += str(w.getValue())
            if w.getValue() == 1 and i == 0:
                print ("getHexFromInitialImg - i:")
                print (i)
                sPos = i
                zeroSpos = True
                ePos = i
            elif w.getValue() == 1 and sPos == 0 and zeroSpos == False:
                sPos = i
                ePos = i
            elif w.getValue() == 1 and i!= 0:
                ePos = i

        print ("sPos")
        print (sPos)
        print ("ePos")
        print (ePos)
        print (binVal[sPos:ePos])
        if sPos == len(binVal) - 1:
            sPos = len(binVal) - 2
        if ePos == len(binVal) - 1:
            ePos = len(binVal) - 2
        intVal = int(binVal[sPos:((ePos + 1) % len(binVal))],2)
        print ("intVal")
        print (intVal)
        hexVal = "{0:x}".format(intVal) 
        print ("hexVal")
        print (hexVal)
        return intVal

    def shortenName(self,inMaxLength, inStr):
        dirPathLength = len(os.getcwd())
        dirLength = len(inStr)
        newDirLength = inMaxLength - dirPathLength
        dirLengthDifference = dirLength - newDirLength
        myStrList = [x for x in inStr]
        if dirLengthDifference > 0:
            popStep = dirLength / dirLengthDifference
            mySliceList = range(0,len(myStrList), popStep)
            for i, v in enumerate(mySliceList):
                myStrList.pop(v-i)
        return "".join(myStrList)

    def writeFile(self, inData, inFullName):
        with open(inFullName, 'w') as myFile:
            myFile.write(inData)

    def createSCADconvex(self, inData, inWrightDirPath, inWidth, inHeight):
        #splitedPath = inDirName.split("/")
        #print splitedPath[len(splitedPath)-1]
        returnString = "\n"
        returnString += "sphereRadius = 0.1; \n"
        returnString += "wallWidth = 4; \n"
        returnString += "$fn = 2; \n"
        returnString += "zStart = 0;\n"
        returnString += "zMax = 60;\n"
        returnString += "\n"
        returnString += "//for(z=[zStart:(len(myBoolMx)-1)]) \n"
        returnString += "for(z=[zStart: (len(myBoolMx)-1) < zMax ? (len(myBoolMx)-1) : zMax])\n"
        returnString += "{ \n"
        returnString += "   for(y=[0:(len(myBoolMx[z])-1)]) \n"
        returnString += "   { \n"
        returnString += "      for(x=[0: len(myBoolMx[z][y])-1]) \n"
        returnString += "      { \n"
        returnString += "//substracted void from inner structure by wallWidth parameter      \n"
        returnString += "         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]) && ((y<wallWidth || y>(len(myBoolMx[z]) - (wallWidth +2)) || (x < wallWidth || x>(len(myBoolMx[z][y]) - (wallWidth + 2)))))) \n"
        returnString += "//substracted void from surface offseted by wallWidth parameter  \n"
        returnString += "//         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]) && ((y>wallWidth + 1 && y<(len(myBoolMx[z]) - (wallWidth + 2)) && (x > wallWidth + 1 && x<(len(myBoolMx[z][y]) - (wallWidth + 2)))))) \n"
        returnString += "//middle cross section XZ plane\n"
        returnString += "//         if(z<len(myBoolMx) && y<(len(myBoolMx[z])/2) && x<len(myBoolMx[z][y]))\n"
        returnString += "//middle cross section YZ plane\n"
        returnString += "//         if(z<len(myBoolMx) && y<(len(myBoolMx[z])) && x<(len(myBoolMx[z][y])/2))\n"
        returnString += "//diagonal section 1\n"
        returnString += "//         if(z<len(myBoolMx) && y>len(myBoolMx[z][y])-x && x<(len(myBoolMx[z][y])))\n"
        returnString += "//diagonal section 2\n"
        returnString += "//         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x>y)\n"
        returnString += "//full volume structure\n"
        returnString += "//         if(z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]))\n"
        returnString += "         {\n"
        returnString += "             point1 = myBoolMx[z][y][x] == 1 ? [x,y,z] : [];\n"
        returnString += "             point2 = myBoolMx[z][y][x+1] == 1 ? [x+1,y,z] : []; \n"
        returnString += "             point3 = myBoolMx[z][y+1][x] == 1 ? [x,y+1,z] : [];\n"
        returnString += "             point4 = myBoolMx[z][y+1][x+1] == 1 ? [x+1,y+1,z] : [];\n"
        returnString += "             point5 = myBoolMx[z+1][y][x] == 1 ? [x,y,z+1] : [];\n"
        returnString += "             point6 = myBoolMx[z+1][y][x+1] == 1 ? [x+1,y,z+1] : [];\n"
        returnString += "             point7 = myBoolMx[z+1][y+1][x] == 1 ? [x,y+1,z+1] : [];\n"
        returnString += "             point8 = myBoolMx[z+1][y+1][x+1] == 1 ? [x+1,y+1,z+1] : [];\n"
        returnString += "             hull()\n"
        returnString += "             {\n"
        returnString += "                 if(len(point1) > 0) {color(\"blue\") translate(point1) sphere(sphereRadius);}\n"
        returnString += "                 if(len(point2) > 0) {color(\"blue\") translate(point2) sphere(sphereRadius);}\n"
        returnString += "                 if(len(point3) > 0) {color(\"blue\") translate(point3) sphere(sphereRadius);}\n"
        returnString += "                 if(len(point4) > 0) {color(\"blue\") translate(point4) sphere(sphereRadius);}\n"  
        returnString += "                 if(len(point5) > 0) {color(\"blue\") translate(point5) sphere(sphereRadius);}\n"    
        returnString += "                 if(len(point6) > 0) {color(\"blue\") translate(point6) sphere(sphereRadius);}\n"
        returnString += "                 if(len(point7) > 0) {color(\"blue\") translate(point7) sphere(sphereRadius);}\n"
        returnString += "                 if(len(point8) > 0) {color(\"blue\") translate(point8) sphere(sphereRadius);}\n"   
        returnString += "             }\n"
        returnString += "         }\n"
        returnString += "      }\n"
        returnString += "   }\n"
        returnString += "}\n"
        returnString += "\n"
        returnString += "myBoolMx = ["
        for b, z in enumerate(inData):
            returnString += "["
            layer = z.getdata()
            for a, y in enumerate(layer):
                if a%inWidth == 0 and a == 0:
                    returnString += "[" + str(returnOne(y[0])) + ", "
                elif a%inWidth == 0 and a > 0:
                    returnString += "], [" + str(returnOne(y[0])) + ", "
                elif a%inWidth == inWidth - 1 and a > 0:
                    returnString += str(returnOne(y[0]))
                else:
                    returnString += str(returnOne(y[0])) + ", "
                if a == len(layer)-1:
                    returnString += "]"
    #            returnString += "-" + str(a) + "-"
            if b != len(inData)-1:
                returnString += "],"
            else:
                returnString += "]"
        returnString += "]; \n"
    
        #fileName = splitedPath[len(splitedPath)-1] + "x" + str(len(inData)) +"_convexHull.scad"
        fileName = "{0}x{1}_{2}_convexHull.scad".format(inWidth, inHeight, len(inData))
        fullName = inWrightDirPath + "\\" + fileName
        self.writeFile(returnString, fullName)
        print ("saved :" + fullName)
        return returnString
    
    def createTextForSCAD(self, inData, inWrightDirPath, inWidth, inHeight):
        #splitedPath = inDirName.split("/")
        #print splitedPath[len(splitedPath)-1]
        returnString = " \n"
        returnString += "wallWidth = 4;\n"    
        returnString += "zStart = 0;\n"
        returnString += "zMax = 60;\n"
        returnString += "for(z=[zStart: (len(myBoolMx)-1) < zMax ? (len(myBoolMx)-1) : zMax]) \n"
        returnString += "{\n"
        returnString += "   for(y=[0:(len(myBoolMx[z])-1)]) \n"
        returnString += "   { \n"
        returnString += "      for(x=[0:(len(myBoolMx[z][y])-1)]) \n"
        returnString += "      { \n"
        returnString += "//substracted void from inner structure offseted by wallWidth parameter \n"
        returnString += "         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<len(myBoolMx[z]) && x<len(myBoolMx[z][y]) && ((y<wallWidth + 1 || y>(len(myBoolMx[z]) - (wallWidth + 2)) || (x < wallWidth + 1 || x>(len(myBoolMx[z][y]) - (wallWidth + 2))))))) \n"
        returnString += "//substracted void from surface offseted by wallWidth parameter \n"
        returnString += "//         if(myBoolMx[z][y][x] == 1  && ((y>wallWidth + 1 && y<(len(myBoolMx[z]) - (wallWidth + 2)) && (x > wallWidth + 1 && x<(len(myBoolMx[z][y]) - (wallWidth + 2)))))) \n"
        returnString += "//middle cross section XZ plane\n"
        returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<(len(myBoolMx[z])/2) && x<len(myBoolMx[z][y])))\n"
        returnString += "//middle cross section YZ plane\n"
        returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<len(myBoolMx[z]) && x<(len(myBoolMx[z][y])/2)))\n"
        returnString += "//diagonal section 1\n"
        returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y>(len(myBoolMx[z][y])-x)) && x<(len(myBoolMx[z][y])))\n"
        returnString += "//diagonal section 2\n"
        returnString += "//         if(myBoolMx[z][y][x] == 1 && (z<len(myBoolMx) && y<len(myBoolMx[z]) && x>y))\n"
        returnString += "//full volume structure\n"
        returnString += "//         if(myBoolMx[z][y][x] == 1) \n"
        returnString += "         { \n"
        returnString += "            translate([x,y,z])\n"
        returnString += "            { \n"
        returnString += "               cube(1.2); \n"
        returnString += "            } \n"
        returnString += "         } \n"
        returnString += "      } \n"
        returnString += "   } \n"
        returnString += "} \n"
        returnString += " \n"
        returnString += "myBoolMx = ["
        for b, z in enumerate(inData):
            returnString += "["
            layer = z.getdata()
            for a, y in enumerate(layer):
                if a%inWidth == 0 and a == 0:
                    returnString += "[" + str(returnOne(y[0])) + ", "
                elif a%inWidth == 0 and a > 0:
                    returnString += "], [" + str(returnOne(y[0])) + ", "
                elif a%inWidth == inWidth - 1 and a > 0:
                    returnString += str(returnOne(y[0]))
                else:
                    returnString += str(returnOne(y[0])) + ", "
                if a == len(layer)-1:
                    returnString += "]"
    #            returnString += "-" + str(a) + "-"
            if b != len(inData)-1:
                returnString += "],"
            else:
                returnString += "]"
        returnString += "]; \n"
        #fileName = splitedPath[len(splitedPath)-1] + "x" + str(len(inData)) +"_cube.scad"
        fileName = "{0}x{1}_{2}_cube.scad".format(inWidth, inHeight, len(inData))
        fullName = inWrightDirPath + "\\" + fileName
        self.writeFile(returnString, fullName)
        print ("saved :" + fullName)
        return returnString

    def saveCAimages(self):
        ensure_dir(self.saveCAimagesPath + CaAPP.ALPHA_NUM_RULE + "/")
        os.chdir(self.saveCAimagesPath + CaAPP.ALPHA_NUM_RULE + "/")
#         print ("saveCAimages -> inOption - {0}".format("blablabla"))
#         saveDir = self.HEX_RULE + "/"
# #        saveDir = self.saveCAimagesPath + base_repr(self.INT_RULE, 36) + "/"
# #        subDir = saveDir + "/" + base_repr(self.getIntFromInitialImg(), 36) + "/"
#         subDir = u"" + base_repr(self.getIntFromInitialImg(), 36)
#         print (subDir)
#         try:
#             ensure_dir(saveDir)
#         except:
#             print ("Error creating or reading directory: {0}".format(saveDir))
#         os.chdir(saveDir)
        
        mySubDirs = []
        for (path, dirnames, filenames) in os.walk(os.getcwd()):              
            mySubDirs.extend(dirnames)
        subDir = "{:03}".format(int(mySubDirs[-1]) + 1 if len(mySubDirs) > 0 else 1)
        print ("Name of subdir is : {0}".format(subDir))
        print (mySubDirs)
        print ("Length of path is : {0} - {1}".format(len(os.getcwd() + subDir), os.getcwd() + "\\" + subDir))
        if len(os.getcwd() + subDir) > 260:
                subDir = self.shortenName(260, subDir)
        print ("Length of path after shortening is : {0} - {1}".format(len(os.getcwd() + subDir), os.getcwd() + "\\" + subDir))
        #try:
        print (subDir + "\\")
        try:
            ensure_dir(subDir + "\\")
            #os.chdir(subDir + "/")
            
            for i, img in enumerate(self.caPILimgs):
    #            img.save(subDir + "{:0>3}".format(str(i)) + ".png")
                img.save(subDir + "\\" + "{:0>3}".format(str(i)) + ".png")
            print ("Length of path is : {0} - {1}".format(len(os.getcwd() + "\\" + subDir), os.getcwd() + "\\" + subDir))
            print ("Files were saved into directory : {0}".format(os.getcwd() + "\\" + subDir))
        except Exception as ex:            
            print ("Error creating or reading directory: {0}".format(os.getcwd() + "\\" + subDir))
        #try:
        self.createTextForSCAD(self.caPILimgs, os.getcwd() + "\\" + subDir, self.caResX, self.caResY)
        self.createSCADconvex(self.caPILimgs, os.getcwd() + "\\" + subDir, self.caResX, self.caResY)
        # except Exception as ex:
        #     error_type, error_instance, traceback = sys.exc_info()
        #     print("{0} \
        #                 Exception: {1} error_type: {2}, error_instance {3}, traceback -{4}" \
        #                 .format("Error creating SCAD data for: {0}".format(os.getcwd() + "\\" + subDir) \
        #                         ,ex \
        #                         ,error_type \
        #                         ,error_instance \
        #                         ,traceback))
            

    def saveOddCAimages(self):
        os.chdir(self.saveCAimagesPath)
        saveDir = self.HEX_RULE + "/"
#        saveDir = self.saveCAimagesPath + base_repr(self.INT_RULE, 36) + "/"
#        subDir = saveDir + "/" + base_repr(self.getIntFromInitialImg(), 36) + "/"
        subDir = u"" + base_repr(self.getIntFromInitialImg(), 36) + "-n/"
        print (subDir)
        try:
            ensure_dir(saveDir)
        except:
            print ("Error creating or reading directory: {0}".format(saveDir))
        os.chdir(saveDir)
        try:
            ensure_dir(subDir)
            os.chdir(subDir)
            for i, img in enumerate(self.caPILimgs):
    #            img.save(subDir + "{:0>3}".format(str(i)) + ".png")
                if i % 2 != 0:
                    img.save("{:0>3}".format(str(i)) + ".png")
        except:
            print ("Error creating or reading directory: {0}".format(subDir))
        
        
    def saveEvenCAimages(self):
        os.chdir(self.saveCAimagesPath)
        saveDir = self.HEX_RULE + "/"
#        saveDir = self.saveCAimagesPath + base_repr(self.INT_RULE, 36) + "/"
#        subDir = saveDir + "/" + base_repr(self.getIntFromInitialImg(), 36) + "/"
        subDir = u"" + base_repr(self.getIntFromInitialImg(), 36) + "-p/"
        print (subDir)
        try:
            ensure_dir(saveDir)
        except:
            print ("Error creating or reading directory: {0}".format(saveDir))
        os.chdir(saveDir)
        try:
            ensure_dir(subDir)
            os.chdir(subDir)
            for i, img in enumerate(self.caPILimgs):
    #            img.save(subDir + "{:0>3}".format(str(i)) + ".png")
                if i % 2 == 0:
                    img.save("{:0>3}".format(str(i)) + ".png")
        except:
            print ("Error creating or reading directory: {0}".format(subDir))
        
        

    # def createMenu(self):
    #     self.menuCanvas = tk.Canvas(self, bg = "gray30", bd = 0)
    #     self.menuCanvas.grid(row=0, column=0, columnspan = 4, sticky=tk.E+tk.W+tk.N)
    #     self.menuFrame = tk.Frame(self.menuCanvas)
    #     self.menuFrame.grid()
    #     self.menuLabel = tk.Label(self.menuFrame, text = "HERE GONNA BE MENU BAR")
    #     self.menuLabel.grid()

    def createMenuBar(self):
        #self.fileMenu = tk.Menu(self)

        top = self.winfo_toplevel()
        print ("createMenuBar -> self.winfo_toplevel() - {0}".format(top["height"]))
        self.menuBar = tk.Menu(top)
        top['menu'] = self.menuBar
        self.fileMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.fileMenu.add_command(label='Save all CA images', command=self.saveCAimages)
        self.fileMenu.add_command(label='Save Odd CA images', command=self.saveOddCAimages)
        self.fileMenu.add_command(label='Save Even CA images', command=self.saveEvenCAimages)
        self.editMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.editMenu.add_command(label='Settings')
        self.aboutMenu = tk.Menu(self.menuBar, tearoff = 0)
        self.aboutMenu.add_command(label='About')
        self.menuBar.add_cascade(label='File', menu=self.fileMenu)
        self.menuBar.add_cascade(label='Edit', menu=self.editMenu)
        self.menuBar.add_cascade(label='Help', menu=self.aboutMenu)        
        print ("createMenuBar -> top.event_info() - {0}".format(top.event_info()))

    def createInspectorMatrixFrame(self):
#        self.inspectorMatrixFrame = ttk.LabelFrame(self, text = "Inspector matrix combinations")
#        self.inspectorMatrixFrame.grid()
        self.leftCanvas = tk.Canvas(self, bg = "orange", bd = 0, width = 200 , height = 50, relief = "flat")
        self.leftCanvas.pack(side=LEFT, fill=BOTH)
        self.rightCanvas = tk.Canvas(self, bg = "magenta", bd = 0, width = 200 , height = 50, relief = "flat")
        self.rightCanvas.pack(side=RIGHT, fill=BOTH)
        self.headCanvas = tk.Canvas(self.leftCanvas, bg = "gray30", bd = 0, width = 200 , height = 50, relief = "flat")
        #self.headCanvas.grid(row=0, column=0, sticky=tk.N)
        #self.headCanvas.grid_propagate(0)
        self.headCanvas.pack(fill=BOTH, expand=1)

        print(["\n{0} > {1}".format(k, v) for k, v in self.headCanvas.configure().items()])

        self.headFrame = tk.Frame(self.headCanvas, bg ="cyan" , bd = 0, relief = "flat")
        self.headFrame.grid(row = 0, column = 0, sticky=tk.E+tk.S)
        #self.headFrame.pack(fill=BOTH, expand=1)
        # self.xButton = tk.Button(self.headFrame, text = "hanges", fg = self.text1Color, bg = self.bgColor)
        # self.xButton.bind("<ButtonRelease-1>", self.updateRule)
        # self.xButton.grid(row = 0, column = 0, sticky = E+W+N+S)
        
        self.label2 = tk.Label(self.headFrame, text = "BIN RULE: " + CaAPP.BIN_RULE, justify = "left", wraplength=self.width*2/3, fg = self.text1Color, bg = self.bgColor)
        self.label2.grid(sticky = W+E)
        
        self.label3 = tk.Label(self.headFrame, text = "INT RULE: " + str(CaAPP.INT_RULE), justify = "left", wraplength=self.width*2/3, fg = self.text1Color, bg = self.bgColor)
        self.label3.grid(sticky = W+E)
        
        self.headCanvas2 = tk.Canvas(self.leftCanvas, bg = "red", bd = 0, relief = "flat")
        #self.headCanvas2.grid(row=1, column=0, sticky=tk.E+tk.W+tk.N)
        self.headCanvas2.pack(fill=BOTH, expand=1)

        self.headFrame2 = tk.Frame(self.headCanvas2,bg = "blue", bd = 0)
        self.headFrame2.grid(sticky = E)

        self.label1 = tk.Label(self.headFrame2, text = "ALPHA NUMERIC RULE: ", justify = "left", wraplength=self.width*int(2/3.5), fg = self.text1Color, bg = self.bgColor)
        self.label1.grid(row = 0, column = 0, sticky = W)

        self.submitMatrixButton = tk.Button(self.headFrame2, text = "Submit by button changes", fg = self.text1Color, bg = self.bgColor)
        self.submitMatrixButton.bind("<ButtonRelease-1>", self.updateRule)
        self.submitMatrixButton.grid(row = 0, column = 1, sticky = E)

        self.ruleEntry = tk.Entry(self.headFrame2, relief = "flat", textvariable = self.ruleStrVar, width = int(self.width*1/16), fg = "black", bg = "white")
        self.ruleEntry.grid(row = 0, column = 2, sticky = W)
        self.ruleEntry.insert(0,CaAPP.ALPHA_NUM_RULE)       
        

        self.inspectorMatrixCanvas = tk.Canvas(self.leftCanvas, bg = "gray30", bd = 0, relief = "flat")
        #self.inspectorMatrixCanvas.grid(row=2, column=0, sticky=tk.E+tk.W+tk.N)
        self.inspectorMatrixCanvas.pack(fill=BOTH, expand=1)
        self.inspectorMatrixFrame = tk.Frame(self.inspectorMatrixCanvas, bg = self.bgColor, bd = 0, relief = "flat")
        self.inspectorMatrixFrame.grid(sticky = W+E)
        
        self.currentRow += 1

        self.buttonImage = PhotoImage(file = r"C:\DANO\_WORK\PYTHON\projects\CA_APP\cross-on.gif")
        
        self.matrixButtons = []
        """
            create inspector matrix buttons:
        """
        
        for i,img in enumerate(self.matrixButtonImgs):
            ruleValue = int(CaAPP.BIN_RULE[i])
            button = MatrixButton(self.inspectorMatrixFrame, self.matrixButtonImgs[i], image=img[ruleValue], bg = self.bgColor, borderwidth = 1, relief = "flat", overrelief = "ridge", padx = 0, pady = 0)
            button.value = ruleValue
            button.setImage()
            button.bind("<ButtonRelease-1>", self.addMatrixSelection)            
            self.matrixButtons.append(button)
        """
            Dislpay inspector matrix buttons
        """
        self.inspMatrixRBaction()
        
        self.currentRow = self.currentRow + (len(self.matrixButtons)/self.cols) + 1

    def createInitialImageCanvas(self):
        
        self.initialImageControlsCanvas = tk.Canvas(self.rightCanvas, bg = "gray30", bd = 0, height = 50)
        self.initialImageControlsCanvas.grid_propagate(0)
        #self.initialImageControlsCanvas.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N, rowspan = 1, columnspan = 3)
        self.initialImageControlsCanvas.pack(fill=BOTH, expand=1)
        
        
        self.initialImageControlsFrame = tk.Frame(self.initialImageControlsCanvas, bg = "green", bd = 0)
        self.initialImageControlsFrame.grid(columnspan =1, sticky=tk.W+tk.E+tk.N)
        #self.initialImageControlsFrame.pack(fill=BOTH, expand=1)

        self.changeRuleButton = tk.Button(self.initialImageControlsFrame, text = "Change by entry Rule", fg = self.text1Color, bg = self.bgColor)
        self.changeRuleButton.bind("<ButtonRelease-1>", self.updateRule)
        self.changeRuleButton.grid(row = 0, column = 0, columnspan = 1, sticky = W+E)

        self.initialImageRBon = tk.Radiobutton(self.initialImageControlsFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Initial condition from matrix", command=self.radiobuttonAction, variable = self.rbVar, value = 1)
        self.initialImageRBon.grid(row = 1, column = 0)

        self.initialImageRBoff = tk.Radiobutton(self.initialImageControlsFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "One pixel initial condition ON", command=self.radiobuttonAction, variable = self.rbVar, value = 0)
        self.initialImageRBoff.grid(row = 1, column = 1)

        self.initialImageCanvas = tk.Canvas(self.rightCanvas, bg = "gray30", bd = 0)
        #self.initialImageCanvas.grid(row=1, column=1, sticky=tk.E+tk.W+tk.N+tk.S, columnspan = 3, rowspan = 2)
        self.initialImageCanvas.pack(fill=BOTH, expand=1)
        self.initialImageFrame = tk.Frame(self.initialImageCanvas, bg = "cyan", bd = 0)
        self.initialImageFrame.grid(columnspan =1)

        

        
        self.initialMatrixButtons = []
        
        imageOn = ImageTk.PhotoImage(Image.new("RGBA",(self.initButtonSize, self.initButtonSize), (255, 255, 255, 255)))
        imageOff = ImageTk.PhotoImage(Image.new("RGBA",(self.initButtonSize, self.initButtonSize), (0, 0, 0,255)))
        for x in range(0, self.intialMatrixWidth * self.intialMatrixWidth):
            button = InitialMatrixButton(self.initialImageFrame, (imageOff, imageOn), image=imageOff, 
                width = self.initButtonSize, height=self.initButtonSize, bg = self.bgColor, borderwidth = 0, 
                relief = "flat", overrelief = "ridge", padx = 0, pady = 0)
            button.value = 0
            button.setImage()
            button.bind("<ButtonPress-1>", self.addInitialMatrixSelection)            
            self.initialMatrixButtons.append(button)
        for i,img in enumerate(self.initialMatrixButtons):
            img.grid(column=i%self.intialMatrixWidth, row = (int(i/self.intialMatrixWidth)), padx=0, pady = 0)

    def create_CA_Canvas(self):
        self.generateCAimgs()
        self.buttonCanvas = tk.Canvas(self.leftCanvas, height = 50, bg = "gray30", bd = 0)
        #self.buttonCanvas.grid(row=3, column=0, sticky=tk.E+tk.W+tk.N)
        self.buttonCanvas.pack(fill=BOTH, expand=1)
        self.buttonFrame = tk.Frame(self.buttonCanvas, bd = 0)
        self.buttonFrame.grid(column = 0, row = 1, sticky = E+W)

#        self.testLabel = tk.Label(self.buttonFrame, text = "BIN RULE: " + CaAPP.BIN_RULE, justify = "left", wraplength=self.width-10, fg = self.text1Color, bg = self.bgColor)
#        self.testLabel.grid(sticky = W)

        self.caLayCountSbLabel = tk.Label(self.buttonFrame, text = "CA Layers Count: ", justify = "left", fg = self.text1Color, bg = self.bgColor)
        self.caLayCountSbLabel.grid(column = 2, row = 0, sticky = W)
        

        self.caLayCountSB = tk.Spinbox(self.buttonFrame, text="CA Layers Count", relief = "flat", bd = 0, fg = self.text1Color, bg = self.bgColor, from_=10, to=300)
        self.caLayCountSB.bind("<ButtonRelease-1>", self.updateCaLaycountSB)
        self.caLayCountSB.bind("<Return>", self.updateCaLaycountSB)
        self.caLayCountSB.grid(column = 3, row = 0, sticky = W)





        self.inspMatrixButtonsOrderRBon = tk.Radiobutton(self.buttonFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Ordered sequence", command=self.inspMatrixRBaction, variable = self.imRbVar, value = 0)
        self.inspMatrixButtonsOrderRBon.grid(row = 0, column = 5)

        self.inspMatrixButtonsOrderRBoff = tk.Radiobutton(self.buttonFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Grouped symetries", command=self.inspMatrixRBaction, variable = self.imRbVar, value = 1)
        self.inspMatrixButtonsOrderRBoff.grid(row = 0, column = 6)

        self.inspMatrixButtonsOrderRBasym = tk.Radiobutton(self.buttonFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Grouped asymetries", command=self.inspMatrixRBaction, variable = self.imRbVar, value = 2)
        self.inspMatrixButtonsOrderRBasym.grid(row = 0, column = 8)

        self.inspMatrixButtonsOrder2axisSym = tk.Radiobutton(self.buttonFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Grouped 2 and 4 axis symetries", command=self.inspMatrixRBaction, variable = self.imRbVar, value = 3)
        self.inspMatrixButtonsOrder2axisSym.grid(row = 0, column = 7)

        

        # self.saveImgsButton = tk.Button(self.buttonFrame, text = "Save CA images", fg = self.text1Color, bg = self.bgColor)
        # self.saveImgsButton.bind("<ButtonRelease-1>", self.saveCAimages)
        # self.saveImgsButton.grid(row = 0, column = 10, sticky = E)
        # (print "create_CA_Canvas -> self.saveImgsButton.event_info() - {0}".format(self.saveImgsButton.event_info(virtual=None)))


        self.currentRow += 1

        self.caCanvas = tk.Canvas(self.leftCanvas, bg = "gray40")
        self.caCanvas.bind("<MouseWheel>", self.caCanvasZoom)
        self.caCanvas.bind("<ButtonPress-2>", self.caCanvasGrab)
        self.caCanvas.bind("<B2-Motion>", self.caCanvasDrag)
        #self.caCanvas.grid(row=4, column=0, sticky=tk.E+tk.W+tk.N, columnspan = 4)
        self.caCanvas.pack(side=LEFT, expand=1)
        
        self.caCanvas.addtag_all("CA")
        self.caCanvas.config(scrollregion=self.caCanvas.bbox(ALL))

        self.zoomInButton = tk.Button(self.buttonFrame, text = "+", fg = self.text1Color, bg = self.bgColor)
        self.zoomInButton.bind("<ButtonRelease-1>", self.zoomIn)
        self.zoomInButton.grid(row = 0, column = 0, sticky = W)

        self.zoomOutButton = tk.Button(self.buttonFrame, text = "-", fg = self.text1Color, bg = self.bgColor)
        self.zoomOutButton.bind("<ButtonRelease-1>", self.zoomOut)
        self.zoomOutButton.grid(row = 0, column = 1, sticky = W)
        
       
#        self.caCanvas.itemconfigure(myCanvWinID, window = )

        
        self.scrollY = tk.Scrollbar(self.leftCanvas, orient=tk.VERTICAL, bg = "black", command=self.caCanvas.yview)
        #self.scrollY.grid(row=4, column=3, sticky=tk.N+tk.S+tk.E)
        self.scrollY.pack(fill=Y,side=LEFT, expand=1)
        self.currentRow += 1
        self.scrollX = tk.Scrollbar(self.leftCanvas, orient=tk.HORIZONTAL, command=self.caCanvas.xview)
        #self.scrollX.grid(row=5, column=0, sticky=tk.E+tk.W)
        self.scrollX.pack(fill=BOTH, expand=1)
        self.currentRow += 1
  
    def radiobuttonAction(self):
        print (self.rbVar.get())
        myConfig = self.initialMatrixButtons[0].config()
        initialBGcolor = myConfig['background'][len(myConfig['background'])-1]
        print ("len(initialBGcolor)")
        print (initialBGcolor)
        for i in self.initialMatrixButtons:
            if self.rbVar.get() == 0:
                i.config(state = DISABLED)
                i.config(bg = initialBGcolor)
                i.setValue(0)

            else:
                i.config(state = NORMAL)
        pass

    def inspMatrixRBaction(self):
        for i in self.matrixButtons:
            i.grid_forget()
        print (self.imRbVar.get())
        if self.imRbVar.get() == 0:
            self.gridOrderedSequence()
        elif self.imRbVar.get() == 1:
            self.gridBySymGroups()
        elif self.imRbVar.get() == 2:
            self.gridByAsymGroups()
        elif self.imRbVar.get() == 3:
            self.gridBy2axisSymetryGroups()

    def gridOrderedSequence(self):
        for i,but in enumerate(self.matrixButtons):
            but.grid(column=i%self.cols, row = int(i/self.cols), padx=0, pady = 0)  
            but.configure(relief = "flat")

    def gridBySymGroups(self):
        self.symetryOneAxisGroups = getSymetryOneAxisGroups()
        self.buttonFramesLev1 = []
        print ("matrixButton.winfo_name() - {c}".format(c = self.matrixButtons[0].winfo_name()))
        for i, lev1 in enumerate(self.symetryOneAxisGroups):
            self.buttonFrameLev1 = tk.Frame(self.buttonFrame, bd = 0)
            self.buttonFrameLev1.grid(row = i)
            self.buttonFramesLev1.append(self.buttonFrameLev1)            
            for j, lev2 in enumerate(lev1):
                print(lev2)
                print ("level 1 count - {count1}; level 2 count - {count2}".format(count1 = i, count2 = j))
                for b, pos in enumerate(lev2):
                    myButton = self.matrixButtons[lev2[b]]
                    myButton.grid(column = b+(len(lev2)*j), row = i)
                    if j % 2 == 0:
                        myButton.configure(relief = "groove")
                    else:
                        myButton.configure(relief = "flat")
        pass

    def gridBy2axisSymetryGroups(self):
        self.symetryTwoAxisGroups = getSym2axisGroup()
        self.buttonFramesLev1 = []
        for i, lev1 in enumerate(self.symetryTwoAxisGroups):
            self.buttonFrameLev1 = tk.Frame(self.buttonFrame, bd = 0)
            self.buttonFrameLev1.grid(row = i)
            self.buttonFramesLev1.append(self.buttonFrameLev1)            
            for j, lev2 in enumerate(lev1):
                print(lev2)
                print ("level 1 count - {count1}; level 2 count - {count2}".format(count1 = i, count2 = j))
                for b, pos in enumerate(lev2):
                    myButton = self.matrixButtons[lev2[b]]
                    myButton.grid(column = b+(len(lev2)*j), row = i)
                    if j % 2 == 0:
                        myButton.configure(relief = "groove")
                    else:
                        myButton.configure(relief = "flat")
        pass

    def gridByAsymGroups(self):
        self.asymetryGroups = getAsymetryGroups()
        self.buttonFramesLev1 = []
        print ("matrixButton.winfo_name() - {c}".format(c = self.matrixButtons[0].winfo_name()))
        for i, lev1 in enumerate(self.asymetryGroups):
            self.buttonFrameLev1 = tk.Frame(self.buttonFrame, bd = 0)
            self.buttonFrameLev1.grid(row = i)
            self.buttonFramesLev1.append(self.buttonFrameLev1)            
            for j, lev2 in enumerate(lev1):
                print(lev2)
                print ("level 1 count - {count1}; level 2 count - {count2}".format(count1 = i, count2 = j))
                for b, pos in enumerate(lev2):
                    myButton = self.matrixButtons[lev2[b]]
                    myButton.grid(column = b+(len(lev2)*j), row = i)
                    if j % 2 == 0:
                        myButton.configure(relief = "groove")
                    else:
                        myButton.configure(relief = "flat")
        pass



        

#mainWindow.geometry("500x500")
app = CaAPP(mainWindow)
app.master.title("Celular automaton Application")

#caCanvas = tk.Canvas(app, height = 650, bg = "black", )
#caCanvas.grid(row=0, column=0, sticky=tk.E+tk.W, columnspan = 50)
# windowFrame = tk.Frame(app.caCanvas, width = 1000, height = 1000, bg = "red", bd = 5)
# windowFrame.grid()
# testLabel = tk.Label(windowFrame, text = "BIN RULE: ", justify = "left", fg = 'white', bg = 'black')
# testLabel.grid(sticky = W, rowspan=30)
# app.caCanvas.create_image(100, 100 , image = app.caIMGs[29], anchor = tk.NW)

app.mainloop()