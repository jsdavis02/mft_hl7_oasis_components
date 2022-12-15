import json
import argparse
import sys
sys.path.append('..')
from oasis_fun import split_pid_3
from oasis_fun import delete_segments
from oasis_fun import update_in2_61
from oasis_fun import update_pid_18
from oasis_fun import update_msh_5_6
from oasis_fun import update_msh_12
from oasis_fun import update_pv1_39
from oasis_fun import update_pv1_18
from oasis_fun import truncate_msh

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

# Call function that updates IN2 61
json_in = update_in2_61.update_in2_61(json_in)

# Call function that updates PID 18
json_in = update_pid_18.update_pid_18(json_in)

# Create a list of keys to be removed
deletekeys = ('CON', 'NK1', 'NTE', 'ZPV', 'ZIN', 'AL1', 'DG1')

# Call function that removes keys
json_in = delete_segments.delete_segments(json_in, deletekeys)

# Call function that updates message header with consumer app
json_in = update_msh_5_6.update_msh_5_6(json_in, args.route, args.env)

# Call function that updates servicing facility in PV1
json_in = update_pv1_39.update_pv1_39(json_in, "EPIC_CMAX_CARE_SITE_map", args.env)

# Call function that updates patient type in PV1
json_in = update_pv1_18.update_pv1_18(json_in, "EPIC_CMAX_VISIT_SITE_map", args.env)

# Call function that updates version id in MSH 12
ver_id = "2.3"
json_in = update_msh_12.update_msh_12(json_in, ver_id)

# Call function that truncates MSH header to 12 fields
json_in = truncate_msh.truncate_msh(json_in)

# Write output file with updated json
if args.output is None:
    sys.stdout.write(json.dumps(json_in))
else:
    with open(args.output, "w") as out:
        json.dump(json_in, out)
