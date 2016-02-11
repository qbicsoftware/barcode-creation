import os
import sys
import subprocess
import binascii, textwrap

pathname = os.path.dirname(sys.argv[0])

PRJ = sys.argv[1][1:5]
bcpath = pathname+"/barcodes/"
tmp = bcpath+'tmp/'
BASEDIR=pathname+"/"+PRJ
png_path=BASEDIR+"/barcodes/png"
os.system('mkdir -p '+png_path)

def hexify(string):
	return textwrap.TextWrapper(subsequent_indent=' ', width=72).fill('<' + binascii.hexlify(string) + '>')

def create_barcode(name):
	pscode = open(tmp+"var.ps","w")
	pscode.write("15 15 moveto "+hexify(name)+" "+hexify("includecheck includetext height=1 width=3")+" "+hexify("code128")+" cvn /uk.co.terryburton.bwipp findresource exec\n")
	pscode.write("showpage")
	pscode.close()
	os.system('cat '+bcpath+'blank.ps '+tmp+'var.ps > '+tmp+name+'.ps')
	box = subprocess.check_output("gs -q -dBATCH -dNOPAUSE -sDEVICE=bbox "+tmp+name+".ps 2>&1 | grep -v HiResBoundingBox", shell=True)
	box = box.split()
	height = str(int(box[4])/2)
	clip = "\"0 -"+height+" translate "+box[1]+" "+height+" "+box[3]+" "+box[4]+" rectclip\""
	os.system('gs -o '+tmp+name+'crop.ps -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS='+box[3]+' -dDEVICEHEIGHTPOINTS='+height+' -dFIXEDMEDIA -c '+clip+' -f '+tmp+name+'.ps')
	os.system('gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r500x600 -dGraphicsAlphaBits=4 -o '+tmp+name+'.png -f '+tmp+name+'crop.ps')
	os.system("mv "+tmp+name+".png "+png_path)

for name in sys.argv[1:]:
	create_barcode(name)