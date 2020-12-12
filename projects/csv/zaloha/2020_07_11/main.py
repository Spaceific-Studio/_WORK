import os
import csv
import copy
path = r"/storage/emulated/0/qpython/projects/csv"
fileName ="2020_04_06-COVID-19 Surveillance Dashboard.csv"
countriesFName = "countries/2020_WORLD_STATES.csv"

filePath = os.path.join(path, fileName)
countriesFilePath = os.path.join(path, countriesFName)
file = open(filePath, "r")
lines = []
allData = []

#with open(filePath, newline='') as f:
#    reader = csv.reader(f)
#    data = list(reader)
with open(countriesFilePath, newline='') as cF:
    cReader = csv.reader(cF)
    cData = list(cReader)
#for line in data:
#    print(line)
csvFiles = []
for root, dirs, files in os.walk(path, topdown=False):
   for name in files:
      if name.split(".")[-1] == "csv" and "2020_WORLD_STATES" not in name:
          csvFiles.append(name)
csvFiles.sort(key = lambda x: x.split("-")[0])
#print(csvFiles)

for file in csvFiles:
    filePath = os.path.join(path, file)
    with open(filePath, newline='') as f:
        reader = list(csv.reader(f))
        firstLine = reader.pop(0)
        allData.append(reader)
#allData.pop()
#print(allData)
    
#firstLine = data.pop(0)
cFirstLine = cData.pop(0)
cSecondLine = cData.pop(0)
cData.pop(-1)

def dToC_ratio(item):
    #commited
    c = float("".join(item[2].split()))
    #dead
    d = float("".join(item[3].split()))
    return d/c if c!= 0 else 0
    
def incCommitPerDayPercent(allData, *args, **kwargs):
    commitSearch = kwargs['commitSearch'] if 'commitSearch' in kwargs else True
    thisDay = copy.deepcopy(allData[-1])
    lastDay = copy.deepcopy(allData[-2])
    bLastDay = copy.deepcopy(allData[-3])
    thisDayCommit = 0
    thisDayDead = 0
    lastDayCommit = 0
    lastDayDead = 0
    bLastDayCommit = 0
    bLastDayDead = 0
    for i, country in enumerate(thisDay):
        if country[0]== country[1]:
            thisDayCommit = float("".join(country[2].split()))
            thisDayDead = float("".join(country[3].split()))
            for j, ldc in enumerate(lastDay):
                if country[0]== ldc[0] and country[1] == ldc[1]:
                    lastDayCommit = float("".join(ldc[2].split()))
                    lastDayDead = float("".join(ldc[3].split()))
            for j, bldc in enumerate(bLastDay):
                if country[0]== bldc[0] and country[1] == bldc[1]:
                    bLastDayCommit = float("".join(bldc[2].split()))
                    bLastDayDead = float("".join(bldc[3].split()))
            incLastDayC = lastDayCommit - bLastDayCommit
            incLastDayD = lastDayDead - bLastDayDead
            incThisDayC = thisDayCommit - lastDayCommit
            incThisDayD = thisDayDead - lastDayDead
            incBLastDayC = thisDayCommit - bLastDayCommit / 2.0
            incBLastDayD = thisDayDead - bLastDayDead / 2.0
            if incLastDayC !=0:
                incPercentC = ((incThisDayC/incLastDayC) - 1) * 100 
            elif incBLastDayC != 0:
                incPercentC = ((incThisDayC/incBLastDayC) - 1) * 100
            else:
                incPercentC = 1
                
            if incLastDayD !=0:
                incPercentD = ((incThisDayD/incLastDayD) - 1) * 100 
            elif incBLastDayD != 0:
                incPercentD = ((incThisDayD/incBLastDayD) - 1) * 100
            else:
                incPercentD = 1
            thisDay[i].append(incPercentC)
            thisDay[i].append(incPercentD)
            #print("\n{0} {1} - {2} thisDayCommit {3} incThisDay {4} lastDayCommit {5}, incLastDay {6}, bLastDayCommit {7}".format(i, country[1], incPercent, thisDayCommit, incThisDay, lastDayCommit, incLastDay, bLastDayCommit))
    return thisDay
    
