import argparse
import configparser
import os
import pyodbc
import sys
import json
from datetime import datetime, timezone, timedelta
sys.path.append('..')
from devops import util_functions

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-c", "--command", dest="cmd", help="put, get, list, rlist")
parser.add_argument("-i", "--input", dest="input", help="specify file path for json input")

args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
mft_endpoint_key_folder = config.get(args.env, 'mft_endpoint_key_folder')

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)


def do_audit_insert(cmd_args, jdata_in: dict):
    return util_functions.do_audit_insert(cmd_args, jdata_in, cnxn)


# input by bw is stdin json so get it here

input_data = ""
line = None
jdata = None

# Read json file and load it in as a python dict
if args.input is None:
    line = sys.stdin.readline()
    while line:
        input_data += line + "\r"
        line = sys.stdin.readline()
    jdata = json.loads(input_data)
else:
    with open(args.input, 'r') as fp:
        jdata = json.load(fp)

if args.cmd.lower() == "insert":
    print(do_audit_insert(args, jdata))
