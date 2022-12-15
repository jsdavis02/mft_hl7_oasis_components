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

# this code chokes if the surname has a hyphen
for fname in os.listdir(args.input):
    fp = os.path.join(args.input, fname)
    f1name = fname.split('-')[6]
    print(f1name)
    f2name = str(f1name).split('.')
    print(f2name)
    newname = str(f2name[0])+'.'+str(f2name[1])
    print(newname)
    shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
