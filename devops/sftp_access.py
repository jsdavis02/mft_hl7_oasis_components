import paramiko
import stat
import argparse
import configparser
import os
import io
import pyodbc
import sys
import json
from datetime import datetime, timedelta
sys.path.append('..')
from devops import prop_encrypt
from mft_scripts import mft_file_filters

# TODO db tables are not updated yet for Logan/Django branch

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-c", "--command", dest="cmd", help="put, get, list, rlist")
#these are for commandline testing convenience bw we use json for avoiding filename spacing issues
parser.add_argument("-k", "--endpoint_key", dest="endpoint_key", help="endpoint db id key")
parser.add_argument("-p", "--put_path", dest="put_path", help="remote path to put files")
parser.add_argument("-lp", "--local_put_path", dest="local_put_path", help="local path for files to put to remote")
parser.add_argument("-lf", "--local_file", dest="local_file", help="local file to either put from or get and write to")
parser.add_argument("-rf", "--remote_file", dest="remote_file", help="remote file name if different then local filename")
parser.add_argument("-ld", "--list_dir", dest="list_dir", help="remote path to list")
parser.add_argument("-pi", "--path_index", dest="path_index", help="Index number of sftp_path_[n] property")
parser.add_argument("-d", "--debug", dest="debug", help="Command line do debug")


args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')
mft_endpoint_key_folder = config.get(args.env, 'mft_endpoint_key_folder')

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
fmt = "%Y-%m-%d %H:%M:%S"


def create_sftp_client2(host, port, username, password, timeout, keyfilepath=None, keyfiletype=None):
    """
    create_sftp_client(host, port, username, password, timeout, keyfilepath, keyfiletype) -> SFTPClient

    Creates a SFTP client connected to the supplied host on the supplied port authenticating as the user with
    supplied username and supplied password or with the private key in a file with the supplied path.
    If a private key is used for authentication, the type of the keyfile needs to be specified as DSA or RSA or Ed25519.
    :rtype: SFTPClient object.
    """
    ssh = None
    sftp = None
    key = None
    try:
        if keyfilepath is not None:
            # Get private key used to authenticate user.
            if keyfiletype == 'DSA':
                # The private key is a DSA type key.
                key = paramiko.DSSKey.from_private_key_file(keyfilepath, password)
            elif keyfiletype == 'Ed25519':
                # The private key is an Ed25519 type key.
                key = paramiko.Ed25519Key.from_private_key_file(keyfilepath, password)
            else:
                # The private key is an RSA key.
                key = paramiko.RSAKey.from_private_key_file(keyfilepath, password)

        # Connect SSH client accepting all host keys.
        ssh = paramiko.SSHClient()
        # print(type(ssh))
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, key, timeout=timeout, auth_timeout=timeout)

        # Using the SSH client, create a SFTP client.
        sftp = ssh.open_sftp()
        # print(type(sftp))
        # Keep a reference to the SSH client in the SFTP client as to prevent the former from
        # being garbage collected and the connection from being closed.
        sftp.sshclient = ssh

        return sftp
    except Exception as e:
        if sftp is not None:
            sftp.close()
        if ssh is not None:
            ssh.close()
        exit('An error occurred creating SFTP client: %s: %s' % (e.__class__, e))
        pass


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
            sys.exit('No endpoint key id specified in json input from stdin or -k argument for sftp property retrieval')
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


def has_file(cmd_args, jdata_in, remote_file, flist=None):
    if flist is None:
        flist = json.loads(do_file_list(cmd_args, jdata_in))
    r = os.path.basename(remote_file)
    # print(type(flist))
    for f in flist:
        # print(f)
        # print(r)
        # print(f['filename'])
        if r == f['filename']:
            return True
    return False


def get_file_data_dict(sftp_file):
    return {
        "filename": sftp_file.filename,
        "longname": sftp_file.longname,
        "file_size": sftp_file.st_size,
        "last_access_time": datetime.fromtimestamp(sftp_file.st_atime).strftime(fmt),
        "last_write_time": datetime.fromtimestamp(sftp_file.st_mtime).strftime(fmt),
        "st_mode": sftp_file.st_mode,
        "st_uid": sftp_file.st_uid,
        "st_gid": sftp_file.st_gid
    }


