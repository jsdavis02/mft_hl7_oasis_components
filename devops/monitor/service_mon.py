import service_alert
import subprocess
import socket
import argparse
import configparser
import pyodbc
import sys

host = socket.gethostname()
config = configparser.ConfigParser(interpolation=None)
config.read("/opt/PythonUtilities/config.ini")

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="Environment config to use [DEV,TST,PPRD,PRD]")
parser.add_argument("-l", "--list", nargs='+', dest="process", help="List of processes to monitor")
args = parser.parse_args(sys.argv[1:])
env = args.env
proc_list = args.process

server = config.get(env, 'database.server')
database = config.get(env, 'database.dbname')
username = config.get(env, 'database.user')
password = config.get(env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

alert_msg = ""
alert_level = ""

for process in proc_list:
    status_up = subprocess.getoutput('/bin/systemctl is-active '+process)
    print("Process: "+process+" is "+status_up+"!")
    if status_up != 'active':
        alert_level_process = ("alert_level-"+process)
        select_alert = "SELECT value FROM app_settings WHERE name = '"+alert_level_process+"' AND env = '"+env+"'"
        cursor = cnxn.cursor()
        cursor.execute(select_alert)
        alert_field = cursor.fetchone()
        alert_level = alert_field[0]
        alert_msg = ("The "+process+" process on "+host+" is not active!\n")
        service_alert.service_alert(env, process, host, alert_msg, alert_level)
    else:
        print("OK")