def dToPop_ratio(item):
    countryIndex = lookUp[item[1]] if item[1] in lookUp else None
    if countryIndex:
        d = float("".join(item[3].split()))
        pop = float("".join(cData[countryIndex][2].split(",")))
        return d/pop if pop != 0 else 0
    else:
        return 0

def cToPop_ratio(item):
    countryIndex = lookUp[item[1]] if item[1] in lookUp else None
    if countryIndex:
        c = float("".join(item[2].split()))
        pop = float("".join(cData[countryIndex][2].split(",")))
        return c/pop if pop != 0 else 0
    else:
        return 0
        
def getLookUpTable(inList, inCountries):
    countries = inCountries.copy()
    lookUpTable = {}
    notInCData = []
    for line in inList:
        inCData = False
        for i, country in enumerate(countries):
            #print("{0}{1}".format(line[1], country[0]))
            if line[1] in country[1]:
                lookUpTable[line[1]] = i
                inCData = True
                break
            elif line[1] == "Mainland China":
                lookUpTable["China"] = i
                inCData = True
                break
        if not inCData and line[1] not in notInCData:
            notInCData.append(line[1])
    return (lookUpTable, notInCData)

def getCountryData(inData, inCName):
    countryDailyData = []
    for i, day in enumerate(inData):
        for j, country in enumerate(day):
            if inCName in country[1] and inCName in country[0] and "Virgin" not in country[0]:
                dayStamp = csvFiles[i].split("-")[0]
                countryDailyData.append(country.copy() + [dayStamp])
    return countryDailyData
    
def dayChartSorting(dayChartSort, data):
    #0__sort by commited
    #1__sort by dead
    #2__sort by death / commited ratio
    #3__sort by death / population ratio
    #4__sort by commited / population ratio
    #5__sort by recovered
    #6__sort by daily increas ratio of commite in %
    #7__sort by country alphabetical wise
    
    if dayChartSort == 0:
        data.sort(key=lambda x: int("".join(x[2].split())), reverse=True)
    elif dayChartSort == 1:
        data.sort(key=lambda x: int("".join(x[3].split())), reverse=True)
    elif dayChartSort == 2:
        data.sort(key=dToC_ratio, reverse=True)
    elif dayChartSort == 3:
        data.sort(key=dToPop_ratio, reverse=True)
    elif dayChartSort == 4:
        data.sort(key=cToPop_ratio, reverse=True)
    elif dayChartSort == 5:
        data.sort(key=lambda x: int("".join(x[4].split())), reverse=True)
    elif dayChartSort == 6:
        data.sort(key=lambda x: x[9] if len(x) > 9 and type(x[9]) == float else 0, reverse=True)
    elif dayChartSort == 7:
        data.sort(key=lambda x: x[10] if len(x) > 9 and type(x[9]) == float else 0, reverse=True)
    elif dayChartSort == 8:
        data.sort(key=lambda x: "".join(x[1].split()), reverse=False)
    return data
    
def countrySorting(sort, data):
    #0__sort counties by population
    #1__sort counties by area
    #2__sort counties by density
    
    if sort == 0:
        data.sort(key=lambda x: int("".join(x[2].split(","))) if len("".join(x[2].split(","))) > 0 else 0, reverse=True)
    elif sort == 1:
        data.sort(key=lambda x: int("".join(x[3].split(","))) if len("".join(x[3].split(","))) > 0 else 0, reverse=True)
    elif sort == 2:
        data.sort(key=lambda x: int("".join(x[4].split(","))) if len("".join(x[4].split(","))) > 0 else 0, reverse=True)
    return data

def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
    
#firstLine = allData[-1].pop(0)
#print("firstLine {0}".format(firstLine))
#data = incCommitPerDayPercent()
data = copy.deepcopy(incCommitPerDayPercent(allData))
#print(data)
print("")
#print(allData[-1])
#data = allData[-1]

