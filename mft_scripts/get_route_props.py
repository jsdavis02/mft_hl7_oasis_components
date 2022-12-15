import os
import configparser
import pyodbc

def get_route_props(env, route_id):
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.join("..", "config.ini"))
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    select_props = "SELECT * FROM oasis.dbo.route_props where route_id = '"+str(route_id)+"' AND env = '"+env+"'"
    cursor = cnxn.cursor()
    cursor.execute(select_props)
    row = cursor.fetchone()
    route_props = []
    column_names = [d[0] for d in cursor.description]
    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            vals[column_names[x]] = row[x]
            x += 1
        route_props.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return route_props
