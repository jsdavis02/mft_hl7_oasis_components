import argparse
import os
import sys
import shutil
import datetime
import time

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

# Append the first and last day of the previous month

today = time.localtime()
last = datetime.date(today.tm_year, today.tm_mon, 1) - datetime.timedelta(1)
first = last.replace(day=1)

last_day = last.strftime('%Y%m%d')
first_day = first.strftime('%Y%m%d')

for fname in os.listdir(args.input):
    split_name = fname.split('.')
    newname = str(split_name[0])+first_day+"_"+last_day+"."+str(split_name[1])
    shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
