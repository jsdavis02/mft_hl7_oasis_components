from email.message import EmailMessage
import configparser
import pyodbc
import smtplib

config = configparser.ConfigParser(interpolation=None)
config.read("/opt/PythonUtilities/config.ini")

def service_alert(env, process, host, alert_msg, alert_level):
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    select_smtp = "SELECT value FROM app_settings WHERE name = 'smtp_server' AND env = '"+env+"'"
    cursor = cnxn.cursor()
    cursor.execute(select_smtp)
    server_field = cursor.fetchone()
    smtp_server = server_field[0]
    # print(smtp_server)

    select_port = "SELECT value FROM app_settings WHERE name = 'smtp_port' AND env = '"+env+"'"
    cursor = cnxn.cursor()
    cursor.execute(select_port)
    port_field = cursor.fetchone()
    smtp_port = port_field[0]
    # print(smtp_port)

    select_sender = "SELECT value FROM app_settings WHERE name = 'notification_sender' AND env = '"+env+"'"
    cursor = cnxn.cursor()
    cursor.execute(select_sender)
    sender_field = cursor.fetchone()
    notification_sender = sender_field[0]
    # print(notification_sender)

    msg = EmailMessage()
    msg.set_content(alert_msg)
    msg['SUBJECT'] = env+" "+process+" on "+host+"!"
    msg['From'] = notification_sender
    msg['To'] = '9146217970@txt.att.net, Juan.Peralta@valleywisehealth.org'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
         # server.set_debuglevel(True)
         server.set_debuglevel(False)
         server.ehlo_or_helo_if_needed()
         server.send_message(msg)
