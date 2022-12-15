import pyodbc
import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("../../config.ini")
def get_active_producers(env):
    active_producers = []
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    sqlselect = "SELECT id FROM OASIS_endpoint WHERE active = '1' AND type = 'HL7' AND direction = 'producer'"
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
        active_producers.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return active_producers
