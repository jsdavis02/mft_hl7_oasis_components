'''
Created on Nov 20, 2018

@author: jdavis24
'''
import argparse
import sys
import csv
import subprocess
import platform
import os
import difflib
import pysftp
from _datetime import datetime, timedelta
import gzip
import pyodbc
from collections import defaultdict
from collections import Counter
import json


#from _threading_local import local


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--segment", dest="segment", help="segment to look for")
parser.add_argument("-e","--element", dest="element", help="dot notation for element in segment Ex for PID 3.4.3 Universal ID Type: 3.4.3")
parser.add_argument("-se", "--includesubelements", dest="includesubelements", help="when you want element parsing to include any sub elements set to true")
parser.add_argument("-nt", "--notrim", dest="notrim", help="when you want element parsing to not trim the value set to 'yes'")
parser.add_argument("-ev", "--includeemptyvals", dest="show_empty", help="include empty values in output of element parse yes or no")
parser.add_argument("-v", "--verbose", dest="verbose", help="set verbosity level [default: %(default)s]")
parser.add_argument("-i", "--input", dest="input", help="full path to input file")

parser.add_argument("-o", "--output", dest="output", help="full path to output file if not std out")
parser.add_argument("-c", "--command", dest="cmd", help="ep=element parse, " +
                                                        "fsp=file split, " +
                                                        "fdc=file dump clean, " +
                                                        "val=run validation, " +
                                                        "vst=validate message set, " +
                                                        "tx=translate msg hl7->xml->hl7, " +
                                                        "dif=run diff, " +
                                                        "garch=get daily archive file to test against, " +
                                                        "tsr=run full test, " +
                                                        "grt=getroute, " +
                                                        "epb=element parse batch")
parser.add_argument("-m", "--message", dest="msg", help="Message Type to split to new file: EX: ADT^A08, MDM^T01 in quotes")
parser.add_argument("-dm", "--destmess", dest="destmess", help="Message Type for destination in route")
parser.add_argument("-g", "--guideline", dest="guideline", help="Guideline to use for validation")
parser.add_argument("-t", "--translatemap", dest="translatemap", help="Map file to run translation with before the _EX.map or _XE.map")
parser.add_argument("-d", "--difffile", dest="difffile", help="Second input file to do diff compare with")
parser.add_argument("-r", "--reportpath", dest="reportpath", help="Folder path to output non data reporting if specified")
parser.add_argument("-x", "--messagemax", dest="messagemax", help="max number of messages to validate in cmds vst or tsr", type=int)
parser.add_argument("-u", "--user", dest="user", help="sql user")
parser.add_argument("-p", "--pass", dest="password", help="sql pass")
parser.add_argument("-si", "--source_id", dest="source_id", help="message source id EX: EPIC, CMAXSS, etc")
parser.add_argument("-ci", "--consumer_id", dest="consumer_id", help="message consumer id EX: EPIC, IMED, etc")
parser.add_argument("-ad", "--archive_date", dest="arch_date",  help="specify Nov_05 or Jun_15 otherwise will do 5 days from today")
parser.add_argument("-ap", "--archive_path", dest="arch_path", help="use path to pull archives instead of route configuration database")
parser.add_argument("-abd", "--archive_batch_days", dest="arch_bat_days", help="number of days back from archive date to pull when running batch")
# parser.add_argument("-mfc", "--message_filter_code", dest="message_filter_code", help="filter element parsing by message")
# parser.add_argument("-mft", "--message_filter_trigger", dest="message_filter_trigger", help="filter element parsing by trigger")
# parser.add_argument('-V', '--version', action='version', version=program_version_message)
args = parser.parse_args(sys.argv[1:])
# print('after parse args: ' + str(args))
# print('segment='+args.segment)


def clean_tmp_file(file):
    os.remove(file)


def line_count(file):
    count = 0
    with open(file) as f:
        count = sum(1 for _ in f)
    return count


def sftp_get(rf, lf, clover):
    print('Getting remote file')

    clover.get(rf, lf)


