# Functions used for MFT operations
import configparser
import os
import pyodbc

def run_selects(sql, env):
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.join("..", "config.ini"))
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    out = {"results": []}
    cursor = cnxn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    column_names = [d[0] for d in cursor.description]

    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            vals[column_names[x]] = row[x]
            x += 1
        out["results"].append(vals)
        row = cursor.fetchone()
        rcount += 1

    return out

