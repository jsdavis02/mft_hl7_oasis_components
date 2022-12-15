import pyodbc
import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("../../config.ini")

def get_active_ports(active_producers, env):
    producers = ([str(p['id']) for p in active_producers])
    active_ports = []
    if len(producers) <= 0:
        return active_ports

    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    separator = ','
    endpoints = separator.join(producers)
    select_port = "SELECT endpoint_id, value FROM OASIS_endpointprop WHERE name = 'producer_port' AND env = '"+env+"' AND endpoint_id IN ("+endpoints+")"
    cursor = cnxn.cursor()
    cursor.execute(select_port)
    row = cursor.fetchone()
    column_names = [d[0] for d in cursor.description]

    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            vals[column_names[x]] = row[x]
            x += 1
        active_ports.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return active_ports
