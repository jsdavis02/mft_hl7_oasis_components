import hl7
import sys
import json
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
args = parser.parse_args(sys.argv[1:])


def convert_to_hl7(msg):
    #print('Converting to hl7')
    jdata = json.loads(msg)
    delim = jdata['MSH.0']['1']
    hdata = ""
    for x, (k, v) in enumerate(jdata.items()):
        hdata += k[:k.index(".")] + delim
        for y, (sk, sv) in enumerate(v.items()):
            # print("index:"+str(x)+" key:"+k+" value:"+str(v) + ", index:"+str(y)+" key:"+sk+" value:"+str(sv))
            hdata += str(sv) + delim
            if x == 0 and sk == '1':  # don't add when MSH 1 cause that is pipe and it shifts fields
                hdata = hdata[:-2]
        hdata = hdata[:-1]  #remove trailing delim
        hdata += "\r" #add CR for segment line
    if args.output is None:
        sys.stdout.write(hdata)
    else:
        with open(args.output, "w") as outf:
            outf.write(hdata)


def convert_to_json(msg):
    #print('Converting to json')
    h = hl7.parse(msg)

    #h[0][2] = str(h[0][2]).replace("\\", "\\\\")
    j = "{"
    i = 0;
    while i < len(h):
        x = 1
        j += "\"" +str(h[i][0]) + "." + str(i).strip() + "\": {"
        while x < len(h[i]):
            #print('Field Value: '+ str(h[i][x]).strip().replace('\"', '\"'))
            #print('Field Value json convert: ' + json.dumps(str(h[i][x]).strip()))
            j += "\"" +str(x) + "\": " + json.dumps(str(h[i][x]).strip()) + ","
            x = x+1
        j = j[0:-1]
        j += "},"
        i += 1;
    j = j[0:-1]
    j += "}"
    #escape all \ in data -- probably others I should do
    #j = j.replace("\\", "\\\\")
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

if hl7.ishl7(data):
    convert_to_json(data)
else:
    convert_to_hl7(data)