def get_output_compare(args, routeprops, clover):
    print('Running outbound archive get to match inbound')
    osval = platform.system()
    tmpdir = "/tmp/"
    if(osval == 'Windows'):
        tmpdir = "c:/tmp/"

    cmesstypecode  = ''
    cmesstrig = ''
    ecname = ''
    for p in routeprops:
        if p['name'] == 'clover_destination_archive':
            # print(p['value'])
            configremotefile = p['value'].split('{date}')
            cmesstypecode = p['consumer_messagetypemessagecode']
            cmesstrig = p['consumer_messagetypetriggerevent']
            ecname = p['ecname']
            break

    # print(configremotefile)
    tday = datetime.today()
    # to only handle gz files go back 20 days instead of 1
    if args.arch_date is None :
        yday = tday - timedelta(days=5)
        yesterdays_archive_folder = yday.strftime('%b_%d')
    else:
        yesterdays_archive_folder = args.arch_date
    # to run dependably we need to pull from production, but for testing we will pull from test folder for now
    remotefile = configremotefile[0]+yesterdays_archive_folder+configremotefile[1]
    remotefilenogz = remotefile[:-3]
    localfile = tmpdir+"CMAXX_ADT_out.old.msg.gz"
    gz = True
    if clover.exists(remotefile):
        localfile = tmpdir+ecname+'_'+cmesstypecode+'_'+cmesstrig+'_out.old.msg.gz'
    elif clover.exists(remotefilenogz):
        gz = False
        remotefile = remotefilenogz
        localfile = tmpdir+ecname+'_'+cmesstypecode+'_'+cmesstrig+'_out.old.msg'
    else:
        print('Cannot find server archive at '+remotefile)
        sys.exit(100)
    print('Getting file archive on server at '+remotefile+' and storing at '+localfile)
    sftp_get(remotefile, localfile, clover)

    if gz:
        with open(localfile[:-3], 'wb') as c:
            with gzip.open(localfile, 'rb') as f:
                c.write(f.read())

        #once extracted lets clean up the gz file, especially for prod
        #data we don't want to leave anything behind!
        clean_tmp_file(localfile)
    return localfile


def get_daily_archive(args, routeprops, clover):
    print('Running daily archive pull')
    osval = platform.system()
    tmpdir = "/tmp/"
    if(osval == 'Windows'):
        tmpdir = "c:/tmp/"
    pmesstypecode  = ''
    pmesstrig = ''
    epname = ''
    configremotefile = ''
    tday = datetime.today()
    # to only handle gz files go back 20 days instead of 1
    if args.arch_date is None :
        yday = tday - timedelta(days=5)
        yesterdays_archive_folder = yday.strftime('%b_%d')
    else:
        yesterdays_archive_folder = args.arch_date
    if args.arch_path is not None:
        # not using routes so lets set vars for batch
        configremotefile = args.arch_path.split('{date}')
        epname = 'batch'
        pmesstypecode = yesterdays_archive_folder.split('_')[0]
        pmesstrig = yesterdays_archive_folder.split('_')[1]
    else:    
        # print(routeprops)
        for p in routeprops:
            # print(p)
            if p['name'] == 'clover_source_archive':
                #print(p['value'])
                configremotefile = p['value'].split('{date}')
                pmesstypecode = p['producer_messagetypemessagecode']
                pmesstrig = p['producer_messagetypetriggerevent']
                epname = p['epname']
                break

    # print(configremotefile)

    # to run dependably we need to pull from production, but for testing we will pull from test folder for now
    remotefile = configremotefile[0]+yesterdays_archive_folder+configremotefile[1]
    remotefilenogz = remotefile[:-3]

    localfile = tmpdir+"EPIC_ADT_in.old.msg.gz"
    gz = True
    if clover.exists(remotefile):
        localfile = tmpdir+epname+'_'+pmesstypecode+'_'+pmesstrig+'_in.old.msg.gz'
    elif clover.exists(remotefilenogz):
        gz = False
        remotefile = remotefilenogz
        localfile = tmpdir+epname+'_'+pmesstypecode+'_'+pmesstrig+'_in.old.msg'
    else:
        print('Cannot find server archive at '+remotefile)
        sys.exit(100)
    print('Getting file archive on server at '+remotefile+' and storing at '+localfile)
    sftp_get(remotefile, localfile, clover)
    if gz:
        newlocal = ''
        with open(localfile[:-3],'wb') as c:
            with gzip.open(localfile,'rb') as f:
                c.write(f.read())
            newlocal = c.name
        # once extracted lets clean up the gz file, especially for prod
        # data we don't want to leave anything behind!
        clean_tmp_file(localfile)
        #make sure we return filename after gz extract
        localfile = newlocal
    return localfile


