# coding: utf8
import os
import sys
import csv
import time
import datetime
import json
from PyRTFloc import *

BASE = os.path.dirname(sys.argv[0])

# Initalization of properties, place file with path in this directory or change
PROPERTIES_FILE_PATH = fline = open(os.path.join(BASE, "properties_path.txt")).readline().rstrip()

GERMAN_TO_RTF = {"Ä": "\\'c4", "Ö": "\\'d6", "Ü": "\\'dc", "ß": "\\'df", "ä": "\\'e4", "ö": "\\'f6", "ü": "\\'fc"}
properties = {}

testmode = sys.argv[-1] == "testmode"
if testmode:
    sys.argv = sys.argv[:-1]  # remove testmode parameter
    PROPERTIES_FILE_PATH = os.path.join(BASE, "test.properties")

for line in open(PROPERTIES_FILE_PATH):
    splt = line.strip().split('=')
    if len(splt) == 2:
        properties[splt[0].strip()] = splt[1].strip()

RESULTS_FOLDER = properties["barcode.results"]

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('_%Y%b%d')


def replace_all_in_dictionary(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


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


with open(sys.argv[1], 'r') as f:
    obj = byteify(json.loads(f.read()))

projectCode = obj["project_code"]
projectName = obj["project_name"]
investigator = obj["investigator"]
contact = obj["contact"]

# inv.put("first", investigator.getFirstName());
# inv.put("last", investigator.getLastName());
# inv.put("phone", investigator.getPhone());
firstCol = obj["cols"][0]
secondCol = obj["cols"][1]

# PRJ = sys.argv[3][1:5]
# firstCol = sys.argv[1]
# secondCol = sys.argv[2]

BASEDIR = os.path.join(RESULTS_FOLDER, projectCode)
pngdir = os.path.join(BASEDIR, "png/")

sheet_path = BASEDIR + "/documents/sample_sheets"
outfile = sheet_path + "/sample_sheet_" + projectCode + st

os.system('mkdir -p ' + sheet_path)


def getPersonLine(personObject):
    # person has a title
    person = ""
    if len(personObject["title"]) > 2:
        person = personObject["title"] + " "
    person = person + personObject["first_name"] + " " + personObject["last_name"] + ", " + personObject[
        "group"] + " - Tel: " + personObject["phone"] + " " + personObject["email"]

    person = replace_all_in_dictionary(person, GERMAN_TO_RTF)
    return person


def getPersonTitleAndName(personObject):
    full_name = ""
    if "title" in personObject:
        if len(personObject["title"]) > 2:
            full_name = personObject["title"] + " "
        full_name = full_name + personObject["first_name"] + " " + personObject["last_name"]
        full_name = replace_all_in_dictionary(full_name, GERMAN_TO_RTF)

    return full_name


def getPersonValue(personObject, value):
    if value in personObject:
        val = personObject[value]
        if val is None:
            return ""
        val = replace_all_in_dictionary(val, GERMAN_TO_RTF)
        return val
    else:
        return ""


def MakeDoc():
    doc = Document()
    ss = doc.StyleSheet
    section = Section()
    doc.Sections.append(section)

    #	text can be added directly to the section
    #	a paragraph object is create as needed

    qbic = Image(os.path.join(BASE, 'qbic_banner.png'), width=500)
    banner = Paragraph(qbic)
    section.append(banner)

    ################################################################
    pi_contact_table = Table(TabPS.DEFAULT_WIDTH * 7, TabPS.DEFAULT_WIDTH * 7)

    empty_line = TEXT(" \line ")

    # PI
    pi_paragraph = Paragraph()
    pi_header = "Principal Investigator:"
    pi_header_bold = B(pi_header)
    pi_title_name = getPersonTitleAndName(investigator)
    pi_group = getPersonValue(investigator, "group")
    pi_street = getPersonValue(investigator, "street")
    pi_city = getPersonValue(investigator, "city")
    pi_zip_code = getPersonValue(investigator, "zip_code")
    pi_phone = getPersonValue(investigator, "phone")
    pi_email = getPersonValue(investigator, "email")

    pi_text = TEXT(pi_title_name + " \line " + " \line "
                   + pi_group + " \line "
                   + pi_street + " \line "
                   + pi_zip_code + " " + pi_city + " \line " + " \line "
                   + pi_phone + " \line "
                   + pi_email)
    pi_paragraph.append(pi_header_bold, empty_line, pi_text)

    pi_cell = Cell(pi_paragraph)

    # Contact/PM
    contact_paragraph = Paragraph()
    contact_header = "QBiC contact:"
    contact_header_bold = B(contact_header)
    contact_title_name = getPersonTitleAndName(contact)
    contact_group = getPersonValue(contact, "group")
    contact_street = getPersonValue(contact, "street")
    contact_city = getPersonValue(contact, "city")
    contact_zip_code = getPersonValue(contact, "zip_code")
    contact_phone = getPersonValue(contact, "phone")
    contact_email = getPersonValue(contact, "email")

    contact_text = TEXT(contact_group + " \line "
                                     + contact_street + " \line "
                                     + contact_zip_code + " " + contact_city + " \line " + " \line "
                                     + contact_phone + " \line "
                                     + contact_email)

    contact_paragraph.append(contact_header_bold, empty_line, contact_title_name, empty_line, empty_line, contact_text)

    contact_cell = Cell(contact_paragraph)

    pi_contact_table.AddRow(pi_cell, contact_cell)
    section.append(pi_contact_table)

    ################################################################

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%d %b, %Y')

    headline = 'Sample Sheet for QBiC Project: ' + projectCode + " - "
    if projectName:
        headline += projectName + " - " + st
    else:
        headline + st
    headline_bold = B(headline)
    headline_paragraph = Paragraph()
    headline_paragraph.append(headline_bold)

    # separate the header from the table
    line_paragraph = Paragraph()
    separator_line = "---------------------------------------------------------------------------------------------------------------------------------"
    line_paragraph.append(separator_line)
    section.append(line_paragraph)
    section.append(headline_paragraph)
    section.append(line_paragraph)

    thin_edge = BorderPS(width=20, style=BorderPS.DOUBLE)
    thin_frame = FramePS(thin_edge, thin_edge, thin_edge, thin_edge)
    no_edge = BorderPS(width=1, style=BorderPS.HAIRLINE)
    no_frame = FramePS(thin_edge, no_edge, no_edge, no_edge)
    TabPS.DEFAULT_WIDTH = 400

    table = Table(TabPS.DEFAULT_WIDTH * 8, TabPS.DEFAULT_WIDTH * 5, TabPS.DEFAULT_WIDTH * 5, TabPS.DEFAULT_WIDTH * 6)
    c1 = Cell(Paragraph('Barcode'), thin_frame)
    c2 = Cell(Paragraph(firstCol), thin_frame)
    c3 = Cell(Paragraph(secondCol), thin_frame)
    c4 = Cell(Paragraph('Notes'), thin_frame)
    table.AddRow(c1, c2, c3, c4)
    # table.AddRow(c2,c3,c4)
    i = -1
    section.append(table)
    table = Table(TabPS.DEFAULT_WIDTH * 8, TabPS.DEFAULT_WIDTH * 5, TabPS.DEFAULT_WIDTH * 5, TabPS.DEFAULT_WIDTH * 6)
    for name in sample_name:
        i += 1
        image = Image(os.path.join(pngdir, name + '.png'), width=2 * 72)
        c1 = Cell(Paragraph(empty_line, image, empty_line), thin_frame)
        c2 = Cell(Paragraph(description[i]), thin_frame)
        c3 = Cell(Paragraph(derived[i]), thin_frame)
        c4 = Cell(Paragraph(str("")), thin_frame)
        table.AddRow(c1, c2, c3, c4)
    section.append(table)
    return doc


def OpenFile(name):
    return file('%s.rtf' % name, 'w')


sample_name = []
description = []
derived = []

for sample in obj["samples"]:
    sample_name.append(sample["code"])
    description.append(sample["info"])
    derived.append(sample["alt_info"])

DR = Renderer()

doc1 = MakeDoc()

DR.Write(doc1, OpenFile(outfile))

os.system("mv " + outfile + ".rtf " + outfile + ".doc")

print("\nDone. Sample sheet created in: " + outfile + "\n")
