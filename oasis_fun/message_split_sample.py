import json
import argparse
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="target environment")
parser.add_argument("-s", "--bwi", dest="bwi", help="source bw ident value")
parser.add_argument("-g", "--guid", dest="guid", help="message guid")
parser.add_argument("-i", "--input", dest="input", help="full path to json input file")
parser.add_argument("-o", "--output", dest="output", help="full path to json output file")
args = parser.parse_args()

# Read json file and load it in as a python dict
if args.input is None:
    json_in = json.load(sys.stdin)
else:
    with open(args.input, 'r') as fp:
        json_in = json.load(fp)

# just duplicate message and write it out for sample testing
# output path will be
# [base folder ex: /opt/oasis_data/message_splitting]/bw-ident/[message type ex: ADT_A08]/guid.x.json
split_count = 2
c = 0
# we know MSH is first segment so
msgtype = json_in['MSH.0']['9'].split('^')
msgpath = msgtype[0]+'_'+msgtype[1]
# we get the splitter ident from BW in the param
# that second stage routes will consider the producing endpoint
bpath = os.path.join(args.output, args.bwi, msgpath)
# make dirs that are missing
if not os.path.exists(bpath):
    os.makedirs(bpath)
while c < split_count:
    fsplitp = os.path.join(bpath, args.guid+'.'+str(c+1)+'.json')
    with open(fsplitp, "w") as out:
        json.dump(json_in, out)
    c += 1

# Write output file with updated json
# if args.output is None:
 #   sys.stdout.write(json.dumps(json_in))
#else:
 #   with open(args.output, "w") as out:
 #       json.dump(json_in, out)