import argparse
import pyodbc
import configparser
import sys
import os

config = configparser.ConfigParser(interpolation=None)
config.read("config.ini")
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="tbl_file", help="the path to clover file")
parser.add_argument("-k", "--key", dest="key", help="the key for sql insert")
parser.add_argument("-e", "--env", dest="env", help="the target env")
args = parser.parse_args(sys.argv[1:])

server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

l = []
d = {}
with open(args.tbl_file) as t:
    afterprologue = False
    haveinput = False
    for line in t.readlines():
        if "end_prologue" in line:
            afterprologue = True
            continue
        if "=" not in line and "#" not in line and afterprologue:
            # print(line)
            if haveinput:
                d['output'] = line.strip()
                d['lookup_key'] = os.path.basename(args.tbl_file)[:-4]
                d['env'] = args.env
                l.append(d)
                d = {}
                haveinput = False
            else:
                d['input'] = line.strip()
                haveinput = True
        elif "dflt=" in line:
            l.append({'input': 'no_match', 'output': line.split("=", 1)[1].strip(), 'lookup_key': os.path.basename(args.tbl_file)[:-4], 'env': args.env})

sqlinsert = "insert into dbo.code_table (input, output, env, lookup_key) values ("
sqlupdate = "update dbo.code_table set output = "
for d in l:
    sqlinsert += "'"+d['input']+"', '"+d['output']+"', '"+d['env']+"', '"+d['lookup_key']+"')"
    sqlupdate += "'"+d['output']+"' where input = '"+d['input']+"' and env = '"+d['env']+"' and lookup_key = '"+d['lookup_key']+"'"
    print(sqlinsert)
    print(sqlupdate)
    cursor = cnxn.cursor()
    cursor.execute(sqlupdate)
    if cursor.rowcount == 0:
        cursor.execute(sqlinsert)
    cursor.commit()
    sqlinsert = "insert into dbo.code_table (input, output, env, lookup_key) values ("
    sqlupdate = "update dbo.code_table set output = "
    