def tx_report_rollup(args, rollupfile):

    print('Rolling up TX Sequence Reports from: '+args.output+"_report.txt to: "+args.reportpath+rollupfile)
    report = args.output+"_report.txt"
    with open(args.reportpath+rollupfile, "a") as bigfile:
        # pull summary first
        with open(report) as r:
            bigfile.write("***************\n")
            bigfile.write("TX Report output:\n")
            bigfile.write("***************\n")
            line = r.readline()
            while line:
                bigfile.write(line)
                line = r.readline()


def run_diff(args):
    print('Running Diff of '+args.input+' and '+args.difffile)

    if args.output != None:
        with open(args.input) as f1, open(args.difffile) as f2:        
            dfer = difflib.HtmlDiff().make_file(f1.readlines(), f2.readlines(), args.input, args.difffile)
            with open(args.output,'a') as h:
                h.write(dfer)
    else:
        with open(args.input) as f1, open(args.difffile) as f2:
            for diff in difflib.context_diff(f1.readlines(), f2.readlines(),fromfile=args.input,tofile=args.difffile):
                sys.stdout.write(diff)


def run_tx(args):
    print('Running TX with input='+args.input+' output='+args.output+' map='+args.translatemap)
    osval = platform.system()
    if osval == 'Linux':
        # TODO make this work on server, but have to update python on server to 3.x
        # so in the meantime we just do tx on windows.
        # print(subprocess.call("which Translator"))
        print('Running TX is not setup for linux yet!')
        return
    txbin = "Translator"
    if osval == 'Windows':
        txbin = "Translator.exe"
    print(subprocess.call([txbin, "-i"+args.input, "-o"+args.output, "-t"+args.translatemap, "-r6"]))


def run_tx_sequence(args):
    print('Doing translation sequencing from HL7 to xml to HL7 test...')
    print('Tibco Translator.exe is expected in path')
    osval = platform.system()
    tmpdir = "/tmp/"
    if osval == 'Windows':
        tmpdir = "c:/tmp/"
    # will be overriding the args for each run so grab for sequence
    if args.reportpath == None:
        args.reportpath = os.path.dirname(args.output)
    args.reportpath = os.path.join(args.reportpath,'')
    seqInput = args.input
    seqOutput = args.output
    seqMapFilePrefix = args.translatemap
    # first run, input same, output and map parms adjusted..
    args.output = tmpdir+os.path.basename(args.input)+".ex.out"
    args.translatemap = seqMapFilePrefix+"_EX.map"
    run_tx(args)
    tx_report_rollup(args, "TXReport.txt")

    # second run, input previous run output, output is original, and map parms adjusted
    args.input = args.output
    args.output = seqOutput
    args.translatemap = seqMapFilePrefix+"_XE.map"
    run_tx(args)
    tx_report_rollup(args, "TXReport.txt")
    clean_tmp_file(tmpdir + os.path.basename(seqInput) + ".ex.out")
    clean_tmp_file(tmpdir + os.path.basename(seqInput) + ".ex.out" + "_report.txt")
    clean_tmp_file(args.output + '_report.txt')
    #reset args.translatemap
    args.translatemap = seqMapFilePrefix


def roll_up_output(rollupfile, tmpfile, summaryfile, errorcount=0):
    rlf = rollupfile+'.good'
    if errorcount > 0:
        rlf = rollupfile+'.bad'
    with open(rlf, "a") as bigfile:
        with open(summaryfile) as r:
            bigfile.write("***************\n")
            bigfile.write("Summary output:\n")
            bigfile.write("***************\n")
            line = r.readline()
            while line:
                bigfile.write(line)
                line = r.readline()
        with open(tmpfile) as r:
            bigfile.write("***************\n")
            bigfile.write("Detail output:\n")
            bigfile.write("***************\n")
            line = r.readline()
            while line:
                bigfile.write(line)
                line = r.readline()

    #run clean tmp of both after testing 
    clean_tmp_file(tmpfile)
    clean_tmp_file(summaryfile)


def get_error_count(summaryFile):
    print('Getting validation error count...')
    errorCount = 0
    with open(summaryFile) as s:
        line = s.readline()
        while line:
            if("SVRTY" in line):
                errorCount  = int(line[36:45])
                break
            line = s.readline()
    return errorCount


