import random
import numpy as np
from numpy import base_repr


def digit_to_char(digit): 
    if digit < 10: 
        return str(digit) 
    return chr(ord('a') + digit - 10) 
    
def str_base(number,base): 
    if number < 0: 
        return '-' + str_base(-number, base) 
    (d, m) = divmod(number, base)
    if d > 0: 
        return str_base(d, base) + digit_to_char(m) 
    return digit_to_char(m)
    

alphaNum = ("0", "1", "2", "3", "4", "5", "6", "7","8","9",
	            "a", "b","c","d","e","f","g","h","i","j","k",
	            "l","m","n","o","p","q","r","s","t","u","v",
	            "w","x","y","z")
	            
ruleOnes = np.ones((512), dtype = np.uint8)
strOnes = "".join([str(z) for z in list(ruleOnes)])
print("ruleOnes {0} shape {1}".format(ruleOnes, ruleOnes.shape))
print("strOnes {0}".format(strOnes))
onesInt = int(strOnes, 2)
print("onesInt {0}".format(onesInt))
onesBin = "{:b}".format(onesInt)
print("onesBin {0}".format(onesBin))
onesIntShifted = onesInt >> 20
onesBinShifted = "{:b}".format(onesIntShifted)
print("onesIntShifted {0}".format(onesIntShifted))
print("onesBinShifted {0}".format(onesBinShifted))

onesInt = int(strOnes, 2)
onesIntDec = onesInt - 500
onesBinDec = "{:b}".format(onesIntDec)
onesBinDecRev = onesBinDec[::-1]
#arrayOnesBinDec = "".join([str(z) for z in list(onesBinDec)])
#arrayOnesBinDecRev = arrayOnesBinDec[len(arrayOnesBinDec),0,-1]
print("onesIntDec {0}".format(onesIntDec))
print("onesBinDec {0}".format(onesBinDec))
print("onesBinDecRev {0}".format(onesBinDecRev))

print (len(alphaNum))
#string1 = "TQB54"

string3 = "GLC"
string4 = "U5"
string5 = "37J"
#string7 = "Lokomotiva-1982"

int1 = 1666597438632046
myString1 = base_repr(int1, base=36)
int2 = 2521268150118790373416267
myString2 = base_repr(int2, base=36)

int3 = int(string3,36)
int4 = int(string4,36)
int5 = int(string5,36)
#int7 = int(string7,36)

print("myString1 {0}".format(myString1.lower()))
myString2First = myString2[0]
myString2 = myString2.lower()
listStr2 = []
listStr2[:0] = myString2
listStr2[0] = myString2First

myString2 = myString2.lower()
#myString2[0] = myString2First
print("myString2 {0}".format("".join(listStr2)))
print ("{fStr} ->> int1 = {fInt}".format(fStr = str, fInt = int1))
print ("{fStr} ->> int2 = {fInt}".format(fStr = str, fInt = int2))
print ("{fStr} ->> int4 = {fInt}".format(fStr = str, fInt = int4))
print ("{fStr} ->> int5 = {fInt}".format(fStr = str, fInt = int5))
#print ("{fStr} ->> int7 = {fInt}".format(fStr = string7, fInt = int7))
bin1 = "{:b}".format(int1)
print ("{fStr} ->> bin1 = {fBin}".format(fStr = str, fBin = bin1))
hex1 = "{:x}".format(int1)
print ("{fStr} ->> hex1 = {fHex}".format(fStr = str, fHex = hex1))
bin2 = "{:b}".format(int2)
print ("{fStr} ->> bin2 = {fBin}".format(fStr = str, fBin = bin2))
hex2 = "{:x}".format(int2)
print ("{fStr} ->> hex2 = {fHex}".format(fStr = str, fHex = hex2))
bin3 = "{:b}".format(int3)
print ("{fStr} ->> bin3 = {fBin}".format(fStr = str, fBin = bin3))
hex3 = "{:x}".format(int3)
print ("{fStr} ->> hex3 = {fHex}".format(fStr = str, fHex = hex3))
myInt = 1
myAnum = base_repr(myInt, base=36)
print ("{fInt} ->> alfaNum = {fAnum}".format(fInt = myInt, fAnum = myAnum))
myHex = "{:x}".format(myInt)
print ("{fInt} ->> hex = {fHex}".format(fInt = myInt, fHex = myHex))
myBin = "{:b}".format(myInt)
print ("{fInt} ->> bin = {fBin}".format(fInt = myInt, fBin = myBin))
#myStr = str_base(int, 64)

myStr = base_repr(int1, base=36)

