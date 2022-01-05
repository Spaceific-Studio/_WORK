import os
import csv
import copy
import sys
import math
import urllib.request

urlRecovered="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
urlConfirmed="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
urlDeads="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

print("file {0}".format(__file__))

os.chdir(r"{}".format("/".join(__file__.split("/")[0:-1])))
myCwd = os.getcwd()
print("my cwd {0}".format(myCwd))
path = r"".format(myCwd)
countriesFName = "countries/2020_WORLD_STATES.csv"

countriesFilePath = os.path.join(path, countriesFName)

def ensure_dir(file_path):
    directory = os.path.dirname(file_path) 
    if not os.path.exists(directory):
        os.makedirs(directory)
        
def download_data(inUrl, dPath):
    connOk = False
    print("{0:_>60}".format(""))
    try:
        response = urllib.request.urlopen(inUrl)
        connOk =True
        
    except Exception as ex:
        pass
        print(sys.exc_info())
        #print(ex)
    if connOk:
        dData = response.read()
        text = dData.decode('utf-8')
        fName = inUrl.split("/")[-1]
        fName = fName.split(".")[0] 
        fName = fName + ".txt"
        fullName = os.path.join(dPath, fName)
        #print("dData {0}".format(text))
        ensure_dir(dPath)
        with open(fullName, 'wb') as myFile:
            myFile.write(dData)
        
        print("DATA DOWNLOADED\nFROM:\n{0}\nTO :\n{1}".format(inUrl, os.path.join(dPath, fullName)))
        
    else:
        print("Unable to connect to: {0}\n".format(inUrl))
    print("{0:_>60}".format(""))


download_data(urlRecovered, os.path.join(myCwd, "JHU"))
download_data(urlDeads, os.path.join(myCwd, "JHU"))
download_data(urlConfirmed, os.path.join(myCwd, "JHU"))

with open(countriesFilePath, newline='') as cF:
    cReader = csv.reader(cF)
    cData = list(cReader)

def transpose(inList):
	returnList = [[inList[j][i] for j in range(len(inList))] for i in range(len(inList[0]))]
	return returnList

class Dic2obj(object):
    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])
