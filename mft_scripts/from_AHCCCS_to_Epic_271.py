import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

newname = ''
tmp_file = ''

for f in os.listdir(args.input):
    fname = os.path.join(args.input, f)
    with open(fname, 'r') as f_in, open(os.path.join(args.output, f), 'w+') as f_out:
        for line in f_in.readlines():
            f_out.write(line.replace('{', '*'))

