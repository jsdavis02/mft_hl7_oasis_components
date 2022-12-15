import json
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
args = parser.parse_args(sys.argv[1:])

def convert_to_string(msg):
    print('Escaping json to string')
    j = json.dumps(msg);
    if args.output is None:
        sys.stdout.write(j)
    else:
        with open(args.output, "w") as outf:
            outf.write(j)

def convert_to_json(msg):
    print('Unescaping string to json')
    j = json.loads(msg)
    if args.output is None:
        sys.stdout.write(j)
    else:
        with open(args.output, "w") as outf:
            outf.write(j)

data = ""
if args.input is None:
    line = sys.stdin.readline()
    while line:
        data += line + "\r"
        line = sys.stdin.readline()
else:
    with open(args.input) as fp:
        line = fp.readline()
        while line:
            data += line + "\r"
            line = fp.readline()
if data.startswith("{"):
    convert_to_string(data)
else:
    convert_to_json(data)