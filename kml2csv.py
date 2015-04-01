import xml.dom.minidom
import sys

def traverseTree(document, rows):
  for child in document.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'Folder' :
            traverseFolder1(child,rows)

def traverseFolder1(document,rows):
  for child in document.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'Folder' :
            traverseFolder2(child,rows)
 
def traverseFolder2(document,rows):
  for child in document.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'Placemark' :
            traversePlacemark(child,rows)

def traversePlacemark(document,rows):
  dict = {}
  for child in document.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'TimeSpan' :
            traverseTimeSpan(child,dict)
        if child.tagName == 'Point' :
            traversePoint(child,dict)
        if child.tagName == 'description' :
            traverseDescription(child,dict)
  #print 'dict' , dict
  rows.append(dict)

def unescape(s):
   s = s.replace("&lt;", "<")
   s = s.replace("&gt;", ">")
   # this has to be last:
   s = s.replace("&amp;", "&")
   return s

def traverseDescription(description,dict):
  desc = unescape(getText(description)) + '</td></tr></table>'
  #print 'description', desc
  descXml = xml.dom.minidom.parseString(desc)
  traverseTable(descXml.documentElement,dict)

def traverseTable(table,dict):
  #print 'table' , table.tagName
  for child in table.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'tr' :
           traverseTR(child,dict)

def traverseTR(tr,dict):
  key=""
  value=""
  first=True
  for child in tr.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'td' :
           if first:
              key = getText(child)
           else:
              value = getText(child)
           first = False
  if key != '' :
     #print 'key', key, 'value', value
     dict[key]=value

def traverseTimeSpan(document,dict):
  for child in document.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'begin' :
           #print 'begin:' , getText(child)
           dict['begin']=getText(child) 

def traversePoint(document,dict):
  for child in document.childNodes:
    if child.nodeType == xml.dom.Node.ELEMENT_NODE:
        if child.tagName == 'coordinates' :
           #print 'coordinates:' , getText(child)
           dict['coordinates']=getText(child)

 
def getText(element):
    rc = []
    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc).strip()

def createCSV(rows,f):
	headerExist = {}
	for row in rows:
		for key,value in row.items():
			headerExist[key] = True
	#print headers
	headerExist["begin"] = False
	headerExist["coordinates"] = False
	
	headers = ["begin","coordinates"]
	line = '"begin";"coordinates'
	for key,value in headerExist.items():
		if value:
			line +='";"'
			line += key
			headers.append(key)
	line += '"\n'
	f.write(line)

	for row in rows:
		line = '"'
		first = True
		for header in headers:
			value = row[header]
			if value is None:
				value = ''
			if not first :
				line+='";"'
			first = False
			line += value
		line += '"\n'
			
		f.write(line)	

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print "Please specify the input kml : kml2csv <input.kml> [<output.csv>]"
		sys.exit(-1)
	filename=sys.argv[1]
	if len(sys.argv) > 2 :
		outputfile = sys.argv[2]
	else:
		outputfile = sys.argv[1] + '.csv'
	rows = []
	dom = xml.dom.minidom.parse(filename)
	traverseTree(dom.documentElement,rows)
	f = open(outputfile,'w')
	createCSV(rows,f)
	f.close()
