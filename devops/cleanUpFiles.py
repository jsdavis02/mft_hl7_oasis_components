import argparse
import os
import sys
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
args = parser.parse_args(sys.argv[1:])

shutil.rmtree(args.input)
