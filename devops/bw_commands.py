import subprocess
import sys
import argparse
import json
import time
import configparser
import os
import pyodbc
from datetime import datetime, timedelta


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cmd", dest="cmd", help="showapps, shownodes, restartapp")
parser.add_argument("-e", "--env", dest="env", help="DEV, TST, PPRD, PRD")
parser.add_argument("-a", "--appspace", dest="appspace", help="Tibco AppSpace the applications are in")
parser.add_argument("-d", "--domain", dest="domain", help="Tibco domain the applications are in")
parser.add_argument("-b", "--bw_ident", dest="bw_ident", help="The bw identifier that is the beginning of the sender or receiver app name")
parser.add_argument("-n", "--appnode", dest="appnode", help="The appnode to start or stop")
parser.add_argument("-m", "--hostname", dest="hostname", help="hostname of the appnode")
parser.add_argument("-p", "--appname", dest="appname", help="The appname to start or stop")
parser.add_argument("-v", "--appver", dest="appver", help="The app version to start or stop")

args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)


def get_config(args, jdata_in):
    fmt = "%Y-%m-%d %H:%M:%S"
    ecfg = {"endpoint": {}, "properties": []}
    bw_ident = None
    if jdata_in is not None and 'bw_ident' in jdata_in and len(jdata_in['bw_ident']) > 0:
        bw_ident = jdata_in['bw_ident']
    else:
        # use arg if we have it as fallback
        if args.bw_ident is not None and len(args.bw_ident) > 0:
            bw_ident = args.bw_ident
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No bw_ident specified in json input from stdin or -b argument for property retrieval')
    sql = "select * from endpoints where bw_process_ident = '"+bw_ident+"'"
    cursor = cnxn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    column_names = [d[0] for d in cursor.description]
    if cursor.rowcount <= 0:
        return None
    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            if isinstance(row[x], datetime):
                row[x] = row[x].strftime(fmt)
            #print(type(row[x]))
            vals[column_names[x]] = row[x]
            x += 1
        ecfg['endpoint'] = vals
        row = cursor.fetchone()
        rcount += 1

    sql = "select * from endpoint_props where endpoint_id = "+str(ecfg['endpoint']['id'])+" and env = '"+args.env+"'"
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
        ecfg['properties'].append(vals)
        row = cursor.fetchone()
        rcount += 1
    # print(ecfg)
    return ecfg


def get_prop_by_name(props, prop_name):
    for p in props:
        if p['name'] == prop_name:
            #print(p['value'])
            return p['value']

    return None


def show_apps_for_appnode(args, appnode):
    oad = []
    # print('Doing bwadmin show -domain OASIS -appspace '+args.appspace+' applications')
    out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin show -domain "+args.domain+" -appspace "+args.appspace+" -n "+appnode+" applications", shell=True)
    lc = 1
    for line in out.splitlines():
        if lc > 5:
            line = line.decode('ascii')
            # print(line)
            app_items = line.split()
            ad = {
                "endpoint": app_items[0],
                "version": app_items[1],
                "appspace": app_items[2],
                "profile": app_items[3],
                "status": app_items[4],
                "config_status": app_items[5],
                #"description": app_items[6],
                #"details": app_items[7]
            }
            oad.append(ad)
        lc += 1
    return json.dumps(oad)


def show_apps_for_appspace(args):
    oad = []
    # print('Doing bwadmin show -domain OASIS -appspace '+args.appspace+' applications')
    out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin show -domain "+args.domain+" -appspace "+args.appspace+" applications", shell=True)
    lc = 1
    for line in out.splitlines():
        if lc > 5:
            line = line.decode('ascii')
            # print(line)
            app_items = line.split()
            ad = {
                "endpoint": app_items[0],
                "version": app_items[1],
                "appspace": app_items[2],
                "profile": app_items[3],
                "status": app_items[4],
                "deployment_status": app_items[5],
                "running_total": app_items[6],
                #"description": app_items[7]
            }
            oad.append(ad)
        lc += 1
    return json.dumps(oad)


