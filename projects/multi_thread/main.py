from os import walk
import os
import os.path as osPath
import threading
import sys
import thread

"""
    utilitka na premenovanie suborov pomocou shiftovania znakov z tabulky ascii_letters
    je treba davat pozor, aby sifrovanie prebehlo bez chyby na cely adresar len raz
    v pripade ze sa nieco nepodari, je potreba spustit fciu renameFilesReversed(inFiles)
    ktora shiftne znaky do povodneho stavu

"""
dirPath = r"/storage/emulated/0/Download/rename"
#dirPath = r"/storage/emulated/0/DCIM"
print dir(threading.Thread)
class AsyncWalkDirs(threading.Thread):
    """Multithread class to acquire all subdirs of 
       defined directory as dirPath.
    """
    def __init__(self, inDirPath):
        threading.Thread.__init__(self)
        self.dirPath = inDirPath
    
    # Overwritten method of parent class(threading.Thread).
    def run(self):
        self.allSubdirs = self.walkDirs(self.dirPath, 0)
      
    def walkDirs(self, inDirPath, inLevel = 0):
        """ Browses all subdirs in defined directory
        
        Args:
            param1 (str): path to required directory as raw string.
            param2 (int): Initial level of recursion.
                Default is 0

        Returns:
            list of strings: Nested list of directory content in format:
                (path/directoryName or path/fileName)

        Raises: not specified yet text under is example template
            AttributeError: The ``Raises`` section is a list of all exceptions
                that are relevant to the interface.
            ValueError: If `param2` is equal to `param1`.
        """
        myFiles = []
        myDirs = []
        myPath = inDirPath
        myPaths = []
        returnDirs = []
        myLevel = inLevel
        for (path, dirnames, filenames) in walk(myPath): 
            if len(dirnames) > 0:
                for d in dirnames:            
                    newPath = "{path}/{dir}".format(path = myPath, dir = d)
                    returnDirs.insert(0, self.walkDirs(newPath, myLevel+1))
            #print filenames
            for f in filenames:
                myFiles.insert(0, "{mPath}/{file}".format(mPath = myPath, file = f))
            returnDirs.insert(0, myFiles)
            return returnDirs
        
        


# def getFileIndex(inFileName):        
#     return inFileName.split("_")[0]

# def adjustFileName(inFName, inReqDigCount, inPos):
#     myIndex = getFileIndex(inFName)
#     zeroesInsert = ""
#     newFName = ""
#     if len(myIndex) < inReqDigCount:
#         reqZeroes = inReqDigCount - len(myIndex)
#         for i in range(0, reqZeroes):
#             zeroesInsert += "0"
#         newFName = zeroesInsert + inFName
#         os.rename(dirPath + inFName, dirPath + newFName)
#         print "the file: " + dirPath + inFName + " was renamed to: " + newFName
# #            os.rename(dirPath + inFName, dirPath + newFName)
# #            print "the file: " + dirPath + inFName + " was renamed to: " + newFName
# #            print "the file: " + dirPath + inFName + " WAS NOT RENAMED"
#     else:
#         newFName = inFName
# #        print "the file: " + dirPath + inFName + " has correct format"
#     return newFName

# def addZeroes(inFiles, inRequiredDigitCount):
#     returnList = []
#     for i, f in  enumerate(inFiles):
#         returnList.append(adjustFileName(f, inRequiredDigitCount, i))
#     return returnList

def flatten(l): 
    if type(l) is list:
        if len(l) > 1:
            return flatten(l[0]) + flatten(l[1:])
        elif len(l) == 1:
            return flatten(l[0]) + []
        else: 
            return []
    else:
        return [l]     
    # return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]

