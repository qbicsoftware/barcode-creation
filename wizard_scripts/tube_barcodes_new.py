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
BASEDIR = pathname + "/" + PRJ
path = pathname + "/barcodes/"

if "/" not in pathname:
    BASEDIR = BASEDIR[1:]
    path = path[1:]
pdfdir = BASEDIR + "/barcodes/pdf"

tmp = path + 'tmp/'
pdf = path + 'pdf/'
eps = path + 'eps/'
os.system('mkdir -p ' + tmp)
os.system('mkdir -p ' + pdf)
os.system('mkdir -p ' + eps)
os.system('mkdir -p ' + pdfdir)


def hexify(string):
    return textwrap.TextWrapper(subsequent_indent=' ', width=72).fill('<' + binascii.hexlify(string) + '>')


# this function attaches variable barcode information to the
# standard "blank" barcode ps-script, so barcodes can be created
def create_barcode(code, name):
    if not name in code:
        code = name + code
    pscode = open(tmp + "var.ps", "w")
    pscode.write("0 0 moveto " + hexify(code) + " " + hexify('') + " " + hexify(
        "microqrcode") + " cvn /uk.co.terryburton.bwipp findresource exec\n")
    pscode.write("showpage")
    pscode.close()
    os.system('cat ' + path + 'barcode.ps ' + tmp + 'var.ps > ' + tmp + name + '.ps')
    box = subprocess.check_output(
        "gs -q -dBATCH -dNOPAUSE -sDEVICE=bbox " + tmp + name + ".ps 2>&1 | grep -v HiResBoundingBox", shell=True)
    box = box.split()
    clip = "\"0 0 translate " + box[1] + " " + box[2] + " " + box[3] + " " + box[4] + " rectclip\""
    os.system(
        'gs -o ' + tmp + name + 'qr.pdf -sDEVICE=pdfwrite -dDEVICEWIDTHPOINTS=' + box[3] + ' -dDEVICEHEIGHTPOINTS=' +
        box[4] + ' -dFIXEDMEDIA -c ' + clip + ' -f ' + tmp + name + '.ps')


def fixInfoString(info):
    return info[:21].replace("_", "\_").replace('#', '\#')


def create_barcodes(codedStrings, qbicCodes, topInfos, bottomInfos):
    for (code, name, topInfo, bottomInfo) in zip(codedStrings, qbicCodes, topInfos, bottomInfos):
        topInfo = fixInfoString(topInfo)
        bottomInfo = fixInfoString(bottomInfo)
        name = name.strip()
        create_barcode(code, name)
        code = fixInfoString(code)
        tex = open(tmp + name + ".tex", "w")
        qr = tmp + name + "qr.pdf"
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
                \multirow{2}{*}{\includegraphics[height=0.62cm, width=0.62cm]{%(qr)s}}	& { \\fontsize{8pt}{0pt} \\ttfamily QICGC001AR} & \multirow{2}{*}{\includegraphics[height=0.62cm, width=0.62cm]{%(qr)s}}  \\\\
                &  {\\vspace{-11pt} \\fontsize{4pt}{0pt} \\ttfamily \scalebox{.8}[1.0]{Liver sample 1}}  &  \\\\
                & {\\vspace{-15pt} \\fontsize{4pt}{0pt} \\ttfamily \scalebox{.8}[1.0]{protein}}&  \\\\
                & { \\vspace{-19pt} \\fontsize{4pt}{0pt} \\ttfamily \scalebox{.8}[1.0]{www.qbic.uni-tuebingen.de}}&\\\\

        \end{tabular}
    \end{table}
\end{document}\n""" % {"qr": qr, "topInfo": topInfo, "bottomInfo": bottomInfo, "name": code})
        tex.close()
        os.system("pdflatex -shell-escape -output-directory=" + tmp + " " + tmp + name + ".tex")
        os.system("mv " + tmp + name + ".pdf " + pdfdir)
    print "done"


codedStrings = []
qbicCodes = []
infosTop = []
infosBottom = []

# reads in parameters from the command line
arglen = len(sys.argv) - 1
if arglen % 4 > 0:
    print "USAGE: python tube_barcodes.py [List of name strings to encode] [List of barcodes] [List of info strings] [List of info strings]\nAll lists must have the same length."
    sys.exit()

print sys.argv
for i in xrange(1, arglen, 4):
    codedStrings.append(sys.argv[i])
    qbicCodes.append(sys.argv[i + 1])
    infosTop.append(sys.argv[i + 2])
    infosBottom.append(sys.argv[i + 3])
create_barcodes(codedStrings, qbicCodes, infosTop, infosBottom)