lookUp, notInLookUp = getLookUpTable(data, cData)
#incCPDP = incCommitPerDayPercent(allData)
#retLine = []
for i, c in enumerate(data):
    incDeadDayPercent = data[i].pop(-1)
    incCommitDayPercent = data[i].pop(-1)
    data[i].append(dToC_ratio(c)*100)
    data[i].append(cToPop_ratio(c)*100)
    data[i].append(incCommitDayPercent)
    data[i].append(incDeadDayPercent)
    #print(allData[-2][i])
#print("data {}".format(data))
#print(retLine)

#print("lookUp: {0} len lookUp: {1} notInLookUp {2} notInLookUp: {3}".format(lookUp, len(lookUp), notInLookUp, len(notInLookUp)))   

ccData = countrySorting(4, cData.copy())
    #0__sort counties by population
    #1__sort counties by area
    #2__sort counties by density
reservedStrings =["q", "p", "a", "de", "d", "c", "dc", "dp", "cp", "r", "ic", "id"]
coutriesOfIterest = [("Czech Republic", "CZE"),("Slovakia", "SVK"), ("United States", "USA"), ("Italy", "ITA"), ("Spain", "ESP"), ("United Kingdom", "UK"), ("Russia", "RUS"), ("Brazil", "BRA"), ("Germany", "GER"), ("Austria", "AUT"), ("France", "FRA"), ("Japan", "JAP"), ("China", "CHI"), ("Switzerland", "SUI"), ("Sweden", "SWE"), ("Finland", "FIN"), ("Romania", "ROM"), ("Argentina", "ARG"), ("Turkey", "TUR"), ("Belarus", "BLR"), ("Mali", "MAL"), ("Hungary", "HUN"), ("Poland", "POL"), ("Estonia", "EST"), ("Pakistan", "PAK"), ("Ecuador", "ECU"), ("Colombia", "COL"), ("India", "IND"), ("Bahrain", "BAH"), ("Venezuela", "VEN")]

inputText = "\n"
for i, c in enumerate(coutriesOfIterest):
    inputText += str(i) + " - " + c[1] + " |"
