import Tkinter as tk 
from Tkinter import *
from ca_func import *
from PIL import ImageTk, Image, ImageDraw
import ttk
import types
from numpy import base_repr

mainWindow = Tk()
mainWindow.grid()
mainWindow.grid_propagate(1)

class MatrixButton(tk.Button):
    INSTANCE_NUM = 0
    def __init__(self, *args, **kwargs):
#        print "len(*args)"
#        print len(args)
#        print args[1][0]
#        print MatrixButton.INSTANCE_NUM
        tk.Button.__init__(self, *args[0:1], **kwargs)
        self.value = 0         
        self.ID = self.INSTANCE_NUM
        MatrixButton.INSTANCE_NUM += 1
#        self.imgON = ImageTk.PhotoImage(args[1])
#        print "self.imgON"
#        print args[1][1]
#        args[1][1].save(r"C:/testPix3b.png")
#        args[1][0].save(r"C:/testPix3a.png")
        self.imgs = [args[1][0], args[1][1]]
#        print "self.imgs-assigned"
        
    def switchValue(self):
        if self.value == 0:
            self.setValue(1)
        elif self.value == 1:
            self.setValue(0)
        self.configure(bg = "red")
        
    def selectionOff(self):
        self.configure(bg = "Gray80")
        self.setImage()
    #def setImage(self):
    #    self.config(image = self.imgs[self.value])
    def setImage(self, *args):
        if len(args) !=0:
            self.imgs = args[0]
            print "MatrixButton->setImage()->self.imgs was set to {0} and {1}".format(args[0][0], args[0][1])
        self.config(image = self.imgs[self.value])
    def reset(self):
        print self.configure()
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
        self.height = 900
        self.bgColor = "Gray16"
        self.text1Color = "white"
        self.text2Color = "Gray30"
 #       self.config(height = 800)
        master.geometry("" + str(self.width) + "x" + str(self.height))
        master.resizable(1, 1)
        self.matrixButtonsToChange = []         
        self.cols = 89
        


#        self.createWidgets()
        self.createMenu()
        self.createInspectorMatrixFrame()        
        self.caLayCount = 30
        self.caCols = 35
        self.caCanvasXscale = 1.0
        self.caCanvasYscale = 1.0
        self.caCanvasScaleInc = 0.05
        self.create_CA_Canvas()
        self.initButtonSize = 13
        
        self.initialMatrixToChange = [] 
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
        print "PIL images created"
        self.matrixButtonImgs = []
        for i, img in enumerate(PILimagesON):
#            imageON = ImageTk.PhotoImage(img)
#            imageOFF = ImageTk.PhotoImage(PILimagesOFF[i])
            self.matrixButtonImgs.append([PILimagesOFF[i], img])
        # print self.matrixButtonImgs
        # print "matrixButtonImgs created"

    def updateMatrixButtons(self):
        for i, w in enumerate(self.matrixButtons):
            w.setValue(int(self.BIN_RULE[i]))
            w.setImage(self.matrixButtonImgs[i])
            


    def getLogData():
        return self.myLogData

    def setGlobals(self):
        CaAPP.HEX_RULE = "0" 
        self.ruleStrVar = CaAPP.HEX_RULE        
        # print "setGlobals - CaAPP.HEX_RULE"
        # print CaAPP.HEX_RULE
        CaAPP.BIN_RULE = getBinRuleFromHex(CaAPP.HEX_RULE)
        
        # print "setGlobals - CaAPP.BIN_RULE"
        # print CaAPP.BIN_RULE
        # print type(CaAPP.BIN_RULE)
        CaAPP.INT_RULE = int(CaAPP.BIN_RULE,2)
        # print "setGlobals - CaAPP.INT_RULE"
        # print CaAPP.INT_RULE
    
    def updateBINrule(self, inBinRule):
        CaAPP.BIN_RULE = inBinRule
    #    print "updateBINrule() - inBinRule" + str(int(inBinRule,2))
    #    print "updateBINrule() - BIN_RULE" + str(int(CaAPP.BIN_RULE,2))
        CaAPP.INT_RULE = int(CaAPP.BIN_RULE,2)
        CaAPP.HEX_RULE = "{0:x}".format(CaAPP.INT_RULE)
        
    def updateHEXrule(self):
        CaAPP.HEX_RULE = self.ruleEntry.get()
        self.ruleStrVar = CaAPP.HEX_RULE
        CaAPP.BIN_RULE = getBinRuleFromHex(CaAPP.HEX_RULE)
        CaAPP.INT_RULE = int(CaAPP.BIN_RULE,2)        
        
    def setPaths(self):
        self.CSV_logPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/LOG/"
        self.saveCAimagesPath = r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/RNDCA2D9-sequence/interesting/"
        self.logReadPath = self.CSV_logPath + "CA2D9_" + self.HEX_RULE + "_" + str(self.caResX) + "x" + str(self.caResY) + ".csv"

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
    # #    print "setBINRuleByHEX - inHex"
    # #    print inHex
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
    #        print "Added to matrixButtonsToChange " + str(udalost.widget.ID)
    #    print self.matrixButtonsToChange
    #    print "hodnota value"
    #    print udalost.widget.value
    #    print "MatrixButton ID"
    #    print udalost.widget.ID

    def addInitialMatrixSelection(self, udalost):
        myButton = udalost.widget
        myConf = myButton.config()
        stateValues = myConf['state']
        stateValue = stateValues[len(stateValues)-1]
        print 'stateValue of button {0} = {1}'.format(myButton.ID, stateValue)
