import argparse
import os
import sys
import configparser
import pyminizip
import pyodbc

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-i", "--input", dest="input", help="input file")

args = parser.parse_args(sys.argv[1:])

print(args.input)
