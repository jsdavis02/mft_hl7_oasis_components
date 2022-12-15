import hl7
import sys
import json
import argparse
from xml.sax.saxutils import escape



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
args = parser.parse_args(sys.argv[1:])


def convert_hl7json_to_xml(msg):
    #print('Converting to hl7')
    jdata = json.loads(msg)
    delim = jdata['MSH.0']['1']
    hdata = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><hl7 xmlns=\"http://www.example.org/HL7Header\">"
    for x, (k, v) in enumerate(jdata.items()):
        hdata += "<" + k[:k.index(".")] + ">"
        for y, (sk, sv) in enumerate(v.items()):
            # print("index:"+str(x)+" key:"+k+" value:"+str(v) + ", index:"+str(y)+" key:"+sk+" value:"+str(sv))
            hdata += "<F-" + sk + ">" + escape(str(sv)) + "</F-" + sk + ">"
        hdata += "</" + k[:k.index(".")] + ">"
    hdata += "</hl7>"
    if args.output is None:
        sys.stdout.write(hdata)
    else:
        with open(args.output, "w") as outf:
            outf.write(hdata)


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

convert_hl7json_to_xml(data)