def get_increment(cmd_args, jdata_in, flist, rfile):
    n_rfile = os.path.basename(rfile)
    i = 0
    name, ext = os.path.splitext(os.path.basename(rfile))
    while has_file(cmd_args, jdata_in, n_rfile, flist):
        i += 1
        n_rfile = name+'_'+str(i)+ext
    # print(n_rfile)
    return n_rfile


def do_file_check(cmd_args, jdata_in, e_cfg, remote_file):
    # does it exist or does prop 'destination_file_exists' has value of 'overwrite' if so just put
    d_file_exists = get_prop_by_name(e_cfg['properties'], 'destination_file_exists')
    if d_file_exists is None or str(d_file_exists).lower() == 'overwrite':
        return remote_file
    flist = json.loads(do_file_list(cmd_args, jdata_in))
    # print(type(flist))
    exists = has_file(cmd_args, jdata_in, remote_file, flist)
    # print(exists)
    if not exists:
        # all logic after this assumes we exist, if we don't then this file put is fine, just do it
        return remote_file
    # if exists and prop 'destination_file_exists' has value of 'rename' then
    # check prop 'rename_behavior' for either 'timestamp' or 'increment'
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
    # if exists and 'destination_file_exists' has value of 'error' then we fail put
    if d_file_exists is not None and str(d_file_exists).lower() == 'error':
        sys.exit('File exists and endpoint is configured to error on delivery')
    # if exists and prop 'destination_file_exists' has value of 'skip' then
    if d_file_exists is not None and str(d_file_exists).lower() == 'skip':
        sys.exit('Skipping')


def do_recursive_list(sftp, path):
    rl = dict()
    r_files = []
    data = sftp.listdir_attr(path)
    for i in data:
        p = os.path.join(path, i.filename).replace("\\", "/") # so this runs on windows locally too
        if stat.S_ISDIR(i.st_mode):
            print(path)
            print(i.filename)
            if i.filename not in path:
                print(type(i.filename))
                print(os.path.join(path, i.filename))
                r_files.append(get_file_data_dict(i))
                rl[p] = do_recursive_list(sftp, p)
            else:
                print('is dir in else:'+str(i.filename))
                rl[path] = do_recursive_list(sftp, p)
        else:
            print('is not a dir:'+str(i.filename))
            fdata = get_file_data_dict(i)
            r_files.append(fdata)
    rl[path] = r_files
    return rl


