import os
import argparse
import sys
import shutil
from datetime import datetime
sys.path.append('..')
from devops import mft_functions

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

# Auto-renames the destination file keeping the existing file intact

datestamp = datetime.today().strftime('%Y%m%d')
count_sql = "select count(*) as count from audit where route_id = "+args.route_id+" and ProcessState = 'mft-fs-send' and datediff(day, created_at, getdate()) = 0"
results = mft_functions.run_selects(count_sql, args.env)

if int(results['results'][0]["count"]) > 25:
    ltr = 'Z_'+str(results['results'][0]["count"])
else:
    ltr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[results['results'][0]["count"]]

for fname in os.listdir(args.input):
    newname = ('MCOEVHMC'+ltr+'.'+datestamp+'.837i')
    shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))

