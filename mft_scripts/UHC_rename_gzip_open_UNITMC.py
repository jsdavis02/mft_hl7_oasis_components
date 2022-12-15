import argparse
import os
import sys
import gzip
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

# Unzip file and rename

for fname in os.listdir(args.input):
    split_fname = str(fname).split('.')
    if 'CLM' in fname:
        clm_file = split_fname[0]+'.'+split_fname[1]
        unzipped_file = os.path.join(args.output, clm_file)
    elif 'MEM' in fname:
        mem_file = split_fname[0]+'.'+split_fname[1]
        unzipped_file = os.path.join(args.output, mem_file)
    zipped_file = os.path.join(args.input, fname)
    with gzip.open(zipped_file, 'rb') as zip_in:
        with open(unzipped_file, 'wb') as zip_out:
            shutil.copyfileobj(zip_in, zip_out)

