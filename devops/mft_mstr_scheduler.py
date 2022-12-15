import argparse
import json
import sys
from datetime import datetime
import time
import socket
import requests

sys.path.append('..')
from devops import util_functions

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-k", "--endpoint_key", dest="endpoint_key", help="endpoint db id key")

args = parser.parse_args(sys.argv[1:])

def do_master_error_audit(args, guid, dt, endpoint_config, msg):
    if dt is None:
        dt = datetime.now()
    audit_data = {
        "ProcessState": "mft-mstr-job-error",
        "MessageGUID": guid,
        "DateTimeofMessage": dt.strftime('%Y-%m-%dT%H:%M:%S'),  # "2020-09-18T09:20:58",
        "proc_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "producer_ident": endpoint_config['endpoint']['bw_process_ident'],
        "description": msg,
        "producer_id": endpoint_config['endpoint']['id'],
        "type": "error",
        "MessageReference": "",
        "data_format": "mft",
        "disk_persist": False,
        "properties": [
            {
                "name": "master_guid",
                "value": guid
            },
            {
                "name": "execution_host",
                "value": socket.gethostname()
            },
        ]
    }
    return util_functions.do_audit_insert(args, audit_data)


def do_master_end_audit(args, guid, dt, endpoint_config):
    if dt is None:
        dt = datetime.now()
    audit_data = {
        "ProcessState": "mft-mstr-job-complete",
        "MessageGUID": guid,
        "DateTimeofMessage": dt.strftime('%Y-%m-%dT%H:%M:%S'),  # "2020-09-18T09:20:58",
        "proc_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "producer_ident": endpoint_config['endpoint']['bw_process_ident'],
        "description": "Multi mft job master job complete",
        "producer_id": endpoint_config['endpoint']['id'],
        "type": "notice",
        "MessageReference": "",
        "data_format": "mft",
        "disk_persist": False,
        "properties": [
            {
                "name": "master_guid",
                "value": guid
            },
            {
                "name": "execution_host",
                "value": socket.gethostname()
            },
        ]
    }
    return util_functions.do_audit_insert(args, audit_data)


def do_master_start_audit(args, guid, dt, endpoint_config):
    if dt is None:
        dt = datetime.now()
    audit_data = {
        "ProcessState": "mft-mstr-job-start",
        "MessageGUID": guid,
        "DateTimeofMessage": dt.strftime('%Y-%m-%dT%H:%M:%S'),  # "2020-09-18T09:20:58",
        "proc_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "producer_ident": endpoint_config['endpoint']['bw_process_ident'],
        "description": "Starting a multi mft master job",
        "producer_id": endpoint_config['endpoint']['id'],
        "type": "notice",
        "MessageReference": "",
        "data_format": "mft",
        "disk_persist": False,
        "properties": [
            {
                "name": "master_guid",
                "value": guid
            },
            {
                "name": "execution_host",
                "value": socket.gethostname()
            },
        ]
    }
    return util_functions.do_audit_insert(args, audit_data)


def get_trigger_schedule(schedules):
    for s in schedules:
        if s['freq_type'] == 'Trigger':
            rem = []
            for k, v in s.items():
                # print('Key:'+str(k)+' Value:'+str(v))
                if v is None:
                    rem.append(k)
            for r in rem:
                s.pop(r)
            return s
    return None

# input by bw is stdin json so get it here
input_data = ""
line = None
jdata = None
if args.endpoint_key is None and args.env is None:
    line = sys.stdin.readline()
    while line:
        input_data += line + "\r"
        line = sys.stdin.readline()

    jdata = json.loads(input_data)
else:
    jdata = {"endpoint_id": args.endpoint_key, "env": args.env}

mstr_endpoint_config = util_functions.get_endpoint_config(jdata['endpoint_id'], jdata['env'])
print(mstr_endpoint_config)

# get number of endpoints to fire for loop
job_total = int(util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'total_job_count'))
# print(job_total)
sleep_interval = int(util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'sleep_interval'))
print(sleep_interval)
# need to get master guid
mstr_guid = util_functions.get_guid(env=jdata['env'])
if mstr_guid is None:
    exit("Could not obtain a Message GUID for Master Job!")
dt_of_message = datetime.now()
# set master job start
mstr_audit = do_master_start_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config)
# print(mstr_audit)

