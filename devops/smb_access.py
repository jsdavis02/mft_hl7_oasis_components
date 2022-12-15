from smb.SMBConnection import SMBConnection, ProtocolError
import argparse
import configparser
import os
import io
import pyodbc
import sys
import json
import socket
from datetime import datetime, timedelta
sys.path.append('..')
from devops import prop_encrypt
from mft_scripts import mft_file_filters


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-c", "--command", dest="cmd", help="put, get, list, flag")
#these are for commandline testing convenience bw we use json for avoiding filename spacing issues
parser.add_argument("-k", "--endpoint_key", dest="endpoint_key", help="endpoint db id key")
parser.add_argument("-p", "--put_path", dest="put_path", help="remote path to put files")
parser.add_argument("-lp", "--local_put_path", dest="local_put_path", help="local path for files to put to remote")
parser.add_argument("-lf", "--local_file", dest="local_file", help="local file to either put from or get and write to")
parser.add_argument("-rf", "--remote_file", dest="remote_file", help="remote file name if different then local filename")
parser.add_argument("-ld", "--list_dir", dest="list_dir", help="remote path to list")
parser.add_argument("-pi", "--path_index", dest="path_index", help="Index number of smb_path_[n] property")

args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
fmt = "%Y-%m-%d %H:%M:%S"


def get_config(args, jdata_in):
    ecfg = {"endpoint": {}, "properties": []}
    e_id = None
    if jdata_in is not None and 'endpoint_id' in jdata_in and len(jdata_in['endpoint_id']) > 0:
        e_id = jdata_in['endpoint_id']
    else:
        # use arg if we have it as fallback
        if args.endpoint_key is not None and len(args.endpoint_key) > 0:
            e_id = args.endpoint_key
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No endpoint key id specified in json input from stdin or -k argument for smb property retrieval')
    sql = "select * from endpoints where id = "+e_id
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

    sql = "select * from endpoint_props where endpoint_id = "+e_id+" and env = '"+args.env+"'"
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
            return p['value']

    return None


def get_file_data_dict(smb_file):
    # this for the shared file smb attributes at: https://pysmb.readthedocs.io/en/latest/api/smb_SharedFile.html

    return {
        "filename": smb_file.filename,
        "last_access_time": datetime.fromtimestamp(smb_file.last_access_time).strftime(fmt),
        "last_write_time": datetime.fromtimestamp(smb_file.last_write_time).strftime(fmt),
        "last_attr_change_time": datetime.fromtimestamp(smb_file.last_attr_change_time).strftime(fmt),
        "file_size": smb_file.file_size,
        "alloc_size": smb_file.alloc_size,
        "file_attributes": smb_file.file_attributes,
        "short_name": smb_file.short_name,
        "file_id": smb_file.file_id
    }


