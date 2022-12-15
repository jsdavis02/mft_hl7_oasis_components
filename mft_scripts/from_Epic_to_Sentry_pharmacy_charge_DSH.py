import os
import argparse
import sys
import shutil
from datetime import datetime
from time import sleep
import re

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

# This is required for the files meant to be transferred to Sentry
# Loop through all files in source fs and prepend timestamp with a 5 second delay between files
timestamp = datetime.today().strftime('%Y%m%d%H%M%S')

for fname in os.listdir(args.input):
    newname = 'DSH_'+timestamp+'_Pharmacy_Charge.csv'
    shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
    sleep(5)

