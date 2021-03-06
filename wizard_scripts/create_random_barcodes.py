import sys
import os
import random

if(len(sys.argv) < 2):
    print "Please provide a number: how many barcodes do you" \
          " want to create?"
    sys.exit(1)


ALPH = "ABCDEFGHIJKLMNOPQRSTUVWX"
NUM = "0123456789"


def create_random_barcode():
    return create_random_info("Q", 5, ALPH) + \
           create_random_info(length=3) + \
           create_random_info(length=2, type=ALPH)


def create_random_info(init_project="", length=0, type=NUM):
    print type
    while len(init_project) < length:
        init_project += random.choice(type)
    return init_project


def main():
    default_sample = "LiverSample"
    default_measurement = "protein"

    arg_list = []

    for i in range(0, int(sys.argv[1])):
        barcode = create_random_barcode()
        arg_list.append(barcode)
        arg_list.append(barcode)
        arg_list.append(default_sample)
        arg_list.append(default_measurement)

    #print("./tube_barcodes.py {0}".format(" ".join(arg_list)))
    #os.system("python2.7 tube_barcodes.py {0}".format(" ".join(arg_list)))

main()