"""
class CountryData():
    INPUT_DATA = None
    ALL_DATA_TRANSPOSED = None
    FIRST_LINE = None
    C_DATA = None
    
    def __init__(self, inputData, inFirstLine):
        if not CountryData.INPUT_DATA:
             CountryData.INPUT_DATA = inputData
        else:
            pass
        if not CountryData.ALL_DATA_TRANSPOSED:
             CountryData.ALL_DATA_TRANSPOSED = transpose(copy.deepcopy(inputData.allData))
        else:
            pass
        CountryData.FIRST_LINE = inFirstLine 
        if not CountryData.FIRST_LINE:
            CountryData.FIRST_LINE = inFirstLine
        else:
            pass
        if not CountryData.C_DATA:
            self.generateCountriesDic() 
        else:
            pass
        self.getNLastData(7,"US")
        
    def generateCountriesDic(self):
        CountryData.C_DATA = {}
        for country in CountryData.ALL_DATA_TRANSPOSED:
            if country[0][0] == country[0][1]:
                allDays = []
                countryDic = {}
                countryDic["name"] = country[0][0]
                cName = country[0][0]
                confirmed = []
                deads = []
                recovered = []
                for i, day in enumerate(country):
                    confirmed.append(day[2])
                    deads.append(day[3])
                    recovered.append([4])
                    allDays.append(day[2:] + [CountryData.FIRST_LINE[i]])
                #print("allDays[-1] {}".format(allDays[-1]))
                countryDic["confirmed"] = confirmed
                countryDic["deads"] = deads
                countryDic["recovered"] = recovered
                CountryData.C_DATA[cName] = countryDic
                
    def getNLastData(self, inRange, inCName):
        lastNData = CountryData.C_DATA[inCName][-inRange:] if len(CountryData.C_DATA[inCName]) >= inRange else None
        print("CountryData.getNLastData {0}".format(lastNData))
        
    def getDailyIncreases(inType, inCName, **kwargs):
        incRange = kwargs["range"] if "range" in kwargs else len(CountryData.C_DATA)
        self.getNLastData(incRange, inCName)
        if inType == "D":
            pass
            
        
    def report(self):
        print("CountryData C_DATA {}".format(CountryData.C_DATA["Slovakia"]))
"""
class InputData():
    C_DATA = None
    C_DATA_OBJ = []
    FIRST_LINE = None
    POP_DATA = None
    LOOKUP = None
    DATES = None
    
    def __init__(self, inPath, inPopData):
        if not InputData.FIRST_LINE:
            InputData.FIRST_LINE = ["Region", "Confirmed", "Deads", "Recovered","D/C %", "C/Pop%", "c7D100k ", "d7D1m ", "incC8DStd%"]
        self.fileNameConfirmedJHU = "time_series_covid19_confirmed_global.txt"
        self.fileNameRecoveredJHU = "time_series_covid19_recovered_global.txt"
        self.fileNameDeathsJHU = "time_series_covid19_deaths_global.txt"
        self.path = inPath
        self.recoveredPath = os.path.join(self.path, self.fileNameRecoveredJHU)
        self.confirmedPath = os.path.join(self.path, self.fileNameConfirmedJHU)
        self.deathsPath = os.path.join(self.path, self.fileNameDeathsJHU)
        allDataConfirmed = self.readFile(self.confirmedPath)
        #print("InputData.allDataConfirmed {0}".format(allDataConfirmed))
        self.confirmedDic = self.allDataToDic(allDataConfirmed)
        #print(self.confirmedDic["Czechia"])
        #print("InputData.confirmedDic {}".format(self.confirmedDic))
        allDataDeaths = self.readFile(self.deathsPath)
        
        #print("InputData.inPopData: {}".format(inPopData))
        self.deathsDic = self.allDataToDic(allDataDeaths)
        allDataRecovered = self.readFile(self.recoveredPath)
        self.recoveredDic = self.allDataToDic(allDataRecovered)
        if not InputData.POP_DATA:
            InputData.POP_DATA = inPopData
        else:
            pass
        if not InputData.C_DATA:
            self.generateCountriesDic() 
        else:
            pass
           
    def readFile(self, inPath):
        self.startDataIndex = 4
        with open(inPath, newline='') as f:
            reader = list(csv.reader(f))
            self.firstLine = reader.pop(0)[self.startDataIndex:]
            if not InputData.DATES:
                InputData.DATES = self.firstLine
            else:
                pass
            #print("InputData.DATES {}".format(InputData.DATES))
            return reader
            
    def allDataToDic(self, inData):
        dic = {}
        for line in inData:
            countryConfirmedData = []
            if line[1] not in dic:
                dic[line[1]] = line[self.startDataIndex:]
            else:
                prevLineData = dic[line[1]]
                newLine = [str(int(prevLineData[i]) + int(v)) for i,v in enumerate(line[self.startDataIndex:])]
                dic[line[1]] = newLine
        return dic
        
    def getDailyIncreases(self, inDailyData):
        #print("getDailyIncreases d{}".format(inDailyData))
        daysBefore = ["0"] + inDailyData[:-1]
        #print("getDailyIncreases db{}".format(daysBefore))
        incs = []
        for i, day in enumerate(inDailyData):
            incs.append(int(day) - int(daysBefore[i]))
        #print("getDailyIncreases incs {}".format(incs))
        return copy.deepcopy(incs)
        
    def generateCountriesDic(self):
        InputData.C_DATA = {}
        for i, values in enumerate(self.confirmedDic.items()):
            countryDic = {}
            countryDic["name"] = values[0]
            countryDic["confirmed"] = values[1]
            countryDic["deads"] = self.deathsDic[values[0]]
            countryDic["recovered"] = self.recoveredDic[values[0]]
            countryDic["active"] = [str(int(x) -int(self.deathsDic[values[0]][j]) - int(self.recoveredDic[values[0]][j])) for j, x in enumerate(values[1])]
            countryDic["increases_Confirmed"] = self.getDailyIncreases(countryDic["confirmed"])
            countryDic["increases_Deads"] = self.getDailyIncreases(countryDic["deads"])
            
            InputData.C_DATA[values[0]] = countryDic
        if not InputData.LOOKUP:
            InputData.LOOKUP, notInLookUp = self.getLookUpTable(InputData.C_DATA, InputData.POP_DATA)
        else:
            pass
            
        for k, c in InputData.C_DATA.items():
            population = int("".join(InputData.POP_DATA[InputData.LOOKUP[k]][2].split(","))) if k in InputData.LOOKUP else None
            InputData.C_DATA[k]["population"] = population
            InputData.C_DATA[k]["c_pop"] = int(InputData.C_DATA[k]["confirmed"][-1]) / InputData.C_DATA[k]["population"] * 100 if InputData.C_DATA[k]["population"] else None
            #print("{0} {1} - {2}".format(InputData.C_DATA[k]["confirmed"][-1], countryDic["name"], type(InputData.C_DATA[k]["confirmed"][-1])))
            InputData.C_DATA[k]["d_c"] = int(InputData.C_DATA[k]["deads"][-1]) / int(InputData.C_DATA[k]["confirmed"][-1]) * 100 if int(InputData.C_DATA[k]["confirmed"][-1]) != 0 else 0
            InputData.C_DATA[k]["d_pop"] = int(InputData.C_DATA[k]["deads"][-1]) / InputData.C_DATA[k]["population"] * 100 if InputData.C_DATA[k]["population"] else None
            
            if len(InputData.C_DATA[k]["confirmed"]) >= 7:
                c7D = InputData.C_DATA[k]["increases_Confirmed"][-7:]
                d7D = InputData.C_DATA[k]["increases_Deads"][-7:]
            else:
                c7D = None
                d7D = None
            if len(InputData.C_DATA[k]["confirmed"]) >= 8:
                c8D = InputData.C_DATA[k]["increases_Confirmed"][-8:-1]
                d8D = InputData.C_DATA[k]["increases_Deads"][-8:-1]
            else:
                c8D = None
                d8D = None
            if len(InputData.C_DATA[k]["confirmed"]) >= 15:
                c2W = InputData.C_DATA[k]["increases_Confirmed"][-15:-8]
                d2W = InputData.C_DATA[k]["increases_Deads"][-15:-8]
            else:
                c2W = None
                d2W = None
            if len(InputData.C_DATA[k]["confirmed"]) >= 22:
                c3W = InputData.C_DATA[k]["increases_Confirmed"][-22:-15]
                d3W = InputData.C_DATA[k]["increases_Deads"][-22:-15]
            else:
                c3W = None
                d3W = None
            if len(InputData.C_DATA[k]["confirmed"]) >= 29:
                c4W = InputData.C_DATA[k]["increases_Confirmed"][-29:-22]
                d4W = InputData.C_DATA[k]["increases_Deads"][-29:-22]
            else:
                c4W = None
                d4W = None
                
            c7D100k = sum(c7D) / population * 100000 if population else None
            c2W100k = sum(c2W) / population * 100000 if population else None
            c3W100k = sum(c3W) / population * 100000 if population else None
            c4W100k = sum(c4W) / population * 100000 if population else None
            d7D1m = sum(d7D) / population * 1000000 if population else None
            d2W1m = sum(d2W) / population * 1000000 if population else None
            d3W1m = sum(d3W) / population * 1000000 if population else None
            d4W1m = sum(d4W) / population * 1000000 if population else None
            
            InputData.C_DATA[k]["c7D100k"] = c7D100k
            InputData.C_DATA[k]["repr7D"] = c7D100k / c2W100k if c2W100k != 0 and c7D100k and c2W100k else 0
            InputData.C_DATA[k]["c2W100k"] = c2W100k
            InputData.C_DATA[k]["repr2W"] = c2W100k / c3W100k if c3W100k != 0 and c2W100k and c3W100k else 0
            InputData.C_DATA[k]["c3W100k"] = c3W100k
            InputData.C_DATA[k]["repr3W"] = c3W100k / c4W100k if c4W100k != 0 and c3W100k and c4W100k else 0
            InputData.C_DATA[k]["c4W100k"] = c4W100k
            InputData.C_DATA[k]["d7D1m"] = d7D1m
            InputData.C_DATA[k]["dCoef7D"] = d7D1m / d2W1m if d2W1m != 0 and d7D1m and d2W1m else 0
            InputData.C_DATA[k]["d2W1m"] = d2W1m
            InputData.C_DATA[k]["dCoef2W"] = d2W1m / d3W1m if d3W1m != 0 and d2W1m and d3W1m else 0
            InputData.C_DATA[k]["d3W1m"] = d3W1m
            InputData.C_DATA[k]["dCoef3W"] = d3W1m / d4W1m if d4W1m != 0 and d3W1m and d4W1m else 0
            InputData.C_DATA[k]["d4W1m"] = d4W1m
            incC7DMean = sum(c7D) / len(c7D)
            incC8DMean = sum(c8D) / len(c8D)
            #c7DMean = sum(int(x) for x in InputData.C_DATA[k]["confirmed"][-7:]) / len(InputData.C_DATA[k]["confirmed"][-7:])
            #InputData.C_DATA[k]["c7DMean"] = c7DMean
            InputData.C_DATA[k]["incC7DMean"] = incC7DMean
            InputData.C_DATA[k]["incC8DMean"] = incC8DMean
            InputData.C_DATA[k]["incD7DMean"] = sum(d7D) / len(d7D)
            InputData.C_DATA[k]["incC7DMedian"] = sorted(c7D)[int(len(c7D)/2)]
            InputData.C_DATA[k]["incD7DMedian"] = sorted(d7D)[int(len(d7D)/2)]
            
            c7DBefore = InputData.C_DATA[k]["increases_Confirmed"][-8:-1]
            InputData.C_DATA[k]["incC7DPercent"] = self.getPercentualIncreases(c7D, c7DBefore)
            InputData.C_DATA[k]["incC7DPercentMean"] = sum(InputData.C_DATA[k]["incC7DPercent"]) / len(InputData.C_DATA[k]["incC7DPercent"])
            variance7D = sum([pow(x - incC7DMean,2) for x in c7D])/len(c7D)
            variance8D = sum([pow(x - incC8DMean,2) for x in c8D])/len(c8D)
            InputData.C_DATA[k]["incC7DStd"] = pow(variance7D,0.5) if variance7D != 0 else 0
            InputData.C_DATA[k]["incC8DStd"] = pow(variance8D,0.5) if variance8D != 0 else 0
            InputData.C_DATA[k]["incC8DToStdDev"] = (int(InputData.C_DATA[k]["increases_Confirmed"][-1]) - incC8DMean) / (InputData.C_DATA[k]["incC8DStd"] if InputData.C_DATA[k]["incC8DStd"] != 0 else 1) * 100
            
            InputData.C_DATA_OBJ.append(Dic2obj(InputData.C_DATA[k]))
            
            
    def getLookUpTable(self, inList, inCountries):
        countries = inCountries.copy()
        lookUpTable = {}
        notInCData = []
        #print("InputData.getLookUpTable")
        for j, line in enumerate(inList.items()):
            #print("{1:0>3} - {0} {2}".format(line[0], j, countries[0]))
            inCData = False
            for i, country in enumerate(countries):
                
                if line[0] in country[1]:
                    lookUpTable[line[0]] = i
                    inCData = True
                    break
                #elif line[1] == "Mainland China":
                    #lookUpTable["China"] = j
                    #print("line [1] {0}-{1}".format(line[1], i))
                    #inCData = True
                    #break
                elif line[0] == "US" and "United States of America" in country[1]:
                    #print("USA line [1] {0}-line[0] inCountries {2} {1}".format(line[1], i, line[0]))
                    lookUpTable["US"] = i
                    inCData = True
                    break
                elif line[0] == "Korea, South" and "South Korea" in country[1]:
                    #print("South Korea line [1] {0}-line[0] inCountries {2} {1}".format(line[1], i, line[0]))
                    lookUpTable["Korea, South"] = i
                    inCData = True
                    break
                
            if not inCData and line[1] not in notInCData:
                notInCData.append(line[0])
            #print(" {0}{1}".format(line[1], country[0]))
        return (lookUpTable, notInCData)
    
    def getPercentualIncreases(self,in7D, in7DBefore):
        if len(in7D) == len(in7DBefore):
            returnArray = []
            for i, x in enumerate(in7D):
                returnArray.append((x/in7DBefore[i] -1)*100 if in7DBefore[i] != 0 else 0)
        return returnArray
        
    def printPopulations(self):
        for c in InputData.C_DATA.keys():
            print("{0} - {1}".format(c, InputData.POP_DATA[InputData.LOOKUP[c]][2] if c in InputData.LOOKUP else None))
            
    def printData(self):
        print("InputData.DATES{}".format(InputData.DATES))
        print(["{1} : {0}".format(x[-1], x[1]) for x in self.allDataConfirmed])
        #print("{}".format(self.confirmedDic))
    
