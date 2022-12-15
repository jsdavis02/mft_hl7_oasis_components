import json
import argparse
import sys
sys.path.append('..')
from oasis_fun import split_pid_3
from oasis_fun import update_pv1_2
from oasis_fun import update_pid_18_with_HAR

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

# Call function that splits PID 3
json_in = split_pid_3.split_pid_3(json_in)

# Call function to update patient class
json_in = update_pv1_2.update_pv1_2(json_in)

# Call function to update PID-18
json_in = update_pid_18_with_HAR.update_pid_18_with_HAR(json_in)

# Write output file with updated json
if args.output is None:
    sys.stdout.write(json.dumps(json_in))
else:
    with open(args.output, "w") as out:
        json.dump(json_in, out)
