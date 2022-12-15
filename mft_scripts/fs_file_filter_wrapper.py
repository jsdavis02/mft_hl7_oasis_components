import sys
import argparse
import json
sys.path.append('..')
from mft_scripts import mft_file_filters

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-fn", "--filter_name", nargs='?', dest="filter_name", help="filter name to run", default='all_files')
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

# bw fs gives us json input as comma list of files split to list
filelistonserver = jdata['input'].split(',')
#make input for filter functions to match sftp and smb calls
jin = []
for f in filelistonserver:
    jin.append({
        "filename": f,
        "last_access_time": "",
        "last_write_time": "",
        "file_size": ""
    })
flist = getattr(mft_file_filters, args.filter_name)(jin)
o = []
for fl in flist:
    o.append(fl["filename"])
out = ''
if len(o) > 0:
    out = ','.join(o)
print(out, end="")