def get_full_tree(cmd_args, jdata_in):
    endpointcfg = get_config(args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'sftp_host')
    port = int(get_prop_by_name(endpointcfg['properties'], 'sftp_port'))
    user = get_prop_by_name(endpointcfg['properties'], 'sftp_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'sftp_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    timeout = 30
    if get_prop_by_name(endpointcfg['properties'], 'sftp_timeout') is not None:
        timeout = int(get_prop_by_name(endpointcfg['properties'], 'sftp_timeout'))
    key_pass = get_prop_by_name(endpointcfg['properties'], 'sftp_key_password')
    key_pass = prop_encrypt.do_decrypt(key_pass, cmd_args.env)
    key = get_prop_by_name(endpointcfg['properties'], 'sftp_key')

    path = None
    path_index = None
    if cmd_args.path_index is not None:
        path = get_prop_by_name(endpointcfg['properties'], 'sftp_path_'+cmd_args.path_index)
        path_index = cmd_args.path_index
    if jdata_in is not None and 'path_index' in jdata_in:
        path = get_prop_by_name(endpointcfg['properties'], 'sftp_path_'+jdata_in['path_index'])
        path_index = jdata_in['path_index']
    # Deprecating using sftp_file at all and using file filter with a default of all files if not
    # specified in config
    # if path is None:
    #     # try sftp_file_1 path first
    #     path = os.path.dirname(get_prop_by_name(endpointcfg['properties'], 'sftp_file_1'))
    # next in priority for path is args so check
    if cmd_args.list_dir is not None and len(cmd_args.list_dir) > 0:
        path = cmd_args.list_dir
    # top priority json parm
    if jdata_in is not None and 'list_dir' in jdata_in and len(jdata_in['list_dir']) > 0:
        path = jdata_in['list_dir']
    if path is None:
        exit('We could not determine a path to list from cmdline or json input')
    ldata = dict()
    # print(path)
    sftp = None
    if key is not None and key_pass is not None:
        sftp = create_sftp_client2(host, port, user, key_pass, timeout, os.path.join(mft_endpoint_key_folder, key))
    else:
        sftp = create_sftp_client2(host, port, user, pswd, timeout)
    
    ldata = do_recursive_list(sftp, path)
    sftp.close()
    return json.dumps(ldata)

def do_file_list(cmd_args, jdata_in):
    # print(jdata_in)
    endpointcfg = get_config(args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'sftp_host')
    port = int(get_prop_by_name(endpointcfg['properties'], 'sftp_port'))
    user = get_prop_by_name(endpointcfg['properties'], 'sftp_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'sftp_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    timeout = 30
    if get_prop_by_name(endpointcfg['properties'], 'sftp_timeout') is not None:
        timeout = int(get_prop_by_name(endpointcfg['properties'], 'sftp_timeout'))
    key_pass = get_prop_by_name(endpointcfg['properties'], 'sftp_key_password')
    key_pass = prop_encrypt.do_decrypt(key_pass, cmd_args.env)
    key = get_prop_by_name(endpointcfg['properties'], 'sftp_key')
    
    path = None
    path_index = None
    if cmd_args.path_index is not None:
        path = get_prop_by_name(endpointcfg['properties'], 'sftp_path_'+cmd_args.path_index)
        path_index = cmd_args.path_index
    if jdata_in is not None and 'path_index' in jdata_in:
        path = get_prop_by_name(endpointcfg['properties'], 'sftp_path_'+jdata_in['path_index'])
        path_index = jdata_in['path_index']
    # Deprecating using sftp_file at all and using file filter with a default of all files if not
    # specified in config
    # if path is None:
    #     # try sftp_file_1 path first
    #     path = os.path.dirname(get_prop_by_name(endpointcfg['properties'], 'sftp_file_1'))
    # next in priority for path is args so check
    if cmd_args.list_dir is not None and len(cmd_args.list_dir) > 0:
        path = cmd_args.list_dir
    # top priority json parm
    if jdata_in is not None and 'list_dir' in jdata_in and len(jdata_in['list_dir']) > 0:
        path = jdata_in['list_dir']
    if path is None:
        exit('We could not determine a path to list from cmdline or json input')
    ldata = []
    # print(path)
    sftp = None
    if key is not None and key_pass is not None:
        sftp = create_sftp_client2(host, port, user, key_pass, timeout, os.path.join(mft_endpoint_key_folder, key))
    else:
        sftp = create_sftp_client2(host, port, user, pswd, timeout)

    data = sftp.listdir_attr(path)
    for i in data:
        if not stat.S_ISDIR(i.st_mode):
            fdata = get_file_data_dict(i)
            safenow = datetime.now() - timedelta(seconds=-30)
            if datetime.strptime(fdata['last_write_time'], fmt) < safenow:
                ldata.append(fdata)
    sftp.close()
    
    if path_index is not None:
        # we got a path index, so we will assume we run a file filter
        file_filter = get_prop_by_name(endpointcfg['properties'], 'sftp_file_filter_'+path_index)
        # print(file_filter)
        if file_filter is None:
            file_filter = 'all_files'
        ldata = getattr(mft_file_filters, file_filter)(ldata)
    ldata = json.dumps(ldata)
    return ldata


def do_file_get(cmd_args, jdata_in):
    endpointcfg = get_config(cmd_args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'sftp_host')
    port = int(get_prop_by_name(endpointcfg['properties'], 'sftp_port'))
    user = get_prop_by_name(endpointcfg['properties'], 'sftp_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'sftp_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    timeout = 30
    if get_prop_by_name(endpointcfg['properties'], 'sftp_timeout') is not None:
        timeout = int(get_prop_by_name(endpointcfg['properties'], 'sftp_timeout'))
    key_pass = get_prop_by_name(endpointcfg['properties'], 'sftp_key_password')
    key_pass = prop_encrypt.do_decrypt(key_pass, cmd_args.env)
    key = get_prop_by_name(endpointcfg['properties'], 'sftp_key')
    delete_source = get_prop_by_name(endpointcfg['properties'], 'delete_sftp_source')
    
    path = None
    path_index = None
    if cmd_args.path_index is not None:
        path = get_prop_by_name(endpointcfg['properties'], 'sftp_path_'+cmd_args.path_index)
        path_index = cmd_args.path_index
    if jdata_in is not None and 'path_index' in jdata_in:
        path = get_prop_by_name(endpointcfg['properties'], 'sftp_path_'+jdata_in['path_index'])
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
            sys.exit('No local file specified in json input from stdin or -lf argument for sftp put')
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
            sys.exit('No remote file specified in json input from stdin or -rf argument for sftp get')
    if len(path) < 1:
        path = os.path.sep
    if os.path.isdir(local_file):
        local_file = os.path.join(local_file, os.path.basename(rfile))

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))
    try:
        sftp = None
        if key is not None and key_pass is not None:
                sftp = create_sftp_client2(host, port, user, key_pass, timeout, os.path.join(mft_endpoint_key_folder, key))
        else:
                sftp = create_sftp_client2(host, port, user, pswd, timeout)

        response = sftp.get(rfile, local_file)
        if delete_source is not None and delete_source.lower() == 'true':
            sftp.remove(rfile)
        sftp.close()
    except FileNotFoundError as e:
        e.strerror = e.strerror+' ...while trying to get %s' % rfile
        raise

    # before we call list here, we know we want to list the dir that we just did a get from
    jdata_in['list_dir'] = path
    return do_file_list(cmd_args, jdata_in)


def do_file_flag(cmd_args, jdata_in):
    endpointcfg = get_config(cmd_args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'sftp_host')
    port = int(get_prop_by_name(endpointcfg['properties'], 'sftp_port'))
    user = get_prop_by_name(endpointcfg['properties'], 'sftp_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'sftp_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    timeout = 30
    if get_prop_by_name(endpointcfg['properties'], 'sftp_timeout') is not None:
        timeout = int(get_prop_by_name(endpointcfg['properties'], 'sftp_timeout'))
    path = get_prop_by_name(endpointcfg['properties'], 'sftp_path')
    key_pass = get_prop_by_name(endpointcfg['properties'], 'sftp_key_password')
    key_pass = prop_encrypt.do_decrypt(key_pass, cmd_args.env)
    key = get_prop_by_name(endpointcfg['properties'], 'sftp_key')
    flag_file = get_prop_by_name(endpointcfg['properties'], 'flag_file')
    put_confirm = get_prop_by_name(endpointcfg['properties'], 'put_confirm')


    rfile = os.path.join(path, flag_file)
    local_file = io.StringIO('')

    sftp = None
    if key is not None and key_pass is not None:
        sftp = create_sftp_client2(host, port, user, key_pass, timeout, os.path.join(mft_endpoint_key_folder, key))
    else:
        sftp = create_sftp_client2(host, port, user, pswd, timeout)

    response = sftp.putfo(fl=local_file, remotepath=rfile, callback=None, confirm=put_confirm)
    sftp.close()
    cmd_args.list_dir = path
    return do_file_list(cmd_args, jdata_in)


def do_file_put(cmd_args, jdata_in):
    endpointcfg = get_config(cmd_args, jdata_in)
    host = get_prop_by_name(endpointcfg['properties'], 'sftp_host')
    port = int(get_prop_by_name(endpointcfg['properties'], 'sftp_port'))
    user = get_prop_by_name(endpointcfg['properties'], 'sftp_username')
    pswd = get_prop_by_name(endpointcfg['properties'], 'sftp_password')
    pswd = prop_encrypt.do_decrypt(pswd, cmd_args.env)
    timeout = 30
    if get_prop_by_name(endpointcfg['properties'], 'sftp_timeout') is not None:
        timeout = int(get_prop_by_name(endpointcfg['properties'], 'sftp_timeout'))
    path = get_prop_by_name(endpointcfg['properties'], 'sftp_path')
    key_pass = get_prop_by_name(endpointcfg['properties'], 'sftp_key_password')
    key_pass = prop_encrypt.do_decrypt(key_pass, cmd_args.env)
    key = get_prop_by_name(endpointcfg['properties'], 'sftp_key')
    put_confirm = get_prop_by_name(endpointcfg['properties'], 'put_confirm')
    put_debug = get_prop_by_name(endpointcfg['properties'], 'put_debug')
    if put_confirm is None or put_confirm.lower() == 'true':
        put_confirm = True
    else:
        put_confirm = False
    local_file = ''
    if jdata_in is not None and 'local_file' in jdata_in and len(jdata_in['local_file']) > 0:
        local_file = jdata_in['local_file']
    else:
        # use arg if we have it as fallback
        if args.local_file is not None and len(args.local_file) > 0:
            local_file = args.local_file
        else:
            # we need this parm from somewhere so fail out
            sys.exit('No local file specified in json input from stdin or -lf argument for sftp put')
    rfile = os.path.join(path, os.path.basename(local_file))
    if jdata_in is not None and 'remote_file' in jdata_in and len(jdata_in['remote_file']) > 0:
        rfile = os.path.join(path, os.path.basename(jdata_in['remote_file']))
    else:
        # use arg if we have it as fallback
        if args.remote_file is not None and len(args.remote_file) > 0:
            rfile = os.path.join(path, os.path.basename(cmd_args.remote_file))
    

    # set path for list
    if jdata_in is None:
        jdata_in = {}
    jdata_in['list_dir'] = path
    # rename logic for sftp puts to increment or timestamp
    rfile = os.path.join(path, do_file_check(cmd_args, jdata_in, endpointcfg, rfile))

    sftp = None
    if key is not None and key_pass is not None:
        sftp = create_sftp_client2(host, port, user, key_pass, timeout, os.path.join(mft_endpoint_key_folder, key))
    else:
        sftp = create_sftp_client2(host, port, user, pswd, timeout)

    # TODO expand and move this logic script wide later
    log_string = ''
    do_log = False
    response = ''
    if args.debug is not None and args.debug == 'yes':
        do_log = True
    if put_debug is not None and put_debug.lower() == 'true':
        do_log = True
    if do_log:
        log_string = f"\n{datetime.now()} - Doing Put with endpoint_id={endpointcfg['endpoint']['id']} with local_file={local_file} and remote_file={rfile} and put_confirm={put_confirm}"
    try:
        response = sftp.put(local_file, rfile, None, put_confirm)
    except Exception as e:
        log_string += f"\n{datetime.now()} - Caught Exception: {e.__str__()}"
        if do_log:
            with open('/opt/archive/oasis/logs/sftp_access.log', "a+") as log:
                log.write(log_string)
        raise e
    if do_log:
        log_string += f"\n{datetime.now()} - Doing Put with endpoint_id={endpointcfg['endpoint']['id']} with local_file={local_file} and remote_file={rfile} and put_confirm={put_confirm} had a response={response}"
    sftp.close()
    if do_log:
        with open('/opt/archive/oasis/logs/sftp_access.log', "a+") as log:
            log.write(log_string)
    cmd_args.list_dir = path
    return do_file_list(args, jdata_in)


# input by bw is stdin json so get it here
input_data = ""
line = None
jdata = None
if args.endpoint_key is None:
    line = sys.stdin.readline()
    while line:
        input_data += line + "\r"
        line = sys.stdin.readline()

    jdata = json.loads(input_data)

if args.cmd.lower() == "list":
    print(do_file_list(args, jdata))
if args.cmd.lower() == "rlist":
    print(get_full_tree(args, jdata))
if args.cmd.lower() == "put":
    print(do_file_put(args, jdata))
if args.cmd.lower() == "flag":
    print(do_file_flag(args, jdata))
if args.cmd.lower() == "get":
    print(do_file_get(args, jdata))
