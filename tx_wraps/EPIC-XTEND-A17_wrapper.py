import json
import argparse
import sys
sys.path.append('..')
from oasis_fun import update_in2_61
from oasis_fun import delete_segments
from oasis_fun import update_pid_18_swap
from oasis_fun import update_msh_5_6
from oasis_fun import update_pv1_18_swap
from oasis_fun import truncate_pid_13_swap
from oasis_fun import truncate_msh
from oasis_fun import update_evn_4
from oasis_fun import update_pid_22_swap
from oasis_fun import update_pv1_10_swap
from oasis_fun import update_pid_12_swap
from oasis_fun import delete_pid_23
from oasis_fun import update_pid_swap
from oasis_fun import truncate_pid_9_swap
from oasis_fun import truncate_pv1_swap
from oasis_fun import truncate_pid_swap

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

# Call function that updates IN2 61
json_in = update_in2_61.update_in2_61(json_in)

# Call function that updates PID 2
json_in = update_pv1_18_swap.update_pv1_18_swap(json_in)

# Call function that updates PID 18
json_in = update_pid_18_swap.update_pid_18_swap(json_in)

# Call function that splits PID 3
json_in = update_pid_swap.update_pid_swap(json_in)

# Call function that updates message header with consumer app
json_in = update_msh_5_6.update_msh_5_6(json_in, args.route, args.env)

# Call function that updates PV1 13
json_in = truncate_pid_13_swap.truncate_pv1_13_swap(json_in)

# Call function that truncates MSH to 12 fields
json_in = truncate_msh.truncate_msh(json_in)

# Call function that truncates PV1 to 50 fields
json_in = truncate_pv1_swap.truncate_pv1_swap(json_in)

# Call function that truncates PID 9 to 2 fields
json_in = truncate_pid_9_swap.truncate_pid_9_swap(json_in)

# Call function that updates EVN 4
json_in = update_evn_4.update_evn_4(json_in)

# Call function that updates PID 22
json_in = update_pid_22_swap.update_pid_22_swap(json_in)

# Call function that updates PID 12
json_in = update_pid_12_swap.update_pid_12_swap(json_in)

# Call function that updates PV1 10
json_in = update_pv1_10_swap.update_pv1_10_swap(json_in)

# Call function that deletes PID 23
json_in = delete_pid_23.delete_pid_23(json_in)

# Call function that truncates PID to 30 fields
json_in = truncate_pid_swap.truncate_pid_swap(json_in)

# Call function that removes keys
deletekeys = ('CON', 'NK1', 'NTE', 'ZPV', 'ZIN', 'AL1', 'DG1', 'GT1', 'IN1', 'IN2', 'PD1', 'PV2')
json_in = delete_segments.delete_segments(json_in, deletekeys)

# Write output file with updated json
if args.output is None:
    sys.stdout.write(json.dumps(json_in))
else:
    with open(args.output, "w") as out:
        json.dump(json_in, out)
