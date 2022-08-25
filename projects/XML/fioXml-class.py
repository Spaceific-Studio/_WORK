import xml.etree.ElementTree as ET

import os
import sys
import shutil
#from PIL import Image, ImageDraw, ImageTk
import time
import re
from datetime import datetime, timedelta, tzinfo
#import kiwi
#import xmltodict

cwd = os.getcwd()
print("cwd {0}".format(cwd))
#runFileDialog = True
runFileDialog = False
haveFileName = False

fioApiLibPath = r"/storage/emulated/0/SdCardBackUp/PowerBI/FIO_API_BANKING/fio_api_module"
sys.path.append(fioApiLibPath)
from api import download_data, getUrlCommonTimeRange, getUrlSpareTimeRange, ensure_dir

"""
if runFileDialog:
	fileDialogWindow = Tk()
	#print("dir Tk {0}".				format(dir(fileDialogWindow)))
	#raise TypeError("Tk.winfo.height {0}".format(fileDialogWindow.winfo.height))
	fileDialogWindow.configure(height=900)
	fileDialogWindow.file_name = filedialog.askopenfile(initialdir=cwd, title="Open clash xml file", filetypes=(("xml files", "*.xml"), ("all files", "*.*")))
	print("Selected file: {0}".format(fileDialogWindow.file_name.name))
	try:
		fdFName = fileDialogWindow.file_name.name
		testName = fdFName.split("/")[-1].split(".")[0]
		fFormat = fdFName.split("/")[-1].split(".")[1]
		haveFileName = True
		fileDialogWindow.destroy()
	except Exception as ex:
		haveFileName = False
elif not haveFileName:
	testName = "2022-06-01_2022-06-30 transactions_common"
	fFormat = "xml"
#raise TypeError("fdName {0}.{1}".format(testName, fFormat))
#testName = "SO_03-02-ARS- MEC - hard"
#fFormat = "xml"
"""
#testName = "2022-06-01_2022-06-30 transactions_common"
class FioXml():
    def __init__(self, **kwargs):
        self.doBackup = kwargs['doBackup'] if 'doBackup' in kwargs else True
        self.testMode = kwargs['testMode'] if 'testMode' in kwargs else True
        self.doDownload = kwargs['doDownload'] if 'doDownload' in kwargs else True
        self.printStatistics = kwargs['printStatistics'] if 'printStatistics' in kwargs else True
        #type of account: 'common', 'spare''
        self.account = kwargs['account'] if 'account' in kwargs else 'common'

        self.testName = "2012-07-01_2022-06-30 transactions_common-test"
        self.mainFileName = "2012_07_01-MAIN"
        self.mainSpareFileName = "2012_07_01-MAIN_SPARE"
        self.fFormat = "xml"
        self.saveDataDirName = "data"
        #fName = "{0}{1}.{2}".format("data/", testName, fFormat)
        self.mainFileName = "{0}.{1}".format(self.mainFileName if self.account == 'common' else self.mainSpareFileName, self.fFormat) 
        self.dir = "/storage/emulated/0/SdCardBackUp/PowerBI/FIO_API_BANKING"
        self.testFilePath = os.path.join(self.dir, self.saveDataDirName, self.testName)
        self.mainFilePath = os.path.join(self.dir, self.mainFileName)
        self.dLine = "{0:_<12}".format("")
        #print(self.dLine)
        print("self.testFilePath {0}".format(self.testFilePath))
        print(self.dLine)
        print("self.mainFilePath {0}".format(self.mainFilePath))
        self.saveDataPath = os.path.join(self.dir, self.saveDataDirName)
        self.saveBackupDirName = "zaloha"
        self.saveBackupPath = os.path.join(self.dir, self.saveDataDirName, self.saveBackupDirName)
        print("self.saveDataPath {0}".format(self.saveDataPath))
        if self.doBackup:
            self.backupMainFile()
        self.setup()
        if len(self.appendingTransactionNodes) > 0:
            self.appendTransactionNodes()
            if not self.testMode:
                self.writeXml()
        if self.printStatistics:
            self.printStats()
        

        
    def backupMainFile(self):
        mainFileExist = False
        try:
            mainFile = open(self.mainFilePath)
            mainFile.close()
            mainFileExist = True
        except Exception as ex:
            print("mainFile {0} doesn't exist, trying to download mainFile data...")
            mainFile = False
        if not mainFile:
            self.nowDate = datetime.now()
            startDate = datetime(year=2012, month=7, day=1)
            if self.account == 'common':
                mainUrl = getUrlCommonTimeRange(startDate, self.nowDate)
            elif self.account == 'spare':
                mainUrl = getUrlSpareTimeRange(startDate, self.nowDate)
            #newMainFile = download_data(mainUrl, self.dir, self.mainFileName)
            print("mainFile has been downloaded to: {0}".format(os.path.join(self.dir, self.mainFileName)))
            
        try:
            if self.doBackup:
                ensure_dir(self.saveBackupPath)
                print("self.saveBackupPath {0}".format(self.saveBackupPath))
                shutil.copyfile(self.mainFilePath, os.path.join(self.saveBackupPath, self.mainFileName))
                print("Backup of main file {0} OK\nbackup dir:{1}".format(self.mainFileName, self.saveBackupPath))
        except Exception as ex:
            raise RuntimeError("Error while doing backup of main file: {0} - {1}".format(self.mainFilePath, sys.exc_info()))        
