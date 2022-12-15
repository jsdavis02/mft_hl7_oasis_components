from email.message import EmailMessage
import configparser
import pyodbc
import json
import os
import argparse
import sys
import smtplib
from datetime import datetime, date, time

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-p", "--producer_id", dest="producer_id", help="endpoint db id for producer")
parser.add_argument("-c", "--consumer_id", dest="consumer_id", help="endpoint db id for consumer")
parser.add_argument("-r", "--route_id", dest="route_id", help="route db id")
parser.add_argument("-s", "--schedule_id", dest="schedule_id", help="schedule db id for producer")
parser.add_argument("-m", "--message", dest="message", help="email msg or error")
parser.add_argument("-g", "--guid", dest="guid", help="msg or job guid")
parser.add_argument("-i", "--input", dest="input", help="json or cmdline")
args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)


def get_prop_by_name(props, prop_name):
    for p in props:
        if p['name'] == prop_name:
            return p['value']

    return None


def get_sender(appcfg):
    sender = get_prop_by_name(appcfg['app_configs'], 'notification_sender')
    if sender is None:
        sender = "oasis@valleywisehealth.org"
    return sender


def get_reply_to(appcfg):
    sender = get_prop_by_name(appcfg['app_configs'], 'notification_reply_to_email')
    if sender is None:
        sender = "ITInterfaceGroup@valleywisehealth.org"
    return sender


def get_alert_level(p_config, c_config):
    # we get the "lowest" value which is the highest alert level of 2 endpoints
    alert_level = {
        "alert_level": '100',
        "Impact": '3',
        "Urgency": '3',
        "notice_string": 'FYI LOW'
    }

    p_alert = 100  # default none
    c_alert = 100  # default none
    if p_config is not None:
        p_alert = p_config['producer_id']['alert_level']
    if c_config is not None:
        c_alert = c_config['consumer_id']['alert_level']
    a_level = min(p_alert, c_alert)
    if a_level == '100':
        # no alerting at all so just exit
        exit('Nothing had any alerting on, so exiting')
    elif a_level == 1:
        alert_level['alert_level'] = '1'
        alert_level['Impact'] = '2'
        alert_level['Urgency'] = '1'
        alert_level['notice_string'] = 'CRITICAL'
    elif a_level == 2:
        alert_level['alert_level'] = '2'
        alert_level['Impact'] = '2'
        alert_level['Urgency'] = '2'
        alert_level['notice_string'] = 'HIGH'
    elif a_level == 3:
        alert_level['alert_level'] = '3'
        alert_level['Impact'] = '2'
        alert_level['Urgency'] = '3'
        alert_level['notice_string'] = 'MEDIUM'
    elif a_level == 4:
        alert_level['alert_level'] = '4'
        alert_level['Impact'] = '3'
        alert_level['Urgency'] = '3'
        alert_level['notice_string'] = 'LOW'
    return alert_level


def get_endpoints_emails(p_config, c_config, prop_name):
    e_emails = []
    if p_config is not None:
        for p in p_config['properties']:
            if p['name'] == prop_name:
                e_emails.append(p['value'])
    if c_config is not None:
        for c in c_config['properties']:
            if c['name'] == prop_name:
                e_emails.append(c['value'])

    return e_emails


def get_system_emails(props, prop_name):
    sys_emails = []
    for p in props['app_configs']:
        if p['name'] == prop_name:
            sys_emails.append(p['value'])

    return sys_emails


def get_input_prop(args, jdata_in, key):
    input_prop_val = None
    if jdata_in is not None and key in jdata_in:
        # print('We have '+str(key)+' with value of '+str(jdata_in[key])+' in jdata')
        input_prop_val = jdata_in[key]
    else:
        # use arg if we have it as fallback
        if getattr(args, key) is not None and len(getattr(args, key)) > 0:
            input_prop_val = getattr(args, key)
    return input_prop_val


def get_env(args, jdata_in):
    env = get_input_prop(args, jdata_in, 'env')
    if env is None:
        sys.exit('No env specified in json input or as command line parameter of -e!')
    return env


def get_app_settings(args, jdata_in):
    app_cfg = {'app_configs': []}
    env = get_env(args, jdata_in)
    sql = "select * from app_settings where env = '"+env+"'"
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
        app_cfg['app_configs'].append(vals)
        row = cursor.fetchone()
        rcount += 1
    return app_cfg


