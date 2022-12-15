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

# Unzip file and rename it with datestamp
datestamp = datetime.today().strftime('%Y%m%d')
unzipped_file = os.path.join(args.input, 'unzipped.txt')
for fname in os.listdir(args.input):
    zipped_file = os.path.join(args.input, fname)
    with gzip.open(zipped_file, 'rb') as zip_in:
        with open(unzipped_file, 'wb') as zip_out:
            shutil.copyfileobj(zip_in, zip_out)

# Create delimited csv file and drop it into the output path
output_cvs = 'UHC_Full_'+datestamp+'.csv'
with open(unzipped_file, 'r') as pipe_txt, open(output_cvs, 'w+', newline='') as csv_file:
    reader_pipe = csv.reader(pipe_txt, delimiter='|')
    writer_delim = csv.writer(csv_file, delimiter=',')
    for row in reader_pipe:
        writer_delim.writerow(row)

shutil.copy(output_cvs, os.path.join(args.output, output_cvs))
os.remove(unzipped_file)
