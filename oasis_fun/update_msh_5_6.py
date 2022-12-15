# Function performs a db lookup to set update the MSH segment
# with the consumer application name and facility for the message

import pyodbc
import configparser

def update_msh_5_6(json_in, route_id, env):
    config = configparser.ConfigParser(interpolation=None)
    config.read("../config.ini")
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    sqlselect1 = "select endpoints.receiving_app from endpoints inner join routes on endpoints.id = routes.consumer_id where routes.id = "+route_id
    cursor = cnxn.cursor()
    cursor.execute(sqlselect1)
    row = cursor.fetchone()

    for (s, value) in json_in.items():
        if s.startswith('MSH'):
            json_in[s].update({'5': row[0]})
            break

    sqlselect2 = "select endpoints.receiving_facility from endpoints inner join routes on endpoints.id = routes.consumer_id where routes.id = "+route_id
    cursor = cnxn.cursor()
    cursor.execute(sqlselect2)
    row = cursor.fetchone()

    for (s, value) in json_in.items():
        if s.startswith('MSH'):
            json_in[s].update({'6': row[0]})
            break

    return json_in
