import json
import argparse
import sys
sys.path.append('..')
from oasis_fun import update_msh_3_dent
from oasis_fun import truncate_msh_dent
from oasis_fun import update_pid_3_dent
from oasis_fun import update_ft1_dent
from oasis_fun import update_ft1_25_dent
from oasis_fun import delete_pv1_3_dent
from oasis_fun import update_zft_dent

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

# Call function that updates the sending application field
json_in = update_msh_3_dent.update_msh_3_dent(json_in)

# Call function tht truncates MSH to 16 fields
json_in = truncate_msh_dent.truncate_msh_dent(json_in)

# Call function that updates PID 3 with facility id
json_in = update_pid_3_dent.update_pid_3_dent(json_in)

# Call function that updates FT1, clear data from 11, 16, and 20
json_in = update_ft1_dent.update_ft1_dent(json_in)

# Call function that updates FT1 field 25, adding BEAP
json_in = update_ft1_25_dent.update_ft1_25_dent(json_in)

# Call function that updates ZFT with procedure details
json_in = update_zft_dent.update_zft_dent(json_in)

# Call function that deletes PV1 field 3, patient location
json_in = delete_pv1_3_dent.delete_pv1_3_dent(json_in)

# Write output file with updated json
if args.output is None:
    sys.stdout.write(json.dumps(json_in))
else:
    with open(args.output, "w") as out:
        json.dump(json_in, out)
