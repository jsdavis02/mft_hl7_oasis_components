import hl7
import sys
import argparse
import json



parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
args = parser.parse_args(sys.argv[1:])


def get_message_header(msg):
    h = hl7.parse(msg)
    message_trigger = 'ACK'
    if str(h.extract_field('MSH', 1, 9, 1, 1)).lower() != 'ack':
        message_trigger = str(h.extract_field('MSH', 1, 9, 1, 2))
    header = {
        "SendingApp": str(h.extract_field('MSH', 1, 3, 1, 1)),
        "SendingFacility": str(h.extract_field('MSH', 1, 4, 1, 1)),
        "ReceivingApp": str(h.extract_field('MSH', 1, 5, 1, 1)),
        "ReceivingFacility": str(h.extract_field('MSH', 1, 6, 1, 1)),
        "DTofMessage": str(h.extract_field('MSH', 1, 7, 1, 1)),
        "Security": str(h.extract_field('MSH', 1, 8, 1, 1)),
        "MessageType": str(h.extract_field('MSH', 1, 9, 1, 1)),
        "MessageTrigger": message_trigger,
        "ControlID": str(h.extract_field('MSH', 1, 10, 1, 1)),
        "ProcessingID": str(h.extract_field('MSH', 1, 11, 1, 1)),
        "VersionID": str(h.extract_field('MSH', 1, 12, 1, 1)),
    }
    if args.output is None:
        sys.stdout.write(json.dumps(header))
    else:
        with open(args.output, "w") as outf:
            outf.write(json.dumps(header))


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

get_message_header(data)
