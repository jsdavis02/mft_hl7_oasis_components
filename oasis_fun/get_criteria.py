# Function performs a db lookup to determine if the ADT
# message should be killed based on criteria

import pyodbc
import configparser
import os

def get_criteria(route_id, env):
    crit_list = []
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.join("..","config.ini"))
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    # TODO this is HL7 stuff we aren't really using so just marking this 
    sqlselect = "select * from route_criterias where route_id = "+route_id
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
        crit_list.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return crit_list