def get_schedule_config(args, jdata_in, key):
    fmt = '%Y-%m-%dT%H:%M:%S.%f-0700'
    dfmt = '%Y-%m-%dT00:00:00-0700'
    tfmt = '%H:%M:00-0700'
    scfg = {'schedule': {}}
    s_id = get_input_prop(args, jdata_in, key)
    #env = get_env(args, jdata_in)
    if s_id is None:
        # we need this parm from somewhere so fail out
        sys.exit('No '+key+' key id specified in json input from stdin or argument for property retrieval')

    sql = "select * from mft_schedule where id = "+str(s_id)
    cursor = cnxn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    column_names = [d[0] for d in cursor.description]

    rcount = 1
    while row:
        x = 0
        vals = {}
        while x < len(column_names):
            if isinstance(row[x], datetime):
                row[x] = row[x].strftime(fmt)
            if isinstance(row[x], date):
                row[x] = row[x].strftime(dfmt)
            if isinstance(row[x], time):
                row[x] = row[x].strftime(tfmt)
            vals[column_names[x]] = row[x]
            x += 1
        scfg['schedule'] = vals
        row = cursor.fetchone()
        rcount += 1
    return scfg


def get_endpoint_config(args, jdata_in, key):
    ecfg = {key: {}, "properties": []}
    e_id = get_input_prop(args, jdata_in, key)
    env = get_env(args, jdata_in)
    if e_id is None:
        # we need this parm from somewhere so fail out
        sys.exit('No '+key+' key id specified in json input from stdin or argument for property retrieval')

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
        ecfg[key] = vals
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
    return ecfg


def get_route_config(args, jdata_in, key):
    rcfg = {'route_id': {}, "properties": []}
    r_id = get_input_prop(args, jdata_in, key)
    env = get_env(args, jdata_in)
    if r_id is None:
        # we need this parm from somewhere so fail out
        sys.exit('No '+key+' key id specified in json input from stdin or argument for property retrieval')

    sql = "select * from routes where id = "+str(r_id)
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
        rcfg[key] = vals
        row = cursor.fetchone()
        rcount += 1

    sql = "select * from route_props where route_id = "+str(r_id)+" and env = '"+env+"'"
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
        rcfg['properties'].append(vals)
        row = cursor.fetchone()
        rcount += 1
    # print(ecfg)
    return rcfg


def get_schedule_msg(schedcfg, appcfg):
    if schedcfg is None:
        return ''
    body = f"Schedule ID: {schedcfg['schedule']['id']} ran. Name={schedcfg['schedule']['name']} and Type={schedcfg['schedule']['freq_type']}\n"
    body += f"Admin Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/mft_schedules/view?id={schedcfg['schedule']['id']}\n"
    return body


def get_guid_msg(guid, appcfg):
    if guid is None:
        return ''
    body = f"Message GUID: {guid} Click the Analyst Audit Link to view the OASIS logs for the failed transfer.\n"
    body += f"Admin Audit Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/audit/?MessageGUID={guid}\n"
    body += f"Analyst Audit Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/audit/analyst?MessageGUID={guid}\n\n"
    body += f"The following error has occurred:\n"
    return body


def get_producer_msg(pdcfg, appcfg):
    if pdcfg is None:
        return ''
    body = f"Producer ID: {pdcfg['producer_id']['id']} ran. Name={pdcfg['producer_id']['name']} and Type={pdcfg['producer_id']['type']}\n"
    body += f"Admin Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/endpoints/view?id={pdcfg['producer_id']['id']}\n"
    body += f"Analyst Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/endpoints/analyst_view?id={pdcfg['producer_id']['id']}\n"
    return body


def get_consumer_msg(cdcfg, appcfg):
    if cdcfg is None:
        return ''
    body = f"Consumer ID: {cdcfg['consumer_id']['id']} ran. Name={cdcfg['consumer_id']['name']} and Type={cdcfg['consumer_id']['type']}\n"
    body += f"Admin Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/endpoints/view?id={cdcfg['consumer_id']['id']}\n"
    body += f"Analyst Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/endpoints/analyst_view?id={cdcfg['consumer_id']['id']}\n"
    return body


