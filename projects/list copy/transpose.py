myList = [[12,7,5],[13,0,6],[4,8,9]]
confirmedDic = {"france":[3,2,0,1], "mozambigue":[4,8,9,10], "filipines":[12,13,14,15], "guatemala":[20,21,22,23], "china":[40,50,51,52]}
deathsDic = {"france":[100,102,103,104], "mozambigue":[200,201,202,203], "filipines":[301,302,303,304], "guatemala":[400,401,402,403], "china":[500,501,502,503]}
recoveredDic = {"france":[1001,1002,1003,1004], "mozambigue":[2000,2001,2002,2003], "filipines":[3001,3002,3003,3004], "guatemala":[4000,4001,4002,4003], "china":[5000,5001,5002,5003]}
def transpose(inList):
	returnList = [[inList[j][i] for j in range(len(inList))] for i in range(len(inList[0]))]
	return returnList
def getTransformedMatrix(inConfirmed, inDeaths, inRecovered):
	confirmedDicValues = [x for x in inConfirmed.values()]
	deathsDicValues = [x for x in inDeaths.values()]
	recoveredDicValues = [x for x in inRecovered.values()]
	confirmedDicValuesTransposed = transpose(confirmedDicValues)
	deathsDicValuesTransposed = transpose(deathsDicValues)
	recoveredDicValuesTransposed = transpose(recoveredDicValues)
	returnMatrix = []
	for i, dayValues in enumerate(confirmedDicValuesTransposed):
		dayMatrix = []
		for j, country in enumerate(inConfirmed.keys()):
			dayMatrix.append([country, country, dayValues[j], deathsDicValuesTransposed[i][j], recoveredDicValuesTransposed[i][j]])
		returnMatrix.append(dayMatrix)

	#print("dayMatrix: {}".format(returnMatrix))
	return returnMatrix

allData = getTransformedMatrix(confirmedDic, deathsDic, recoveredDic)
print("allData: {}".format(allData))

