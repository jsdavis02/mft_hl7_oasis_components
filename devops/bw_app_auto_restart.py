import argparse
import sys
import configparser
import pyodbc
import os
import subprocess
from datetime import datetime, timedelta
import json

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)


def get_endpoints():
    elist = []
    sql = "select * from endpoints where active = 1 and type = 'hl7'"
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
        elist.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return elist


def get_endpoints_stats(id):
    elist = []
    sql = "select top 50 * from endpoint_status where endpoint_id = "+str(id)+" order by modified DESC"
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
        elist.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return elist


def get_endpoint_setting_db(id):
    elist = []
    sql = "select * from endpoint_props where endpoint_id = "+str(id)+" and name LIKE 'auto_restart%'"
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
        elist.append(vals)
        row = cursor.fetchone()
        rcount += 1

    return elist


def get_endpoint_setting(e_id):
    esettings = get_endpoint_setting_db(e_id)
    outsettings = {"auto_restart": True, "auto_restart_max": 3, "auto_restart_minutes_window": 30}
    for es in esettings:
        if es['name'] == "auto_restart" and es['value'].lower() == "false":
            outsettings['auto_restart'] = False
        if es['name'] == "auto_restart_max":
            outsettings['auto_restart_max'] = int(es['value'])
        if es['name'] == "auto_restart_minutes_window":
            outsettings['auto_restart_minutes_window'] = int(es['value'])
    return outsettings

def is_shutdown(estats):
    if len(estats) > 0:
        #print(estats[0])
        if 'app_state' in estats[0] and estats[0]['app_state'] != 'Running':
            return True
    return False

def is_alerted(estats):
    if len(estats) > 0:
        #print(estats[0])
        if 'action' in estats[0] and estats[0]['action'] == 'Alerted':
            return True
    return False

def is_max(estats,eprops):
    #print(eprops)
    # get current date and minutes back
    current_time = datetime.now()
    past_time = current_time - timedelta(minutes=eprops['auto_restart_minutes_window'])
    auto_start_count = 0
    for est in estats:
        if est['action'] == 'Auto-Restart':
            # is between time window
            if est['modified'] < current_time and est['modified'] > past_time:
                auto_start_count += 1
    #print(auto_start_count)
    if auto_start_count >= eprops['auto_restart_max']:
        return True
    return False


def insert_restart_status(rid):
    sqlin = "insert into endpoint_status (endpoint_id, app_state, action, modified) values ("+str(rid)+", 'Running', 'Auto-Restart',getdate())"
    cursor = cnxn.cursor()
    cursor.execute(sqlin)
    cursor.commit()


elist = get_endpoints()
#print(elist)
endpoint_stats = {}
endpoint_config = {}
endpoints_maxed = []
endpoints_restarted = []
for e in elist:
    #print(get_endpoints_stats(e['id']))
    endpoint_stats[e['id']] = get_endpoints_stats(e['id'])
    if is_shutdown(endpoint_stats[e['id']]):
        endpoint_config[e['id']] = get_endpoint_setting(e['id'])
        if not endpoint_config[e['id']]['auto_restart']:
            #specifically set to not restart
            continue
        if is_alerted(endpoint_stats[e['id']]):
            #we don't try again if last record is Alerted
            continue
        #print(endpoint_config[e['id']])
        # check if max
        if is_max(endpoint_stats[e['id']], endpoint_config[e['id']]):
            #record we hit max for error handling
            endpoints_maxed.append(e)
            #we hit max, don't restart
            continue
        # record Auto restart first assuming restart works since auto shutdown can be so fast we want records in right time order
        insert_restart_status(e['id'])
        # do restart
        out = ''
        try:
            out = subprocess.check_output("python3 bw_commands.py -c restartapp -d OASIS -a Oasis-HL7 -b "+e['bw_process_ident'], shell=True)
        except subprocess.CalledProcessError as e:
            exit(e)
        js_out = json.loads(out)
        for eo in js_out:
            #print(eo)
            if eo['endpoint'].startswith(e['bw_process_ident']):
                #print('restarted '+eo['endpoint'])
                endpoints_restarted.append(e)

# return output of what hit max and what was restarted
results = {"maxed": endpoints_maxed, "restarted": endpoints_restarted}
sys.stdout.write(json.dumps(results))