jc = 1
while jc <= job_total:
    pre_delay = util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'pre_delay_'+str(jc))
    post_delay = util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'post_delay_'+str(jc))
    sub_endpoint_id = util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'producer_id_'+str(jc))
    get_response = util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'get_response_'+str(jc))
    no_files_ok = util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'no_files_ok_'+str(jc))
    no_routes_ok = util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'no_routes_ok_'+str(jc))
    wait_response = util_functions.get_prop_field_or_none(mstr_endpoint_config['properties'], 'wait_response_'+str(jc))
    if wait_response is None:
        wait_response = 5
    else:
        wait_response = int(wait_response)
    sub_endpoint_config = util_functions.get_endpoint_config(sub_endpoint_id, jdata['env'])
    delete_only = util_functions.get_prop_field_or_none(sub_endpoint_config['properties'], 'delete_only')
    #print(sub_endpoint_config)
    #get schedules
    trigger_schedule = get_trigger_schedule(sub_endpoint_config['schedules'])
    # check a pre delay
    if pre_delay is not None and int(pre_delay) > 0:
        time.sleep(int(pre_delay))
    # print(trigger_schedule)
    response = util_functions.run_mft_producer_check(trigger_schedule, jdata['env'], mstr_guid)
    # print(response)
    if response.status_code != requests.codes.ok:
        msg = 'Producer RESTful call for schedule ID: '+str(trigger_schedule['id'])+' failed with '+str(response.status_code)+' so stopping Master job with GUID: '+str(mstr_guid)
        e_mstr_audit = do_master_error_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config, msg)
        exit(msg)
    # lets give ourselves a second then get sub guid
    time.sleep(1)
    sub_guid = util_functions.get_sub_job_guid(mstr_guid, jdata['env'])
    if sub_guid is None:
        msg = 'Master job with GUID: '+str(mstr_guid)+' failed to get the sub job guid in the 1 second window after invoking that sub job!'
        e_mstr_audit = do_master_error_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config, msg)
        exit(msg)
    start_check = time.time()
    check = time.time()
    time_diff = int(start_check - check)
    if get_response is None or get_response == 'false':
        # here we just wait the time frame in wait_response
        time.sleep(wait_response)
    else:
        job_response = None
        while time_diff < wait_response:
            time.sleep(sleep_interval)
            # check for response and break once we have it
            job_response = util_functions.check_job_response(sub_guid, jdata['env'], sub_endpoint_id, delete_only)
            if job_response == 'mft-job-complete':
                # job finished no need to continue time check loop
                break
            if job_response == 'mft-no-files-complete':
                if no_files_ok is None or no_files_ok == 'false':
                    msg = 'Job with GUID: '+str(sub_guid)+' had no files and no_files_ok_'+str(jc)+' is not set to "true"! so stopping Master job with GUID: '+str(mstr_guid)
                    e_mstr_audit = do_master_error_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config, msg)
                    exit(msg)
                else:
                    # no files ok and job finished so move on
                    break
            if job_response == 'mft-job-fail':
                msg = 'Job with GUID: '+str(sub_guid)+' failed and get_response_'+str(jc)+' is set to "true"! so stopping Master job with GUID: '+str(mstr_guid)
                e_mstr_audit = do_master_error_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config, msg)
                exit(msg)
            if job_response == 'no_active_routes':
                if no_routes_ok:
                    # we are ok with this so move on
                    break
                else:
                    # fail it
                    msg = 'Job with GUID: '+str(sub_guid)+' has no active routes and no_routes_ok_'+str(jc)+' is NOT set to "true"! so stopping Master job with GUID: '+str(mstr_guid)
                    e_mstr_audit = do_master_error_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config, msg)
                    exit(msg)
            check = time.time()
            time_diff = int(check - start_check)
            # print(check)
            # print(time_diff)
        if job_response is None:
            msg = 'Job with GUID: '+str(sub_guid)+' did not set a finish or fail state and get_response_'+str(jc)+' is set to "true" and wait_response_'+str(jc)+' timed out so stopping Master job with GUID: '+str(mstr_guid)
            e_mstr_audit = do_master_error_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config, msg)
            exit(msg)
    # if here we got response needed or did audit and exited so check for post delay
    if post_delay is not None and int(post_delay) > 0:
        time.sleep(int(post_delay))
    jc = jc+1

# set master job complete
mstr_audit_done = do_master_end_audit(args, mstr_guid, dt_of_message, mstr_endpoint_config)
