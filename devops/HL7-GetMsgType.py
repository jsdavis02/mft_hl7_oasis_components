import hl7
import sys
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
args = parser.parse_args(sys.argv[1:])


def get_message_type(msg):
    #print('Converting to json')
    h = hl7.parse(msg)
    if args.output is None:
        sys.stdout.write(str(h.extract_field('MSH', 1, 9, 1, 1))+'^'+h.extract_field('MSH', 1, 9, 1, 2))
    else:
        with open(args.output, "w") as outf:
            outf.write(str(h.extract_field('MSH', 1, 9, 1, 1))+'^'+h.extract_field('MSH', 1, 9, 1, 2))


data = ""
if args.input is None:
    line = sys.stdin.readline()
    while line:
        data += line + "\r"
        line = sys.stdin.readline()
else:
    with open(args.input) as fp:
        line = fp.readline()
        while line:
            data += line + "\r"
            line = fp.readline()

get_message_type(data)
