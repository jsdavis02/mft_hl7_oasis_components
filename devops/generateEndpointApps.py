import argparse
import sys
import configparser
import pyodbc
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-k", "--key", dest="endpoint_key", help="primary key or bw ident string for single endpoint")
parser.add_argument("-c", "--cmd", dest="cmd", help="1=all active, 2=all, 3=all active outbound, 4=all active receivers, 5=specific endpoint specify ident or id with -k")
args = parser.parse_args(sys.argv[1:])
print('running endpoint generation')
# get db records based off selection

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
elist  = []
sql = None
if args.cmd == '1':
    sql = "select * from endpoints where active = 1 and direction <> 'splitter' and type = 'HL7'"
elif args.cmd == '2':
    sql = "select * from endpoints where type = 'HL7'"
elif args.cmd == '3':
    sql = "select * from endpoints where active = 1 and direction = 'consumer' and type = 'HL7'"
elif args.cmd == '4':
    sql = "select * from endpoints where active = 1 and direction = 'producer' and type = 'HL7'"
elif args.cmd == '5':
    if args.endpoint_key.isdigit():
        sql = "select * from endpoints where id = "+args.endpoint_key
    else:
        sql = "select * from endpoints where bw_process_ident = '"+args.endpoint_key+"'"
else:
    exit(1)

# print(sql)
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

# print(elist)

for ep in elist:

    psql = "select * from endpoint_props where endpoint_id = "+str(ep['id'])
    cursor = cnxn.cursor()
    cursor.execute(psql)
    row = cursor.fetchone()
    column_names = [d[0] for d in cursor.description]
    ep['properties'] = []
    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            vals[column_names[x]] = row[x]
            x += 1
        ep['properties'].append(vals)
        row = cursor.fetchone()
        rcount += 1

# print(elist)

# loop through and run generation
for e in elist:
    # todo check for bw ident first

    # get info we need out of dict
    direction = e['direction']
    host = 'virps0esb20i03' #assume dev bw node
    port = 0
    msinterval = 10000
    numretry = 3
#    print(direction)
    for p in e['properties']:
        if 'producer' in direction:
            if 'producer_host' in p['name'] and args.env in p['env']:
                host = p['value']
            if 'producer_port' in p['name'] and args.env in p['env']:
                port = p['value']
        if 'consumer' in direction:
            if 'consumer_host' in p['name'] and args.env in p['env']:
                host = p['value']
            if 'consumer_port' in p['name'] and args.env in p['env']:
                port = p['value']
            if 'send_retry_max' in p['name'] and args.env in p['env']:
                numretry = p['value']
            if 'send_retry_sleep' in p['name'] and args.env in p['env']:
                msinterval = p['value']
#    print(port)
#    print(host)
    # todo print run command
    if 'producer' in direction:
        subprocess.run('python generateReceiverBWApp.py -a '+e['bw_process_ident']+' -d '+str(host)+' -p '+str(port))
    if 'consumer' in direction:
        subprocess.run('python generateOutboundBWApp.py -a '+e['bw_process_ident']+' -d '+str(host)+' -p '+str(port)+' -m '+str(msinterval)+' -n '+str(numretry))
