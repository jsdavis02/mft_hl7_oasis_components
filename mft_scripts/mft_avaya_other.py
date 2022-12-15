import os
import argparse
import sys
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if args.input is None or len(args.input) == 0:
    print('', end='')
    exit(0)

if not os.path.exists(args.output):
    os.makedirs(args.output)

filestoexclude = [
    'PIM_EXP_ApptReminder_1000_Campaign_Gen_EngSpn_',
    'PIM_EXP_COVID_Vaccine_9000_Contacts_EngSpn',
    'PIM_EXP_RTS_8000_Campaign_EngSpn_',
    'PIM_EXP_RTS_8200_Campaign_EngSpn_',
    'PIM_EXP_ApptReminder_1000',
    'PIM_EXP_CHC_Peds_0003',
    'PIM_EXP_CHC_Peds_0004'
]

filestocopy = []

for fname in os.listdir(args.input):
    include = True
    for f in filestoexclude:
        if f in fname:
            include = False
    if include:
        filestocopy.append(fname)

for c in filestocopy:
        fname = c
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, fname))