def show_appnodes(args):
    oad = []
    # print('Doing bwadmin show -domain OASIS -appspace '+args.appspace+' applications')
    out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin show -domain "+args.domain+" -appspace "+args.appspace+" appnodes", shell=True)
    lc = 1
    for line in out.splitlines():
        if lc > 2:
            line = line.decode('ascii')
            # print(line)
            app_items = line.split()
            ad = {
                "appnode": app_items[0],
                "status": app_items[1],
                "appspace": app_items[2],
                "mgmtport": app_items[3],
                "agent": app_items[4],
                "configstate": app_items[5],
                "up_time": app_items[6]
            }
            oad.append(ad)
        lc += 1
    return json.dumps(oad)


def showall(args):
    oad = []
    jout = []
    # print('Doing bwadmin show -domain OASIS -appspace '+args.appspace+' applications')
    out = None
    try:
        out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin show -domain "+args.domain+" appspaces", shell=True)
    except subprocess.CalledProcessError as e:
        # bail out and bubble up
        exit(e)
    lc = 1
    for line in out.splitlines():
        if lc > 4:
            line = line.decode('ascii')
            #print(line)
            app_items = line.split()
            ad = {
                "appspace": app_items[0],
                "min_nodes": app_items[1],
                "status": app_items[2],
                "nodes": app_items[3],
                "app_count": app_items[4]
            }
            oad.append(ad)
        lc += 1
    for ap in oad:
        #maybe move this to a standalone function but for now
        apn_list = []
        applist = []
        ap_out = None
        try:
            ap_out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin show -domain "+args.domain+" -appspace "+ap["appspace"]+" appnodes", shell=True)
        except subprocess.CalledProcessError as e:
            # bail out and bubble up
            exit(e)
        lc = 1
        for apline in ap_out.splitlines():
            if lc > 2:
                apline = apline.decode('ascii')
                #print(apline)
                appn_items = apline.split()
                apn = {
                    "appnode": appn_items[0],
                    "status": appn_items[1],
                    "appspace": appn_items[2],
                    "mgmt_port": appn_items[3],
                    "agent": appn_items[4],
                    "config_state": appn_items[5],
                    "up_time": appn_items[6]
                }
                apn_list.append(apn)
                # so doing application list at appspace will show running 1/2 if one is down so lets get apps by appnode
                # so we see status of stopped per node
                appslc = 1
                as_out = None
                try:
                    as_out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin show -domain "+args.domain+" -appspace "+ap["appspace"]+" -appnode "+apn["appnode"]+" applications", shell=True)
                except subprocess.CalledProcessError as e:
                    # bail out and bubble up
                    exit(e)
                for apsline in as_out.splitlines():
                    #print(apsline)
                    if appslc > 5:
                        apsline = apsline.decode('ascii')
                        apps = apsline.split()
                        #print(apps)
                        appd = {
                            "appnode": apn["appnode"],
                            "application": apps[0],
                            "version": apps[1],
                            "appspace": apps[2],
                            "profile": apps[3],
                            "status": apps[4],
                            "cfg_state": apps[5]
                        }
                        # print(appd)
                        applist.append(appd)
                    appslc += 1
            lc += 1
        # end get appnodes of appspace
        root_elem = {
            "bw_app_ident": ap["appspace"].replace('receiver', '').replace('outbound', ''),
            "appspace": ap,
            "appnodes": apn_list,
            "applications": applist
        }
        jout.append(root_elem)

    return json.dumps(jout)


