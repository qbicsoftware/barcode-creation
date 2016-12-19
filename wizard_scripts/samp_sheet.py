
# coding: utf8
import os
import sys
import csv
import time
import datetime
import json
from PyRTFloc import *

BASE = os.path.dirname(sys.argv[0])+"/"

# Initalization of properties, place file with path in this directory or change
PROPERTIES_FILE_PATH = fline=open(BASE+"properties_path.txt").readline().rstrip()

properties = {}

for line in open(PROPERTIES_FILE_PATH):
    splt = line.strip().split('=')
    if len(splt) == 2:
        properties[splt[0].strip()] = splt[1].strip()

RESULTS_FOLDER = properties["barcode.results"]

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('_%Y%b%d')

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

with open(sys.argv[1],'r') as f:
    obj = byteify(json.loads(f.read()))

PRJ = obj["project_code"]
projectName = obj["project_name"]
investigator = obj["investigator"]
contact = obj["contact"]
#inv.put("first", investigator.getFirstName());
#inv.put("last", investigator.getLastName());
#inv.put("phone", investigator.getPhone());
firstCol = obj["cols"][0]
secondCol = obj["cols"][1]

#PRJ = sys.argv[3][1:5]
#firstCol = sys.argv[1]
#secondCol = sys.argv[2]

BASEDIR = os.path.join(RESULTS_FOLDER, PRJ)
pngdir = os.path.join(BASEDIR, "png/")

sheet_path=BASEDIR+"/documents/sample_sheets"
outfile=sheet_path+"/sample_sheet_"+PRJ+st

os.system('mkdir -p '+sheet_path)

def getPersonLine(personObject):
	return personObject["first"]+" "+personObject["last"]+" - Tel: "+personObject["phone"]

def MakeDoc() :
	doc     = Document()
	ss      = doc.StyleSheet
	section = Section()
	doc.Sections.append( section )

	#	text can be added directly to the section
	#	a paragraph object is create as needed

	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%d %b, %Y')
	section.append( 'Sample sheet QBiC project: ' + PRJ + " "+st)
	thin_edge  = BorderPS( width=20, style=BorderPS.DOUBLE )
	thin_frame  = FramePS( thin_edge,  thin_edge,  thin_edge,  thin_edge )
	no_edge = BorderPS( width=1, style=BorderPS.HAIRLINE )
	no_frame = FramePS ( thin_edge, no_edge, no_edge, no_edge)
	TabPS.DEFAULT_WIDTH = 800

	#header = Table(TabPS.DEFAULT_WIDTH * 6, TabPS.DEFAULT_WIDTH * 6)
	if projectName:
		nameCell = Paragraph( projectName )
		section.append(nameCell)
	if investigator:
		p1 = Paragraph()
		p1.append("Principal Investigator")
		p2 = Paragraph()
		p2.append(getPersonLine(investigator))
		section.append(p1)
		section.append(p2)
	if contact:
		p3 = Paragraph()
		p3.append("Contact Person")
		p4 = Paragraph()
		p4.append(getPersonLine(contact))
		section.append(p3)
		section.append(p4)

	#section.append(header)

	table = Table( TabPS.DEFAULT_WIDTH * 4, TabPS.DEFAULT_WIDTH * 3, TabPS.DEFAULT_WIDTH * 3, TabPS.DEFAULT_WIDTH * 2 )
	c1 = Cell( Paragraph( 'Barcode' ), thin_frame )
	c2 = Cell( Paragraph( firstCol ), thin_frame )
	c3 = Cell( Paragraph( secondCol ), thin_frame )
	c4 = Cell( Paragraph( 'Notes' ), thin_frame )
	table.AddRow(c1, c2, c3, c4)
	#table.AddRow(c2,c3,c4)
	i = -1
	for name in sample_name:
		i+=1
		section.append(table)
		table = Table (TabPS.DEFAULT_WIDTH * 12)
		#if(name in cats):
		#	c1 = Cell( Paragraph( cats[name] ), thin_frame ) 
		#	table.AddRow(c1)
		image = Image( pngdir+'/'+ name +'.png' , width=2*72)
		c1 = Cell( Paragraph( image ), thin_frame ) 
		section.append(table)
		table = Table( TabPS.DEFAULT_WIDTH * 4, TabPS.DEFAULT_WIDTH * 3, TabPS.DEFAULT_WIDTH * 3, TabPS.DEFAULT_WIDTH * 2 )
		c2 = Cell(Paragraph (description[i]), thin_frame )
		c3 = Cell(Paragraph (derived[i]), thin_frame )
		c4 = Cell(Paragraph (str("")), thin_frame )
		table.AddRow(c1, c2, c3, c4)
	section.append(table)
	return doc

def OpenFile( name ) :
	return file( '%s.rtf' % name, 'w' )

sample_name=[]
description=[]
derived=[]

for sample in obj["samples"]:
	sample_name.append(sample["code"])
	description.append(sample["info"])
	derived.append(sample["alt_info"])

#cats={}
#cat = False
#currCat = ""
#i = 0
f#or word in sys.argv[3:]:
#	if(word.startswith("-c")):
#		cat = True
#	elif(cat):
#		cat = False
#		currCat = word
#	elif(i==0):
#		word = word.strip()
#		if(currCat!=""):
#			cats[word] = currCat
#			currCat=""
#		sample_name.append(word)
#		i+=1
#	elif(i==1):
#		description.append(word)
#		i+=1
#	else:
#		derived.append(word)
#		i=0

DR = Renderer()

doc1 = MakeDoc()

DR.Write( doc1, OpenFile( outfile ) )

os.system("mv "+outfile+".rtf "+outfile+".doc")

print "\nDone. Sample sheet created in: "+outfile+"\n";