#        print stateValue
        if stateValue != "disabled":
            udalost.widget.switchValue()
            self.updateInitialImageMatrix(udalost.widget.getID(), udalost.widget.getValue())
            print "mozes kludne"

        else:
            print "nene nezmenis hodnotu"
            pass
    #    self.initialMatrixButtons

    def createInitialImage(self):
        img = Image.new("RGBA",(self.caResX,self.caResY), (0,0,0,255))
        if self.rbVar.get() == 0:
            img = createFirstLayerFromScratch(self.caResX, self.caResY)
        return img

    def updateRule(self, udalost):
#        updatedRule = self.switchRuleValues(self.BIN_RULE)
    #    print "self.INT_RULE"
    #    print self.INT_RULE
        print "len(self.matrixButtonsToChange)"
        print len(self.matrixButtonsToChange)
        print "udalost.widget.cget(text)"
        print udalost.widget.cget('text')
        self.caLayCount = int(self.caLayCountSB.get())
        if udalost.widget.cget('text') == 'Change Rule':
            self.updateHEXrule()
        else:
            updatedRule = self.getNewRule()
            self.updateBINrule(updatedRule)
        self.setPaths()
        print "Path to LOG file was updated to : {0}".format(self.logReadPath)
        self.generateCAimgs()
        self.getMatrixImgs()        
        self.updateMatrixButtons()
        if len(self.matrixButtonsToChange) != 0:            
    #        self.createInspectorMatrixFrame()
            for i in self.matrixButtonsToChange: 
                self.matrixButtons[i].selectionOff()
                self.matrixButtons[i].setImage()
        elif udalost.widget.cget('text') == 'Change Rule':            
            for i, w in enumerate(self.matrixButtons):
                w.setValue(int(CaAPP.BIN_RULE[i]))
        self.matrixButtonsToChange = []
        
        self.label2.configure(text = "BIN RULE: " + CaAPP.BIN_RULE)
        self.label3.configure(text = "INT RULE: " + str(CaAPP.INT_RULE))
       
        ruleEntryText = self.ruleEntry.get()     
        print ruleEntryText
        self.ruleEntry.delete(0, len(ruleEntryText))    
        self.ruleEntry.insert(0,CaAPP.HEX_RULE)
        self.updateCanvas()
        self.createInitialImage()
        #    print "self.INT_RULE"
        #    print self.INT_RULE

    def updateCanvas(self):        
        self.caCanvas.delete("all")
        yOffset = 50
        for i, image in enumerate(self.caIMGs): 
            
            #imgXsize = image.size[0]
            #imgYsize = image.size[1]
            #resImg = image.resize((int(imgXsize * self.caCanvasXscale), int(imgYsize * self.caCanvasYscale)), Image.ANTIALIAS)
            self.caPILimgs[0].save(r"C:/_WORK/PYTHON/CELULAR_AUTOMAT-2D/RNDCA2D9-sequence/eeee.png")
            #pImage = ImageTk.PhotoImage(image)
            pImage = image
            print "photoImage width - {w} - height {h}".format(w = pImage.width(), h = pImage.height())
            print pImage
            self.caCanvas.create_image((i % self.caCols)*pImage.width(), yOffset + ((i / self.caCols) * pImage.height()) , image = pImage, anchor = tk.NW)
       
    def updateInspMatrixImgs(self, udalost):        
        self.caCanvas.delete("all")
        yOffset = 50        
        myHexRule1 = "38084200800000565465431654984321e549684321665abcd767323486132546879843573573573398984984948484dffd888484123213516516513516513213"
        myBinRule1 = getBinRuleFromHex(myHexRule1)
        myLogDataPath = self.getLOGpath(myHexRule1)
        myLogData = readCSV_Log(myLogDataPath)
        print "myLogData from path: {0} was loaded".format(myLogDataPath)
        self.myNewImages0 = getCrossImgs(getBinRuleFromHex("0"), getInspArraySeqence(9), 2, myLogData)
        self.myNewImages1 = getCrossImgs(getBinRuleFromHex("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"), 
                                         getInspArraySeqence(9), 2, myLogData)
        self.matrixButtonImgs = []
        for i, v in enumerate(self.myNewImages0):
            self.matrixButtonImgs.append([v, self.myNewImages1[i]])        
        for j, b in enumerate(self.matrixButtons):
            b.setImage(self.matrixButtonImgs[j])
        myCaimage = self.caIMGs[5]
        rImage = self.caPILimgs[5].resize((200,200))
        self.resizedImage = ImageTk.PhotoImage(rImage)
        for i, img in enumerate(self.myNewImages0):
            
            self.caCanvas.create_image(i*50, 0 ,image = img, anchor = tk.NW)
            self.caCanvas.create_image(i*50, 50 ,image = self.myNewImages1[i], anchor = tk.NW)
        #print myCaimage       
        self.testButton = tk.Button(self.caCanvas, image = myCaimage)
        self.caCanvas.create_image(100, 0 ,image = self.resizedImage, anchor = tk.NW)
        self.testButton.grid()
        #self.buttonFrame = tk.Frame(self.caCanvas, width = 100, height = 20, bd = 0)
        #self.buttonFrame.grid(sticky = N+S+E+W)
        #self.caCanvas.create_image(0, 0 , image = myCaimage, anchor = tk.NW)
        #self.caCanvas.create_window(0,0, height = 100, width = 100)

    def caCanvasZoom(self, udalost):
        print udalost.delta
        if udalost.delta>0: print "ZOOM IN!"
        elif udalost.delta<0: print "ZOOM OUT!"
    
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
        print type(self.caLayCount)
        print self.caLayCount
        print "self.caLayCount was updated"
        print int(udalost.widget.winfo_geometry().split("x")[0])

    def zoomIn(self, udalost):
        #self.caCanvas.delete("all")
        self.caCanvasXscale += self.caCanvasScaleInc
        self.caCanvasYscale += self.caCanvasScaleInc
        self.caCanvas.scale("all", 0, 0, 1 + self.caCanvasScaleInc, 1 + self.caCanvasScaleInc)
        #self.updateCanvas()
    
    def zoomOut(self, udalost):
        #self.caCanvas.delete("all")
        self.caCanvasXscale -= self.caCanvasScaleInc
        self.caCanvasYscale -= self.caCanvasScaleInc
        self.caCanvas.scale("all", 1 - self.caCanvasScaleInc, 1 - self.caCanvasScaleInc)
        #updateCanvas()

    def getNewRule(self):
        returnRule = ""
        for i in self.matrixButtons:
            returnRule += str(i.value)
    #    print "getNewRule() - returnRule" + str(int(returnRule,2))
    #    print "getNewRule() - BIN_RULE" + str(int(self.BIN_RULE,2))
        return returnRule

    def switchRuleValues(self, inRule):
        
        if type(inRule) is types.StringType:
            returnRule = ""
    #        print "type = StringType"
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
    #        print "type = ListType"
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
                print "getHexFromInitialImg - i:"
                print i
                sPos = i
                zeroSpos = True
                ePos = i
            elif w.getValue() == 1 and sPos == 0 and zeroSpos == False:
                sPos = i
                ePos = i
            elif w.getValue() == 1 and i!= 0:
                ePos = i

        print "sPos"
        print sPos
        print "ePos"
        print ePos
        print binVal[sPos:ePos]
        if sPos == len(binVal) - 1:
            sPos = len(binVal) - 2
        if ePos == len(binVal) - 1:
            ePos = len(binVal) - 2
        intVal = int(binVal[sPos:((ePos + 1) % len(binVal))],2)
        print "intVal"
        print intVal
        hexVal = "{0:x}".format(intVal) 
        print "hexVal"
        print hexVal
        return intVal

    def saveCAimages(self, udalost):
        print os.getcwd()
        os.chdir(self.saveCAimagesPath)
        print os.getcwd()
        saveDir = self.HEX_RULE + "/"
