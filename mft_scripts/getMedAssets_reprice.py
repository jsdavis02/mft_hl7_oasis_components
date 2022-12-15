import argparse
import os
import sys
import shutil
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

timestamp = datetime.today().strftime('%y%m%d')

for fname in os.listdir(args.input):
    newname = ''
    if fname.startswith('AR'+timestamp+'RA'):
        newname = 'reprice.txt'
    elif fname.startswith('AR'+timestamp+'RB'):
        newname = 'repriceB.txt'
    elif fname.startswith('AR'+timestamp+'RC'):
        newname = 'repriceC.txt'
    else:
        newname = fname

    shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