def stop_appnode(args):
    if args.bw_ident is not None and args.hostname is not None:
        # lets derive app node and app space for it is hl7 apps that are isolated
        # bw_ident will come from bw as HL7-Endpoint-ID.outbound and be set to
        #appspace of HL7EndpointIDoutbound and appnode of HL7EndpointIDoutbound-i04 the end of the hostname lower case
        asp = args.bw_ident.split('.')
        aspc = asp[0].replace('-', '')
        args.appspace = aspc+asp[1].lower()
        #print(args.appspace)
        h = args.hostname.split('.')
        #print(h[0])
        args.appnode = args.appspace+'-'+h[0][-3:].lower()
        #print(args.appnode)
        
    # build out function to stop appnode since we will be moving to each app having it's own appspace with clustered appnodes for HL7 endpoints
    # print('function to stop an appnode')
    try:
        stop_out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin stop -timeout 1 -d "+args.domain+" -appspace "+args.appspace+" -appnode "+args.appnode, shell=True)
        return stop_out
    except subprocess.CalledProcessError as e:
        # bail out and bubble up
        return e


def restart_app(args):
    # this is a sequence of calls
    # 1. get apps is already running or stopped
    # 2. get appnodes, have to loop through them
    # 3. stop if already started,
    # 4. start app,
    # 5. return show apps\
    init_apps_state = json.loads(show_apps_for_appspace(args))
    app_nodes = json.loads(show_appnodes(args))
    # print(app_nodes)
    # print(init_apps_state)
    # print(type(init_apps_state))
    for a in init_apps_state:
        if a["endpoint"].startswith(args.bw_ident+'.'):
            # print(a)
            for an in app_nodes:
                #get the app data on the app node
                node_apps = json.loads(show_apps_for_appnode(args, an["appnode"]))
                for app in node_apps:
                    # I think when app is in stopping state we hang it issuing start so check and skip
                    if app["status"].lower() == "stopping":
                        continue
                    if a["endpoint"] == app["endpoint"]:
                        if app["status"].lower() == "running":
                            # stop it first
                            try:
                                stop_out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin stop -d "+args.domain+" -a "+args.appspace+" -n "+an["appnode"]+" application "+a["endpoint"]+" "+a["version"], shell=True)
                            except subprocess.CalledProcessError as e:
                                #bail out and bubble up
                                return e
                            # print(stop_out)
                            time.sleep(30)
                        try:
                            start_out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin start -d "+args.domain+" -a "+args.appspace+" -n "+an["appnode"]+" application "+a["endpoint"]+" "+a["version"], shell=True)
                        except subprocess.CalledProcessError as e:
                            #bail out and bubble up
                            return e
                        # print(start_out)
    return show_apps_for_appspace(args)


def start_appnode(args):
    # print(args)
    # print('Running: '+"/opt/tibco/bw/6.6/bin/bwadmin start -domain "+args.domain+" -appspace "+args.appspace+" -appnode "+args.appnode)
    try:
        out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin start -domain "+args.domain+" -appspace "+args.appspace+" -appnode "+args.appnode, shell=True)
        return out
    except subprocess.CalledProcessError as e:
        print(e)


def start_app(args):
    # print(args)
    # print('Running: '+"/opt/tibco/bw/6.6/bin/bwadmin start -d "+args.domain+" -a "+args.appspace+" -n "+args.appnode+" application "+args.appname+" "+args.appver)
    try:
        out = subprocess.check_output("/opt/tibco/bw/6.6/bin/bwadmin start -d "+args.domain+" -a "+args.appspace+" -n "+args.appnode+" application "+args.appname+" "+args.appver, shell=True)
        return out
    except subprocess.CalledProcessError as e:
        print(e)


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


def is_alerted(estats):
    if len(estats) > 0:
        #print(estats[0])
        if 'action' in estats[0] and estats[0]['action'] == 'Alerted':
            return True
    return False


