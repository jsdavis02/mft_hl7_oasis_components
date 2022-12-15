import os
import argparse
import sys
import pyminizip
import get_route_props

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])
route_props = get_route_props.get_route_props(args.env, args.route_id)

if not os.path.exists(args.output):
    os.makedirs(args.output)

zip_pass = None
for prop in route_props:
    if prop['name'] == 'zip_password':
        zip_pass = prop['value']

for fname in os.listdir(args.input):
    pyminizip.compress(os.path.join(args.input, fname), '', os.path.join(args.output, os.path.splitext(os.path.basename(fname))[0]+'.zip'), zip_pass, 5)


