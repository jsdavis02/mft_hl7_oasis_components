import hl7
import sys
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-c", "--ack_code", dest="ack_code", help="AA(accept), AR(reject), AE(error)")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
args = parser.parse_args(sys.argv[1:])


def gen_ack(msg, a_code):
    h = hl7.parse(msg)
    if args.output is None:
        sys.stdout.write(str(h.create_ack(a_code)))
    else:
        with open(args.output, "w") as outf:
            outf.write(str(h.create_ack(a_code)))


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

gen_ack(data, args.ack_code)
