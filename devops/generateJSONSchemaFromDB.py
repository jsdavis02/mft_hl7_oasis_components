import argparse
import pyodbc
import configparser
import os
import sys
import json

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database to pull from")
parser.add_argument("-t", "--table", dest="table", help="table to generate from")
args = parser.parse_args(sys.argv[1:])
config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

cursor = cnxn.cursor()
jout = {}
for row in cursor.columns(table=args.table):

    jout[row.column_name] = ''

print(json.dumps(jout))