#        saveDir = self.saveCAimagesPath + base_repr(self.INT_RULE, 36) + "/"
#        subDir = saveDir + "/" + base_repr(self.getIntFromInitialImg(), 36) + "/"
        subDir = u"" + base_repr(self.getIntFromInitialImg(), 36) + "/"
        print subDir
        try:
            ensure_dir(saveDir)
        except:
            print "Error creating or reading directory: {0}".format(saveDir)
        os.chdir(saveDir)
        try:
            ensure_dir(subDir)
        except:
            print "Error creating or reading directory: {0}".format(subDir)
        os.chdir(subDir)
        for i, img in enumerate(self.caPILimgs):
#            img.save(subDir + "{:0>3}".format(str(i)) + ".png")
            img.save("{:0>3}".format(str(i)) + ".png")

    def createMenu(self):
        self.menuCanvas = tk.Canvas(self, bg = "gray30", bd = 0)
        self.menuCanvas.grid(row=0, column=0, columnspan = 4, sticky=tk.E+tk.W+tk.N)
        self.menuFrame = tk.Frame(self.menuCanvas)
        self.menuFrame.grid()
        self.menuLabel = tk.Label(self.menuFrame, text = "HERE GONNA BE MENU BAR")
        self.menuLabel.grid()

    def createInspectorMatrixFrame(self):