def do_file_list(cmd_args, jdata_in):
    endpointcfg = get_config(args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'smb_host')
    domain = get_prop_by_name(endpointcfg['properties'], 'smb_domain')
    user = get_prop_by_name(endpointcfg['properties'], 'smb_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'smb_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    share = get_prop_by_name(endpointcfg['properties'], 'smb_share')
    path = None
    path_index = None
    if cmd_args.path_index is not None:
        path = get_prop_by_name(endpointcfg['properties'], 'smb_path_'+cmd_args.path_index)
        path_index = cmd_args.path_index
    if jdata_in is not None and 'path_index' in jdata_in:
        path = get_prop_by_name(endpointcfg['properties'], 'smb_path_'+jdata_in['path_index'])
        path_index = jdata_in['path_index']
    # next in priority for path is args so check
    if cmd_args.list_dir is not None and len(cmd_args.list_dir) > 0:
        path = cmd_args.list_dir
    # top priority json parm
    if jdata_in is not None and 'list_dir' in jdata_in and len(jdata_in['list_dir']) > 0:
        path = jdata_in['list_dir']
    if path is None:
        exit('We could not determine a path to list from cmdline or json input')
    client_hostname = socket.gethostname()
    conn = SMBConnection(user, pswd, client_hostname, host, domain=domain, use_ntlm_v2=True,
                         is_direct_tcp=True)
    try:
        conn.connect(host, 445, timeout=200)

    except ProtocolError:
        conn.connect(host, 445, timeout=200)

    sfiles = conn.listPath(share, path)
    flist = []
    for sfile in sfiles:
        if not sfile.isDirectory:
            fdata = get_file_data_dict(sfile)
            # do not add to file list if last access is less then 30 seconds old
            safenow = datetime.now() - timedelta(seconds=-30)
            if datetime.strptime(fdata['last_write_time'], fmt) < safenow:
                flist.append(fdata)
        # print(sfile.last_access_time)
    if path_index is not None:
        # we got a path index, so we will assume we run a file filter
        file_filter = get_prop_by_name(endpointcfg['properties'], 'smb_file_filter_'+path_index)
        if file_filter is None:
            file_filter = 'all_files'
        flist = getattr(mft_file_filters, file_filter)(flist)
    flist = json.dumps(flist)
    conn.close()
    return flist


def has_file(cmd_args, jdata_in, remote_file, flist=None):
    if flist is None:
        flist = do_file_list(cmd_args, jdata_in)
    r = os.path.basename(remote_file)
    for f in flist:
        #print(r)
        #print(f['filename'])
        if r == f['filename']:
            return True
    return False


def get_increment(cmd_args, jdata_in, flist, rfile):
    n_rfile = os.path.basename(rfile)
    i = 0
    name, ext = os.path.splitext(os.path.basename(rfile))
    while has_file(cmd_args, jdata_in, n_rfile, flist):
        i += 1
        n_rfile = name+'_'+str(i)+ext
    return n_rfile


def do_file_check(cmd_args, jdata_in, e_cfg, remote_file):
    # does it exist or does prop 'destination_file_exists' has value of 'overwrite' if so just put
    d_file_exists = get_prop_by_name(e_cfg['properties'], 'destination_file_exists')
    if d_file_exists is None or str(d_file_exists).lower() == 'overwrite':
        return remote_file
    flist = do_file_list(cmd_args, jdata_in)
    exists = has_file(cmd_args, jdata_in, remote_file, flist)
    # print(exists)
    if not exists:
        # all logic after this assumes we exist, if we don't then this file put is fine, just do it
        return remote_file
    # if exists and prop 'destination_file_exists' has value of 'rename' then
        #check prop 'rename_behavior' for either 'timestamp' or 'increment'
    if d_file_exists is not None and str(d_file_exists).lower() == 'rename':
        rename_action = get_prop_by_name(e_cfg['properties'], 'rename_behavior')
        if rename_action is None:
            sys.exit('Endpoint property of destination_file_exists set to rename but there is no rename_behavior property set')
        if str(rename_action).lower() == 'increment':
            return get_increment(cmd_args, jdata_in, flist, remote_file)
        else:
            # lets default if not increment to timestamp for now
            timestamp = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
            name, ext = os.path.splitext(os.path.basename(remote_file))
            return name+'_'+timestamp+ext
    #if exists and 'destination_file_exists' has value of 'error' then we fail put
    if d_file_exists is not None and str(d_file_exists).lower() == 'error':
        sys.exit('File exists and endpoint is configured to error on delivery')
    #if exists and prop 'destination_file_exists' has value of 'skip' then
    if d_file_exists is not None and str(d_file_exists).lower() == 'skip':
        sys.exit('Skipping')


def do_file_delete(cmd_args, jdata_in):
    endpointcfg = get_config(cmd_args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'smb_host')
    domain = get_prop_by_name(endpointcfg['properties'], 'smb_domain')
    user = get_prop_by_name(endpointcfg['properties'], 'smb_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'smb_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    share = get_prop_by_name(endpointcfg['properties'], 'smb_share')
    #path = get_prop_by_name(endpointcfg['properties'], 'smb_path')
    client_hostname = socket.gethostname()
    conn = SMBConnection(user, pswd, client_hostname, host, domain=domain, use_ntlm_v2=True,
                         is_direct_tcp=True)
    conn.connect(host, 445, timeout=120)

    rfile = ''
    #print(jdata_in)
    if jdata_in is not None and 'remote_file' in jdata_in and len(jdata_in['remote_file']) > 0:
        rfile = jdata_in['remote_file']
    else:
        # use arg if we have it as fallback
        if args.remote_file is not None and len(args.remote_file) > 0:
            rfile = cmd_args.remote_file
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No remote file specified in json input from stdin or -rf argument for smb get')

    conn.deleteFiles(share, rfile)
    conn.close()
    jdata_in['list_dir'] = os.path.dirname(rfile)
    return do_file_list(cmd_args, jdata_in)


def do_file_get(cmd_args, jdata_in):
    if jdata_in is None:
        jdata_in = {}
    endpointcfg = get_config(cmd_args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'smb_host')
    domain = get_prop_by_name(endpointcfg['properties'], 'smb_domain')
    user = get_prop_by_name(endpointcfg['properties'], 'smb_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'smb_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    share = get_prop_by_name(endpointcfg['properties'], 'smb_share')
    path = get_prop_by_name(endpointcfg['properties'], 'smb_path')
    delete_source = get_prop_by_name(endpointcfg['properties'], 'delete_smb_source')
    client_hostname = socket.gethostname()
    conn = SMBConnection(user, pswd, client_hostname, host, domain=domain, use_ntlm_v2=True,
                         is_direct_tcp=True)
    conn.connect(host, 445, timeout=200)

    # similar to put but inverse so lets still use local/remote file parms
    path = None
    path_index = None
    if cmd_args.path_index is not None:
        path = get_prop_by_name(endpointcfg['properties'], 'smb_path_'+cmd_args.path_index)
        path_index = cmd_args.path_index
    if jdata_in is not None and 'path_index' in jdata_in:
        path = get_prop_by_name(endpointcfg['properties'], 'smb_path_'+jdata_in['path_index'])
        path_index = jdata_in['path_index']

    local_file = ''
    if jdata_in is not None and 'local_file' in jdata_in and len(jdata_in['local_file']) > 0:
        local_file = jdata_in['local_file']
    else:
        # use arg if we have it as fallback
        if args.local_file is not None and len(args.local_file) > 0:
            local_file = args.local_file
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No local file specified in json input from stdin or -lf argument for smb get')

    rfile = ''
    if jdata_in is not None and 'remote_file' in jdata_in and len(jdata_in['remote_file']) > 0:
        if path is not None:
            rfile = os.path.join(path, os.path.basename(jdata_in['remote_file']))
        else:
            path = os.path.dirname(jdata_in['remote_file'])
            rfile = jdata_in['remote_file']
    else:
        # use arg if we have it as fallback
        if args.remote_file is not None and len(args.remote_file) > 0:
            if path is not None:
                rfile = os.path.join(path, os.path.basename(cmd_args.remote_file))
            else:
                path = os.path.dirname(cmd_args.remote_file)
                rfile = cmd_args.remote_file
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No remote file specified in json input from stdin or -rf argument for smb get')
    if len(path) < 1:
        path = os.path.sep
    if os.path.isdir(local_file):
        local_file = os.path.join(local_file, os.path.basename(rfile))
    # print('Local File:'+str(local_file))
    # print('Remote File:'+str(rfile))
    # print(os.path.exists(os.path.dirname(local_file)))
    # print(os.path.dirname(local_file))
    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    with open(local_file, "wb") as lf:
        # print('doing retrieve')
        response = conn.retrieveFile(share, rfile, lf)
    # print(response)
    if delete_source is not None and delete_source.lower() == 'true':
        jdata_in['remote_file'] = rfile
        #print(jdata_in)
        do_file_delete(cmd_args, jdata_in)
    conn.close()
    # before we call list here, we know we want to list the dir that we just did a get from
    jdata_in['list_dir'] = path
    return do_file_list(cmd_args, jdata_in)


def do_file_flag(cmd_args, jdata_in):
    if jdata_in is None:
        jdata_in = {}
    endpointcfg = get_config(cmd_args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'smb_host')
    domain = get_prop_by_name(endpointcfg['properties'], 'smb_domain')
    user = get_prop_by_name(endpointcfg['properties'], 'smb_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'smb_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    share = get_prop_by_name(endpointcfg['properties'], 'smb_share')
    path = get_prop_by_name(endpointcfg['properties'], 'smb_path')
    flag_file = get_prop_by_name(endpointcfg['properties'], 'flag_file')
    client_hostname = socket.gethostname()
    conn = SMBConnection(user, pswd, client_hostname, host, domain=domain, use_ntlm_v2=True,
                         is_direct_tcp=True)
    conn.connect(host, 445, timeout=200)
    rfile = os.path.join(path, flag_file)
    # 0 byte file and isn't local anywhere, we just create from empty string file obj
    lf = io.StringIO('')
    conn.storeFile(share, rfile, lf, 60)
    conn.close()

    jdata_in['list_dir'] = path
    return do_file_list(cmd_args, jdata_in)


def do_file_put(cmd_args, jdata_in):
    endpointcfg = get_config(cmd_args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'smb_host')
    domain = get_prop_by_name(endpointcfg['properties'], 'smb_domain')
    user = get_prop_by_name(endpointcfg['properties'], 'smb_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'smb_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    share = get_prop_by_name(endpointcfg['properties'], 'smb_share')
    path = get_prop_by_name(endpointcfg['properties'], 'smb_path')

    client_hostname = socket.gethostname()
    conn = SMBConnection(user, pswd, client_hostname, host, domain=domain, use_ntlm_v2=True,
                         is_direct_tcp=True)
    conn.connect(host, 445, timeout=200)

    #path = None
    # path_index = None
    # if cmd_args.path_index is not None:
    #     path = get_prop_by_name(endpointcfg['properties'], 'smb_path_'+cmd_args.path_index)
    #     path_index = cmd_args.path_index
    # if jdata_in is not None and 'path_index' in jdata_in:
    #     path = get_prop_by_name(endpointcfg['properties'], 'smb_path_'+jdata_in['path_index'])
    #     path_index = jdata_in['path_index']

    local_file = ''
    if jdata_in is not None and 'local_file' in jdata_in and len(jdata_in['local_file']) > 0:
        local_file = jdata_in['local_file']
    else:
        # use arg if we have it as fallback
        if args.local_file is not None and len(args.local_file) > 0:
            local_file = args.local_file
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No local file specified in json input from stdin or -lf argument for smb put')

    rfile = ''
    if jdata_in is not None and 'remote_file' in jdata_in and len(jdata_in['remote_file']) > 0:
        if path is not None:
            rfile = os.path.join(path, os.path.basename(jdata_in['remote_file']))
        else:
            path = os.path.dirname(jdata_in['remote_file'])
            rfile = jdata_in['remote_file']
    else:
        # use arg if we have it as fallback
        if args.remote_file is not None and len(args.remote_file) > 0:
            if path is not None:
                rfile = os.path.join(path, os.path.basename(cmd_args.remote_file))
            else:
                path = os.path.dirname(cmd_args.remote_file)
                rfile = cmd_args.remote_file
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No remote file specified in json input from stdin or -rf argument for smb get')
    if len(path) < 1:
        path = os.path.sep

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    # run file check logic
    rfile = os.path.join(path, do_file_check(cmd_args, jdata_in, endpointcfg, rfile))
    # print(rfile)
    with open(local_file, "rb") as lf:
        conn.storeFile(share, rfile, lf, 60)
    conn.close()
    #before we call list here, we know we want to list the dir that we just did a get from
    jdata_in['list_dir'] = path
    return do_file_list(cmd_args, jdata_in)

# input by bw is stdin json so get it here
input_data = ''
jdata = None
if args.endpoint_key is None:
    line = sys.stdin.readline()
    while line:
        input_data += line + "\r"
        line = sys.stdin.readline()

    jdata = json.loads(input_data)

if args.cmd.lower() == "list":
    print(do_file_list(args, jdata))
if args.cmd.lower() == "put":
    print(do_file_put(args, jdata))
if args.cmd.lower() == "flag":
    print(do_file_flag(args, jdata))
if args.cmd.lower() == "get":
    print(do_file_get(args, jdata))
if args.cmd.lower() == "delete":
    print(do_file_delete(args, jdata))



