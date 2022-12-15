import argparse
import os
import sys
import shutil
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

tdate = datetime.today().strftime('%Y%m%d')
ttime = datetime.today().strftime('%H%M%S')

for fname in os.listdir(args.input):
    newname = ''
    if fname == 'DepM.txt':
        newname = 'Facil_DepM_30025_'+tdate+'_'+ttime+'_1.txt'
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
    elif fname == 'ITMI.txt':
        newname = 'Facil_ITMI_30025_'+tdate+'_'+ttime+'_1.txt'
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
    elif fname == 'PurH.txt':
        newname = 'Facil_PurH_30025_'+tdate+'_'+ttime+'_1.txt'
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
    elif fname == 'ItmM.txt':
        newname = 'Facil_ItmM_30025_'+tdate+'_'+ttime+'_1.txt'
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
    elif fname == 'InvH.txt':
        newname = 'Facil_InvH_30025_'+tdate+'_'+ttime+'_1.txt'
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
    elif fname == 'InvD.txt':
        newname = 'Facil_InvD_30025_'+tdate+'_'+ttime+'_1.txt'
        shutil.copy(os.path.join(args.input, fname), os.path.join(args.output, newname))
    else:
        exit('Route script did not find matching files to rename!')
