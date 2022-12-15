import configparser
import json
import os
import sys
from datetime import date
from datetime import datetime, timedelta, timezone
from datetime import time
import requests
import pyodbc


def get_prop_field_or_none(prop_data_dict_list, key):
    for prop in prop_data_dict_list:
        if key in prop.values():
            for k, v in prop.items():
                if k == 'name' and v == key:
                    # this prop is the one
                    return prop['value']

    return None


def parse_dt_string(dt_string):
    # print(dt_string)
    if dt_string is None:
        return None

    format_list = ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f-0700', '%Y-%m-%dT%H:%M:%S.%f-07:00', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S-%z', '%Y-%m-%dT%H:%M:%S-0700', '%H:%M:%S%z', '%H:%M:%S-0700')
    for fmt in format_list:
        try:
            # print(fmt)
            return datetime.strptime(dt_string, fmt).replace(tzinfo=timezone(-timedelta(hours=7)))
        except ValueError:
            pass
    raise ValueError('Could not parse the date string: '+dt_string+' with the given formats: '+str(format_list))


def do_audit_insert(cmd_args, jdata_in: dict, cnxn=None):
    if cnxn is None:
        cnxn = get_db_connection(get_config(), cmd_args.env)
    cursor = cnxn.cursor()
    vals = []
    cols = []
    for row in cursor.columns(table="audit"):
        # need to know the column type to know if quoted
        if row.column_name in jdata_in.keys():
            cols.append(row.column_name)
            # if not a string, change the val to not be quoted
            # print(row.type_name)
            # print(row.column_name)
            # print(jdata_in[row.column_name])
            # print(type(jdata_in[row.column_name]))
            if 'int' in row.type_name or 'bit' in row.type_name:
                # covers bigint also
                vals.append(str(jdata_in[row.column_name]))
            elif 'datetime' in row.type_name:
                dto = parse_dt_string(jdata_in[row.column_name])
                vals.append("'"+dto.strftime('%Y-%m-%d %H:%M:%S')+"'")
            else:
                vals.append("'"+str(jdata_in[row.column_name]).replace("'", "")+"'")
    # print(cols)
    # print(vals)
    # print(type(vals))
    # print(','.join(cols))
    # print(type(','.join(vals)))
    sql = f"insert into audit ({','.join(cols)}) values ({','.join(vals)})"
    # print(sql)
    cursor.execute(sql)
    cursor.execute("select @@IDENTITY")
    id = int(cursor.fetchval())
    cursor.commit()
    jdata_in['id'] = id
    # print(id)
    committed_props = []
    if 'properties' in jdata_in:
        for prop in jdata_in['properties']:
            statement = "insert into audit_props (audit_id, name, value) values (?, ?, ?)"
            # print(prop['name'])
            # print(prop['value'])
            cursor.execute(statement, id, prop['name'], prop['value'])
            cursor.execute("select @@IDENTITY")
            pid = cursor.fetchval()
            cursor.commit()
            committed_props.append({
                "id": int(pid),
                "name": prop['name'],
                "value": prop['value']
            })
        jdata_in['properties'] = committed_props
    return json.dumps(jdata_in)


def run_mft_producer_check(schedule, env, masterGUID=None):
    current_time = datetime.now(tz=datetime.utcnow().astimezone().tzinfo).strftime('%Y-%m-%dT%H:%M:%S')
    # print(current_time)
    config = get_config()
    rURL = config.get(env, 'mft_engine_rest_url')+'producer_check'
    rAuth = config.get(env, 'rest_auth_string')
    rPayload = json.dumps({"schedule": schedule, "current_run_time": str(current_time), "master_GUID": masterGUID})
    rHeaders = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": rAuth}
    # print(rPayload)
    return requests.post(rURL, data=rPayload, headers=rHeaders)


def get_config():
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.join("..", "config.ini"))
    return config


def get_db_connection(config, env):
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    return cnxn


def get_guid(env):
    cnxn = get_db_connection(get_config(), env)
    sql = "select next value for dbo.message_guid as messageGUID"
    cursor = cnxn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    # print(row[0])
    if row is None:
        return None
    return row[0]


