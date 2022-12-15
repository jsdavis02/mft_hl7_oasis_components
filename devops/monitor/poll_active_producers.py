# Script checks the timestamp for the last
# successful connection to active HL7 producers.

from . import get_active_producers
import configparser
import argparse
import sys
import pyodbc
from datetime import datetime
from datetime import timedelta
from . import send_notification

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--env", dest="env", help="Environment config to use [DEV,TST,PPRD,PRD]")
args = parser.parse_args(sys.argv[1:])
env = args.env

# Get environment configuration from config.ini
config = configparser.ConfigParser(interpolation=None)
config.read("../../config.ini")
server = config.get(env, 'database.server')
database = config.get(env, 'database.dbname')
username = config.get(env, 'database.user')
password = config.get(env, 'database.pass')
admin_ui = config.get(env, 'admin_ui.url')
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

# Make function calls to get list of active producers
active_producers = get_active_producers.get_active_producers(env)

# Exit if there are no active ports, avoids an sql query on Null.
producers = ([str(p['id']) for p in active_producers])
print(producers)
if len(producers) <= 0:
    exit(0)

for producer in producers:
    try:
        sqlselect = "SELECT portmon_time from OASIS_endpoint WHERE id = "+producer
        cursor = cnxn.cursor()
        cursor.execute(sqlselect)
        time_field = cursor.fetchone()
        last_time = time_field[0]

        sqlalert = "SELECT alert_level from OASIS_endpoint WHERE id = "+producer
        cursor = cnxn.cursor()
        cursor.execute(sqlalert)
        alert_field = cursor.fetchone()
        alert_level = alert_field[0]

        select_name = "SELECT name FROM OASIS_endpoint WHERE id = "+producer
        cursor = cnxn.cursor()
        cursor.execute(select_name)
        name_field = cursor.fetchone()
        endpoint_name = name_field[0]
        
        #$print(str(producer)+" "+str(alert_level)+" "+str(last_time))

        if alert_level == 100:
            print("FYI: Active producer with id: "+producer+" has alert level set to "+str(alert_level)+" and is down.")
            print("I will not alert!")
        else:
            time_format = '%Y-%m-%d %H:%M:%S'
            current_time = datetime.today()
            lt = datetime.now() - timedelta(minutes=6)
            
            if last_time is None:
                print("ALERT: Active producer with id: "+producer+" has alert set to "+str(alert_level)+" and has not been listening")
                alert_msg = "There was an error while attempting to connect to an active OASIS endpoint, "+endpoint_name+"!and the Endpoint view at "+admin_ui+"/endpoints/view?id="+producer+" for issues."
                alert_sub = "OASIS "+env+" endpoint, "+endpoint_name+" and ID, "+producer+" is down!"
                send_notification.send_notification(env, producer, alert_level, alert_msg, alert_sub)

            elif last_time is not None:
                lt = last_time
                diff = current_time - lt
                minutes = (diff.seconds / 60)
                elapsed_m = round(minutes, 2)
                print(str(elapsed_m) + ' Minutes')

                if elapsed_m > 5:
                    print("ALERT: Active producer with id: "+producer+" has alert set to "+str(alert_level)+" and is not listening")
                    alert_msg = "There was an error while attempting to connect to an active OASIS endpoint, "+endpoint_name+"!and the Endpoint view at "+admin_ui+"/endpoints/view?id="+producer+" for issues."
                    alert_sub = "OASIS "+env+" endpoint, "+endpoint_name+" and ID, "+producer+" is not listening!"
                    send_notification.send_notification(env, producer, alert_level, alert_msg, alert_sub)
                else:
                    print("All is well with active producer "+producer+"!")

            else:
                print("Error assessing the last time "+producer+" was listening.")

    except:
        print("Check process failed!")

