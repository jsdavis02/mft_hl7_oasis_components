import json
import argparse
import sys
sys.path.append('..')
from oasis_fun import check_criteria

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

# Call function to evaluate for message kill criteria
result = check_criteria.check_criteria(json_in, args.route, args.env)


# Write output file with boolean results
if args.output is None:
    sys.stdout.write(result)
else:
    with open(args.output, "w") as out:
        out.write(result)
        out.close()