#        self.inspectorMatrixFrame = ttk.LabelFrame(self, text = "Inspector matrix combinations")
#        self.inspectorMatrixFrame.grid()
        
        self.headCanvas = tk.Canvas(self, bg = "gray30", bd = 0, relief = "flat")
        self.headCanvas.grid(row=1, column=0, columnspan = 4, sticky=tk.E+tk.W+tk.N)

        self.headFrame = tk.Frame(self.headCanvas, bd = 0, relief = "flat")
        self.headFrame.grid(columnspan =1)

        
        
        self.label2 = tk.Label(self.headFrame, text = "BIN RULE: " + CaAPP.BIN_RULE, justify = "left", wraplength=self.width*2/3, fg = self.text1Color, bg = self.bgColor)
        self.label2.grid(row = 0, columnspan = 1, sticky = W+E)
        
        self.label3 = tk.Label(self.headFrame, text = "INT RULE: " + str(CaAPP.INT_RULE), justify = tk.LEFT, wraplength=self.width*2/3, fg = self.text1Color, bg = self.bgColor)
        self.label3.grid(row = 1, columnspan = 1, sticky = W+E)
        

        self.headCanvas2 = tk.Canvas(self, bg = "gray30", bd = 0, relief = "flat")
        self.headCanvas2.grid(row=2, column=0, columnspan = 3, sticky=tk.E+tk.W+tk.N)

        self.headFrame2 = tk.Frame(self.headCanvas2, bd = 0)
        self.headFrame2.grid(columnspan =1, sticky = E)

        self.label1 = tk.Label(self.headFrame2, text = "HEX RULE: ", justify = "left", wraplength=self.width*int(2/3.5), fg = self.text1Color, bg = self.bgColor)
        self.label1.grid(row = 0, sticky = W)

        self.ruleEntry = tk.Entry(self.headFrame2, relief = "flat", textvariable = self.ruleStrVar, width = self.width*2/3, fg = "black", bg = "white")
        self.ruleEntry.grid(row = 0, column = 1, sticky = W)
        self.ruleEntry.insert(0,CaAPP.HEX_RULE)

        self.inspectorMatrixCanvas = tk.Canvas(self, bg = "gray30", bd = 0, relief = "flat")
        self.inspectorMatrixCanvas.grid(row=4, column=0, columnspan = 2, sticky=tk.E+tk.W+tk.N)

        self.inspectorMatrixFrame = tk.Frame(self.inspectorMatrixCanvas, bg = self.bgColor, bd = 0, relief = "flat")
        self.inspectorMatrixFrame.grid(sticky = W+E)
        

        self.buttonImage = PhotoImage(file = "cross-on.gif")
        
        self.matrixButtons = []
        """
            create inspector matrix buttons:
        """
        
        for i,img in enumerate(self.matrixButtonImgs):
            ruleValue = int(CaAPP.BIN_RULE[i])
            button = MatrixButton(self.inspectorMatrixFrame, self.matrixButtonImgs[i], image=img[ruleValue], bg = self.bgColor, borderwidth = 1, relief = "flat", overrelief = "ridge", padx = 0, pady = 0)
            button.value = ruleValue
            button.bind("<ButtonRelease-1>", self.addMatrixSelection)            
            self.matrixButtons.append(button)
        """
            Dislpay inspector matrix buttons
        """
        self.inspMatrixRBaction()
        
        
    def create_CA_Canvas(self):
        self.generateCAimgs()
        self.buttonCanvas = tk.Canvas(self, height = 50, bg = "gray30", bd = 0)
        self.buttonCanvas.grid(row=3, column=0, sticky=tk.E+tk.W, columnspan = 1)
        
        self.buttonFrame = tk.Frame(self.buttonCanvas, bd = 0)
        self.buttonFrame.grid(columnspan =1)

