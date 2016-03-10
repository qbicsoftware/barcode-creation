import os
import sys
import subprocess
import binascii, textwrap
import time

BASE = os.path.dirname(sys.argv[0])+"/"

# Initalization of properties, place file with path in this directory or change
PROPERTIES_FILE_PATH = fline=open(BASE+"properties_path.txt").readline().rstrip()

properties = {}

for line in open(PROPERTIES_FILE_PATH):
    splt = line.strip().split('=')
    if len(splt) == 2:
        properties[splt[0].strip()] = splt[1].strip()

PS_SCRIPT_FOLDER = properties["barcode.postscript"]
TMP_FOLDER = properties["tmp.folder"]
RESULTS_FOLDER = properties["barcode.results"]
PS_BLANK_SCRIPT = BASE+'barcodes/blank.ps'

PRJ = sys.argv[1][1:5]
BASEDIR = os.path.join(RESULTS_FOLDER, PRJ)

pngdir = os.path.join(BASEDIR, "png/")
os.system('mkdir -p ' + pngdir)
tmp = os.path.join(TMP_FOLDER, 'tmp/')
os.system('mkdir -p ' + tmp)


def hexify(string):
	return textwrap.TextWrapper(subsequent_indent=' ', width=72).fill('<' + binascii.hexlify(string) + '>')

def create_barcode(name):
	timestamp = str(time.time()).replace(".","")
	psFile = timestamp+"var.ps"
	pscode = open(tmp + psFile, "w")
	pscode.write("15 15 moveto "+hexify(name)+" "+hexify("includecheck includetext height=1 width=3")+" "+hexify("code128")+" cvn /uk.co.terryburton.bwipp findresource exec\n")
	pscode.write("showpage")
	pscode.close()
	os.system('cat ' + PS_BLANK_SCRIPT + ' ' + tmp + psFile +' > ' + tmp + name + '.ps')
	box = subprocess.check_output("gs -q -dBATCH -dNOPAUSE -sDEVICE=bbox "+tmp+name+".ps 2>&1 | grep -v HiResBoundingBox", shell=True)
	box = box.split()
	height = str(int(box[4])/2)
	clip = "\"0 -"+height+" translate "+box[1]+" "+height+" "+box[3]+" "+box[4]+" rectclip\""
	os.system('gs -o '+tmp+name+'crop.ps -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS='+box[3]+' -dDEVICEHEIGHTPOINTS='+height+' -dFIXEDMEDIA -c '+clip+' -f '+tmp+name+'.ps')
	os.system('gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r500x600 -dGraphicsAlphaBits=4 -o '+tmp+name+'.png -f '+tmp+name+'crop.ps')
	os.system("mv "+tmp+name+".png "+pngdir)
	os.system("rm " + tmp + psFile)


for name in sys.argv[1:]:
	create_barcode(name)