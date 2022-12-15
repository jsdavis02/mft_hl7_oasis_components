import argparse
import sys
import pyodbc
import configparser
import os
import glob
import subprocess
import hl7
import time



parser = argparse.ArgumentParser()
parser.add_argument("-r", "--route", dest="route", help="Route to test run")
parser.add_argument("-e", "--env", dest="env", help="Environment config to use [DEV,TST,PPRD,PRD]")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")
parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-m", "--message", dest="msg", help="Message Type to split to new file: EX: ADT^A08, MDM^T01 in quotes")
parser.add_argument("-x", "--messagemax", dest="messagemax", help="max number of messages to validate in cmds vst or tsr", type=int)
parser.add_argument("-ad", "--archive_date", dest="arch_date",  help="specify Nov_05 or Jun_15 otherwise will do 5 days from today")
parser.add_argument("-t", "--test_type", dest="test_type", help="specify py or bw for testing just python script sequence or bw send/receive")
args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read("../config.ini")
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

# PULL ROUTE CONFIG
sqlselect = "select * from routes where routes.id = "+args.route
cursor = cnxn.cursor()
cursor.execute(sqlselect)
row = cursor.fetchone()
# print(row)
route = []
column_names = [d[0] for d in cursor.description]
rcount = 1
while row:
  # print (row)
  # print (column_names)
  x = 0
  vals = {}
  while x < len(column_names):
    vals[column_names[x]] = row[x]
    x += 1
  route.append(vals)
  row = cursor.fetchone()
  rcount += 1
#print(route)

# PULL ROUTE PROPERTIES

rtpropselect = "select * from route_props where route_id = "+args.route
cursor = cnxn.cursor()
cursor.execute(rtpropselect)
row2 = cursor.fetchone()
# print(row)
routeprops = []
column_names = [d[0] for d in cursor.description]
rcount = 1
while row2:
  # print (row)
  # print (column_names)
  x = 0
  vals = {}
  while x < len(column_names):
    vals[column_names[x]] = row2[x]
    x += 1
  routeprops.append(vals)
  row2 = cursor.fetchone()
  rcount += 1
print(routeprops)

# PULL source endpoint

sendselect = "select * from endpoints where id = "+str(route[0]['producer_id'])
cursor = cnxn.cursor()
cursor.execute(sendselect)
row3 = cursor.fetchone()
# print(row)
sourceendpoint = []
column_names = [d[0] for d in cursor.description]
rcount = 1
while row3:
  # print (row)
  # print (column_names)
  x = 0
  vals = {}
  while x < len(column_names):
    vals[column_names[x]] = row3[x]
    x += 1
  sourceendpoint.append(vals)
  row3 = cursor.fetchone()
  rcount += 1
print(sourceendpoint)

# PULL source endpoint props

sendpropselect = "select * from endpoint_props where endpoint_id = "+str(sourceendpoint[0]['id'])+" and env = '"+args.env+"'"
cursor = cnxn.cursor()
cursor.execute(sendpropselect)
row4 = cursor.fetchone()
# print(row)
sourceendpointprops = []
column_names = [d[0] for d in cursor.description]
rcount = 1
while row4:
  # print (row)
  # print (column_names)
  x = 0
  vals = {}
  while x < len(column_names):
    vals[column_names[x]] = row4[x]
    x += 1
  sourceendpointprops.append(vals)
  row4 = cursor.fetchone()
  rcount += 1
print(sourceendpointprops)

# PULL consumer endpoint

cendselect = "select * from endpoints where id = "+str(route[0]['consumer_id'])
cursor = cnxn.cursor()
cursor.execute(cendselect)
row4 = cursor.fetchone()
# print(row)
consumerendpoint = []
column_names = [d[0] for d in cursor.description]
rcount = 1
while row4:
  # print (row)
  # print (column_names)
  x = 0
  vals = {}
  while x < len(column_names):
    vals[column_names[x]] = row4[x]
    x += 1
  consumerendpoint.append(vals)
  row4 = cursor.fetchone()
  rcount += 1
