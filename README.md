# barcode-creation
Scripts to create barcodes for tagging samples

Uses postscript and different python scripts to create RTF sample sheets and QR Code for sample tube stickers. Barcode creation scripts are used by qnavigator and the projectwizard portlets.

# Instructions
Download barcode.ps from the monolithic release of postscriptbarcode:
https://github.com/bwipp/postscriptbarcode/releases/tag/2017-07-10
We recommend to move barcode.ps to /usr/share/postscriptbarcode/ or similar. The path to this script needs to be set in the config file linked in test_path.txt (for the testing config) as well as properties_path.txt (production config) along with a user-defined setup for the following paths:

barcode.postscript = /usr/share/postscriptbarcode/
barcode.results = /Users/<x>/Desktop/barcodes/
tmp.folder = /tmp/
