import json
import argparse
import sys
sys.path.append('..')
from oasis_fun import truncate_msh
from oasis_fun import update_msh_12
from oasis_fun import update_msh_11
from oasis_fun import truncate_pv1
from oasis_fun import truncate_pid_5
from oasis_fun import delete_segments
from oasis_fun import truncate_orc
from oasis_fun import update_ft1_soft

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

# Call function that truncates MSH segment to 12 fields
json_in = truncate_msh.truncate_msh(json_in)

# Call function that updates the version field in MSH
json_in = update_msh_12.update_msh_12(json_in, "2.3")

# Call function that updates the processing id in MSH
json_in = update_msh_11.update_msh_11(json_in)

# Call function that truncate PV1 segment to 46 fields
json_in = truncate_pv1.truncate_pv1(json_in)

# Call function that truncates PID segment, field 5
json_in = truncate_pid_5.truncate_pid_5(json_in)

# Call function that deletes segments
deletekeys = 'DG1'
json_in = delete_segments.delete_segments(json_in, deletekeys)

# Call function that truncates segment ORC to 13 fields
json_in = truncate_orc.truncate_orc(json_in, 13)

# Call function that updates FT1 and extends it to 25 fields
json_in = update_ft1_soft.update_ft1_soft(json_in)

# Write output file with updated json
if args.output is None:
    sys.stdout.write(json.dumps(json_in))
else:
    with open(args.output, "w") as out:
        json.dump(json_in, out)
