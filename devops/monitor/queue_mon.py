import subprocess
import argparse
import sys
import configparser
import re
import socket
import pyodbc
import queue_alert

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

for l in active_chk.splitlines():
    if l != "":
        l = (re.split(r'\s+', l))
        if l[1] == 'State:':
            check = l[2]
            if check == 'active':
                queues = "/opt/PythonUtilities/devops/monitor/ems_queues.txt"
                out = subprocess.getoutput("/opt/tibco/ems/8.4/bin/tibemsadmin -server tcp://"+host+":"+ems_port+" -user "+user+" -password "+passwd+" -script "+queues)

                for line in out.splitlines():
                    if line != "":
                        line = (re.split(r'\s+', line))
                        if line[1].startswith('oasis'):
                            queue = line[1]
                            split_queue = queue.split('.')
                            bw_ident = split_queue[2]
                            select_active = "SELECT active FROM OASIS_endpoint WHERE bw_process_ident = '"+bw_ident+"'"
                            cursor = cnxn.cursor()
                            cursor.execute(select_active)
                            active_field = cursor.fetchone()
                            is_active = active_field[0]

                            sqlalert = "SELECT alert_level from OASIS_endpoint WHERE bw_process_ident = '"+bw_ident+"'"
                            cursor = cnxn.cursor()
                            cursor.execute(sqlalert)
                            alert_field = cursor.fetchone()
                            alert_level = alert_field[0]

                            if is_active is True and alert_level != 100:
                                if int(line[4]) > 0:
                                    print("Queue: "+queue+" is fine!")
                                else:
                                    depth = line[5]
                                    alert_msg = "The listener for queue: "+queue+" is not up! Queue depth is: "+depth+"."
                                    print(alert_msg)
                                    queue_alert.queue_alert(env, queue, depth, bw_ident, alert_msg)
                            else:
                                print("Queue is not active")
            elif check == 'fault-tolerant-standby':
                # Just making sure the ems server is in an acceptable state
                print("EMS Server is in passive state.")
            else:
                print("EMS Server is not in an acceptable state!")  # We can alert further on this

