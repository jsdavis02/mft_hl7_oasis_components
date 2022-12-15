import argparse
import sys
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

filelistonserver = jdata['input'].split(',')
filestohunt = [
    '0007',
    '0006'
]
filestoget = []

for f in filelistonserver:
    for h in filestohunt:
        if h in f:
            filestoget.append(f)

out = ''
if len(filestoget) > 0:
    out = ','.join(filestoget)
print(out, end="")
