import argparse
import os
import sys
import csv
import gzip
from datetime import datetime
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

datestamp = datetime.today().strftime('%Y%m%d')

# Unzip file and rename

for fname in os.listdir(args.input):
    if 'CLM' in fname:
        unzipped_file = os.path.join(args.output, 'UHC_CLM_'+datestamp+'.txt')
    elif 'MEM' in fname:
        unzipped_file = os.path.join(args.output, 'UHC_MEM_'+datestamp+'.txt')
    zipped_file = os.path.join(args.input, fname)
    with gzip.open(zipped_file, 'rb') as zip_in:
        with open(unzipped_file, 'wb') as zip_out:
            shutil.copyfileobj(zip_in, zip_out)