cFirstLine = cData.pop(0)
cSecondLine = cData.pop(0)
cData.pop(-1)

filePathJHU = os.path.join(path, "JHU")
#print("filePathJHU: {}".format(filePathJHU)) 

inputJHU = InputData(filePathJHU, cData)

def getCountryData(inData, inCName):
    countryDailyData = []
    for i, day in enumerate(inData):
        for j, country in enumerate(day):
            #print("getCountryData firstLine: {}".format(inputJHU.firstLine))
            #print("inCName: {0} country[1]: {1}".format(inCName, country[1]))
            if inCName in country[1] and inCName in country[0] and "Virgin" not in country[0]:
                #dayStamp = csvFiles[i].split("-")[0]
                splitedLine = inputJHU.firstLine[i].split("/")
                #print("splitedLine: {}".format(splitedLine))
                dayStamp = "20{2}_{0}_{1}".format(*splitedLine)
                countryDailyData.append(country.copy() + [dayStamp])
    return countryDailyData
    
def dayChartSorting(dayChartSort, data):
    #0__sort by confirmed
    #1__sort by dead
    #2__sort by death / confirmeded ratio
    #3__sort by death / population ratio
    #4__sort by commited / population ratio
    #5__sort by recovered
    #6__sort by daily increas ratio of commited in %
    #7__sort by daily increas ratio of dead in %
    #8__sort by country alphabetical wise
    #9__sort by c7D100k
    #10__sort by incC8DStd
    
    if dayChartSort == 0:
        data = sorted(data, key=lambda x: int(x.confirmed[-1]), reverse=False)
    elif dayChartSort == 1:
        data = sorted(data, key=lambda x: int(x.deads[-1]), reverse=False)
    elif dayChartSort == 2:
        data = sorted(data, key=lambda x: x.d_c, reverse=False)
    elif dayChartSort == 3:
        data = sorted(data, key=lambda x: x.d_pop if x.d_pop else 0, reverse=False)
    elif dayChartSort == 4:
        data = sorted(data, key=lambda x: x.c_pop if x.c_pop else 0, reverse=False)
    elif dayChartSort == 5:
        data = sorted(data, key=lambda x: int(x.recovered[-1]), reverse=False)
    elif dayChartSort == 6:
        data = sorted(data, key=lambda x: x.incC7DPercentMean if x.incC7DPercentMean else 0, reverse=False)
    elif dayChartSort == 7:
        data.sort(key=lambda x: x[10] if len(x) > 9 and type(x[9]) == float else 0, reverse=False)
    elif dayChartSort == 8:
        data.sort(key=lambda x: "".join(x[1].split()), reverse=False)
    elif dayChartSort == 9:
        data = sorted(data, key=lambda x: x.c7D100k if x.c7D100k else 0, reverse=False)
    elif dayChartSort == 10:
        data = sorted(data, key=lambda x: x.d7D1m if x.d7D1m else 0, reverse=False)
    elif dayChartSort == 11:
        data = sorted(data, key=lambda x: x.incC8DToStdDev if x.incC8DToStdDev else 0, reverse=False)
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
    divisor = src[1]-src[0]
    return ((val - src[0]) / divisor if divisor != 0 else 0) * (dst[1]-dst[0]) + dst[0]