def check_job_response(guid, env, endpoint_id=None, delete_only=None):
    # get states
    cnxn = get_db_connection(get_config(), env)
    sql = "select ProcessState from audit where MessageGUID = ? and  (ProcessState = ? OR ProcessState = ? OR ProcessState = ?) order by created_at desc"
    cursor = cnxn.cursor()
    cursor.execute(sql, guid, 'mft-no-files-complete', 'mft-job-fail', 'mft-job-complete')
    row = cursor.fetchone()
    # print(row[0])
    if row is None:
        return None
    column_names = [d[0] for d in cursor.description]
    job_states = []
    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            vals[column_names[x]] = row[x]
            x += 1
        job_states.append(vals)
        row = cursor.fetchone()
        rcount += 1
    #get endpoint id if not provided as parm
    if endpoint_id is None:
        sql = "select top 1 producer_id from audit where MessageGUID = ? and  (ProcessState = ? OR ProcessState = ? OR ProcessState = ?) order by created_at desc"
        cursor = cnxn.cursor()
        cursor.execute(sql, guid, 'mft-no-files-complete', 'mft-job-fail', 'mft-job-complete')
        row = cursor.fetchone()
        # print(row[0])
        if row is None:
            return None
        endpoint_id = row[0]
    # get route count
    cnxn = get_db_connection(get_config(), env)
    sql = "select count(*) from routes where producer_id = ? and active = 1"
    cursor = cnxn.cursor()
    cursor.execute(sql, endpoint_id)
    row = cursor.fetchone()
    # print(row[0])
    if row is None:
        return None
    route_count = int(row[0])
    # here we need to know if delete cause it will have 0 routes
    if route_count == 0 and delete_only != 'true':
        return 'no_active_routes'
    single_job_state = 'mft-job-complete'
    for job in job_states:
        for k, v in job.items():
            # any instance fails mean we fail
            if v == 'mft-job-fail':
                return v
            # any instance is no files complete (though would really only be one
            if v == 'mft-no-files-complete':
                return v
    # if we don't have the total count we didn't finish all routes yet so return None
    # if we got here cause we did not have a fail or no files complete already
    if len(job_states) < route_count:
        return None
    # here we should return one job state to rule them all ;)
    # and since all other conditions should have returned by now we succeed
    return single_job_state


def get_endpoint_config(e_id, env):
    cnxn = get_db_connection(get_config(), env)
    ecfg = {"endpoint": {}, "properties": [], "schedules": []}
    if e_id is None:
        # we need this parm from somewhere so fail out
        sys.exit('No endpoint key id specified in json input from stdin or -k argument for sftp property retrieval')
    sql = "select * from endpoints where id = "+str(e_id)
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
        ecfg['endpoint'] = vals
        row = cursor.fetchone()
        rcount += 1

    sql = "select * from endpoint_props where endpoint_id = "+str(e_id)+" and env = '"+env+"'"
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
    
    #schedules
    fmt = '%Y-%m-%dT%H:%M:%S'
    dfmt = '%Y-%m-%dT00:00:00-0700'
    tfmt = '%H:%M:00-0700'

    sql = "select * from mft_schedule where endpoint_id = "+str(e_id)
    cursor = cnxn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    column_names = [d[0] for d in cursor.description]

    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            # print(type(row[x]))
            if isinstance(row[x], datetime):
                row[x] = row[x].strftime(fmt)
            if isinstance(row[x], date):
                row[x] = row[x].strftime(dfmt)
            if isinstance(row[x], time):
                row[x] = row[x].strftime(tfmt)
            vals[column_names[x]] = row[x]
            x += 1
        ecfg['schedules'].append(vals)
        row = cursor.fetchone()
        rcount += 1

    return ecfg


def get_sub_job_guid(masterGUID, env):
    cnxn = get_db_connection(get_config(), env)
    sql = "select top 1 MessageGUID from audit where ProcessState = 'mft-set-master-guid' and MessageControlID = ? order by created_at desc"
    cursor = cnxn.cursor()
    cursor.execute(sql, masterGUID)
    row = cursor.fetchone()
    if row is None:
        return None
    # print(row[0])

    return row[0]


def clean_file_names(path):
    for count, filename in enumerate(os.listdir(path)):
        nn = filename.replace(',', '_').replace(';', '_').replace('=', '_').replace("'", "_").replace('"', '_').replace('_', '').replace(' ', '_').replace('-', '_')
        os.rename(os.path.join(path, filename), os.path.join(path, nn))
