import pyodbc
import configparser
import argparse
import sys

# Set environment
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="Environment config to use [DEV,TST,PPRD,PRD]")
args = parser.parse_args(sys.argv[1:])
env = args.env

config = configparser.ConfigParser(interpolation=None)
config.read("../config.ini")

server = config.get(env, 'database.server')
database = config.get(env, 'database.dbname')
username = config.get(env, 'database.user')
password = config.get(env, 'database.pass')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

# Set MFT schedules inactive
disable_sched = "update app_settings set value = 'true' where name = 'stop_all_mft_schedules'"
print(disable_sched)
cursor = cnxn.cursor()
cursor.execute(disable_sched)
cnxn.commit()
cnxn.close()


