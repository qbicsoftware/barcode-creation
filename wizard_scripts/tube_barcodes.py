# creates *.eps and *pdf barcodes from input file sample_ids.tsv
# the .eps files include the sample IDs+checksum and the actual barcode
# the .pdf files include the "QBIC Dr.Sven Nahnsen etc" and 
# are ready to print with the label printer: 26x18mm

# USAGE python tube_barcodes.py [sampleID] [tissue/technology] [name/comment]

import sys
import os
import csv
import math
import subprocess
import binascii, textwrap

pathname = os.path.dirname(sys.argv[0])
PRJ = sys.argv[2][1:5]
BASEDIR = pathname+"/"+PRJ
path = pathname+"/barcodes/"

if "/" not in pathname:
	BASEDIR = BASEDIR[1:]
	path = path[1:]
pdfdir = BASEDIR+"/barcodes/pdf"

tmp = path+'tmp/'
pdf = path+'pdf/'
eps = path+'eps/'
os.system('mkdir -p '+tmp)
os.system('mkdir -p '+pdf)
os.system('mkdir -p '+eps)
os.system('mkdir -p '+pdfdir)

def hexify(string):
	return textwrap.TextWrapper(subsequent_indent=' ', width=72).fill('<' + binascii.hexlify(string) + '>')

# this function attaches variable barcode information to the
# standard "blank" barcode ps-script, so barcodes can be created
def create_barcode(code, name):
	if not name in code:
		code = name + code
	pscode = open(tmp+"var.ps","w")
	pscode.write("0 0 moveto "+hexify(code)+" "+hexify('')+" "+hexify("qrcode")+" cvn /uk.co.terryburton.bwipp findresource exec\n")
	pscode.write("showpage")
	pscode.close()
	os.system('cat '+path+'barcode.ps '+tmp+'var.ps > '+tmp+name+'.ps')
	box = subprocess.check_output("gs -q -dBATCH -dNOPAUSE -sDEVICE=bbox "+tmp+name+".ps 2>&1 | grep -v HiResBoundingBox", shell=True)
	box = box.split()
	clip = "\"0 0 translate "+box[1]+" "+box[2]+" "+box[3]+" "+box[4]+" rectclip\""
	os.system('gs -o '+tmp+name+'qr.pdf -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS='+box[3]+' -dDEVICEHEIGHTPOINTS='+box[4]+' -dFIXEDMEDIA -c '+clip+' -f '+tmp+name+'.ps')

def fixInfoString(info):
	return info[:21].replace("_","\_").replace('#','\#')

def create_barcodes(codedStrings, qbicCodes, topInfos, bottomInfos):
	for (code, name, topInfo, bottomInfo) in zip(codedStrings, qbicCodes, topInfos, bottomInfos):
		topInfo = fixInfoString(topInfo)
		bottomInfo = fixInfoString(bottomInfo)
		name = name.strip()
		create_barcode(code, name)
		code = fixInfoString(code)
		tex = open(tmp+name+".tex","w")
		qr = tmp+name+"qr.pdf"
		tex.write('''\documentclass[a4paper]{article}
\usepackage{graphicx}
 \usepackage[paperwidth=39mm,paperheight=9.8mm]{geometry}
 \\begin{document}
 \hoffset=-5.0mm
\\thispagestyle{empty} 
 \\begin{table} [ht] 
  \\begin{tabular}{l}
	  \\begin{minipage}[t]{40mm}  
	  \\begin{center} 
	  \\begingroup
		\\renewcommand*\\rmdefault{arial}
		\\ttfamily
		    \\fontsize{8pt}{11pt}\selectfont
		\\vskip -0.36cm
               \\hskip -0.12cm
		    %(name)s
	   \endgroup
	   \end{center} 
	\\vskip -0.35cm
	 \\begin{tabular}{p{9mm}p{17mm}p{9mm}}
	\\hskip -0.1cm
		\includegraphics[width=.62cm, height=.62cm]{%(qr)s} & 
	 
			  \\begingroup
				\\renewcommand*\\rmdefault{arial}
				\\ttfamily
				    \\fontsize{5pt}{8pt}\selectfont
				\\vskip -0.65cm
				 \\hskip -0.7cm
				 \\begin{minipage}[t]{1.4cm}  
				   \\mbox{%(topInfo)s}
				\\vskip -0.12cm \\mbox{%(bottomInfo)s}
				 \end{minipage}
	   		  \endgroup   
	               \\begingroup
				\\renewcommand*\\rmdefault{arial}
				\\ttfamily
				    \\fontsize{4pt}{6pt}\selectfont
				\\vskip -0.06cm
				 \\hskip -0.7cm
				 \\begin{minipage}[t]{1cm}  
				   \\vskip -0.05cm \\mbox{QBiC: +4970712972163} 
				 \end{minipage}
			  \endgroup   &
\\hskip -0.8cm
	 \includegraphics[width=.62cm, height=.62cm]{%(qr)s} 
	    \end{tabular}
 
        \end{minipage}
 \end{tabular}
 \end{table}
\end{document}\n''' %{"qr" : qr, "topInfo" : topInfo, "bottomInfo" : bottomInfo, "name" : code})
		tex.close()
		os.system("pdflatex -shell-escape -output-directory="+tmp+" "+tmp+name+".tex")
		os.system("mv "+tmp+name+".pdf " +pdfdir)
	print "done"

codedStrings = []
qbicCodes = []
infosTop = []
infosBottom = []

# reads in parameters from the command line
arglen = len(sys.argv)-1
if arglen%4 > 0:
	print "USAGE: python tube_barcodes.py [List of name strings to encode] [List of barcodes] [List of info strings] [List of info strings]\nAll lists must have the same length."
	sys.exit()

print sys.argv
for i in xrange(1,arglen,4):
	codedStrings.append(sys.argv[i])
	qbicCodes.append(sys.argv[i+1])
	infosTop.append(sys.argv[i+2])
	infosBottom.append(sys.argv[i+3])
create_barcodes(codedStrings, qbicCodes, infosTop, infosBottom)
