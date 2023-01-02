"""
Ak je doBackup True potom stahuje vsetky transakcie nanovo
"""

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
from api import download_data, getUrlCommonTimeRange, getUrlSpareTimeRange, getUrlSpare2TimeRange, ensure_dir

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
testName = "2012-07-01_2022-06-30 transactions_common-test"

#change mainFileName to download data for specific account

#mainFileName = "2012_07_01-MAIN"
#mainFileName = "2012_07_01-MAIN_SPARE"
mainFileName = "2012_07_01-MAIN_SPARE2"

fFormat = "xml"
fName = "{0}{1}.{2}".format("data/", testName, fFormat)
mainFileName = "{0}.{1}".format(mainFileName, fFormat)
dir = "/storage/emulated/0/SdCardBackUp/PowerBI/FIO_API_BANKING"
testFilePath = os.path.join(dir, fName)
mainFilePath = os.path.join(dir, mainFileName)
dLine = "{0:_<12}".format("")
#print(dLine)
print("testFilePath {0}".format(testFilePath))
print(dLine)
print("mainFilePath {0}".format(mainFilePath))
saveDataDirName = "data"
saveDataPath = os.path.join(dir, saveDataDirName)
saveBackupDirName = "zaloha"
saveBackupPath = os.path.join(dir, saveDataDirName, saveBackupDirName)
print("saveDataPath {0}".format(saveDataPath))
testMode = False
doDownload = True
doBackup = False
reportDateStart = datetime(2012,7,1)
try:
    if doBackup:
        ensure_dir(saveBackupPath)
        print("saveBackupPath {0}".format(saveBackupPath))
        shutil.copyfile(mainFilePath, os.path.join(saveBackupPath, mainFileName))
        print("Backup of main file {0} OK\nbackup dir:{1}".format(mainFileName, saveBackupPath))
except Exception as ex:
    raise RuntimeError("Error while doing backup of main file: {0} - {1}".format(mainFilePath, sys.exc_info()))

#with open(testFilePath, mode='w') as xmlFile:
#	data = xmlFile.read().replace("\n", "")

	
def getNodeWithAttribute(parrentNode, inAttrName):
    #function returns first subnode from search list with atribute name of xml node
    nodes = parrentNode.findall("./*[@name = '{0}']".format(inAttrName))
    if not hasattr(nodes, '__iter__'):
        return nodes
    elif len(nodes) > 0:
        return nodes[0]
    else:
        return None
        
def getReportDay(inInfoNode, **kwargs):
    returnStartDate = kwargs['start'] if 'start' in kwargs else True
    sDateNodeName = "dateStart"
    eDateNodeName = "dateEnd"
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

