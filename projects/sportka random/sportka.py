from math import *
import random

inputText = "q - quit\ng - generate random number\n"
#cDailyData = getCountryData(allData, coutriesOfIterest[0][0])
myInput = input(inputText)

while myInput != "q" or myInput != "Q":
    if myInput == "g" or myInput == "G":
        num = random.randint(1,49)
        print("{}".format(num))
        myInput = input(inputText)