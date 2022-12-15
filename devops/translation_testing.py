import argparse
import sys
import pyodbc
import configparser
import pysftp
import os
import gzip
from _datetime import datetime, timedelta
import shutil
import glob
import HL7MessageParser
import subprocess
import difflib
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

# Execute test against a local file
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

else:
    source = None
    destination = None
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    clover = pysftp.Connection(host="virps0pim50i01",username="hci",password="gofish", cnopts=cnopts)
    tday = datetime.today()
    yday = tday - timedelta(days=5)
    yesterdays_archive_folder = yday.strftime('%b_%d')
    if args.arch_date is not None:
        yesterdays_archive_folder = args.arch_date
    configremotefile = None
    tx_script = None
    for p in routeprops:
        if p['name'] == 'clover_source_archive':
            configremotefile = p['value'].split('{date}')
        if p['name'] == 'clover_destination_archive':
            # print(p['value'])
            configremotefile2 = p['value'].split('{date}')
        if p['name'] == 'translate_script':
            tx_script = p['value']
    remotefile = configremotefile[0]+yesterdays_archive_folder+configremotefile[1]
    remotefilenogz = remotefile[:-3]
    
    #output to compare against
    remotefile2 = configremotefile2[0]+yesterdays_archive_folder+configremotefile2[1]
    remotefilenogz2 = remotefile2[:-3]
    
    datadir = os.path.join(os.path.dirname(sys.argv[0]), '..', 'data_samples')
    trdirs = glob.glob(os.path.join(datadir, "test_run_*"))
    testrundir = 'test_run_1'
    if len(trdirs) > 0:
        testrundir = testrundir[:-1]+str(len(trdirs)+1)
    os.makedirs(os.path.join(datadir, testrundir))
    
    localfile = None
    gz = True
    if clover.exists(remotefile):
        localfile = os.path.join(datadir, yesterdays_archive_folder+'_'+os.path.basename(remotefile))
    elif clover.exists(remotefilenogz):
        gz = False
        remotefile = remotefilenogz
        localfile = os.path.join(datadir, yesterdays_archive_folder+'_'+os.path.basename(remotefile))
    else:
        print('Cannot find server archive at '+remotefile)
        sys.exit(100)
    print('Getting file archive on server at '+remotefile+' and storing at '+localfile)
    source = localfile
    if not os.path.exists(localfile):
        clover.get(remotefile, localfile)
        if gz:
            newlocal = ''
            with open(localfile[:-3],'wb') as c:
                with gzip.open(localfile,'rb') as f:
                    c.write(f.read())
                newlocal = c.name
                source = newlocal
    # output stuff
    gz = True
    if clover.exists(remotefile2):
        localfile = os.path.join(datadir, yesterdays_archive_folder+'_'+os.path.basename(remotefile2))
    elif clover.exists(remotefilenogz2):
        gz = False
        remotefile2 = remotefilenogz2
        localfile = os.path.join(datadir, yesterdays_archive_folder+'_'+os.path.basename(remotefile2))
    else:
        print('Cannot find server archive at '+remotefile2)
        sys.exit(100)
    print('Getting file archive on server at '+remotefile2+' and storing at '+localfile)
    destination = localfile
    if not os.path.exists(localfile):
        clover.get(remotefile2, localfile)
        if gz:
            newlocal = ''
            with open(localfile[:-3],'wb') as c:
                with gzip.open(localfile,'rb') as f:
                    c.write(f.read())
                newlocal = c.name       
                destination = newlocal
    args.input = source
    args.output = None
    source = HL7MessageParser.run_file_clean(args)
    #print(source)
    args.input = source
    args.msg = route[0]['producer_messagetypemessagecode']+'^'+route[0]['producer_messagetypetriggerevent']
    #args.output = 
    #print(args.output)
    splitresults = HL7MessageParser.run_file_split(args)
    #print(splitresults)
    #print(args.output)
    source = os.path.join(datadir, route[0]['producer_messagetypemessagecode']+'_'+route[0]['producer_messagetypetriggerevent']+'_'+os.path.basename(source))
    shutil.move(splitresults['filename'], source)
    args.input = destination
    destination = HL7MessageParser.run_file_clean(args)
    #on the rare occasion like route 1 where a file is 
    # conditionally flipped in route to different msg type 
    # we can't find if we split file here
    # args.msg = route[0]['consumer_messagetypemessagecode']+'^'+route[0]['consumer_messagetypetriggerevent']
    # args.input = destination
    # splitresultsout = HL7MessageParser.run_file_split(args)
    # destination = os.path.join(datadir, route[0]['consumer_messagetypemessagecode']+'_'+route[0]['consumer_messagetypetriggerevent']+'_'+os.path.basename(destination))
    # shutil.move(splitresultsout['filename'], destination)
    
    #pull a msg from source
    messSetInput = source
    #print(messSetInput)
    #print(type(messSetInput))
    totallines = HL7MessageParser.line_count(messSetInput)
    controlnums = []
    lastfile = False
    
    with open(messSetInput) as fp:
        line = fp.readline()
        msgcnt = 1
        linecnt = 1
        singleInput = os.path.join(datadir, testrundir, "r_"+args.route+"_msg_"+route[0]['producer_messagetypemessagecode']+'_'+route[0]['producer_messagetypetriggerevent']+'_'+str(msgcnt)+".hl7")
        #singleOutput = tmpdir+"msg"+str(msgcnt)+".val.out"
        #summaryOutput = tmpdir+"Summary_msg"+str(msgcnt)+".val.out"
        fo = open(singleInput, "w")
        while line:
            #print(line)
            errorCount = 0
            if "MSH|^~\&" in line:
                msh = line.split("|")
                # print(msh)
                controlnums.append(msh[9])
                # print('Control Number is '+msh[9]+' Storing in '+controlnum)
            if ("[new message]" in line or linecnt == totallines) and linecnt > 1:
                # print('skipping new message line or end of file so running validation of message')
                fo.close()
                # setup for next message split
                if linecnt < totallines:
                    msgcnt += 1
                    singleInput = os.path.join(datadir, testrundir, "r_"+args.route+"_msg_"+route[0]['producer_messagetypemessagecode']+'_'+route[0]['producer_messagetypetriggerevent']+'_'+str(msgcnt)+".hl7")
                    fo = open(singleInput, "w")
                else:
                    lastfile = True
                    break
            else:
                if "[new message]" not in line:
                    fo.write(line.strip()+'\r')
            line = fp.readline()
            linecnt += 1
            # if we have a max message count parm and we are past it, break out
            if args.messagemax is not None and msgcnt > args.messagemax:
                # stop while loop
                line = None
                break
    
        fo.close()
        if not lastfile:
            os.remove(singleInput)
    
    testmessages = glob.glob(os.path.join(datadir, testrundir, "r_"+args.route+"_msg_"+route[0]['producer_messagetypemessagecode']+'_'+route[0]['producer_messagetypetriggerevent']+"_*.hl7"))
    
    for t in testmessages:
        if args.test_type is None or args.test_type == "py":
            print("Convert file: "+t+" to: "+t+".in.json")
            subprocess.run('python HL7-JSONConverter.py -i '+t+' -o '+t+'.in.json')
            print("Run TX wrapper file: "+tx_script+" with input: "+t+".in.json and output: "+t+'.updated.json')
            subprocess.run('python '+tx_script+' -i '+t+'.in.json -o '+t+'.updated.json -e '+args.env+' -r '+args.route, cwd='../tx_wraps')
            print("Convert file: "+t+".updated.json to: "+t+".updated.hl7")
            subprocess.run('python HL7-JSONConverter.py -i '+t+'.updated.json -o '+t+'.updated.hl7')
        else:
            print('doing send through bw')
            #get control number
            m = ""
            with open(t) as td:
                line = td.readline()
                while line:
                    m += line + "\r"
                    line = td.readline()
            h = hl7.parse(m)
            cn = str(h.segment('MSH')(10))
            print('Control Number is: '+cn)
            
            # do mllp_send to BW
            print('Running Command: '+'mllp_send -p '+str(pport)+' -f '+t+' --loose '+str(phost))
            subprocess.run('mllp_send -p '+pport+' -f '+t+' --loose '+phost)
            
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
    
            #save output for diff
            #print(auditrecord[0].keys())
            with open(t+'.updated.hl7','w') as out:
                if len(auditrecord) > 0:
                    out.write(auditrecord[0]['MessagePayload'])
                else:
                    out.write('')
            out.close()
        
    print(controlnums)
    
    oc = 1
    with open(os.path.join(datadir, testrundir, "diff_roll_up.html"), 'a') as d_out:
        for c in controlnums:
            args.msg = c
            args.input = destination
            args.output = os.path.join(datadir, testrundir, "r_"+args.route+'_msg_'+route[0]['consumer_messagetypemessagecode']+'_'+route[0]['consumer_messagetypetriggerevent']+'_'+str(oc)+'_'+c+"_compare.out.hl7")
            HL7MessageParser.run_file_split(args)
            with open(os.path.join(datadir, testrundir, "r_"+args.route+'_msg_'+route[0]['consumer_messagetypemessagecode']+'_'+route[0]['consumer_messagetypetriggerevent']+'_'+str(oc)+'_'+c+"_compare.out.hl7")) as f1, open(os.path.join(datadir, testrundir,"r_"+args.route+"_msg_"+route[0]['producer_messagetypemessagecode']+'_'+route[0]['producer_messagetypetriggerevent']+'_'+str(oc)+".hl7.updated.hl7")) as f2:
                dfer = difflib.HtmlDiff(wrapcolumn=40).make_file(f1.readlines(), f2.readlines(), os.path.join(datadir, testrundir, "r_"+args.route+'_msg_'+route[0]['consumer_messagetypemessagecode']+'_'+route[0]['consumer_messagetypetriggerevent']+'_'+str(oc)+'_'+c+"_compare.out.hl7"), os.path.join(datadir, testrundir,"r_"+args.route+"_msg_"+route[0]['producer_messagetypemessagecode']+'_'+route[0]['producer_messagetypetriggerevent']+'_'+str(oc)+".hl7.updated.hl7"))
                with open(os.path.join(datadir, testrundir, 'r_'+args.route+'_msg_'+str(oc)+'_diff.html'), 'a') as h:
                    h.write(dfer)
                #dfro = difflib.unified_diff(f1.readlines(), f2.readlines(), os.path.join(datadir, testrundir, "r_"+args.route+'_msg_'+route[0]['consumer_messagetypemessagecode']+'_'+route[0]['consumer_messagetypetriggerevent']+'_'+str(oc)+'_'+c+"_compare.out.hl7"), os.path.join(datadir, testrundir,"r_"+args.route+"_msg_"+route[0]['producer_messagetypemessagecode']+'_'+route[0]['producer_messagetypetriggerevent']+'_'+str(oc)+".hl7.updated.hl7"))
                d_out.write(dfer)
            oc += 1