def runValSet(args):
    print('Doing full message set validation run...')
    val_results = {'good': {'count': 0, 'msg_controls': [], 'tx_file_name': []}, 'failed': {'count': 0, 'msg_controls': []}}
    # will override input/output args for individual validation calls so get our roll up args now
    messSetInput = args.input
    messSetOutput = args.output
    totallines = line_count(messSetInput)
    controlnum = ''
    osval = platform.system()
    tmpdir = "/tmp/"
    if osval == 'Windows':
        tmpdir = "c:/tmp/"
    with open(messSetInput) as fp:
        line = fp.readline()
        msgcnt = 1
        linecnt = 1
        singleInput = tmpdir+"msg"+str(msgcnt)+".hl7"
        singleOutput = tmpdir+"msg"+str(msgcnt)+".val.out"
        summaryOutput = tmpdir+"Summary_msg"+str(msgcnt)+".val.out"
        fo = open(singleInput, "w")
        while line:
            errorCount = 0
            fo.write(line)
            if "MSH" in line:
                msh = line.split("|")
                # print(msh)
                controlnum = msh[9]
                # print('Control Number is '+msh[9]+' Storing in '+controlnum)
            if "[new message]" in line or linecnt == totallines:
                print('skipping new message line or end of file so running validation of message')
                args.input = singleInput
                args.output = singleOutput
                fo.close()
                run_validation(args)
                # lets get actual error count from summary file
                errorCount = get_error_count(summaryOutput)
                print('Error Count: '+str(errorCount))

                if errorCount == 0:
                    val_results['good']['count'] += 1
                    val_results['good']['msg_controls'].append(controlnum)
                    # print('saved cntrl num: '+controlnum)
                    if args.cmd == 'tsr':
                        # run tx sequence for message
                        args.output = singleInput+".tx.out"
                        run_tx_sequence(args)
                        val_results['good']['tx_file_name'].append(args.output)
                else:
                    val_results['failed']['count'] += 1
                    val_results['failed']['msg_controls'].append(controlnum)
                    # print('saved cntrl num: '+controlnum)
                # run function to pull in output and clean input
                clean_tmp_file(singleInput)
                roll_up_output(messSetOutput, singleOutput, summaryOutput, errorCount)

                # setup for next message split
                if linecnt < totallines:
                    msgcnt += 1
                    singleInput = tmpdir+"msg"+str(msgcnt)+".hl7"
                    singleOutput = tmpdir+"msg"+str(msgcnt)+".val.out"
                    summaryOutput = tmpdir+"Summary_msg"+str(msgcnt)+".val.out"
                    fo = open(singleInput, "w")
            line = fp.readline()
            linecnt += 1
            # if we have a max message count parm and we are past it, break out
            if args.messagemax is not None and msgcnt > args.messagemax:
                # stop while loop
                line = None
                break

        fo.close()
        print(val_results)
        return val_results


def run_validation(args):
    print('Doing validation run - HVInstream[.exe] is expected to be in PATH')

    osval = platform.system()
    hvin = "HVInStream"
    if osval == 'Windows':
        hvin = "HVInStream.exe"
    print('Executing: '+hvin+" -i"+args.input+" -g"+args.guideline+" -o"+args.output)
    print(subprocess.call([hvin,"-i"+args.input,"-g"+args.guideline,"-o"+args.output]))


def run_file_clean(args):
    print('Doing file dump clean operation...')
    if args.output is not None and len(args.output) > 0:
        fo = open(args.output, "w")
    else:
        fo = open(args.input + '.cln', "w")
    with open(args.input) as fp:
        line = fp.readline()
        cnt = 1

        while line:
            if "[new message]" in line:
                print('skipping new message line')
            else:
                if "MSH|" in line:
                    if line.find("MSH|") > 0:
                        # clean everything before MSH
                        # TODO below is not slicing right fix it
                        line = line[line.find("MSH|"):]

                    fo.write("[new message]\n")
                # print(line, end = "")
                fo.write(line)
            cnt += 1
            line = fp.readline()
    fo.close()
    return fo.name


def run_file_split(args):
    returnval = {}
    print('Doing file split operation on messages with: '+args.msg+' and file input: '+args.input)
    if args.output is not None and len(args.output) > 0:
        fo = open(args.output, "w")
    else:
        fo = open(args.input + '.splt', "w")
    with open(args.input) as fp:
        line = fp.readline()
        cnt = 1
        outcnt =0
        inmsgtosplit = False
        while line:
            if "MSH|^~\&" in line:
                #print(line)
                #print(type(args.msg))
                if args.msg in line:
                    if outcnt > 0:
                        fo.write("[new message]\n")
                    #print(args.msg)
                    #print('Found Message to split into '+ fo.name)
                    inmsgtosplit = True
                    # start outputting until next MSH
                    outcnt += 1
                else:
                    inmsgtosplit = False
            if inmsgtosplit :
                if "[new message]" not in line:
                    # print(line, end = "")
                    fo.write(line)
            cnt += 1
            line = fp.readline()
        returnval['msg_count'] = outcnt
        returnval['message'] = args.msg
    fo.close()
    returnval['filename'] = fo.name
    return returnval