inputText += "\n daily charts sorting:\nc - sort by commited\nd - sort by dead\ndc - sort by commit/dead ratio\ndp - sort by dead/population ratio\ncp - sort by commited/population ratio\nr - sort by recovered\nic - sort by daily increas ratio of commite in %\nid - sort by daily increas ratio of dead in %\na - sort countries by alphabetical order\n"
inputText += "q - quit\n"
#cDailyData = getCountryData(allData, coutriesOfIterest[0][0])
myInput = input(inputText)
while myInput != "q" or myInput != "Q":
    if myInput not in reservedStrings:
        cDailyData = getCountryData(allData, coutriesOfIterest[int(myInput) if int(myInput) < len(coutriesOfIterest) else 0][0])
    elif myInput == "q" or myInput == "Q":
        break
    print("test-{:d}".format(int("".join(ccData[5][2].split(",")))))
    print("{0:>3} {1:<15.15} {2:<14.14} {3:<12.12} {4:<10.10}".format(*cFirstLine))
    print("{0:>3} {1:<15.15} {2:<14.14} {3:<12.12} {4:<10.10}".format(*cSecondLine))
    for i, line in enumerate(ccData):
        print("{0:0>3} {1:<15.15} {2:<14} {3:<12} {4:<10}".format(*line))

    if myInput == "c":
        data = dayChartSorting(0, data)
    elif myInput == "d":
        data = dayChartSorting(1, data)
    elif myInput == "dc":
        data = dayChartSorting(2, data)
    elif myInput == "dp":
        data = dayChartSorting(3, data)
    elif myInput == "cp":
        data = dayChartSorting(4, data)
    elif myInput == "r":
        data = dayChartSorting(5, data)
    elif myInput == "ic":
        data = dayChartSorting(6, data)
    elif myInput == "id":
        data = dayChartSorting(7, data)
    elif myInput == "a":
        data = dayChartSorting(8, data)
    #0__sort by commited
    #1__sort by dead
    #2__sort by death / commited ratio
    #3__sort by death / population ratio
    #4__sort by commited / population ratio
    #5__sort by recovered
    #6__sort by daily increas ratio of commited in %
    #7__sort by daily increas ratio of dead in %
    #8__sort by country alphabetical wise
    #print(data)
    print("{0:>3} {2:<15.15} {3:<9.9} {4:<9.9} {5:<9.9}   {8:<7.7}{9:>32.32}  {10:<11} {11:<11}".format("", *firstLine, "D/C %", "C/POP %", "incC %", "incD %"))
    for i, line in enumerate(data):
        if line[0] == line[1] and int("".join(line[2].split())) > 0:
            print("{0:0>3} {2:<15.15} C {3:<7} D {4:<7} R {5:<7}   {8:< 7.2f}{9:> 31.4f}   {10:> 7.2f}     {11:> 7.2f}".format(i, *line))
            #print("{0:0>3} {2:<15.15} C {3:<7} D {4:<7} R {5:<7}   {8:>5.2f}  {9:>31.4f}".format(i, *line))

    #print("Daily Data: {0} len(cDailyData {1}):".format(cDailyData, len(cDailyData)))
    #print("cDailyData {0}".format(cDailyData))
    dailyIncreasC = []
    dailyIncreasD = []
    for i, day in enumerate(cDailyData):
        formerC = 0 if i == 0 else int("".join(cDailyData[i-1][2].split()))
        formerD = 0 if i == 0 else int("".join(cDailyData[i-1][3].split()))
        dailyIncreasC.append(int("".join(day[2].split())) - formerC)
        dailyIncreasD.append(int("".join(day[3].split())) - formerD)
    print("dailyIncreasC: {0} dailyIncreasD: {1}".format(dailyIncreasC, dailyIncreasD))
    
    maxValC = max(dailyIncreasC)
    maxValD = max(dailyIncreasD)
    tableRange = 40
    
    # country daily chart
    print("\n{0:<19} {3:<9.9} {4:<9.9} {5:<9.9} {6:<9.9}".format(cDailyData[0][1], *firstLine))
    for i, line in enumerate(cDailyData):
        if line[0] == line[1] and int("".join(line[2].split())) > 0:
            print("{8:<19} C {3:<7} D {4:<7} R {5:<7} A {6:<7}".format(i, *line))
            
    # commited daily increas graph
    text = "\n{0:<19} {1}{2:>" + str(int(tableRange / 2) -1) + "}{3:>" + str(int(tableRange / 2) -1) + "}"
    print(text.format("Daily Inc. Commit",0 ,int(maxValC/2), maxValC))
    for i, line in enumerate(dailyIncreasC):
        intVal = int(scale(line,(0,maxValC), (0,tableRange)))
        strVal = str(intVal) if intVal >= 0 else str(0)
        text = "{1:<12} {2:>6} {0:-<" + strVal + "}"
        #print(text.format(line, cDailyData[7]))
        print(text.format("",cDailyData[i][7], line))
        
    # deads daily increas graph
    text = "\n{0:<19} {1}{2:>" + str(int(tableRange / 2) -1) + "}{3:>" + str(int(tableRange / 2) -1) + "}"
    print(text.format("Daily Inc. Deads",0 ,int(maxValD/2), maxValD))
    for i, line in enumerate(dailyIncreasD):
        intVal = int(scale(line,(0,maxValD), (0,tableRange)))
        strVal = str(intVal) if intVal >= 0 else str(0)
        text = "{1:<12} {2:>6} {0:-<" + strVal + "}"
        #print(text.format(line, cDailyData[7]))
        print(text.format("",cDailyData[i][7], line))
    print("\n{0:<19}".format(cDailyData[0][1]))
    myInput = input(inputText)
