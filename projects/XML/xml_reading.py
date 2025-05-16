import xml.etree.ElementTree as ET
import xmltodict
import os
cwd = os.getcwd()
print("cwd {0}".format(cwd))
fName = "export1.xml"
filePath = os.path.join(cwd, fName)
print("filePath {0}".format(filePath))

#read as string
with open(filePath) as xmlFile:
	dataGPS = xmlFile.read().replace("\n", "")
#print("dataGPS {0}".format(dataGPS))
xmlDict = xmltodict.parse(dataGPS)
print("xmlDict {0}".format(xmlDict))

tree = ET.parse(filePath)
root = tree.getroot()
print("dir root {0}".format(dir(root)))
#print("root.items {0}".format(root.items()))
print("root.getchildren {0}".format(root.getchildren()))
print("root.iterfind {0}".format(root.iterfind('trk')))
for item in root.iterfind('trk'):
	print("iterfind tag {0}, iterfind attrib {1}".format(item.tag, item.attrib))
print("root.tag {0}, root.attrib {1}".format(root.tag, root.attrib))

for i, child in enumerate(root.iter()):
	print("child.findall {0}".format(child.findall('trkpt]')))
	print("root child {0:3>0} - {1}:{2}".format(i, child.tag, child.attrib))
	name = child.findall("name")
	trkseg = child.findall("trkseg")
	print("name {0}".format(name))
	print("trkseg {0}".format(trkseg))
	for j, chChild in enumerate(child.iter()):
		print("{0}-child child {0:3>0} - {1}:{2}".format(j, chChild, chChild))
		print("chChild.findall {0}".format(chChild.findall('trk')))
		for k, chChChild in enumerate(chChild):
			#name = chChild.find("name").text
			lat = chChChild.get("lat")
			lon = chChChild.get("lon")
			print("{0:0>3}\nlat {1}\nlon {2}".format(k,lat, lon))
			#print("{0}-child child child {0:3>0} - {1}:{2}".format(k, chChChild, chChChild))
		
name = root.findall('trk')
#print("iter trk {0}".format(trk.attrib))
print("name:{0}".format(root.findall("name")))

#for trkpt in root.iter('trkpt'):
#	lat = trkpt.get("lat")
#	lon = trkpt.get("lon")
#	print("trkpt.attrib {0}".format(trkpt.attrib))
#	#print("{0:3>0 - lat={1}:lon={2}".format(i, lat, lon))

for name in root.findall('name'):
	print("name.text {0}".format(name.text))
	#print("{0:3>0 - lat={1}:lon={2}".format(i, lat, lon))
	

fName = "test.xml"
filePath = os.path.join(cwd, fName)
print("filePath {0}".format(filePath))
tree = ET.parse(filePath)
root2 = tree.getroot()
print("root2.tag {0}, root2.attrib {1}".format(root2.tag, root2.attrib))
for rank in root2.iter('rank'):
	print("rank {0}".format(rank.text))
trkpts = root.findall('trkpt')
print("trkpts {0} - len {1}".format(trkpts, len(trkpts)))
for item in root.iter('trkpt'):
	print("iterfind tag {0}, iterfind attrib {1}".format(item.tag, item.attrib))

def getElementToAppend(inCountry, **kwargs):
	rank = kwargs['rank'] if 'rank' in kwargs else None
	year = kwargs['year'] if 'year' in kwargs else None
	neighbors = kwargs['neighbors'] if 'neighbors' in kwargs else None
	gdppc = kwargs['gdppc'] if 'gdppc' in kwargs else None
	newEl = ET.Element("country", {"name":inCountry})
	ET.SubElement(newEl, "rank").text="{0}".format(rank) if rank else None
	ET.SubElement(newEl, "year").text = "{0}".format(year) if year else None
	ET.SubElement(newEl, "gdppc").text="{0}".format(gdppc) if gdppc else None
	if neighbors:
		for neighbor in neighbors:
			ET.SubElement(newEl, "neighbor", {"name":neighbor["name"], "direction":neighbor["direction"]})
	return newEl
	
neighborsHu = [{"name":"Slovakia", "direction":"N"}, {"name":"Austria", "direction":"W"}]
newEl = getElementToAppend("Hungary", rank=20, year=2000, gdppc=15654, neighbors=neighborsHu)
root2.append(newEl)
for country in root2.findall('country'):
	print("appended {0}".format(country.get("name")))
tree.write("output.xml")

fName = "ÚV Želivka 3.stavba.xml"
filePath = os.path.join(cwd, fName)
print("filePath {0}".format(filePath))
tree = ET.parse(filePath)
root3 = tree.getroot()
print("root3.tag {0}, root3.attrib {1}".format(root3.tag, root3.attrib))
for check in root3.findall("./Heading/Section/Check"):
	print("{0}".format(check.get('CheckName')))

##read as string
#with open(filePath) as xmlFile:
#	data = xmlFile.read().replace("\n", "")

#print("data {0}".format(data))
#xmlDict = xmltodict.parse(data)
#print("xmlDict {0}".format(xmlDict))