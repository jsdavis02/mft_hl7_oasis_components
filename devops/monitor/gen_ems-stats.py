import subprocess
import argparse
import sys
import configparser
import socket
import pyodbc
import re

config = configparser.ConfigParser(interpolation=None)
config.read("../../config.ini")

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="Environment config to use [DEV,TST,PPRD,PRD]")
args = parser.parse_args(sys.argv[1:])
env = args.env
ems_port = config.get(env, 'ems_admin.port')
user = config.get(env, 'ems_admin.user')
passwd = config.get(env, 'ems_admin.passwd')
host = socket.gethostname()

server = config.get(env, 'database.server')
database = config.get(env, 'database.dbname')
username = config.get(env, 'database.user')
password = config.get(env, 'database.pass')
tea_url = config.get(env, 'tea.url')
# admin_ui = config.get(env, 'admin_ui.url')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

show = "/opt/PythonUtilities/devops/monitor/ems_show.txt"
active_chk = subprocess.getoutput("/opt/tibco/ems/8.4/bin/tibemsadmin -server tcp://"+host+":"+ems_port+" -user "+user+" -password "+passwd+" -script "+show)

for line in active_chk.splitlines():
    if line != "":
        line = (re.split(r'\s+', line))
        if line[1] == 'State:':
            check = line[2]
            if check == 'active':
                cmd = "/opt/PythonUtilities/devops/monitor/ems_cmd.txt"
                out = subprocess.getoutput("/opt/tibco/ems/8.4/bin/tibemsadmin -server tcp://"+host+":"+ems_port+" -user "+user+" -password "+passwd+" -script "+cmd)

                with open('/opt/oasis_data/monitoring/queuelist.txt', 'w') as f:
                    f.write(out)
                for l in out.splitlines():
                    print(l)