def is_max(estats,eprops):
    #print(eprops)
    # get current date and minutes back
    # logic for defaults so we aren't with None Type
    auto_restart_max = get_prop_by_name(eprops, 'auto_restart_max')
    if auto_restart_max is None:
        auto_restart_max = 3
    else:
        auto_restart_max = int(auto_restart_max)
    auto_restart_minutes_window = get_prop_by_name(eprops, 'auto_restart_minutes_window')
    if auto_restart_minutes_window is None:
        auto_restart_minutes_window = 30
    else:
        auto_restart_minutes_window = int(auto_restart_minutes_window)
    current_time = datetime.now()
    past_time = current_time - timedelta(minutes=auto_restart_minutes_window)
    auto_start_count = 0
    for est in estats:
        if est['action'] == 'Auto-Restart':
            # is between time window
            if est['modified'] < current_time and est['modified'] > past_time:
                auto_start_count += 1
    #print(auto_start_count)
    if auto_start_count >= auto_restart_max:
        return True
    return False


def insert_restart_status(rid):
    sqlin = "insert into endpoint_status (endpoint_id, app_state, action, modified) values ("+str(rid)+", 'Running', 'Auto-Restart',getdate())"
    cursor = cnxn.cursor()
    cursor.execute(sqlin)
    cursor.commit()


def auto_restart(args):
    # rebuilt restart with new cluster setup and naming.
    # get state of everything first
    domain_state = json.loads(showall(args))
    # print(domain_state)
    # find stopped apps and appnodes
    appnodes_to_restart = []
    apps_to_restart = []
    ecfgs_to_restart = []
    endpoints_maxed = []
    for ap in domain_state:

        for aps in ap["applications"]:
            # print(aps)
            if aps["status"].lower() == 'stopped':
                # get config for auto restart
                bwid = aps["application"].split('.')[0]
                e = get_config(args, {"bw_ident": bwid})
                if e is None:
                    # not an endpoint app
                    continue
                ar_start = get_prop_by_name(e['properties'], 'auto_restart')
                # get status table info 
                # print()
                # print(e)
                # print()
                estats = get_endpoints_stats(e['endpoint']['id'])
                # print(estats)
                # print(ar_start)
                if ar_start is not None and ar_start.lower() == 'false':
                    # print('auto start false, ignoring endpoint')
                    # specifically set to not restart
                    continue
                if is_alerted(estats):
                    # we don't try again if last record is Alerted
                    #print('already alerted, ignoring endpoint for restart')
                    continue
                if is_max(estats, e['properties']):
                    #record we hit max for error handling
                    #print('endpoint has hit max restarts')
                    endpoints_maxed.append(e['endpoint'])
                    #we hit max, don't restart
                    continue
                if ar_start is None or ar_start.lower() == 'true':
                    #print('endpoint should be restarted')
                    apps_to_restart.append(aps)
                    ecfgs_to_restart.append(e['endpoint'])
                    insert_restart_status(e['endpoint']['id'])
                    for an in ap["appnodes"]:
                        # print(an)
                        if an['status'].lower() == 'stopped' and an['appnode'] == aps['appnode']:
                            appnodes_to_restart.append(an)
    # print(appnodes_to_restart)
    # print(apps_to_restart)
    # restart appnode then restart app
    for a in appnodes_to_restart:
        args.appspace = a["appspace"]
        args.appnode = a["appnode"]
        ao = start_appnode(args)
        #print(ao)
    for p in apps_to_restart:
        args.appspace = p["appspace"]
        args.appnode = p["appnode"]
        args.appname = p["application"]
        args.appver = p["version"]
        ap = start_app(args)
        #print(ap)


    results = {"maxed": endpoints_maxed, "restarted": ecfgs_to_restart}
    sys.stdout.write(json.dumps(results))
    
if args.cmd.lower() == "showapps":
    print(show_apps_for_appspace(args))
if args.cmd.lower() == "showall":
    print(showall(args))
if args.cmd.lower() == "shownodes":
    print(show_appnodes(args))
if args.cmd.lower() == "restartapp":
    print(restart_app(args))
if args.cmd.lower() == "stopappnode":
    print(stop_appnode(args))
if args.cmd.lower() == "startappnode":
    print(start_appnode(args))
if args.cmd.lower() == "startapp":
    print(start_app(args))
if args.cmd.lower() == "autorestart":
    auto_restart(args)
