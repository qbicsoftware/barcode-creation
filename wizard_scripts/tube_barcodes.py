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

PRJ = sys.argv[1][5:10] #mind the file name prefix
BASEDIR = os.path.join(RESULTS_FOLDER, PRJ)

pdfdir = os.path.join(BASEDIR, "pdf/")
os.system('mkdir -p ' + pdfdir)
tmp = os.path.join(TMP_FOLDER, 'tmp/')
os.system('mkdir -p ' + tmp)

def hexify(string):
    return textwrap.TextWrapper(subsequent_indent=' ', width=72).fill('<' + binascii.hexlify(string) + '>')


# this function attaches variable barcode information to the
# standard "blank" barcode ps-script, so barcodes can be created
def create_barcode(name):
    code = name[5:]#mind the file name prefix
    timestamp = str(time.time()).replace(".","")
    psFile = timestamp+"var.ps"
    pscode = open(tmp + psFile, "w")
    pscode.write("0 0 moveto " + hexify(code) + " " + hexify('') + " " + hexify(
        "microqrcode") + " cvn /uk.co.terryburton.bwipp findresource exec\n")
    pscode.write("showpage")
    pscode.close()
    os.system('cat ' + PS_SCRIPT_FOLDER + 'barcode.ps ' + tmp + psFile +' > ' + tmp + name + '.ps')
    box = subprocess.check_output(
        "gs -q -dBATCH -dNOPAUSE -sDEVICE=bbox " + tmp + name + ".ps 2>&1 | grep -v HiResBoundingBox", shell=True)
    box = box.split()
    clip = "\"0 0 translate " + box[1] + " " + box[2] + " " + box[3] + " " + box[4] + " rectclip\""
    os.system(
        'gs -o ' + tmp + name + 'qr.pdf -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS=' + box[3] + ' -dDEVICEHEIGHTPOINTS=' +
        box[4] + ' -dFIXEDMEDIA -c ' + clip + ' -f ' + tmp + name + '.ps')

    os.system("rm " + tmp + psFile)

def fixInfoString(info):
    info = info[:21]
    return escapeTexSymbols(info)

def escapeTexSymbols(string):
    return string.replace("_", "\_").replace('#', '\#').replace('&','\&')

def fixIDString(id):
    id = id[:15]
    return escapeTexSymbols(id)

def create_barcodes(fileNames, IDInfos, topInfos, bottomInfos):
    for (fileName, id, topInfo, bottomInfo) in zip(fileNames, IDInfos, topInfos, bottomInfos):
        topInfo = fixInfoString(topInfo)
        bottomInfo = fixInfoString(bottomInfo)
        fileName = fileName.strip()
        create_barcode(fileName)
        id = fixIDString(id)
        tex = open(tmp + fileName + ".tex", "w")
        qr = tmp + fileName + "qr.pdf"
        tex.write("""\documentclass[a4paper]{article}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage[paperwidth=40mm,paperheight=10mm]{geometry}
\usepackage{multirow}
\geometry{
    top=1.5mm,
    left=-2mm,
    right=-2mm
    }
\\renewcommand{\\baselinestretch}{0.8}
\\begin{document}
    \\newcolumntype{L}[1]{>{\\raggedright\\arraybackslash}p{#1}}
    \\thispagestyle{empty}

    \\begin{table}
        \setlength\\tabcolsep{1pt}
        \centering
        \\begin{tabular}{cL{2.2cm}c}
                \multirow{2}{*}{\includegraphics[height=0.62cm, width=0.62cm]{%(qr)s}}	& { \\fontsize{8pt}{0pt}
                \\ttfamily %(name)s} & \multirow{2}{*}{\includegraphics[height=0.62cm, width=0.62cm]{%(qr)s}}  \\\\
                &  {\\vspace{-11pt} \\fontsize{4pt}{0pt} \\ttfamily \scalebox{.8}[1.0]{%(topInfo)s}}  &  \\\\
                & {\\vspace{-15pt} \\fontsize{4pt}{0pt} \\ttfamily \scalebox{.8}[1.0]{%(bottomInfo)s}}&  \\\\
                & { \\vspace{-19pt} \\fontsize{4pt}{0pt} \\ttfamily \scalebox{.8}[1.0]{www.qbic.life}}&\\\\

        \end{tabular}
    \end{table}
\end{document}\n""" % {"qr": qr, "topInfo": topInfo, "bottomInfo": bottomInfo, "name": id})
        tex.close()
        os.system("pdflatex -shell-escape -output-directory=" + tmp + " " + tmp + fileName + ".tex")
        os.system("mv " + tmp + fileName + ".pdf " + pdfdir)
        os.system("rm " + tmp + fileName + "*")

    print ("done")

fileNames = []
IDInfos = []
infosTop = []
infosBottom = []

# reads in parameters from the command line
arglen = len(sys.argv) - 1
if arglen % 4 > 0:
    print ("USAGE: python tube_barcodes.py [List of name strings to encode] [List of barcodes] [List of info strings] [List of info strings]\nAll lists must have the same length.")
    sys.exit()

print (sys.argv)
for i in xrange(1, arglen, 4):
    fileNames.append(sys.argv[i])
    IDInfos.append(sys.argv[i + 1])
    infosTop.append(sys.argv[i + 2])
    infosBottom.append(sys.argv[i + 3])
create_barcodes(fileNames, IDInfos, infosTop, infosBottom)