#        self.testLabel = tk.Label(self.buttonFrame, text = "BIN RULE: " + CaAPP.BIN_RULE, justify = "left", wraplength=self.width-10, fg = self.text1Color, bg = self.bgColor)
#        self.testLabel.grid(sticky = W)

        self.caLayCountSbLabel = tk.Label(self.buttonFrame, text = "CA Layers Count: ", justify = "left", fg = self.text1Color, bg = self.bgColor)
        self.caLayCountSbLabel.grid(column = 2, row = 0, sticky = W)
        

        self.caLayCountSB = tk.Spinbox(self.buttonFrame, text="CA Layers Count", relief = "flat", bd = 0, fg = self.text1Color, bg = self.bgColor, from_=10, to=300)
        self.caLayCountSB.bind("<ButtonRelease-1>", self.updateCaLaycountSB)
        self.caLayCountSB.bind("<Return>", self.updateCaLaycountSB)
        self.caLayCountSB.grid(column = 3, row = 0, sticky = W)

        self.submitMatrixButton = tk.Button(self.buttonFrame, text = "Submit changes", fg = self.text1Color, bg = self.bgColor)
        self.submitMatrixButton.bind("<ButtonRelease-1>", self.updateRule)
        self.submitMatrixButton.grid(row = 0, column = 8, sticky = W)

        self.zoomInButton = tk.Button(self.buttonFrame, text = "+", fg = self.text1Color, bg = self.bgColor)
        self.zoomInButton.bind("<ButtonRelease-1>", self.zoomIn)
        self.zoomInButton.grid(row = 0, column = 0, sticky = W)

        self.zoomOutButton = tk.Button(self.buttonFrame, text = "-", fg = self.text1Color, bg = self.bgColor)
        self.zoomOutButton.bind("<ButtonRelease-1>", self.zoomOut)
        self.zoomOutButton.grid(row = 0, column = 1, sticky = W)

        self.inspMatrixButtonsOrderRBon = tk.Radiobutton(self.buttonFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Ordered sequence", command=self.inspMatrixRBaction, variable = self.imRbVar, value = 0)
        self.inspMatrixButtonsOrderRBon.grid(row = 0, column = 5)

        self.inspMatrixButtonsOrderRBoff = tk.Radiobutton(self.buttonFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Grouped symetries", command=self.inspMatrixRBaction, variable = self.imRbVar, value = 1)
        self.inspMatrixButtonsOrderRBoff.grid(row = 0, column = 6)

        self.inspMatrixButtonsOrderRBasym = tk.Radiobutton(self.buttonFrame, fg = self.text2Color, bg = self.bgColor,
            indicatoron = 0, text = "Grouped asymetries", command=self.inspMatrixRBaction, variable = self.imRbVar, value = 2)
        self.inspMatrixButtonsOrderRBasym.grid(row = 0, column = 7)

        

        self.saveImgsButton = tk.Button(self.buttonFrame, text = "Update Inspector Matrix Images", fg = self.text1Color, bg = self.bgColor)
        self.saveImgsButton.bind("<ButtonRelease-1>", self.updateInspMatrixImgs)
        self.saveImgsButton.grid(row = 0, column = 9, sticky = E)

        self.caCanvas = tk.Canvas(self, bg = "gray40")
        self.caCanvas.bind("<MouseWheel>", self.caCanvasZoom)
        self.caCanvas.bind("<ButtonPress-2>", self.caCanvasGrab)
        self.caCanvas.bind("<B2-Motion>", self.caCanvasDrag)
        self.caCanvas.grid(row=5, column=0, sticky=tk.E+tk.W+tk.N, columnspan = 4)
        self.caCanvas.addtag_all("CA")
        self.caCanvas.config(scrollregion=self.caCanvas.bbox(ALL))
        
       
#        self.caCanvas.itemconfigure(myCanvWinID, window = )

        
        self.scrollY = tk.Scrollbar(self, orient=tk.VERTICAL, bg = "black", command=self.caCanvas.yview)
        self.scrollY.grid(row=5, column=3, sticky=tk.N+tk.S+tk.E)
        self.scrollX = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.caCanvas.xview)
        self.scrollX.grid(row=6, column=0, columnspan = 4, sticky=tk.E+tk.W)
  
    def inspMatrixRBaction(self):
        for i in self.matrixButtons:
            i.grid_forget()
        print self.imRbVar.get()
        if self.imRbVar.get() == 0:
            self.gridOrderedSequence()
        elif self.imRbVar.get() == 1:
            self.gridBySymGroups()
        elif self.imRbVar.get() == 2:
            self.gridByAsymGroups()

    def gridOrderedSequence(self):
        for i,but in enumerate(self.matrixButtons):
            but.grid(column=i%self.cols, row = i/self.cols, padx=0, pady = 0)  
            but.configure(relief = "flat")

    def gridBySymGroups(self):
        self.symetryOneAxisGroups = getSymetryOneAxisGroups()
        self.buttonFramesLev1 = []
        print "matrixButton.winfo_name() - {c}".format(c = self.matrixButtons[0].winfo_name())
        for i, lev1 in enumerate(self.symetryOneAxisGroups):
            self.buttonFrameLev1 = tk.Frame(self.buttonFrame, bd = 0)
            self.buttonFrameLev1.grid(row = i)
            self.buttonFramesLev1.append(self.buttonFrameLev1)            
            for j, lev2 in enumerate(lev1):
                print(lev2)
                print "level 1 count - {count1}; level 2 count - {count2}".format(count1 = i, count2 = j)
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
        print "matrixButton.winfo_name() - {c}".format(c = self.matrixButtons[0].winfo_name())
        for i, lev1 in enumerate(self.asymetryGroups):
            self.buttonFrameLev1 = tk.Frame(self.buttonFrame, bd = 0)
            self.buttonFrameLev1.grid(row = i)
            self.buttonFramesLev1.append(self.buttonFrameLev1)            
            for j, lev2 in enumerate(lev1):
                print(lev2)
                print "level 1 count - {count1}; level 2 count - {count2}".format(count1 = i, count2 = j)
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