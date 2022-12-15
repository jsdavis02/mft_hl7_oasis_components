import argparse
import sys
import get_route_props
import os
import gnupg
from datetime import datetime

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
timestamp = datetime.today().strftime('%Y%m%d')

gpg = gnupg.GPG(gnupghome="/home/srvps0tibco20@hs.maricopa.gov/.gnupg")

if not os.path.exists(args.output):
    os.makedirs(args.output)

recvr_email = None
for prop in route_props:
    if prop['name'] == 'encrypt_email':
        recvr_email = prop['value']

pass_phrase = None
for prop in route_props:
    if prop['name'] == 'passphrase':
        pass_phrase = prop['value']

for f in os.listdir(args.input):
    fp = os.path.join(args.input, f)
    sname = f.split('.')
    ename = os.path.join(args.output, sname[0])
    encrypt = "/bin/gpg  --sign --armor  --passphrase "+pass_phrase+" --recipient "+recvr_email+" --output "+ename+timestamp+".txt.pgp"+" --encrypt "+fp
    os.system(encrypt)
