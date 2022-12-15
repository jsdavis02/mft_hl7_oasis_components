import os
import sys
import json
import shutil

data = ""
line = sys.stdin.readline()
while line:
    data += line + "\r"
    line = sys.stdin.readline()

jdata = json.loads(data)
if not os.path.exists(jdata['output']):
    os.makedirs(jdata['output'])
if 'rename' in jdata.keys() and jdata['rename'] != os.path.basename(jdata['input']):
    shutil.copy(os.path.join(jdata['input']), os.path.join(jdata['output'], os.path.basename(jdata['rename'])))
else:
    shutil.copy(os.path.join(jdata['input']), os.path.join(jdata['output'], os.path.basename(jdata['input'])))