#with open(testFilePath, mode='w') as xmlFile:
#	data = xmlFile.read().replace("\n", "")

    def getNodeWithAttribute(self, parrentNode, inAttrName):
        #function returns first subnode from search list with atribute name of xml node
        nodes = parrentNode.findall("./*[@name = '{0}']".format(inAttrName))
        if not hasattr(nodes, '__iter__'):
            return nodes
        elif len(nodes) > 0:
            return nodes[0]
        else:
            return None
        
    def getReportDay(self, inInfoNode, **kwargs):
        returnStartDate = kwargs['start'] if 'start' in kwargs else True
        self.mainSDateNodeName = "dateStart"
        self.mainEDateNodeName = "dateEnd"
        dateName = "dateStart" if returnStartDate and returnStartDate == True else "dateEnd"
        print("dateName = {0}".format(dateName))
        """
        for child in inInfoNode:
            print("inInfoNode.{0} = {1}".format(child.tag, child.text))
        """
        dateStr = inInfoNode.findall("./{0}".format(dateName))[0].text if inInfoNode.findall("./dateStart") else None
        print("{0}: {1}".format(dateName, dateStr))
        if dateStr:
            splited = dateStr.split("+")
            print("splited {0}".format(splited))
            date = datetime.strptime(splited[0].strip(), "%Y-%m-%d")
            print("{0} {1}".format(dateName, date))
            return (date, dateStr)
        else:
            return None
            
    def setup(self):
        self.attrList = { \
                    'ID pohybu':0, \
                    'Datum':0, \
                    'Měna':0,\
                    'Objem':0,\
                    'Protiúčet':0,\
                    'Název protiúčtu':0,\
                    'Kód banky':0,\
                    'Název banky':0,\
                    'KS':0,\
                    'VS':0,\
                    'SS':0,\
                    'Uživatelská identifikace':0,\
                    'Zpráva pro příjemce':0,\
                    'Typ':0,\
                    'Provedl':0,\
                    'Upřesnění':0,\
                    'Komentář':0,\
                    'BIC':0,\
                    'ID Pokynu':0,\
                    'Reference plátce':0\
                    }
        self.mainTree = ET.parse(self.mainFilePath)
        self.mainRoot = self.mainTree.getroot()
        self.mainInfoNode = self.mainRoot.find("./Info")
        print("self.mainInfoNode {0}".format(self.mainInfoNode.tag))
        self.mainSDate, self.mainSDateStr = self.getReportDay(self.mainInfoNode, start=True)
        self.mainEDate, self.mainEDateStr = self.getReportDay(self.mainInfoNode, start=False)
        print(self.dLine)
        print("self.mainSDate {0}\nself.mainEDate {1}".format(self.mainSDate, self.mainEDate))
        print("self.mainSDateStr {0}\nself.mainEDateStr {1}".format(self.mainSDateStr, self.mainEDateStr))
        self.mainTransactionNodes = self.mainRoot.findall(".//Transaction")
        
        #GENERATE URL
        print(self.dLine)        
        self.nowDate = datetime.now()
        print(self.dLine)
        print("self.nowDate {0}".format(self.nowDate))
        if self.account == 'common':
            self.appendUrl = getUrlCommonTimeRange(self.mainEDate, self.nowDate)
        else:
            self.appendUrl = getUrlSpareTimeRange(self.mainEDate, self.nowDate)
        print(self.dLine)
        print("self.appendUrl {0}".format(self.appendUrl))
        
        #DOWNLOAD PART
        if self.doDownload:
            self.filePathToAppend = download_data(self.appendUrl, self.dir, os.path.join(self.saveDataDirName, self.mainFileName))
            
        else:
            #USING ALLREADY DOWLOADED TEST FILE
            self.filePathToAppend = "/storage/emulated/0/SdCardBackUp/PowerBI/FIO_API_BANKING/data/2022-06-30_2022-08-18 transactions_common-test.xml"
        print("self.filePathToAppend {0}".format(self.filePathToAppend))
        self.appendingTree = ET.parse(self.filePathToAppend)
        self.appendingRoot = self.appendingTree.getroot()
        self.appendingInfoNode = self.appendingRoot.find("./Info")
        
        self.appendingSDate, self.appendingSDateStr = self.getReportDay(self.appendingInfoNode, start=True)
        self.appendingEDate, self.appendingEDateStr = self.getReportDay(self.appendingInfoNode, start=False)
        self.appendingTransactionNodes = self.appendingRoot.findall(".//Transaction")
        print(self.dLine)
        print("self.appendingSDate {0}\nself.appendingEDate {1}".format(self.appendingSDate, self.appendingEDate))
        print("self.appendingSDateStr {0}\nself.appendingEDateStr {1}".format(self.appendingSDateStr, self.appendingEDateStr))
        
        #Main ID > Transaction node map
        self.mainIdMap = {}
        mainRemovedNodes = []
        for tNode in self.mainTransactionNodes:
            iD = self.getNodeWithAttribute(tNode, "ID pohybu").text
            if iD not in self.mainIdMap:
                self.mainIdMap[iD] = tNode
            else:
                mainRemovedNodes.append(iD)
                self.mainRoot.find("TransactionList").remove(tNode)
        if len(mainRemovedNodes) > 0:
            print(self.dLine)
            print("Removed {0} duplicated nodes {1}".format(len(mainRemovedNodes), mainRemovedNodes))
        
        self.mainEndDateNode = self.mainInfoNode.find("./dateEnd")
        print("self.mainEndDateNode {0}".format(self.mainEndDateNode.text))
        self.mainEndDateNode.text = self.appendingEDateStr
        print("after setting new date - self.mainEndDateNode {0}".format(self.mainEndDateNode.text))
        
        """
        #NOT ACTUALLY NECESSARY in this version
        #Main Transactions child > parrent map
        
        self.mainTPM = dict((c, p) for p in self.mainTransactionNodes for c in p)
            
        #Appending Transactions child > parrent map
        
        self.appendingTPM = dict((c, p) for p in self.appendingTransactionNodes for c in p)
        searchText = ".//Transaction/*[.=\'{0}\']".format(self.mainEDateStr.strip())
        print("searchText {0}".format(searchText))
        
        #get all transaction elements from first day of Appending report
        self.appendingFirstDayTransactions = [self.appendingTPM[x] for x in self.appendingRoot.findall(searchText.strip())]
        print(self.dLine)
        print("self.appendingFirstDayTransactions {0}".format(self.appendingFirstDayTransactions))
        
        #get all transaction elements from last day of Main report
        self.mainLastDayTransactions = [self.mainTPM[x] for x in root.findall(searchText.strip())]
        print("self.mainLastDayTransactions {0}".format(self.mainLastDayTransactions))
        """
        
    def appendTransactionNodes(self):
        #Appending logic:
        print(self.dLine)
        print("len(self.mainTransactionNodes) {0}".format(len(self.mainTransactionNodes)))
            
        collidingTransactions = []
        uniqueTransactions = []
        for appTNode in self.appendingTransactionNodes:
            iD = self.getNodeWithAttribute(appTNode, "ID pohybu").text
            if iD not in self.mainIdMap:
                self.mainIdMap[iD] = appTNode
                self.mainRoot.find("TransactionList").append(appTNode)
                uniqueTransactions.append(iD)
            else:
                collidingTransactions.append(iD)
        
        self.mainTransactionNodes = self.mainRoot.findall(".//Transaction")
        print("after appending\nlen(self.mainTransactionNodes):  {0}\nnew uniqueTransactions: {1}\ncollidingTransactions: {2}".format(len(self.mainTransactionNodes), len(uniqueTransactions), len(collidingTransactions)))
    
    def writeXml(self):
        try:
            self.mainTree.write(os.path.join(self.dir, self.mainFileName))
        except Exception as ex:
            raise RuntimeError("Error while writing {0} - {1}".format(os.path.join(self.dir, self.mainFileName), sys.exc_info()))
            
    def printStats(self):
        transactionList = {}
        foodSearch = {}
        foodKeyWords = ['lidl', 'billa', 'albert', 'tesco', 'kaufland', 'globus', 'potraviny', 'penny', 'fruitisimo', 'obcerstveni', 'bistro', 'bageterie', 'ovoc', 'zeleni']
        
        travelKeyWords = ['shell', 'benzin', 'čerpac', 'mol']
        travelSearch = {}
        
        for item in self.mainRoot.iter('Transaction'):
            transaction = {}
            for attrName, count in self.attrList.items():
            #attrName = 'ID pohybu'
                itemNode = self.getNodeWithAttribute(item, attrName)
                if itemNode != None:
                    transaction[itemNode.get('name')] = itemNode.text if hasattr(itemNode, 'text') else None
                    self.attrList[attrName] = count + 1
        
            transactionList[transaction['ID pohybu']] = transaction
        
        print("{0:_<60}".format(""))
        for attrName, count in self.attrList.items():
            print(attrName, count)
        
        indx=1 
        objem = 0.0
        for ID, data in foodSearch.items():
            print("{0:0>3} ID {1} - {2} {3} objem {4}".format(indx, ID, data[0], data[1], data[2]))
            indx += 1
            objem += data[2]
        print("Potraviny - objem {0}".format(-objem))
        
        indx=0
        for ID, data in travelSearch.items():
            print("{0:0>3} ID {1} - {2} {3} objem {4}".format(indx, ID, data[0], data[1], data[2]))
            indx += 1
            objem += data[2]
        print("Travel - objem {0}".format(-objem))
        
fioCommon = FioXml( \
                account='common', \
                doDownload=True, \
                testMode=False, \
                doBackup=True)

fioSpare = FioXml( \
                account='spare', \
                doDownload=True, \
                testMode=False, \
                doBackup=True)