def get_route_msg(rcfg, appcfg):
    if rcfg is None:
        return ''
    body = f"Route ID: {rcfg['route_id']['id']} ran. Name={rcfg['route_id']['name']} and Type={rcfg['route_id']['type']}\n"
    body += f"Admin Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/routes/view?id={rcfg['route_id']['id']}\n"
    body += f"Analyst Link: {get_prop_by_name(appcfg['app_configs'], 'oasis_ui')}/routes/analyst_view?id={rcfg['route_id']['id']}\n"
    return body


def get_snow_msg(appcfg, alert_level):
    body = f"Affected Users: Oasis\n"
    body += f"Category: Application\n"
    body += f"Subcategory: OASIS\n"
    body += f"Assignment Group: {get_prop_by_name(appcfg['app_configs'], 'snow_group_id')}\n"
    body += f"Impact: {alert_level['Impact']}\n"
    body += f"Urgency: {alert_level['Urgency']}\n"
    return body


def do_send(cmd_args, jdata_in):
    # print(jdata_in)
    env = get_env(cmd_args, jdata_in)
    app_config = get_app_settings(cmd_args, jdata_in)
    sys_emails = get_system_emails(app_config, 'notification_email')
    schedule_id = get_input_prop(cmd_args, jdata_in, 'schedule_id')
    guid = get_input_prop(cmd_args, jdata_in, 'guid')
    scfg = None
    if schedule_id is not None:
        scfg = get_schedule_config(cmd_args, jdata_in, 'schedule_id')
    producer_id = get_input_prop(cmd_args, jdata_in, 'producer_id')
    pcfg = None
    if producer_id is not None:
        pcfg = get_endpoint_config(cmd_args, jdata_in, 'producer_id')
    consumer_id = get_input_prop(cmd_args, jdata_in, 'consumer_id')
    ccfg = None
    if consumer_id is not None:
        ccfg = get_endpoint_config(cmd_args, jdata_in, 'consumer_id')
    route_id = get_input_prop(cmd_args, jdata_in, 'route_id')
    rcfg = None
    if route_id is not None:
        rcfg = get_route_config(cmd_args, jdata_in, 'route_id')
    e_emails = get_endpoints_emails(pcfg, ccfg, 'error_notification_email')
    alert_lvl = get_alert_level(pcfg, ccfg)
    message = get_input_prop(cmd_args, jdata_in, 'message')
    # print(env)
    # print(app_config)
    # print(schedule_id)
    # print(scfg)
    # print(producer_id)
    # print(pcfg)
    # print(consumer_id)
    # print(ccfg)
    # print(route_id)
    # print(rcfg)
    # print(get_route_msg(rcfg, app_config))
    # print(type(get_route_msg(rcfg, app_config)))
    # print(sys_emails)
    # print(e_emails)
    # print(alert_lvl)
    # print(guid)
    # print(get_guid_msg(guid, app_config))
    # print(type(get_guid_msg(guid, app_config)))
    # print(message)
    # print(type(message))
    smtp_server = get_prop_by_name(app_config['app_configs'], 'smtp_server')
    smtp_port = get_prop_by_name(app_config['app_configs'], 'smtp_port')
    msg = EmailMessage()
    msg.set_content(
        get_snow_msg(app_config, alert_lvl)+"\n" +
        get_schedule_msg(scfg, app_config)+"\n" +
        get_producer_msg(pcfg, app_config)+"\n" +
        get_consumer_msg(ccfg, app_config)+"\n" +
        get_route_msg(rcfg, app_config)+"\n" +
        get_guid_msg(guid, app_config)+"\n" + str(message)
    )
    msg['SUBJECT'] = f"INFORM {alert_lvl['notice_string']} {env} OASIS File Transfer Error!"
    msg['From'] = get_sender(app_config)
    msg['To'] = ", ".join(sys_emails)
    msg['cc'] = ", ".join(e_emails)
    msg['Reply-To'] = get_reply_to(app_config)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.set_debuglevel(True)
        server.set_debuglevel(False)
        server.ehlo_or_helo_if_needed()
        server.send_message(msg)


# input by bw is stdin json so get it here
input_data = ''
jdata = None
if args.input == 'json':
    line = sys.stdin.readline().rstrip()
    while line:
        input_data += line
        line = sys.stdin.readline().rstrip()

    # print(input_data)
    jdata = json.loads(input_data)

do_send(args, jdata)