ccData = countrySorting(4, cData.copy())
    #0__sort counties by population
    #1__sort counties by area
    #2__sort counties by density
reservedStrings =["q", "p", "a", "de", "d", "c", "dc", "dp", "cp", "r", "ic", "id", ">", "<", "c100k", "std", "d1m"]
coutriesOfIterest = [("Czechia", "CZE"),("Slovakia", "SVK"), ("US", "USA"), ("Italy", "ITA"), ("Spain", "ESP"), ("Croatia", "CRO"), ("Montenegro", "MTN"), ("Slovenia", "SLO"), ("United Kingdom", "UK"), ("Ireland", "IRL"), ("Russia", "RUS"), ("Brazil", "BRA"), ("Germany", "GER"), ("Austria", "AUT"), ("Denmark", "DEN"), ("Belgium","BEL"), ("Netherlands", "NED"), ("France", "FRA"), ("Iceland", "ICE"), ("New Zealand", "NZL"), ("Australia", "AUS"), ("Israel", "IZR"), ("Greece", "GRE"), ("Japan", "JAP"), ("China", "CHI"), ("Switzerland", "SUI"), ("Sweden", "SWE"), ("Finland", "FIN"), ("Norway", "NOR"), ("Romania", "ROM"), ("Argentina", "ARG"), ("Turkey", "TUR"), ("Belarus", "BLR"), ("Mali", "MAL"), ("Hungary", "HUN"), ("Poland", "POL"), ("Estonia", "EST"), ("Pakistan", "PAK"), ("Ecuador", "ECU"), ("Colombia", "COL"), ("India", "IND"), ("Bahrain", "BAH"), ("Lebanon", "LEB"), ("Venezuela", "VEN"), ("Mexico", "MEX##"), ("South Africa", "JAR"), ("South Korea", "SKO"), ("Singapore", "SIN"), ("Thailand", "THJ"), ("Seychelles", "SEY")]