def run_element_parse(args):
    distinctvals = set()
    valcounts = {}
    elscol = args.element.split(".")
    delims = ['|','^','~','\\','&']
    # print(str(elscol))
    print('Running element parse on '+args.input+' with segment: '+ args.segment + ' and element: '+ args.element)
    segmentfieldmax = 0
    with open(args.input) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            els = line.split(delims[0])
            if args.segment in els[0]:
                if len(els) > segmentfieldmax:
                    segmentfieldmax = len(els)
                # print(els)
                # print(elscol[0])
                # print(str(els[int(elscol[0])]))
                edex = 0
                val = ''
                # print(len(elscol))
                while edex < len(elscol):
                    #print('segment line = ' + str(els))
                    #print('element index = ' + str(edex))
                    #print('element number = ' + elscol[edex])
                    #print(int(elscol[edex])-1)
                    #print(len(els))
                    #print(els)
                    if edex >= len(els):
                        break
                    if int(elscol[edex])-1 > len(els):
                        edex += 1
                        break
                    if edex > 0:
                        val = els[int(elscol[edex])-1]
                        els = els[int(elscol[edex])-1].split(delims[edex+1])
                    else:
                        val = els[int(elscol[edex])]
                        els = els[int(elscol[edex])].split(delims[edex+1])
                    # print(str(val))
                    edex += 1
                if len(val) > 0 or args.show_empty == "yes":
                    if args.notrim != "yes":
                        val = val.strip()
                    if args.includesubelements != "yes":
                        for d in delims:
                            if(d in val):
                                val = val[0:val.find(d)]
                    distinctvals.add(val)
                    if len(val) < 1:
                        val = 'EMPTY'
                    if val in valcounts:
                        valcounts[val] = valcounts[val]+1
                    else:
                        valcounts[val] = 1
            line = fp.readline()
            cnt += 1
    print(distinctvals)
    print(valcounts)
    print('Maximum Fields in Segment: '+str(segmentfieldmax-1))
    maxvallength = 0
    for val in distinctvals:
        if maxvallength < len(val):
            maxvallength = len(val)
    print("Maximum character length of code set: " + str(maxvallength))
    if args.output is not None and len(args.output) > 0:
        # output to import file for tibco standards code tables
        fieldnames = ["Code", "Desc", "Expl", "Note 1", "Note 2", "Note 3"]
        with open(args.output, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
            writer.writeheader()
            for val in distinctvals:
                if maxvallength < len(val):
                    maxvallength = len(val)
                writer.writerow({'Code': val, 'Desc': 'Epic Value'})
        print("")
        print('Generated csv file ' + args.output + ' for code values to import in Segment ' + args.segment + ' at location ' + args.element)
    return valcounts


def full_test_run(args):
    print('Running full test sequence...')
    osval = platform.system()
    tmpdir = "/tmp/"
    tday = datetime.today()
    if osval == 'Windows':
        tmpdir = "c:/tmp/"
    # full test run if date not specified set here
    if args.arch_date is None :
        yday = tday - timedelta(days=5)
        args.arch_date = yday.strftime('%b_%d')
    else:
        args.arch_date = args.arch_date
    routeprops = get_route_props_from_db(args)
    # print(routeprops)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    clover = pysftp.Connection(host="virps0pim50i01",username="hci",password="gofish", cnopts=cnopts)
    # get input data from clover archive
    # args.output = tmpdir+"input_archive.msg"
    inputarchive = get_daily_archive(args, routeprops, clover)

    args.output = tmpdir+"output_archive.msg"
    output_archive = get_output_compare(args, routeprops, clover)
    clover.close()
    # clean file
    args.output = None
    args.input = inputarchive
    iarchclean = run_file_clean(args)
    args.input = output_archive
    oarchclean = run_file_clean(args)
    # split out the msg set we are testing
    args.input = iarchclean
    iarchsplitrp = run_file_split(args)
    iarchsplit = iarchsplitrp['filename']
    # print(iarchsplitrp)
    # store count in props
    add_daily_message_count_to_route_props_db(args, routeprops, iarchsplitrp['msg_count'], "clover_source_archive")
    args.input = oarchclean
    args.output = None
    oarchsplitrp = run_file_split(args)
    oarchsplit = oarchsplitrp['filename']
    # store count in props
    add_daily_message_count_to_route_props_db(args, routeprops, oarchsplitrp['msg_count'], "clover_destination_archive")
    # run validation
    args.input = iarchsplit
    args.output = os.path.join(args.reportpath,'validation_report.out')
    # tx is run from val loop when cmd is tsr 'this function'
    val_results = runValSet(args)
   
    # find in clover output
    for controlnum in val_results['good']['msg_controls']:
        # we can use file split with msg changed to control
        args.msg = controlnum
        args.input = oarchsplit
        args.output = tmpdir+controlnum+".out.hl7"
        run_file_split(args)
    # run diff
    args.output = os.path.join(args.reportpath,'archive_tx_diff.html')
    diff_count = 0
    while diff_count < len(val_results['good']['tx_file_name']):
        args.input = val_results['good']['tx_file_name'][diff_count]
        args.difffile = tmpdir+val_results['good']['msg_controls'][diff_count]+".out.hl7"
        run_diff(args)
        diff_count += 1
    # clean up everything but the reports so no data is left, especially prod data outside error/diffs
    clean_tmp_file(inputarchive)
    clean_tmp_file(output_archive)
    clean_tmp_file(iarchclean)
    clean_tmp_file(oarchclean)
    clean_tmp_file(iarchsplit)
    clean_tmp_file(oarchsplit)
    valcount = 0
    while valcount < len(val_results['good']['tx_file_name']):
        clean_tmp_file(tmpdir + val_results['good']['msg_controls'][valcount] + ".out.hl7")
        clean_tmp_file(val_results['good']['tx_file_name'][valcount])
        valcount += 1


def add_daily_message_count_to_route_props_db(args, routeprops, msg_count, propkey):
    print('adding route property of daily message count from clover')
    # print(routeprops)
    # print(msg_count)
    sqlinsert = "insert into dbo.route_props (route_id, name, value) values ("
    sqlupdate = "update dbo.route_props set value = '" + str(msg_count) + "' where route_id = "
    if args.arch_date is None :
        # we do not want to add an assumed date for this function so just return
        return
    for p in routeprops:
        if p['name'] == propkey:
            sqlinsert += str(p['route_id'])
            sqlupdate += str(p['route_id'])
            if 'source' in p['name']:
                sqlinsert += ", 'clover_source_count_"
                sqlupdate += " and name = 'clover_source_count_"
            else:
                sqlinsert += ", 'clover_destination_count_"
                sqlupdate += " and name = 'clover_destination_count_"
            sqlinsert += str(args.arch_date) + "', '" + str(msg_count) + "')"
            sqlupdate += str(args.arch_date) + "'"
            break


    # print(sqlinsert)
    # print(sqlupdate)
    server = 'tcp:L01PS0INF50DA02'
    database = 'oasis'
    username = args.user
    password = args.password
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    cursor.execute(sqlupdate)
    if cursor.rowcount == 0:
        cursor.execute(sqlinsert)
    cursor.commit()


def get_route_props_from_db(args):
    print('Pulling route properties configuration')
    # print(args.msg)
    # print(args.destmess)
    # print(args.msg.split('^'))
    # print(args.destmess.split('^'))
    propslist = []
    prd_messtypecode = args.msg.split('^')[0]
    prd_messtrigcode = args.msg.split('^')[1]
    cnsmr_messtypecode = args.destmess.split('^')[0]
    cnsmr_messtrigcode = args.destmess.split('^')[1]
    sqlselect = "SELECT rt.id as route_id, rt.consumer_id, rt.producer_id, rt.producer_messagetypemessagecode, rt.producer_messagetypetriggerevent, "
    sqlselect += "rt.consumer_messagetypemessagecode, rt.consumer_messagetypetriggerevent, ep.endpoint_name as epname, "
    sqlselect += "ep.id as epid, ec.endpoint_name as ecname, ec.id as ecid, rp.id as rpid, rp.name, rp.value "
    sqlselect += "FROM [dbo].[routes] as rt "
    sqlselect += "inner join dbo.route_props as rp on rt.id = rp.route_id "
    sqlselect += "inner join dbo.endpoints as ep on rt.producer_id = ep.id "
    sqlselect += "inner join dbo.endpoints as ec on rt.consumer_id = ec.id "
    sqlselect += "where rt.producer_messagetypemessagecode = '"+prd_messtypecode+ "' and "
    sqlselect += "rt.producer_messagetypetriggerevent = '"+prd_messtrigcode+"' and "
    sqlselect += "rt.consumer_messagetypemessagecode = '"+cnsmr_messtypecode+"' and "
    sqlselect += "rt.consumer_messagetypetriggerevent = '"+cnsmr_messtrigcode+"'"
    # print(sqlselect)
    server = 'tcp:L01PS0INF50DA02'
    database = 'oasis'
    username = args.user
    password = args.password
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    cursor.execute(sqlselect)
    row = cursor.fetchone()
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
        propslist.append(vals)
        row = cursor.fetchone()
        rcount += 1
    # print(propslist)
    return propslist


def element_parse_batch(args):
    print("Executing element parse from clover archives as a batch");
    osval = platform.system()
    tmpdir = "/tmp/"
    tday = datetime.today()
    if osval == 'Windows':
        tmpdir = "c:/tmp/"
    segmentbatch = args.segment.split(',')
    elementbatch = args.element.split(',')
    #print(segmentbatch)
    #print(elementbatch)
    #print(len(segmentbatch))
    #print(len(elementbatch))
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    clover = pysftp.Connection(host="virps0pim50i01",username="hci",password="gofish", cnopts=cnopts)
    lfiles = []
    clfiles = []
    spltfiles = []
    # arch_date is just month and day format so get today so we have year for day iterations
    tday = datetime.today()
    print(tday.year)
    startdate = datetime.strptime(args.arch_date+'_'+str(tday.year), '%b_%d_%Y')
    # get archives from server
    # to only handle gz files go back 20 days instead of 1
    args.arch_bat_days = int(args.arch_bat_days)
    if args.arch_bat_days is not None and args.arch_bat_days > 1:
        # loop each day and get archive
        while args.arch_bat_days > 0:
            lfiles.append(get_daily_archive(args, None, clover))
            args.arch_bat_days -= 1
            startdate = startdate - timedelta(days=1)
            args.arch_date = startdate.strftime('%b_%d')
    else:
        # get the single file set
        lfiles.append(get_daily_archive(args, None, clover))
    # run file clean
    for f in lfiles:
        args.input = f
        clfiles.append(run_file_clean(args))
    # if we have msg parm and set, we need to split
    if args.msg is not None:
        #split in case we are doing more then one message type in batch
        splitreturn = {}
        msgsplit = args.msg.split(',')
        for c in clfiles:
            for m in msgsplit:
                print("Splitting out message: "+m)
                args.msg = m
                msplit = m.split('^')
                args.input = c
                args.output = c+'.'+msplit[0]+'.'+msplit[1]+'.splt'
                splitreturn = run_file_split(args)
                args.output = None
                print(splitreturn)
                spltfiles.append(splitreturn)
    # run parse on each
    allvals = defaultdict(dict)
    listofvalcounts = defaultdict(dict)
    total = 0
    output = defaultdict(dict)

    if len(spltfiles) > 0:
        for s in spltfiles:
            print('Processing split file: ' + str(s))
            args.input = s['filename']
            if s['message'] not in listofvalcounts:
                listofvalcounts[s['message']] = defaultdict(dict)
                #listofvalcounts[s['message']][segmentbatch[idx]] = defaultdict(dict)
                #listofvalcounts[s['message']][segmentbatch[idx]][elementbatch[idx]] = defaultdict(dict)
                listofvalcounts[s['message']] = {'message_count': s['msg_count']}
            else:
                print('Adding '+str(listofvalcounts[s['message']]['message_count'])+' and '+str(s['msg_count']))
                listofvalcounts[s['message']]['message_count'] += s['msg_count']
                print('Total Message Count:'+str(listofvalcounts[s['message']]['message_count']))
            for idx, val in enumerate(segmentbatch):
                args.segment = segmentbatch[idx]
                args.element = elementbatch[idx]
                if segmentbatch[idx] not in listofvalcounts[s['message']]:
                    listofvalcounts[s['message']][segmentbatch[idx]] = defaultdict(dict)
                singlefileparse = run_element_parse(args)
                for ix, vl in singlefileparse.items():
                    print(ix)
                    print(vl)
                    print(listofvalcounts[s['message']][segmentbatch[idx]][elementbatch[idx]])
                    if ix not in listofvalcounts[s['message']][segmentbatch[idx]][elementbatch[idx]]:
                        listofvalcounts[s['message']][segmentbatch[idx]][elementbatch[idx]][ix] = vl
                    else:
                        print('Getting existing count for '+str(ix)+' of '+str(listofvalcounts[s['message']][segmentbatch[idx]][elementbatch[idx]][ix])+' and adding count of '+str(vl))
                        listofvalcounts[s['message']][segmentbatch[idx]][elementbatch[idx]][ix] += vl
                print('valcounts right after parse')
                print(listofvalcounts)
    else:
        listofvalcounts['all'] = defaultdict(dict)
        listofvalcounts['all'] = {'message_count': 'Not Counted'}
        for cf in clfiles:
            args.input = cf
            for idx, val in enumerate(segmentbatch):
                args.segment = segmentbatch[idx]
                args.element = elementbatch[idx]
                if segmentbatch[idx] not in listofvalcounts['all']:
                    print('No '+segmentbatch[idx]+' in listofvalcounts')
                    listofvalcounts['all'][segmentbatch[idx]] = defaultdict(dict)
                singlefileparse = run_element_parse(args)
                for ix, vl in singlefileparse.items():
                    if ix not in listofvalcounts['all'][segmentbatch[idx]][elementbatch[idx]]:
                        listofvalcounts['all'][segmentbatch[idx]][elementbatch[idx]][ix] = vl
                    else:
                        print('Getting existing value:')
                        print(listofvalcounts['all'][segmentbatch[idx]][elementbatch[idx]][ix])
                        listofvalcounts['all'][segmentbatch[idx]][elementbatch[idx]][ix] += vl
                print('valcounts right after parse')
                print(listofvalcounts)
    for vci, vcv in listofvalcounts.items():
        for idx, val in enumerate(segmentbatch):
            if segmentbatch[idx] not in allvals[vci]:
                allvals[vci][segmentbatch[idx]] = {elementbatch[idx]: {}}
            if elementbatch[idx] not in allvals[vci][segmentbatch[idx]]:
                print('No '+elementbatch[idx]+' in allvals')
                allvals[vci][segmentbatch[idx]][elementbatch[idx]] = defaultdict(dict)
            output[vci]['message_count'] = listofvalcounts[vci]['message_count']
            if segmentbatch[idx] not in output[vci]:
                output[vci][segmentbatch[idx]] = {elementbatch[idx]: {}}
            if elementbatch[idx] not in output[vci][segmentbatch[idx]]:
                print('No '+elementbatch[idx]+' in allvals')
                output[vci][segmentbatch[idx]][elementbatch[idx]] = defaultdict(dict)
            elementtotal = 0
            print('List of valcounts')
            print(listofvalcounts[vci][segmentbatch[idx]][elementbatch[idx]])
            for x, y in listofvalcounts[vci][segmentbatch[idx]][elementbatch[idx]].items():
                elementtotal += y
                if x in allvals[vci][segmentbatch[idx]][elementbatch[idx]]:
                    allvals[vci][segmentbatch[idx]][elementbatch[idx]][x] += y
                else:
                    allvals[vci][segmentbatch[idx]][elementbatch[idx]][x] = y
            print("List of allvals")
            print(allvals)
            output[vci][segmentbatch[idx]][elementbatch[idx]]['total'] = elementtotal
            for x, y in allvals[vci][segmentbatch[idx]][elementbatch[idx]].items():
                output[vci][segmentbatch[idx]][elementbatch[idx]][x] = {'count': y, 'percent': str((y/elementtotal)*100)+'%'}

    print(output)
    json.dump(output, open(tmpdir+'elementbatchparse.json', 'w'))


if args.cmd == "grt":
    get_route_props_from_db(args)
if args.cmd == "tsr":
    full_test_run(args)
if args.cmd == "ep":
    run_element_parse(args)
if args.cmd == "fsp":
    run_file_split(args)
if args.cmd == "fdc":
    run_file_clean(args)
if args.cmd == "val":
    run_validation(args)
if args.cmd == "vst":
    runValSet(args)
if args.cmd == "tx":
    run_tx_sequence(args)
if args.cmd == "dif":
    run_diff(args)
if args.cmd == "garch":
    get_daily_archive(args)
if args.cmd == "epb":
    element_parse_batch(args)