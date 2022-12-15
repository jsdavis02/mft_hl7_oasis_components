import argparse
import os
import sys
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

# Create file, add the header and drop it into the output path
concat_file = os.path.join(args.input, 'Volume.txt')
# the format is fixed width as 50, 50, 50, 256, 10(right justified), 10(MM/DD/YYYY), 10(MM/DD/YYYY)
header_text = 'FCLTY_NBR'+' '*41+'DEPT_NBR'+' '*42+'BILL_COD'+' '*42+'BILL_COD_DES'+' '*244+'VOL_QTY'+' '*3+'POST_DAT'+' '*2+'SVC_DAT\n'
with open(concat_file, 'w+', newline='\r\n') as fh:
    fh.write(header_text)

# Append all files to Volume.txt
for f in sorted(os.listdir(args.input)):
    if f in concat_file:
        continue
    with open(concat_file, 'a', newline='\r\n') as outfile:
        with open(args.input+'/'+f, 'r', newline=None) as infile:
            outfile.write(infile.read())

shutil.copy(concat_file, os.path.join(args.output, 'Volume.txt'))
