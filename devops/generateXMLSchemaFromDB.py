import argparse
import pyodbc
import configparser
import os
import sys

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
xsdblock = ''
for row in cursor.columns(table=args.table):
    xsdtype = 'string'
    if 'int' in row.type_name:
        # covers bigint also
        xsdtype = 'int'
    if 'bit' in row.type_name:
        xsdtype = 'boolean'

    xsdblock += '<element name="'+row.column_name+'" type="'+xsdtype+'"></element>\n'

print(xsdblock)