def renameFiles(inFiles):
    newNames = []
    print inFiles
    for f in inFiles:        
        newFname = ""
        newFext = ""
 #       print f
        splitedPath = f.split("/")
        fName = splitedPath[-1].split(".")[-2]
        #print fName
        fExt = splitedPath[-1].split(".")[-1]
        #print fExt
        for ch in fName: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)        
                newFname += ascii_letters[(charPos + 1) % len(ascii_letters)]
            else:
                newFname += ch
            #print ord(ch)
        #print newFname
        for ch in fExt: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)           
                newFext += ascii_letters[(charPos + 1) % len(ascii_letters)]
            else:           
                newFext += ch
            #print ord(ch)
        #print newFext
        myPath = "/".join(splitedPath[:-1])
        returnName = myPath + "/" + newFname + "." + newFext
        os.rename(f, returnName)
        print "file {oldName} was renamed to : {nName}".format(oldName = f, nName = returnName)

        newNames.append(returnName)

#    print newNames
    return newNames

def renameFilesReversed(inFiles):
    newNames = []
    for f in inFiles:        
        newFname = ""
        newFext = ""
#        print f
        splitedPath = f.split("/")
        fName = splitedPath[-1].split(".")[-2]
        #print fName
        fExt = splitedPath[-1].split(".")[-1]
        #print fExt
        for ch in fName: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)        
                newFname += ascii_letters[(charPos - 1) % len(ascii_letters)]
            else:
                newFname += ch
            #print ord(ch)
        #print newFname
        for ch in fExt: 
            if ch in ascii_letters:
                charPos = ascii_letters.find(ch)           
                newFext += ascii_letters[(charPos - 1) % len(ascii_letters)]
            else:           
                newFext += ch
            #print ord(ch)
        #print newFext
        myPath = "/".join(splitedPath[:-1])
        returnName = myPath + "/" + newFname + "." + newFext
        os.rename(f, returnName)
        print "file {oldName} was renamed to : {nName}".format(oldName = f, nName = returnName)
        newNames.append(returnName)
 #   print newNames
    return newNames

inputText = "Do you really want to rename all files in " + dirPath + " ? - Yes / No / R read dirs\n"
while 1:
    try:
        myInput = raw_input(inputText)
        if myInput == "y" or myInput == "Y" or myInput == "yes" or myInput == "YES":
            inputText = "Do you want to rename or reverse_rename " + dirPath + " ? - R / REV\n"
            while 1:
                try:
                    my2Input = raw_input(inputText)
                    background = AsyncWalkDirs(dirPath)
                    background2 = AsyncWalkDirs(dirPath2)
                    background.start()
                    
                    background.join()
                    myOldList = background.allSubdirs
                    print myOldList
                    flattened = flatten(myOldList)
                    ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    if my2Input == "r" or my2Input == "R" or my2Input == "rename" or my2Input == "RENAME":
                        try: 
                            renameFiles = thread.start_new_thread( renameFiles, (flattened,) ) 
                        except TypeError as err: 
                            error_type, error_instance, traceback = sys.exc_info()
                            print(err.args)
                            #print "error_type: {0}, error_instance{1}, traceback -{2}".format(error_type, error_instance, traceback)
                           # print "Error: unable to start thread"
                        #renameFiles = renameFiles(flattened)
                        break
                    elif my2Input == "REC" or my2Input == "rev" or my2Input == "reversed" or my2Input == "REVERSED":
                        renameFiles = thread.start_new_thread( renameFilesReversed, (flattened,) ) 
                        #renameFilesReversed = renameFilesReversed(flattened)
                        break
                    else:
                        raise ValueError("bad value inserted...")
                        
                except ValueError:
                    error_type, error_instance, traceback = sys.exc_info()
                    print "error_type: {0}, error_instance{1}, traceback -{2}".format(error_type, error_instance, traceback)
                    
        elif myInput == "r" or myInput == "R" or myInput == "read" or myInput == "READ":
            background = AsyncWalkDirs(dirPath)
            background.start()
            print 'The main program continues to run in foreground.'
            background.join() # Wait for the background task to finish 
            print 'Main program waited until background was done.'
            print background.allSubdirs
            break
        else:
             raise ValueError("Your input doesn't seem to apear as a proper value")
    except ValueError:
        error_type, error_instance, traceback = sys.exc_info()
        print "error_type: {0}, error_instance{1}, traceback -{2}".format(error_type, error_instance, traceback)