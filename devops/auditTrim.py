import argparse
import os
import sys
import shutil
import pyodbc
import configparser
from datetime import datetime
from os import path

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-k", "--audit_record", nargs='?', dest="audit_record", help="key for a specific audit entry")
args = parser.parse_args(sys.argv[1:])

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))

env = args.env
audit_records = []

server = config.get(env, 'database.server')
database = config.get(env, 'database.dbname')
username = config.get(env, 'database.user')
password = config.get(env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

select_process_states_to_trim = "SELECT value FROM app_settings WHERE name = 'process_states_to_trim' AND env = '"+env+"'"
cursor = cnxn.cursor()
cursor.execute(select_process_states_to_trim)
row = cursor.fetchone()
process_states_to_trim = row[0]

select_num_records = "SELECT value FROM app_settings WHERE name = 'num_records_trim' AND env = '"+env+"'"
cursor = cnxn.cursor()
cursor.execute(select_num_records)
row = cursor.fetchone()
num_records = row[0]

select_days_old = "SELECT value FROM app_settings WHERE name = 'days_old_trim' AND env = '"+env+"'"
cursor = cnxn.cursor()
cursor.execute(select_days_old)
row = cursor.fetchone()
days = row[0]

select_archive_dir = "SELECT value FROM app_settings WHERE name = 'archive_dir' AND env = '"+env+"'"
cursor = cnxn.cursor()
cursor.execute(select_archive_dir)
row = cursor.fetchone()
archive_dir = row[0]

# Delete the audit records for no file found that are 30 days or older
try:
    delete_no_files = "delete from audit where created_at <= dateadd(day, -30, getdate()) and ProcessState like ('%mft-no-files-complete%')"
    cursor = cnxn.cursor()
    cursor.execute(delete_no_files)
    cursor.commit()
except:
    print("Could not delete no-files audit entries")
    
if args.audit_record is not None:
    select_records = "SELECT * FROM audit WHERE id = "+args.audit_record
else:
    select_records = "SELECT TOP "+num_records+" * FROM audit WHERE created_at <= dateadd(day, "+days+", getdate()) and ProcessState IN ("+process_states_to_trim+") order by created_at ASC"

cursor = cnxn.cursor()
cursor.execute(select_records)
row = cursor.fetchone()
column_names = [d[0] for d in cursor.description]

rcount = 1
while row:
    x = 0
    vals = {}
    while x < len(column_names):
        vals[column_names[x]] = row[x]
        x += 1
    audit_records.append(vals)
    row = cursor.fetchone()
    rcount += 1

# Exit if no records were found that match select
files_archived_count = 0
records_purged_count = 0
audit_props_purged = 0

records = ([str(r['id']) for r in audit_records])
if len(records) <= 0:
    print('no records processed')
    exit(0)

current_time = datetime.now(tz=datetime.utcnow().astimezone().tzinfo)
# Walk through the audit records identified for purge
for record in audit_records:
    record_id = record['id']

# Check for audit records that are for mft and require data persistence, ie, save the transfer file(s)
    if record['data_format'] == 'mft' and record['MessageReference'] is not None and len(record['MessageReference']) > 0:
        mft_archive_path = archive_dir+'/'+record['created_at'].strftime('%Y')+'/'+record['created_at'].strftime('%m')+'/'+record['created_at'].strftime('%d')+'/'
        # print(mft_archive_path)
        if not os.path.exists(mft_archive_path):
            os.makedirs(mft_archive_path)
        if path.exists(record['MessageReference']):  # In case we deleted the file already!!
            shutil.copy(os.path.join(record['MessageReference']), os.path.join(mft_archive_path, os.path.basename(record['MessageReference'])))
        files_archived_count += 1

# Now delete all the audit records identified for purging
    try:
        delete_record = "delete from audit where id = "+str(record_id)
        cursor = cnxn.cursor()
        cursor.execute(delete_record)
        cursor.commit()
        records_purged_count += 1
    except:
        print("Could not delete "+str(record_id)+" from audit")

# Also delete all audit props related to the purged audit records
    try:
        delete_audit_prop = "delete from audit_props where audit_id = "+str(record_id)
        cursor = cnxn.cursor()
        cursor.execute(delete_audit_prop)
        cursor.commit()
        audit_props_purged += 1
    except:
        print("Could not delete "+str(record_id)+" from audit_props")

with open('/opt/archive/oasis/logs/audittrim.log', "a+") as log:
    log.write("\nBW Run Time: "+str(current_time)+' : Python Log Write Time: '+str(datetime.now())+' : Script Finished'+"\n")

print(str(records_purged_count)+' records and '+str(audit_props_purged)+' audit props deleted and '+str(files_archived_count) + ' files archived to '+archive_dir)





