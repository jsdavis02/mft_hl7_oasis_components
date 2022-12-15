import argparse
import sys
import os
import xlrd

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-r", "--route", dest="route_id", help="The route id to run this mft script for")

args = parser.parse_args(sys.argv[1:])

if not os.path.exists(args.output):
    os.makedirs(args.output)

for f_in in os.listdir(args.input):
    wb = None
    try:
        wb = xlrd.open_workbook(os.path.join(args.input, f_in))
    except xlrd.XLRDError as x_err:
        exit('Bad formatting in xls file!')
    sheet = wb.sheet_by_name('Stat')
    t_out = str(f_in).split('.')[0]+'.txt'
    f_out = os.path.join(args.output, t_out)
    with open(f_out, 'w') as outfile:
        for i in range(1, sheet.nrows):
            colvals = []
            for c in range(sheet.ncols):
                cval = sheet.cell_value(i, c)
                if type(cval) != 'str' and i > 0:
                    cval = str(cval).split('.')[0]
                if c > 4 and i > 0:
                    # creates the formatted date correctly
                    cval = xlrd.xldate_as_datetime(sheet.cell_value(i, c), wb.datemode).strftime('%m/%d/%Y')
                colvals.append(cval)
        # the format is fixed width as 50, 50, 50, 256, 10(right justified), 10(MM/DD/YYYY), 10(MM/DD/YYYY)
            line = f"{colvals[0].ljust(50)}{colvals[1].ljust(50)}{colvals[2].ljust(50)}{colvals[3].ljust(256)}{colvals[4].rjust(10)}{colvals[5]}{colvals[6]}\n"
            outfile.write(line)

