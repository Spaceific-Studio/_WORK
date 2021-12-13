import xml.etree.ElementTree as ET
import os
#import xmltodict

cwd = os.getcwd()
print("cwd {0}".format(cwd))
fName = "SO_03-02-ARS- MEC - hard.xml"
subDir1 = "clashtest"
filePath = os.path.join(cwd, subDir1)
filePath = os.path.join(filePath, fName)
print("filePath {0}".format(filePath))
with open(filePath) as xmlFile:
	data = xmlFile.read().replace("\n", "")
#xmlDict = xmltodict.parse(data)
#print("xmlDict {0}".format(xmlDict))
tree = ET.parse(filePath)
root = tree.getroot()
#print("dir root {0}".format(dir(root)))
#print("root.getchildren {0}".format(root.getchildren()))

for clashResult in root.iter('clashresult'):
	clashResultAttrs = {}
	#print("clashResult {0}".format(clashResult.attrib['name']))
	clashResultObjsAttrs = []
	for clashObject in clashResult.iter('clashobject'):
		clashObjAttribNames = []
		clashObjAttribValues = []
		for clashObjAttrName in clashObject.iter('name'):
			clashObjAttribNames.append(clashObjAttrName.text)
			#print("clashObjectAttrName {0}".format(clashObjAttrName.text))
		for clashObjAttrValue in clashObject.iter('value'):
			clashObjAttribValues.append(clashObjAttrValue.text)
			#print("clashObjectAttrName {0}".format(clashObjAttrValue.text))
		zipObj = zip(clashObjAttribNames, clashObjAttribValues)
		clashObjDict = dict(zipObj)
		clashResultObjsAttrs.append(clashObjDict)
	pos3fList = [x for x in clashResult.iter('pos3f')]
	clashResultPos = pos3fList[0] if len(pos3fList) >0 else None
	posDict ={}
	xPos = clashResultPos.attrib['x']
	yPos = clashResultPos.attrib['y']
	posDict ={}
	posDict['x'] = xPos
	posDict['y'] = yPos
	clashResultAttrs['clashResultPos'] = posDict
	clashResultAttrs['clashResultName'] = clashResult.attrib['name']
	clashResultAttrs['clashResultObjsAttrs'] = clashResultObjsAttrs
	print("{0}\n\telement_1-ID {1}, item name {2}, item type {3}\n\telement_2-ID {4} item name {5}, item type {6}\n\tx:{7}\n\ty:{8}\n".format(clashResultAttrs['clashResultName'], clashResultAttrs['clashResultObjsAttrs'][0]['Element ID'], clashResultAttrs['clashResultObjsAttrs'][0]['Item Name'], clashResultAttrs['clashResultObjsAttrs'][0]['Item Type'], clashResultAttrs['clashResultObjsAttrs'][1]['Element ID'], clashResultAttrs['clashResultObjsAttrs'][1]['Item Name'], clashResultAttrs['clashResultObjsAttrs'][1]['Item Type'], clashResultAttrs['clashResultPos']['x'], clashResultAttrs['clashResultPos']['y']))
#for element in root.iter('clashobject'):
#	print("clashobject {}".format([x for x in element.iter('objectattribute')]))
#for item in root.iterfind('batchtest'):
#	print("iterfind tag {0}, iterfind attrib {1}".format(item.tag, item.attrib))
#	for tests in item.iterfind('clashtests'):
#		print("clashtests tag {0}, clashtest attrib {1}".format(tests.tag, tests.attrib))
#		for test in tests.iterfind('clashtest'):
#			print("clashtest tag {0}, clashtest attrib {1}".format(test.tag, test.attrib))
#			for results in test.iterfind('clashresults'):
#				print("clashresults tag {0}, clashresults attrib {1}".format(results.tag, results.attrib))
#				for result in results.iterfind('clashresult'):
					#print("clashresult tag {0}, clashresult attrib {1}".format(result.tag, result.attrib))
#					for clashObject in result.iterfind('clashobjects'):
#						for element in clashObject.iterfind('clashobject'):
#							print('clashobject {0}'.format(element.getchildren()))
#						print("clashObject {}".format(clashObject))
#					print("{0} - {1}".format(result.attrib['name'], result.attrib['guid']))
#batchTests = root.iterfind('batchtests')
#print("batchTests:\n{0}".format(batchTests))
#for clashTest in batchTests.findall('clashtests'):
#	print("clashTests:\n{0}".format(clashTests))
#for i, child in enumerate(root.iter()):
#	print("i-{0}, child.findall {1}".format(i, child.findall('clashresults')))
	#print("root child {0:3>0} - {1}:{2}".format(i, child.tag, child.attrib))
	
