import argparse
import sys
from datetime import datetime
import json

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
# parser.add_argument("-i", "--input", dest="input", help="input file")

args = parser.parse_args(sys.argv[1:])
# changing from file list as an argument to json on std in
# if args.input is None or len(args.input) == 0:
#     print('', end='')
#     exit(0)

data = ""
line = sys.stdin.readline()
while line:
    data += line + "\r"
    line = sys.stdin.readline()

jdata = json.loads(data)
if jdata['input'] is None or len(jdata['input']) == 0:
    print('', end='')
    exit(0)

timestamp = datetime.today().strftime('%Y%m%d')

filelistonserver = jdata['input'].split(',')
filestohunt = [
    'Gen POM Incoming.err',
    'Gen POM Incoming.txt'
]
filestoget = []

for f in filelistonserver:
    if f in filestohunt:
        filestoget.append(f)

out = ''
if len(filestoget) > 0:
    out = ','.join(filestoget)
print(out, end="")
