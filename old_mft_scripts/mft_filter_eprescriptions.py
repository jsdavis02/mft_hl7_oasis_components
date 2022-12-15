import argparse
import sys
from datetime import datetime, timedelta
import json

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
args = parser.parse_args(sys.argv[1:])

data = ""
line = sys.stdin.readline()
while line:
    data += line + "\r"
    line = sys.stdin.readline()

jdata = json.loads(data)
if jdata['input'] is None or len(jdata['input']) == 0:
    print('', end='')
    exit(0)

timestamp = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

filelistonserver = jdata['input'].split(',')
filestohunt = [
    'DSH_electronic_prescription_'+timestamp,
    'FQHC_electronic_prescription_'+timestamp
]
filestoget = []

for f in filelistonserver:
    for h in filestohunt:
        if f.startswith(h):
            filestoget.append(f)
out = ''
if len(filestoget) > 0:
    out = ','.join(filestoget)
print(out, end="")