attrList = { \
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
            
#xmlDict = xmltodict.parse(data)
#print("xmlDict {0}".format(xmlDict))
"""
parser = ET.XMLPullParser(['start', 'end'])
parser.feed('<Transaction><column_22><id>')
#list(parser.read_events())
for event, element in parser.read_events():
    print("event {0}\n tag {1}\n text{2}".format(event, element.tag, element.text))
"""
if doBackup:
    tree = ET.parse(mainFilePath)
    root = tree.getroot()
    #print(dLine)
    #print("root tag:\n{0}".format(root.tag))
    #for child in root:
    #    print("root.{0}".format(child.tag))
    #for item in root.findall('AccountStatement'):
    #    print("AccountStatement.{0}".format(item.tag))
    #print("dir root {0}".format(dir(root)))
    #print("root.getchildren {0}".format(root.getchildren()))
    
    #for node in root.findall("./AccountStatement/TransactionList"):
    #    print("node {0}".format(node.tag))
    testInfoList = [x for x in root.findall("./Info")]
    testInfoNode =  testInfoList[0] if testInfoList and len(testInfoList) > 0 else None
    print("testInfoNode {0}".format(testInfoNode.tag))
    #sDate = "dateStart"
    #eDate = "dateEnd"
    """
    for child in testInfoNode:
        print("testInfoNode.{0} = {1}".format(child.tag, child.text))
    startDateStr = testInfoNode.findall("./dateStart")[0].text if testInfoNode.findall("./dateStart") else None
    print("start date: {0}".format(startDateStr))
    splited = startDateStr.split("+")
    print("splited {0}".format(splited))
    startDate = datetime.strptime(splited[0].strip(), "%Y-%m-%d")
    """
    sDate, sDateStr = getReportDay(testInfoNode, start=True)
    eDate, eDateStr = getReportDay(testInfoNode, start=False)
    print(dLine)
    print("sDate {0}\neDate {1}".format(sDate, eDate))
    print("sDateStr {0}\neDateStr {1}".format(sDateStr, eDateStr))
    print(dLine)
    print("UrlCommonTimeRange: {0}".format(getUrlCommonTimeRange(sDate, eDate)))
    print(dLine)
    print("UrlSpareTimeRange: {0}".format(getUrlSpareTimeRange(sDate, eDate)))
    nowDate = datetime.now()
    print(dLine)
    print("nowDate {0}".format(nowDate))
    appendUrl = getUrlCommonTimeRange(eDate, nowDate)
    print(dLine)
    print("appendUrl {0}".format(appendUrl))

#DOWNLOAD PART
if mainFileName == "2012_07_01-MAIN_SPARE2.xml" in mainFileName:
    filepathToAppend = download_data(getUrlSpare2TimeRange(reportDateStart, datetime.now()), saveDataPath, mainFileName)
elif mainFileName == "2012_07_01-MAIN_SPARE.xml":
    filepathToAppend = download_data(getUrlSpareTimeRange(reportDateStart, datetime.now()), saveDataPath, mainFileName)
elif mainFileName == "2012_07_01-MAIN.xml":
    filepathToAppend = download_data(getUrlCommonTimeRange(reportDateStart, datetime.now()), saveDataPath, mainFileName)
else:
    raise RuntimeError("mainFileName does not contain any of this: SPARE2, SPARE, MAIN")
#print("filePathToAppend {0}".format(filePathToAppend))



#filepathToAppend = "/storage/emulated/0/SdCardBackUp/PowerBI/FIO_API_BANKING/data/2022-06-30_2022-08-18 transactions_common-test.xml"
appendingTree = ET.parse(filepathToAppend)
appendingRoot = appendingTree.getroot()

#print(appendingRoot.findall(".//Transaction"))
#day before last day
"""
dBLastDay = eDate - timedelta(days=-1)
dBNextDay = eDate + timedelta(days=10)
dBLastDayStr = "{0}-{1}-{2}+02:00".format(dBLastDay.strftime("%Y"), dBLastDay.strftime("%m"), dBLastDay.strftime("%d"))
dBNextDayStr = "{0}-{1}-{2}+02:00".format(dBNextDay.strftime("%Y"), dBNextDay.strftime("%m"), dBNextDay.strftime("%d"))
print(dLine)
print("dBLastDayStr {0}".format(dBLastDayStr))
print("dBNextDayStr {0}".format(dBNextDayStr))
"""
appendingInfoNode = appendingRoot.find("./Info")
appendingSDate, appendingSDateStr = getReportDay(appendingInfoNode, start=True)
appendingEDate, appendingEDateStr = getReportDay(appendingInfoNode, start=False)
print(dLine)
print("appendingSDate {0}\nappendingEDate {1}".format(appendingSDate, appendingEDate))
print("appendingSDateStr {0}\nappendingEDateStr {1}".format(appendingSDateStr, appendingEDateStr))

if doBackup:
    #Main Transactions parrent map
    mainTransactionNodes = root.findall(".//Transaction")
    mainTPM = dict((c, p) for p in mainTransactionNodes for c in p)
    
    #Main ID > Transaction node map
    mainIdMap = {}
    removedNodes = []
    for tNode in mainTransactionNodes:
        iD = getNodeWithAttribute(tNode, "ID pohybu").text
        if iD not in mainIdMap:
            mainIdMap[iD] = tNode
        else:
            removedNodes.append(iD)
            root.find("TransactionList").remove(tNode)
    if len(removedNodes) > 0:
        print(dLine)
        print("Removed {0} duplicated nodes {1}".format(len(removedNodes), removedNodes))
            
            
    #mainIdMap = dict((, p) for p in mainTransactionNodes)
    #print("mainIdMap {0}".format(mainIdMap))
    #print("mainTransactionNodes {0}".format(mainTransactionNodes))
    #print("mainTPM {0}".format(mainTPM))
    
    #Appending Transactions parrent map
    appendingTransactionNodes = appendingRoot.findall(".//Transaction")
    appendingTPM = dict((c, p) for p in appendingTransactionNodes for c in p)
    
    #print(dLine)
    #print("appendingTransactionNodes {0}".format(appendingTransactionNodes))
    
    #print(dLine)
    #print("appendingTPM {0}".format(appendingTPM))
    
    #search string for last day Transaction/Datum element
    searchText = ".//Transaction/*[.=\'{0}\']".format(eDateStr.strip())
    #searchText = ".//Transaction/*[.=\'{0}\']".format(dBNextDayStr.strip())
    #searchText = ".//Transaction/*[.='2022-05-30+02:00']"
    print("searchText {0}".format(searchText))
    
    #get all transaction elements from first day of Appending report
    appendingFirstDayTransactions = [appendingTPM[x] for x in appendingRoot.findall(searchText.strip())]
    print(dLine)
    print("appendingFirstDayTransactions {0}".format(appendingFirstDayTransactions))
    
    #get all transaction elements from last day of Main report
    mainLastDayTransactions = [mainTPM[x] for x in root.findall(searchText.strip())]
    print("mainLastDayTransactions {0}".format(mainLastDayTransactions))
    
    #Appending logic: in case, there are unique transaction IDs in first day of appending report comparing with last day of main report, which must be the same, script will extend main report with theese unique IDs
    print(dLine)
    print("len(mainTransactionNodes) {0}".format(len(mainTransactionNodes)))
        
    collidingTransactions = []
    uniqueTransactions = []
    for appTNode in appendingTransactionNodes:
        iD = getNodeWithAttribute(appTNode, "ID pohybu").text
        if iD not in mainIdMap:
            mainIdMap[iD] = appTNode
            root.find("TransactionList").append(appTNode)
            uniqueTransactions.append(iD)
        else:
            collidingTransactions.append(iD)
    
    mainTransactionNodes = root.findall(".//Transaction")
    print("after appending\nlen(mainTransactionNodes):  {0}\nnew uniqueTransactions: {1}\ncollidingTransactions: {2}".format(len(mainTransactionNodes), len(uniqueTransactions), len(collidingTransactions)))
    
    """
    uniqueTransactions = []
    
    if len(appendingFirstDayTransactions) == len(mainLastDayTransactions):
        if len(appendingFirstDayTransactions) > 0:
            for appT in appendingFirstDayTransactions:
                appTID = getNodeWithAttribute(appT, "ID pohybu").text
                isUnique = True
                for mainT in mainLastDayTransactions:
                    mainTID = getNodeWithAttribute(mainT, "ID pohybu").text
                    if mainTID == appTID:
                        isUnique = False
                        break
                if isUnique:
                    uniqueTransactions.append(appT)
                else:
                    colideTransactions.append(appT)
                    
                        
            #appendingTrIds = [getNodeWithAttribute(x, 'Datum') for x in appendingFirstDayTransactions]
            #appendingTrIds = [x.findall("*[@name='Datum']/...") for x in appendingFirstDayTransactions]
            #print("appendingTrIds {0}".format(appendingTrIds))
            if len(uniqueTransactions) > 0:
                print("There are {0} unique transactions in appending day: {1}".format(len(uniqueTransactions), uniqueTransactions))
            else:
                print("mainLastDayTransactions has the same length as appendingFirstDayTransactions")
    
        print("colideTransactions {0}".format(colideTransactions))
        print("len(appendingTransactionNodes) {0}".format(len(appendingTransactionNodes)))
        if len(colideTransactions) > 0:
            for ct in colideTransactions:
                appendingRoot.find("TransactionList").remove(ct)
        appendingTransactionNodes = appendingRoot.findall(".//Transaction")
        print("after removing len(appendingTransactionNodes) {0}".format(len(appendingTransactionNodes)))
    """
    mainEndDateNode = testInfoNode.find("./dateEnd")
    print("mainEndDateNode {0}".format(mainEndDateNode.text))
    mainEndDateNode.text = appendingEDateStr
    print("after setting new date - mainEndDateNode {0}".format(mainEndDateNode.text))
        
    if not testMode:
        try:
            tree.write(os.path.join(dir, mainFileName))
        except Exception as ex:
            raise RuntimeError("Error while writing {0} - {1}".format(os.path.join(dir, mainFileName), sys.exc_info()))
        
            #    for appTNode in appendingTransactionNodes:
                    
    """
    elif len(appendingFirstDayTransactions) > len(mainLastDayTransactions):
        print("appendFirstDayTransactions has more transactions as mainLastDayTransactions !!!")
    else:
        print("appendFirstDayTransactions has less transactions as mainLastDayTransactions !!!")
    """    
    transactionList = {}
    
    foodSearch = {}
    foodKeyWords = ['lidl', 'billa', 'albert', 'tesco', 'kaufland', 'globus', 'potraviny', 'penny', 'fruitisimo', 'obcerstveni', 'bistro', 'bageterie', 'ovoc', 'zeleni']
    
    travelKeyWords = ['shell', 'benzin', 'čerpac', 'mol']
    travelSearch = {}
    
    
    for item in root.iter('Transaction'):
        """
        print("{0:_>12}".format(""))
        """
        transaction = {}
        for attrName, count in attrList.items():
        #attrName = 'ID pohybu'
            itemNode = getNodeWithAttribute(item, attrName)
            if itemNode != None:
                transaction[itemNode.get('name')] = itemNode.text if hasattr(itemNode, 'text') else None
                attrList[attrName] = count + 1
                """
                print("transaction['{0}'] = {1}".format(attrName, transaction[attrName]))
                
                if attrName == 'Uživatelská identifikace':
                    for keyWord in foodKeyWords:
                        search = re.search(keyWord, itemNode.text, re.IGNORECASE)
                        if search:
                            foodSearch[getNodeWithAttribute(item, 'ID pohybu').text] = (getNodeWithAttribute(item, 'Datum').text, itemNode.text, float(getNodeWithAttribute(item, 'Objem').text))
                        else:
                            search = None
                            break
                    if not search:
                        for keyWord in travelKeyWords:
                            search = re.search(keyWord, itemNode.text, re.IGNORECASE)
                            travelSearch[getNodeWithAttribute(item, 'ID pohybu').text] = (getNodeWithAttribute(item, 'Datum').text, itemNode.text, float(getNodeWithAttribute(item, 'Objem').text))
                """
        transactionList[transaction['ID pohybu']] = transaction
    
    print("{0:_<60}".format(""))
    for attrName, count in attrList.items():
        print(attrName, count)
    ("") 
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
        
#print(transactionList)
    

