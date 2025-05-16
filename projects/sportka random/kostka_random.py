import random
inputText = "Generuj cislo: y/n"
myInput = input(inputText)
while myInput != "n" or myInput != "N":
    cislo = random.randint(1,6)
    print(cislo)
    myInput = input(inputText)
        