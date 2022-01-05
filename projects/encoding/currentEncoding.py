import sys
import os
import codecs
import io
import chardet
#from bs4 import UnicodeDammit

print("current encoding: {0}".format(sys.stdin.encoding))
#import pip
#import magic

#pip.main(['install', 'python-magic'])

path = r"/storage/emulated/0/Download"
#fileName = "revit_classes.txt"
fileName = "2022_01_04-SNIM-Assembly_code_ANSI.txt"
filePath = os.path.join(path, fileName)
#blob = open(filePath, 'rb').read()
#m = magic.open(magic.MAGIC_MIME_ENCODING)
#m.load()
#encoding = m.buffer(blob)
#print("encoding {0}: {1}".format(encoding, filePath))
def predict_encoding(file_path, n_lines=50):
    '''Predict a file's encoding using chardet'''
    

    # Open the file as binary data
    with open(file_path, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']

enc = predict_encoding(filePath)
print("chardet encoding of {1}: {0}".format(enc, filePath))


#encodings = ['utf-8', 'windows-1250' , 'windows-1251', 'windows-1252', 'iso-8859-1', 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 'utf_8', 'utf_8_sig'] # add more
#for e in encodings:
#    try:
#        #fh = codecs.open(filePath, 'r', encoding=e)
#        fh = io.open(filePath, 'r', encoding=e)
#        fh.readlines()
#        fh.seek(0)
#    except UnicodeDecodeError:
#        print('got unicode error with %s , trying different encoding' % e)
#    else:
#        print('opening the file with encoding:  %s ' % e)
#        #break
        
