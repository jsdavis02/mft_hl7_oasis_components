import os
import argparse
import sys
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

for fname in os.listdir(args.input):
    if 'PIM_EXP_CHC_Peds_0003' in fname or 'PIM_EXP_CHC_Peds_0004' in fname:
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, fname))

