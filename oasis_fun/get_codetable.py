import argparse
import pyodbc
import sys
import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("../config.ini")
# parser = argparse.ArgumentParser()
# parser.add_argument("-k", "--key", dest="key", help="lookup table key")
# parser.add_argument("-e", "--env", dest="env", help="target environment")
# parser.add_argument("-i", "--input", dest="input", help="full path to json input file")
# parser.add_argument("-o", "--output", dest="output", help="full path to json output file")

#args = parser.parse_args(sys.argv[1:])

def get_codetable(key, env):
    propslist =[]
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    sqlselect = "SELECT * FROM code_table WHERE lookup_key = '"+key+"' AND env = '"+env+"'"
    cursor = cnxn.cursor()
    cursor.execute(sqlselect)
    row = cursor.fetchone()
    column_names = [d[0] for d in cursor.description]

    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            vals[column_names[x]] = row[x]
            x += 1
        propslist.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return propslist
