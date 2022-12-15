# Script checks that the ports are listening on all active HL7 producers.

from . import get_active_producers
from . import get_active_ports
from socket import socket
import configparser
import argparse
import sys
import pyodbc
from datetime import datetime

# Set environment
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="Environment config to use [DEV,TST,PPRD,PRD]")
args = parser.parse_args(sys.argv[1:])
env = args.env

# Get environment configuration from config.ini
config = configparser.ConfigParser(interpolation=None)
config.read("../../config.ini")
server = config.get(env, 'database.server')
database = config.get(env, 'database.dbname')
username = config.get(env, 'database.user')
password = config.get(env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

# Make function call to get list of active endpoints
active_producers = get_active_producers.get_active_producers(env)

# Iterate through list of endpoints, testing each host and port combination,
# Update the database with a timestamp when the connection succeeds.
producers = ([str(p['id']) for p in active_producers])
if len(producers) <= 0:
    exit(0)

for producer in producers:
    try:
        print(producer)
        select_host = "SELECT value FROM OASIS_endpointprop WHERE name = 'producer_host' AND endpoint_id = '"+producer+"' AND env = '"+env+"'"
        cursor = cnxn.cursor()
        cursor.execute(select_host)
        host_row = cursor.fetchone()
        host = host_row[0]
        print(host)
    
        select_port = "SELECT value FROM OASIS_endpointprop WHERE name = 'producer_port' AND endpoint_id = '"+producer+"' AND env = '"+env+"'"
        cursor = cnxn.cursor()
        cursor.execute(select_port)
        port_row = cursor.fetchone()
        port = port_row[0]
        print(port)
        
        try:
            sock = socket()
            sock.settimeout(3)
            sock.connect((host, port))
            sock.close()
            timestmp = datetime.today()
            endpt = port["endpoint_id"]
            print("Successfully connected to "+str(host)+" at "+timestmp.strftime('%Y-%m-%d %H:%M:%S')+".")
            sqlselect = "UPDATE OASIS_endpoint SET portmon_host='"+str(host)+"', portmon_time='"+timestmp.strftime('%Y-%m-%d %H:%M:%S')+"' WHERE id = "+str(endpt)
            cursor = cnxn.cursor()
            cursor.execute(sqlselect)
            cnxn.commit()
        except:
            print("Could not connect to "+host+":"+port+"!")
    except:
        print("There was a problem connecting to endpoint "+producer+", validate the endpoint properties.")

cnxn.close()

