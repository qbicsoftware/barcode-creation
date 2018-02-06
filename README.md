# barcode-creation
Scripts to create barcodes for tagging samples

Uses postscript and different python scripts to create RTF sample sheets and QR Code for sample tube stickers. Barcode creation scripts are used by qnavigator and the projectwizard portlets.

# Instructions
Download barcode.ps from the monolithic release of postscriptbarcode:

https://github.com/bwipp/postscriptbarcode/releases/tag/2017-07-10

We recommend to move barcode.ps to /usr/share/postscriptbarcode/ or similar.

## Production Config

To run barcode creation from a portal instance, we recommend to put these config settings in the same file qPortal uses for other config parameters (see our qPortal Howto):
barcode.postscript = /usr/share/postscriptbarcode/

barcode.results = [path where resulting barcode files should end up]

tmp.folder = [path to folder to write intermediate files used to create pdfs and pngs]

You should link to this config file path in properties_path.txt and place it in wizard_scripts

## Testing Config

To test locally, put the same configuration parameters in a file test.properties and place it in wizard_scripts