inputText = "\n"
for i, c in enumerate(coutriesOfIterest):
    inputText += str(i) + " - " + c[1] + " |"
inputText += "\n daily charts sorting:\nc - sort by confirmed\nd - sort by dead\ndc - sort by confirm/dead ratio\ndp - sort by dead/population ratio\ncp - sort by confirmed/population ratio\nr - sort by recovered\na - sort countries by alphabetical order\nd1m - sort by dead for last 7 days to 1 mil citicenz\nc100k - sort countries by last 7 days confirmed increase / 100k citizens\nstd - sort by actual increas of confirmed to standard deviation for last 8 days\n"
inputText += "q - quit\n"
countryName = coutriesOfIterest[0][0]
myInput = input(inputText)
while myInput != "q" or myInput != "Q":
    if myInput not in reservedStrings:
        countryName = coutriesOfIterest[int(myInput) if int(myInput) < len(coutriesOfIterest) else 0][0]
    elif myInput == "q" or myInput == "Q":
        break
    
    print("{0:>3} {1:<15.15} {2:<14.14} {3:<12.12} {4:<10.10}".format(*cFirstLine))
    print("{0:>3} {1:<15.15} {2:<14.14} {3:<12.12} {4:<10.10}".format(*cSecondLine))
    for i, line in enumerate(ccData):
        print("{0:0>3} {1:<15.15} {2:<14} {3:<12} {4:<10}".format(*line))

    if myInput == "c":
        data = dayChartSorting(0, InputData.C_DATA_OBJ)
    elif myInput == "d":
        data = dayChartSorting(1, InputData.C_DATA_OBJ)
    elif myInput == "dc":
        data = dayChartSorting(2, InputData.C_DATA_OBJ)
    elif myInput == "dp":
        data = dayChartSorting(3, InputData.C_DATA_OBJ)
    elif myInput == "cp":
        data = dayChartSorting(4, InputData.C_DATA_OBJ)
    elif myInput == "r":
        data = dayChartSorting(5, InputData.C_DATA_OBJ)
    elif myInput == "ic":
        data = dayChartSorting(6, InputData.C_DATA_OBJ)
    elif myInput == "id":
        data = dayChartSorting(7, InputData.C_DATA_OBJ)
    elif myInput == "a":
        data = dayChartSorting(8, InputData.C_DATA_OBJ)
    elif myInput == "c100k":
        data = dayChartSorting(9, InputData.C_DATA_OBJ)
    elif myInput == "d1m":
        data = dayChartSorting(10, InputData.C_DATA_OBJ)
    elif myInput == "std":
        data = dayChartSorting(11, InputData.C_DATA_OBJ)
    else:
        data = InputData.C_DATA_OBJ
    #elif myInput == ">":
        
    #0__sort by confirmed
    #1__sort by dead
    #2__sort by death / confirmeded ratio
    #3__sort by death / population ratio
    #4__sort by commited / population ratio
    #5__sort by recovered
    #6__sort by daily increas ratio of commited in %
    #7__sort by daily increas ratio of dead in %
    #8__sort by country alphabetical wise
    #9__sort by c7D100k
    #10__sort by d7D1m
    #11__sort by incC8DStd
    
    #print("InputData.FIRST_LINE {}".format(InputData.FIRST_LINE))
    
    print("{0:>3} {1:<15.15} {2:<9.9} {3:<9.9} {4:<9.9}   {5:<7.7}{6:>29}    {7:<7}  {8:<7}{9:<7}".format("", *InputData.FIRST_LINE))
    print("{0:_>60}".format(""))
    for i, line in enumerate(data):
            print("{0:0>3} {1:<15.15} C {2:<7} D {3:<7} R {4:<7}   {5:< 7.2f}      {6:< 14,}{7:> 9.4f}   {8:< 8.2f}  {9:> 4.2f}  {10:> 4.0f}%".format(len(data)-i, line.name, line.confirmed[-1], line.deads[-1], line.recovered[-1], line.d_c, line.population if line.population else 0, line.c_pop if line.c_pop else 0, line.c7D100k if line.c7D100k else 0, line.d7D1m if line.d7D1m else 0, line.incC8DToStdDev if line.incC8DToStdDev else 0))
    print("{0:_>60}".format(""))
    print("{0:>3} {1:<15.15} {2:<9.9} {3:<9.9} {4:<9.9}   {5:<7.7}{6:>29}    {7:<7}  {8:<7}{9:<7}".format("", *InputData.FIRST_LINE))
    
    maxValC = max(InputData.C_DATA[countryName]["increases_Confirmed"])
    maxValD = max(InputData.C_DATA[countryName]["increases_Deads"])
    tableRange = 40
    
    # country daily chart
    """
    print("\n{0:<19} {3:<9.9} {4:<9.9} {5:<9.9} {6:<9.9}".format("", *firstLine))
    for i, line in enumerate(InputData.C_DATA[countryName]["confirmed"]):
        #if line[0] == line[1] and int("".join(line[2].split())) > 0:
        #print("{0:<19} C {1:<7} D {2:<7} R {3:<7} A {4:<7}".format(InputData.DATES[i],line[i],"A", "B", "C", "D", "E", "F"))
        deads = InputData.C_DATA[countryName]["deads"][i]
        recovered = InputData.C_DATA[countryName]["recovered"][i]
        active = int(line) - int(deads) - int(recovered)
        print("{0:<19} C {1:<7} D {2:<7} R {3:<7} A {4:<7}".format("20{2}_{0:0>2}_{1:0>2}".format(*InputData.DATES[i].split("/")),line, deads, recovered, active, "D", "E", "F"))
    """
    
    # deads daily increas graph
    print("")
    textHeader = "{0:<19} {1}{2:>" + str(int(tableRange / 2) -1) + "}{3:>" + str(int(tableRange / 2) -1) + "}"
    print(textHeader.format("Daily Inc. Deads",0 ,int(maxValD/2), maxValD))
    print("{0:_>60}".format(""))
    for i, line in enumerate(InputData.C_DATA[countryName]["increases_Deads"]):
        intVal = int(scale(line,(0,maxValD), (0,tableRange)))
        strVal = str(intVal) if intVal >= 0 else str(0)
        text = "{1:<12} {2:>6} {0:-<" + strVal + "}"
        
        #print(text.format(line, cDailyData[7]))
        print(text.format("", "20{2}_{0:0>2}_{1:0>2}".format(*InputData.DATES[i].split("/")), line))
    print("{0:_>60}".format(""))
    print(textHeader.format("Daily Inc. Deads",0 ,int(maxValD/2), maxValD))
    
    # confirmed daily increas graph
    print()
    # standard deviation range
    stdC8D = InputData.C_DATA[countryName]["incC8DStd"] if InputData.C_DATA[countryName]["incC8DStd"] else 0
    stdMean = InputData.C_DATA[countryName]["incC8DMean"] if InputData.C_DATA[countryName]["incC8DMean"] else 0
    stdMin = stdMean - stdC8D
    stdMeanScaled = int(scale(stdMean,(0,maxValC), (0,tableRange)))
    stdMinScaled = int(scale(stdMin,(0,maxValC), (0,tableRange)))
    stdMinScaled = stdMinScaled if stdMinScaled >=0 else 0
    stdC8DScaled = int(scale(stdC8D,(0,maxValC), (0,tableRange)))
    stdRangeText = "{0: <19}{0: >" + str(stdMinScaled) +"}{1: <" + str(stdC8DScaled) +"}{1: <" + str(stdC8DScaled) +"}|"
    textHeader = "{0:<19} {1}{2:>" + str(int(tableRange / 2) -1) + "}{3:>" + str(int(tableRange / 2) -1) + "}"
    print(textHeader.format("Daily Inc. Confirm",0 ,int(maxValC/2), maxValC))
    print("{0:_>60}".format(""))
    for i, line in enumerate(InputData.C_DATA[countryName]["increases_Confirmed"]):
        intVal = int(scale(line,(0,maxValC), (0,tableRange)))
        strVal = str(intVal) if intVal >= 0 else str(0)
        text = "{1:<12} {2:>6} {0:-<" + strVal + "}"
        #print(text.format(line, cDailyData[7]))
        print(text.format("", "20{2}_{0:0>2}_{1:0>2}".format(*InputData.DATES[i].split("/")), line))
        
    print(stdRangeText.format("", "|"))
    print("{0:_>60}".format(""))
    print(textHeader.format("Daily Inc. Confirm",0 ,int(maxValC/2), maxValC))
    print("")
        
    print("\n{0:<19} population {1:_}".format(countryName, InputData.C_DATA[countryName]["population"] if InputData.C_DATA[countryName]["population"] else 0))
    print("{0:_>60}".format(""))
    print("{0: <12} - Last 7 days median of confirmed increas".format(InputData.C_DATA[countryName]["incC7DMedian"]))
    print("{0: <12.2f} - Last 7 days mean of confirmed increas".format(InputData.C_DATA[countryName]["incC7DMean"]))
    print("{0: <12.2f} - Last 8 days mean of confirmed increas\n".format(InputData.C_DATA[countryName]["incC8DMean"]))
    print("{0: <12} - Last 7 days median of deads increas".format(InputData.C_DATA[countryName]["incD7DMedian"]))
    print("{0: <12.2f} - Last 7 days mean of deads increas\n".format(InputData.C_DATA[countryName]["incD7DMean"]))
    print("{0: <7.2f} {1: >4.2f} - Last 7 days confirmed / 100k citizens".format(InputData.C_DATA[countryName]["c7D100k"] if InputData.C_DATA[countryName]["c7D100k"] else 0, InputData.C_DATA[countryName]["repr7D"]))
    print("{0: <7.2f} {1: >4.2f} - 1 week ago confirmed / 100k citizens".format(InputData.C_DATA[countryName]["c2W100k"] if InputData.C_DATA[countryName]["c2W100k"] else 0, InputData.C_DATA[countryName]["repr2W"]))
    print("{0: <7.2f} {1: >4.2f} - 2 weeks ago confirmed / 100k citizens".format(InputData.C_DATA[countryName]["c3W100k"] if InputData.C_DATA[countryName]["c3W100k"] else 0, InputData.C_DATA[countryName]["repr3W"]))
    print("{0: <12.2f} - 3 weeks ago confirmed / 100k citizens\n".format(InputData.C_DATA[countryName]["c4W100k"] if InputData.C_DATA[countryName]["c4W100k"] else 0))
    print("{0: <7.2f} {1: >4.2f} - Last 7 days deads / 1 mil citizens".format(InputData.C_DATA[countryName]["d7D1m"] if InputData.C_DATA[countryName]["d7D1m"] else 0, InputData.C_DATA[countryName]["dCoef7D"]))
    print("{0: <7.2f} {1: >4.2f} - 1 week ago deads / 1 mil citizens".format(InputData.C_DATA[countryName]["d2W1m"] if InputData.C_DATA[countryName]["d2W1m"] else 0, InputData.C_DATA[countryName]["dCoef2W"]))
    print("{0: <7.2f} {1: >4.2f} - 2 weeks ago deads / 1 mil citizens".format(InputData.C_DATA[countryName]["d3W1m"] if InputData.C_DATA[countryName]["d3W1m"] else 0, InputData.C_DATA[countryName]["dCoef3W"]))
    print("{0: <12.2f} - 2 weeks ago deads / 1 mil citizens\n".format(InputData.C_DATA[countryName]["d4W1m"] if InputData.C_DATA[countryName]["d4W1m"] else 0))
    print("{0: <12.2f} - Last 7 days Standard deviation".format(InputData.C_DATA[countryName]["incC7DStd"] if InputData.C_DATA[countryName]["incC7DStd"] else 0))
    print("{0: <12.2f} - Last 8 days Standard deviation".format(InputData.C_DATA[countryName]["incC8DStd"] if InputData.C_DATA[countryName]["incC8DStd"] else 0))
    print("{1:.2f} < Extremes > {0:.2f}\n".format(InputData.C_DATA[countryName]["incC7DMean"] + InputData.C_DATA[countryName]["incC7DStd"], InputData.C_DATA[countryName]["incC7DMean"] - InputData.C_DATA[countryName]["incC7DStd"]))
    
    print("{0: >8.0f}% - Inc. of Confirm. cases to last 8 days Std dev".format(InputData.C_DATA[countryName]["incC8DToStdDev"] if InputData.C_DATA[countryName]["incC8DToStdDev"] else 0))
    print("{0:_>60}".format(""))
    myInput = input(inputText)