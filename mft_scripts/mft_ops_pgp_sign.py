import argparse
import sys
import get_route_props
import os


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if args.input is None or len(args.input) == 0:
    print('', end='')
    exit(0)

route_props = get_route_props.get_route_props(args.env, args.route_id)

pgp_dir = "/opt/oasis_data/pgp_keys"

if not os.path.exists(args.output):
    os.makedirs(args.output)

key_id = None
for prop in route_props:
    if prop['name'] == 'key_id':
        key_id = prop['value']

pass_phrase = None
for prop in route_props:
    if prop['name'] == 'passphrase':
        pass_phrase = prop['value']

for f in os.listdir(args.input):
    fp = os.path.join(args.input, f)
    fp_pgp = os.path.join(args.output, f+".pgp")
    sign_file = "/bin/gpg --homedir "+pgp_dir+" --batch --yes --passphrase "+pass_phrase+" --default-key "+key_id+" --output "+fp_pgp+" --sign "+fp
    os.system(sign_file)



