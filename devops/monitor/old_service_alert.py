from email.message import EmailMessage
import configparser
import pyodbc
import smtplib

config = configparser.ConfigParser(interpolation=None)
config.read("/opt/PythonUtilities/config.ini")

def service_alert(env, process, host, alert_msg, alert_level):
    email_dist = []
    server = config.get(env, 'database.server')
    database = config.get(env, 'database.dbname')
    username = config.get(env, 'database.user')
    password = config.get(env, 'database.pass')
    tea_url = config.get(env, 'tea.url')
    # admin_ui = config.get(env, 'admin_ui.url')
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    # select_emails = "SELECT value FROM app_settings WHERE name = 'notification_email' AND env = '"+env+"'"
    # cursor = cnxn.cursor()
    # cursor.execute(select_emails)
    # email_field = cursor.fetchone()
    # column_names = [d[0] for d in cursor.description]
    # 
    # rcount = 1
    # while email_field:
    #     x = 0
    #     vals = {}
    #     while x < len(column_names):
    #         vals[column_names[x]] = email_field[x]
    #         x += 1
    #     email_dist.append(vals['value'])
    #     email_field = cursor.fetchone()
    #     rcount += 1
    #  
    # email_distribution = ', '
    # email_distribution = email_distribution.join(email_dist)

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

    # select_group = "SELECT value FROM app_settings WHERE name = 'snow_group_id' AND env = '"+env+"'"
    # cursor = cnxn.cursor()
    # cursor.execute(select_group)
    # group_field = cursor.fetchone()
    # group_id = group_field[0]
    # # print(group_id)

    select_sender = "SELECT value FROM app_settings WHERE name = 'notification_sender' AND env = '"+env+"'"
    cursor = cnxn.cursor()
    cursor.execute(select_sender)
    sender_field = cursor.fetchone()
    notification_sender = sender_field[0]
    # print(notification_sender)

    # select_category = "SELECT value FROM app_settings WHERE name = 'snow_category' AND env = '"+env+"'"
    # cursor = cnxn.cursor()
    # cursor.execute(select_category)
    # category_field = cursor.fetchone()
    # snow_category = category_field[0]
    # print(snow_category)

    # select_sub_category = "SELECT value FROM app_settings WHERE name = 'snow_sub_category' AND env = '"+env+"'"
    # cursor = cnxn.cursor()
    # cursor.execute(select_sub_category)
    # sub_category_field = cursor.fetchone()
    # snow_sub_category = sub_category_field[0]
    # print(snow_category)

    # impact = '1'
    # urgency = '2'
    # notice_string = 'CRITICAL'
    # if alert_level == '100':
    #     exit(0)
    # elif alert_level == '2':
    #     impact = '2'
    #     notice_string = 'NOTICE'
    # elif alert_level == '3':
    #     impact = '2'
    #     urgency = '3'
    #     notice_string = 'NOTICE'
    # elif alert_level == '4':
    #     impact = '3'
    #     urgency = '3'
    #     notice_string = 'NOTICE'

    # msg = EmailMessage()
    # msg.set_content("Affected User: OASIS\n "
    #                 "Category: "+snow_category+"\n "
    #                 "Subcategory: "+snow_sub_category+"\n "
    #                 "Assignment Group: "+group_id+"\n "
    #                 "Impact: "+impact+"\n Urgency: "+urgency+"\n\n "+notice_string+": "+alert_msg+"\n\nPlease check the TEA server at "+tea_url+".")
    # msg['SUBJECT'] = "FYI "+notice_string+" --- OASIS "+env+" "+queue+" on host "+host+" is not running!"
    # msg['From'] = notification_sender
    # msg['To'] = email_distribution

    msg = EmailMessage()
    msg.set_content(alert_msg)
    msg['SUBJECT'] = env+" "+process+" on "+host+" is not running!"
    msg['From'] = notification_sender
    msg['To'] = '9146217970@txt.att.net,Juan.Peralta@valleywisehealth.org'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
         # server.set_debuglevel(True)
         server.set_debuglevel(False)
         server.ehlo_or_helo_if_needed()
         server.send_message(msg)