print(consumerendpoint)

# PULL consumer endpoint props

cendpropselect = "select * from endpoint_props where endpoint_id = "+str(consumerendpoint[0]['id'])+" and env = '"+args.env+"'"
cursor = cnxn.cursor()
cursor.execute(cendpropselect)
row5 = cursor.fetchone()
# print(row)
consumerendpointprops = []
column_names = [d[0] for d in cursor.description]
rcount = 1
while row5:
  # print (row)
  # print (column_names)
  x = 0
  vals = {}
  while x < len(column_names):
    vals[column_names[x]] = row5[x]
    x += 1
  consumerendpointprops.append(vals)
  row5 = cursor.fetchone()
  rcount += 1
print(consumerendpointprops)
cport = None
chost = None
phost = None
pport = None
for p in consumerendpointprops:
  if p['name'] == 'consumer_port':
    cport = p['value']
  if p['name'] == 'consumer_host':
    chost = p['value']
for p in sourceendpointprops:
  if p['name'] == 'producer_port':
    pport = p['value']
  if p['name'] == 'producer_host':
    phost = p['value']

if args.input is not None:
  testmessage = args.input
  datadir = os.path.join(os.path.dirname(sys.argv[0]), '..', 'data_samples')
  trdirs = glob.glob(os.path.join(datadir, "test_run_*"))
  testrundir = 'test_run_1'
  if len(trdirs) > 0:
    testrundir = testrundir[:-1]+str(len(trdirs)+1)
    os.makedirs(os.path.join(datadir, testrundir))
  with open(args.input) as fp:
    line = fp.readline()
    if "MSH|^~\&" in line:
      msh = line.split("|")
      controlnum = (msh[9])

  if args.test_type is None or args.test_type == "py":
    print("Convert file: "+testmessage+" to: "+testmessage+".in.json")
    subprocess.run('python HL7-JSONConverter.py -i '+testmessage+' -o '+testmessage+'.in.json')
    print("Run TX wrapper file: "+tx_script+" with input: "+testmessage+".in.json and output: "+testmessage+'.updated.json')
    subprocess.run('python '+tx_script+' -i '+testmessage+'.in.json -o '+testmessage+'.updated.json -e '+args.env, cwd='../tx_wraps')
    print("Convert file: "+testmessage+".updated.json to: "+testmessage+".updated.hl7")
    subprocess.run('python HL7-JSONConverter.py -i '+testmessage+'.updated.json -o '+testmessage+'.updated.hl7')
  else:
    print('doing send through bw')
    #get control number
    m = ""
    with open(testmessage) as td:
      line = td.readline()
      while line:
        m += line + "\r"
        line = td.readline()
    h = hl7.parse(m)
    cn = str(h.segment('MSH')(10))
    print('Control Number is: '+cn)

    # do mllp_send to BW
    print('Running Command: '+'mllp_send -p '+str(pport)+' -f '+testmessage+' --loose '+str(phost))
    subprocess.run('mllp_send -p '+pport+' -f '+testmessage+' --loose '+phost)
  
    #wait then check db audit
    time.sleep(5)
    sqlaudit = "select top 1 * from audit where MessageControlID = '"+cn+"' and ProcessState = 'hl7-before-send' and consumer_id = "+str(consumerendpoint[0]['id'])+"order by proc_time DESC"
    cursor = cnxn.cursor()
    cursor.execute(sqlaudit)
    row6 = cursor.fetchone()
    # print(row)
    auditrecord = []
    column_names = [d[0] for d in cursor.description]
    rcount = 1
    while row6:
      # print (row)
      # print (column_names)
      x = 0
      vals = {}
      while x < len(column_names):
        vals[column_names[x]] = row6[x]
        x += 1
      auditrecord.append(vals)
      row6 = cursor.fetchone()
      rcount += 1
    print(auditrecord)
  
    with open(testmessage+'.updated.hl7','w') as out:
      if len(auditrecord) > 0:
        out.write(auditrecord[0]['MessagePayload'])
      else:
        out.write('')
    out.close()

print(controlnum)

