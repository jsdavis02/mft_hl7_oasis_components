import json
import argparse
import sys
sys.path.append('..')
import os
from copy import deepcopy
from oasis_fun import split_endo_msgs
from oasis_fun import update_pid_endo
from oasis_fun import truncate_pid_endo
from oasis_fun import truncate_pv1_2_endo
from oasis_fun import update_txa_2_endo
from oasis_fun import update_txa_12_endo
from oasis_fun import update_obr_3_endo
from oasis_fun import update_ctrlnum_endo

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="target environment")
parser.add_argument("-s", "--bwi", dest="bwi", help="source bw ident value")
parser.add_argument("-g", "--guid", dest="guid", help="message guid")
parser.add_argument("-i", "--input", dest="input", help="full path to json input file")
parser.add_argument("-o", "--output", dest="output", help="full path to json output file")
parser.add_argument("-r", "--route", dest="route", help="route id")
args = parser.parse_args()

# Read json file and load it in as a python dict
if args.input is None:
    json_in = json.load(sys.stdin)
else:
    with open(args.input, 'r') as fp:
        json_in = json.load(fp)

# Create two copies of the json to work on separately
rtf_json = deepcopy(json_in)
pdf_json = deepcopy(json_in)

# Call function that cleans the json dictionaries for separate processing
split_endo_msgs.split_endo_msgs(pdf_json, rtf_json)

# Call function that updates the PID 2 value
update_pid_endo.update_pid_endo(pdf_json, rtf_json)

# Call function that truncates PID segment to 13 fields
truncate_pid_endo.truncate_pid_endo(pdf_json, rtf_json)

# Call function that truncates PV1 2 to one character
truncate_pv1_2_endo.truncate_pv1_2_endo(rtf_json, pdf_json)

# Call function that updates TXA 2, document type
update_txa_2_endo.update_txa_2_endo(rtf_json, pdf_json)

# Call function that updates TXA 12, Universal ID
update_txa_12_endo.update_txa_12_endo(rtf_json, pdf_json)

# Call function that updates OBR 3, filler order number
update_obr_3_endo.update_obr_3_endo(rtf_json, pdf_json)

# Call function that updates the MSH control number
update_ctrlnum_endo.update_ctrlnum_endo(rtf_json, pdf_json)

# Write output file with updated jsons
if args.output is None:
    sys.stdout.write(json.dumps(rtf_json))
    sys.stdout.write(json.dumps(pdf_json))
else:
    jsons = (rtf_json, pdf_json)
    fcount = 1
    for j in jsons:
        msgtype = j['MSH.0']['9'].split('^')
        msgpath = msgtype[0]+'_'+msgtype[1]
        bpath = os.path.join(args.output, args.bwi, msgpath)
        print(bpath)
        if not os.path.exists(bpath):
            os.makedirs(bpath)
        else:
            fsplitp = os.path.join(bpath, args.guid+'.'+str(fcount+1)+'.json')
            print(fsplitp)
            with open(fsplitp, "w") as out:
                json.dump(j, out)
            fcount += 1