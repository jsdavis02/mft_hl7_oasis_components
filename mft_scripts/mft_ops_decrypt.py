import argparse
import sys
import get_route_props
import os
import gnupg

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

gpg = gnupg.GPG(gnupghome="/opt/oasis_data/pgp_keys")

if not os.path.exists(args.output):
    os.makedirs(args.output)

for ename in os.listdir(args.input):
    fp = os.path.join(args.input, ename)
    sname = ename.split('.')
    # Need to know what the outfile name has to be
    dname = os.path.join(args.output, sname[0])
    decrypt = "/bin/gpg --output "+dname+" --decrypt "+fp
    os.system(decrypt)
