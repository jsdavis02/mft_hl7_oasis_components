import json
import argparse
import sys
sys.path.append('..')
from oasis_fun import update_pid_3_txa_12
from oasis_fun import update_nte_3
from oasis_fun import delete_pid_18
from oasis_fun import delete_txa_13
from oasis_fun import update_pv1_19

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="target environment")
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

# Call function that pads PID3.1 value with leading "000"
# and pads TXA12.3 value with a leading "C"
json_in = update_pid_3_txa_12.update_pid_3_txa_12(json_in)

# Call function that adds segment NTE 3 and inserts value from TXA 13
json_in = update_nte_3.update_nte_3(json_in)

# Call function that updates PV1
json_in = update_pv1_19.update_pv1_19(json_in)

# Call function that deletes PID 18
json_in = delete_pid_18.delete_pid_18(json_in)

# Call function that deletes TXA 13
json_in = delete_txa_13.delete_txa_13(json_in)

# Write output file with updated json
if args.output is None:
    sys.stdout.write(json.dumps(json_in))
else:
    with open(args.output, "w") as out:
        json.dump(json_in, out)
