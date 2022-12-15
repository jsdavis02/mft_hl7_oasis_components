import json
import argparse
import configparser
import pyodbc
import os
import sys
from datetime import datetime, timedelta, date, time, timezone
from dateutil.relativedelta import relativedelta
import calendar
import socket

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", dest="input", help="json input string")
parser.add_argument("-o", "--output", dest="output", help="json output string")
parser.add_argument("-e", "--env", dest="env", help="env for database props to pull")
parser.add_argument("-k", "--endpoint_id", dest="endpoint_id", help="endpoint id to get schedules and evaluate through filter for testing")
parser.add_argument("-t", "--schedule_type", dest="schedule_type", help="schedule type if specified otherwise all: Minutes, Daily, Hours, Monthly, etc.")
args = parser.parse_args()

config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join("..", "config.ini"))
server = config.get(args.env, 'database.server')
database = config.get(args.env, 'database.dbname')
username = config.get(args.env, 'database.user')
password = config.get(args.env, 'database.pass')


def get_sched_field_or_none(scd, key):
    if key in scd and scd[key] is not None:
        if isinstance(scd[key], str):
            if scd[key].lower() != 'none' and len(scd[key]) > 0:
                return scd[key]
            else:
                return None
        return scd[key]
    return None


def parse_dt_string(dt_string):
    # print(dt_string)
    if dt_string is None:
        return None

    format_list = ('%Y-%m-%dT%H:%M:%S.%f-0700', '%Y-%m-%dT%H:%M:%S.%f-07:00', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S-%z', '%Y-%m-%dT%H:%M:%S-0700', '%H:%M:%S%z', '%H:%M:%S-0700')
    for fmt in format_list:
        try:
            # print(fmt)
            return datetime.strptime(dt_string, fmt).replace(tzinfo=timezone(-timedelta(hours=7)))
        except ValueError:
            pass
    raise ValueError('Could not parse the date string with the given formats: '+str(format_list))


def run_sched_with_pause(schedule, ctime):
    # print(ctime)
    pause_start = get_sched_field_or_none(schedule, 'pause_start')
    pause_end = get_sched_field_or_none(schedule, 'pause_end')
    if pause_start is not None and pause_end is not None:
        psdt = parse_dt_string(pause_start).time()
        pedt = parse_dt_string(pause_end).time()
        ct = ctime.time()
        # print(psdt)
        # print(pedt)
        # print(ct)
        # exit(str(psdt)+' - '+str(pedt)+' - '+str(ct));
        if psdt <= ct <= pedt:
            # current time is in between start and stop pause
            return False
    return True


def spec_time_check(schedule, ctime):
    # print(schedule['spec_time'])
    # print(type(schedule['spec_time']))
    spec_time = get_sched_field_or_none(schedule, 'spec_time')
    # doing <= instead of == so that any schedule lock or skip doesn't miss a spec time for the day
    if spec_time is not None:
        # print(spec_time)
        # print(type(spec_time))
        spec_time = parse_dt_string(spec_time)
        if spec_time.time().strftime('%H:%M') <= ctime.strftime('%H:%M'):
            return True  # Specific time matches, run it
    else:
        # no sub day, and spec time doesn't match
        return False


def hourly_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime):
    # will this be last run
    lr_of_sub_day = do_sub_day_last_run_check(schedule, ctime)
    # identify if testing cause we don't want to update sub day last run on testing
    cmd_testing = False
    if args.endpoint_id is not None:
        cmd_testing = True
    if lrdt + timedelta(hours=sub_day_freq_interval) <= ctime:
        if sub_day_start is None and sub_day_end is None:
            if not cmd_testing and lr_of_sub_day:
                update_sub_day_last_run(schedule['id'], ctime)
            return True     # Ran the last hour interval ago, run it
        if sub_day_start is not None and sub_day_end is not None:
            start_time = datetime.strptime(sub_day_start, '%H:%M:%S%z').time().strftime('%H:%M')
            end_time = datetime.strptime(sub_day_end, '%H:%M:%S%z').time().strftime('%H:%M')
            cur_time = ctime.strftime('%H:%M')
            if start_time <= cur_time <= end_time:
                if sub_day_stop_sched is False:
                    if not cmd_testing and lr_of_sub_day:
                        update_sub_day_last_run(schedule['id'], ctime)
                    return True     # Ran the last minute interval ago, run it
                else:
                    # sub day stop is set to true
                    if 'last_files_found' not in schedule:
                        # got no files found so stop doesn't matter
                        if not cmd_testing and lr_of_sub_day:
                            update_sub_day_last_run(schedule['id'], ctime)
                        return True
                    # is last files Not today?
                    last_files_found = parse_dt_string(schedule['last_files_found'])
                    # print(last_files_found)
                    if last_files_found is None or last_files_found.date().strftime('%Y-%m-%d') != ctime.strftime('%Y-%m-%d'):
                        if not cmd_testing and lr_of_sub_day:
                            update_sub_day_last_run(schedule['id'], ctime)
                        return True     # Ran the last minute interval ago, run it
    return False


def minute_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime):
    # will this be last run
    lr_of_sub_day = do_sub_day_last_run_check(schedule, ctime)
    # identify if testing cause we don't want to update sub day last run on testing
    cmd_testing = False
    if args.endpoint_id is not None:
        cmd_testing = True
    if lrdt + timedelta(minutes=sub_day_freq_interval) <= ctime:
        if sub_day_start is None and sub_day_end is None:
            # print('Daily with Minute sub day and no start/stop times')
            # print(lr_sub_date + timedelta(minutes=sub_day_freq_interval))
            # print(ctime)
            if not cmd_testing and lr_of_sub_day:
                update_sub_day_last_run(schedule['id'], ctime)
            return True     # Ran the last minute interval ago, run it
        if sub_day_start is not None and sub_day_end is not None:
            start_time = datetime.strptime(sub_day_start, '%H:%M:%S%z').time().strftime('%H:%M')
            end_time = datetime.strptime(sub_day_end, '%H:%M:%S%z').time().strftime('%H:%M')
            cur_time = ctime.strftime('%H:%M')
            if start_time <= cur_time <= end_time:
                if sub_day_stop_sched is False:
                    if not cmd_testing and lr_of_sub_day:
                        update_sub_day_last_run(schedule['id'], ctime)
                    return True     # Ran the last minute interval ago, run it
                else:
                    # sub day stop is set to true
                    if 'last_files_found' not in schedule:
                        # got no files found so stop doesn't matter
                        if not cmd_testing and lr_of_sub_day:
                            update_sub_day_last_run(schedule['id'], ctime)
                        return True
                    # is last files Not today?
                    last_files_found = parse_dt_string(schedule['last_files_found'])
                    # print(last_files_found)
                    if last_files_found is None or last_files_found.date().strftime('%Y-%m-%d') != ctime.strftime('%Y-%m-%d'):
                        if not cmd_testing and lr_of_sub_day:
                            update_sub_day_last_run(schedule['id'], ctime)
                        return True     # Ran the last minute interval ago, run it


def do_sub_day_last_run_check(sc, ctime):
    # here we check that this would be the last run of schedule for the day if so, we update the sub day last run
    # essentially we forward look to see if next iteration in sub day would put us in next day
    # being mindful of start stop windows
    # easy one first no start/stop on minutes or hours
    sub_day_start = get_sched_field_or_none(sc, 'sub_day_start_time')
    sub_day_end = get_sched_field_or_none(sc, 'sub_day_end_time')
    sub_day_freq_interval = get_sched_field_or_none(sc, 'sub_day_freq_interval')
    sub_day_freq_type = sc['sub_day_freq_type']
    # if either of the start stop sub day fields is empty we ignore them, must have both
    if sub_day_start is None or sub_day_end is None:
        if sub_day_freq_type == 'Minutes':
            next_run = ctime + timedelta(minutes=sub_day_freq_interval)
            if ctime.day < next_run.day:
                #last run of day
                return True
        if sub_day_freq_type == 'Hours':
            next_run = ctime + timedelta(hours=sub_day_freq_interval)
            if ctime.day < next_run.day:
                #last run of day
                return True
    elif sub_day_start is not None and sub_day_end is not None:
        sub_end_time = parse_dt_string(sub_day_end).time()
        if sub_day_freq_type == 'Minutes':
            next_run = ctime + timedelta(minutes=sub_day_freq_interval)
            n_run_time = next_run.time()
            if n_run_time > sub_end_time or ctime.day < next_run.day:
                #last run of day
                return True
        if sub_day_freq_type == 'Hours':
            next_run = ctime + timedelta(hours=sub_day_freq_interval)
            n_run_time = next_run.time()
            if n_run_time > sub_end_time or ctime.day < next_run.day:
                #last run of day
                return True
    #assume it's not end of the day otherwise
    return False


def check_scheduler_lock(ctime, cmd_args):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    fmt = '%Y-%m-%dT%H:%M:%S.%f-0700'
    sql = "select top 1 last_run from scheduler_lock where type ='All'"
    if args.schedule_type is not None:
        freq_type = args.schedule_type
        sql = "select top 1 last_run from scheduler_lock where type='"+freq_type+"'"
    cursor = cnxn.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    lr_date = row[0]
    lr_string = lr_date.strftime(fmt)
    # print(lr_string)
    same = ctime.strftime('%Y-%m-%dT%H:%M') == lr_date.strftime('%Y-%m-%dT%H:%M')
    # print(same)
    return same


def update_scheduler_lock(ctime, cmd_args):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    sql = "update scheduler_lock set last_run = '"+ctime.strftime('%Y-%m-%d %H:%M:%S')+"' where type='All'"
    if args.schedule_type is not None:
        freq_type = args.schedule_type
        sql = "update scheduler_lock set last_run = '"+ctime.strftime('%Y-%m-%d %H:%M:%S')+"' where type='"+freq_type+"'"
    cursor = cnxn.cursor()
    try:
        cursor.execute(sql)
        cursor.commit()
    except pyodbc.DatabaseError as err:
        exit(err)


def update_sub_day_last_run(s_id, ctime):
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
    sql = "update mft_schedule set sub_day_last_run = '"+ctime.strftime('%Y-%m-%d %H:%M:%S')+"' where id ="+str(s_id)
    if args.schedule_type is not None:
        freq_type = args.schedule_type
        sql = "update scheduler_lock set last_run = '"+ctime.strftime('%Y-%m-%d %H:%M:%S')+"' where type='"+freq_type+"'"
    cursor = cnxn.cursor()
    try:
        cursor.execute(sql)
        cursor.commit()
    except pyodbc.DatabaseError as err:
        exit(err)


def get_active_schedules(args):
    # we don't require -e except during testing so connection to db and config read must be here
    fmt = '%Y-%m-%dT%H:%M:%S.%f-0700'
    dfmt = '%Y-%m-%dT00:00:00-0700'
    tfmt = '%H:%M:00-0700'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    schedule_records = []
    sql = "select * from mft_schedule where active = 1"
    if args.schedule_type is not None:
        sql = "select * from mft_schedule where active = 1 and freq_type = '"+args.schedule_type+"' and (sub_day_freq_type = 'None' or sub_day_freq_type is NULL)"
        freq_type = args.schedule_type
        if "-" in args.schedule_type:
            s_t = str(args.schedule_type).split('-')
            freq_type = s_t[0]
            sub_type = s_t[1]
            sql = "select * from mft_schedule where active = 1 and freq_type = '"+freq_type+"' and sub_day_freq_type = '"+sub_type+"'"
        
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
        schedule_records.append(vals)
        row = cursor.fetchone()
        rcount += 1
    return schedule_records


def get_endpoint_schedules(args):
    # we don't require -e except during testing so connection to db and config read must be here
    fmt = '%Y-%m-%dT%H:%M:%S.%f-0700'
    dfmt = '%Y-%m-%dT00:00:00-0700'
    tfmt = '%H:%M:00-0700'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)

    schedule_records = []
    sql = "select * from mft_schedule where endpoint_id = "+args.endpoint_id
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
        schedule_records.append(vals)
        row = cursor.fetchone()
        rcount += 1
    return schedule_records


def is_weekday_in_month(ctime, wkdayinterval):
    weekday = ctime.weekday()
    day = ctime.day
    weekday_count_in_month = 0
    this_wkday_iteration = 0
    # print('day:'+str(day))
    # print('weekday:'+str(weekday))
    # monday first weekday even though we shift in oasis, to get weekday count here just use Python monday default
    cal = calendar.Calendar(firstweekday=0)
    for week in cal.monthdayscalendar(ctime.year, ctime.month):
        dc = 0
        # print(week)
        while dc < len(week):
            if week[dc] > 0 and dc == weekday:
                weekday_count_in_month += 1
                if day == week[dc]:
                    this_wkday_iteration = weekday_count_in_month
            dc += 1
    if wkdayinterval == -1:
        # last weekday of the month
        if weekday_count_in_month == this_wkday_iteration:
            return True
        else:
            return False
    else:
        return wkdayinterval == this_wkday_iteration


def check_minutes(schedule, ctime):
    should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
    if not should_we_run_pause_check:
        return should_we_run_pause_check
    last_run = get_sched_field_or_none(schedule, 'last_run')
    if last_run is None:
        return True
    lrdt = parse_dt_string(last_run)

    # for every mins we need to drop milliseconds, just not predictable at that timescale
    lrdt = lrdt.replace(microsecond=0)
    ctime = ctime.replace(microsecond=0)
    if lrdt + timedelta(minutes=schedule['freq_interval']) <= ctime:
        return True
    return False


def check_hours(schedule, ctime):
    should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
    if not should_we_run_pause_check:
        return should_we_run_pause_check
    last_run = get_sched_field_or_none(schedule, 'last_run')
    if last_run is None:
        return True
    lrdt = parse_dt_string(last_run)
    if lrdt + timedelta(hours=schedule['freq_interval']) <= ctime:
        return True
    return False


def check_daily(schedule, ctime):
    # Below is no longer valid, we now require either sub day freq type of minute or hour or a specific time
    # if 'last_run' not in schedule and schedule['sub_day_freq_type'] == 'None' or 'sub_day_freq_type' not in schedule:
    #     return True     # Never ran, does not have sub day schedule, run it
    # if 'last_run' in schedule and schedule['sub_day_freq_type'] == 'None' or 'sub_day_freq_type' not in schedule:  # Ran before, check if it should run again
    #     lr_date = datetime.strptime(schedule['last_run'], '%Y-%m-%dT%H:%M:%S.%f%z')
    #     if lr_date + timedelta(days=schedule['freq_interval']) <= ctime:
    #         return True     # Ran the last day interval ago, no sub day schedule run it
    # pause window is always respected so check time for daily and return if in pause window

    should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
    if not should_we_run_pause_check:
        return should_we_run_pause_check

    last_run = get_sched_field_or_none(schedule, 'last_run')
    sub_day_freq_type = get_sched_field_or_none(schedule, 'sub_day_freq_type')
    freq_interval = get_sched_field_or_none(schedule, 'freq_interval')
    if last_run is not None:
        # lets make sure we have not run today and the day matches frequency
        if sub_day_freq_type is None:
            # we don't have sub day so last run should be today-frequency
            # if we do have sub day, below will handle so we just return false
            # to end on no sub day and today-frequency don't match last run
            lr = parse_dt_string(last_run)
            nxt_run = datetime.strftime(lr + timedelta(days=freq_interval), '%Y-%m-%d')
            tdy = ctime.strftime('%Y-%m-%d')
            dt_nxt_run = datetime.strptime(nxt_run, '%Y-%m-%d').date()
            dt_tdy = datetime.strptime(tdy, '%Y-%m-%d').date()
            dt_diff = (dt_tdy - dt_nxt_run).days
            
            # Updated code to fire schedule if last run date is older than the freq_interval
            # or if next run is today
            if dt_diff >= freq_interval or nxt_run == tdy:
                # was just return True and think this was ignoring and running at midnight
                return spec_time_check(schedule, ctime)
            else:
                return False
            # if nxt_run != tdy:
            #   return False
    # if no sub day we just check hour/minute of the required spec time or sub day sched
    if sub_day_freq_type is None:
        return spec_time_check(schedule, ctime)
    if schedule['sub_day_freq_type'] == 'Hours' or schedule['sub_day_freq_type'] == 'Minutes':  # We have a sub day schedule
        # this way we know its either None or a valuelast_run = getSchedFieldOrNone(schedule, 'last_run') #
        sub_day_start = get_sched_field_or_none(schedule, 'sub_day_start_time')
        sub_day_end = get_sched_field_or_none(schedule, 'sub_day_end_time')
        sub_day_stop_sched = get_sched_field_or_none(schedule, 'sub_day_stop_schedule')
        sub_day_freq_interval = get_sched_field_or_none(schedule, 'sub_day_freq_interval')
        sub_day_freq_type = schedule['sub_day_freq_type']
        if 'sub_day_last_run' not in schedule or schedule['sub_day_last_run'] is None:
            schedule['sub_day_last_run'] = datetime.strftime(ctime+timedelta(days=-1), '%Y-%m-%dT%H:%M:%S%z')
        # previous date we ran updated when final schedule of the day
        # use parser so we can handle a couple diff datetime formats
        lr_sub_date = parse_dt_string(schedule['sub_day_last_run'])
        # print(lr_sub_date)
        if lr_sub_date + timedelta(days=schedule['freq_interval']) <= ctime:  # Are we X days ahead? if not, don't run
            #print('we a day ahead')
            # We actually compare sub day interval against last_run, which is updated every sched run
            # sub day last run is updated on the last sub day run of the day, so the above check can identify we flipped
            # to next day so lets get last run
            last_run = get_sched_field_or_none(schedule, 'last_run')
            lrdt = None
            if last_run is not None:
                lrdt = parse_dt_string(last_run)
            if sub_day_freq_type == 'Minutes':
                return minute_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
            if sub_day_freq_type == 'Hours':
                return hourly_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
    return False    # Schedule should not run now


def check_weekly(schedule, ctime):
    # if 'last_run' not in schedule and weekday == schedule['freq_interval'] and schedule['sub_day_freq_type'] == 'None' or 'sub_day_freq_type' not in schedule:
    #     return True     # Never ran, day of week matches, and there is no sub day schedule
    # if 'last_run' in schedule and weekday == schedule['freq_interval'] and schedule['sub_day_freq_type'] == 'None'or 'sub_day_freq_type' not in schedule:
    #     lr_date = datetime.strptime(schedule['last_run'], '%Y-%m-%dT%H:%M:%S.%f%z')
    #     if lr_date.strftime('%Y-%m-%d') < ctime.strftime('%Y-%m-%d'):
    #         return True     # Ran before, day of week matches, no sub day schedule, last run was before current time

    weekday = datetime.today().weekday()
    if weekday == 6:  # Sunday
        weekday = 1  # Set to integer value of Sunday in oasis
    else:
        weekday = weekday + 2  # Plus 2 accounts for integer values of oasis days

    # check if we are in the right weekday first
    if weekday == schedule['freq_interval']:
        # pause check
        should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
        if not should_we_run_pause_check:
            return should_we_run_pause_check
        # if no sub day we just check hour/minute and make sure last run isn't today
        last_run = get_sched_field_or_none(schedule, 'last_run')
        if 'sub_day_freq_type' not in schedule or schedule['sub_day_freq_type'] == 'None':
            if last_run is not None:
                lr = parse_dt_string(last_run).strftime('%Y-%m-%d')
                tdy = ctime.strftime('%Y-%m-%d')
                if lr == tdy:
                    # we aren't doing sub day, we are right day of week, but last run is today so we don't run again
                    return False
            # if here, no sub day, no last run or no last run today so check time and return
            return spec_time_check(schedule, ctime)
        # sub day logic
        if schedule['sub_day_freq_type'] == 'Hours' or schedule['sub_day_freq_type'] == 'Minutes':  # We have a sub day schedule
            sub_day_start = get_sched_field_or_none(schedule, 'sub_day_start_time')
            sub_day_end = get_sched_field_or_none(schedule, 'sub_day_end_time')
            sub_day_stop_sched = get_sched_field_or_none(schedule, 'sub_day_stop_schedule')
            sub_day_freq_interval = get_sched_field_or_none(schedule, 'sub_day_freq_interval')
            sub_day_freq_type = schedule['sub_day_freq_type']

            if 'sub_day_last_run' not in schedule or schedule['sub_day_last_run'] is None:
                schedule['sub_day_last_run'] = datetime.strftime(ctime+timedelta(days=-7), '%Y-%m-%dT%H:%M:%S%z')
            lr_sub_date = parse_dt_string(schedule['sub_day_last_run'])  # previous date we ran updated when final schedule of the day
            # our compare to sub day here should be is it at least 7 days back from today, since we know we are on the right weekday
            # if are already to this code
            if lr_sub_date + timedelta(days=-7) <= ctime:
                last_run = get_sched_field_or_none(schedule, 'last_run')
                lrdt = None
                if last_run is not None:
                    lrdt = parse_dt_string(last_run)
                if sub_day_freq_type == 'Minutes':
                    return minute_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
                if sub_day_freq_type == 'Hours':
                    return hourly_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
    return False    # Schedule should not run now


def check_monthly(schedule, ctime):
    # print('check monthly')
    # pause check off time of day regardless so do it first
    should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
    if not should_we_run_pause_check:
        # print('pause check')
        return should_we_run_pause_check
    # we need to check the freq_interval for the month to be todays day of month before
    # spec time check
    cur_day = ctime.day
    freq_int_day = get_sched_field_or_none(schedule, 'freq_interval')
    if freq_int_day == -1:
        freq_int_day = calendar.monthrange(ctime.year, ctime.month)[1]
    # print(cur_day)
    # print(freq_int_day)
    if cur_day != freq_int_day:
        return False
    last_run = get_sched_field_or_none(schedule, 'last_run')
    # if no sub day we just check hour/minute of the required spec time or sub day sched
    if 'sub_day_freq_type' not in schedule or schedule['sub_day_freq_type'] == 'None':
        if last_run is not None:
            lr = parse_dt_string(last_run).strftime('%Y-%m-%d')
            tdy = ctime.strftime('%Y-%m-%d')
            if lr == tdy:
                # we aren't doing sub day, we are right day of week, but last run is today so we don't run again
                return False
        # print('no sub day')
        return spec_time_check(schedule, ctime)
        # sub day logic
    if schedule['sub_day_freq_type'] == 'Hours' or schedule['sub_day_freq_type'] == 'Minutes':  # We have a sub day schedule
        sub_day_start = get_sched_field_or_none(schedule, 'sub_day_start_time')
        sub_day_end = get_sched_field_or_none(schedule, 'sub_day_end_time')
        sub_day_stop_sched = get_sched_field_or_none(schedule, 'sub_day_stop_schedule')
        sub_day_freq_interval = get_sched_field_or_none(schedule, 'sub_day_freq_interval')
        sub_day_freq_type = schedule['sub_day_freq_type']
        if 'sub_day_last_run' not in schedule or schedule['sub_day_last_run'] is None:
            schedule['sub_day_last_run'] = datetime.strftime(ctime+relativedelta(months=-1), '%Y-%m-%dT%H:%M:%S%z')
        lr_sub_date = parse_dt_string(schedule['sub_day_last_run'])  # previous date we ran updated when final schedule of the day
        # our compare to sub day here should be is it at least 7 days back from today, since we know we are on the right weekday
        # if are already to this code
        if lr_sub_date + relativedelta(months=-1) <= ctime:
            last_run = get_sched_field_or_none(schedule, 'last_run')
            lrdt = None
            if last_run is not None:
                lrdt = parse_dt_string(last_run)
            if sub_day_freq_type == 'Minutes':
                return minute_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
            if sub_day_freq_type == 'Hours':
                return hourly_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
    return False    # Schedule should not run now


def check_monthly_weekly(schedule, ctime):
    # print('check monthly_weekly')
    # print(type(ctime))
    # pause check off time of day regardless so do it first
    should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
    if not should_we_run_pause_check:
        # print('pause check')
        return should_we_run_pause_check
    weekday = datetime.today().weekday()

    if weekday == 6:  # Sunday
        weekday = 1  # Set to integer value of Sunday in oasis
    else:
        weekday = weekday + 2  # Plus 2 accounts for integer values of oasis days

    if weekday != schedule['sub_freq_interval']:
        # print(weekday)
        # regardless of iteration in month it is not the right weekday so just bail
        return False
    # check if today is the right iteration weekday
    if not is_weekday_in_month(ctime, schedule['freq_interval']):
        # print('return false from weekday of month check')
        # if true we will continue with sub day or spec time checks but if false we want to return false
        return False
    # if no sub day we just check hour/minute of the required spec time or sub day sched
    last_run = get_sched_field_or_none(schedule, 'last_run')
    if 'sub_day_freq_type' not in schedule or schedule['sub_day_freq_type'] == 'None':
        if last_run is not None:
            lr = parse_dt_string(last_run).strftime('%Y-%m-%d')
            tdy = ctime.strftime('%Y-%m-%d')
            if lr == tdy:
                # we aren't doing sub day, we are right day of week, but last run is today so we don't run again
                return False
        # print('no sub day')
        return spec_time_check(schedule, ctime)
        # sub day logic
    if schedule['sub_day_freq_type'] == 'Hours' or schedule['sub_day_freq_type'] == 'Minutes':  # We have a sub day schedule
        sub_day_start = get_sched_field_or_none(schedule, 'sub_day_start_time')
        sub_day_end = get_sched_field_or_none(schedule, 'sub_day_end_time')
        sub_day_stop_sched = get_sched_field_or_none(schedule, 'sub_day_stop_schedule')
        sub_day_freq_interval = get_sched_field_or_none(schedule, 'sub_day_freq_interval')
        sub_day_freq_type = schedule['sub_day_freq_type']
        if 'sub_day_last_run' not in schedule or schedule['sub_day_last_run'] is None:
            schedule['sub_day_last_run'] = datetime.strftime(ctime+relativedelta(months=-1), '%Y-%m-%dT%H:%M:%S%z')
        lr_sub_date = parse_dt_string(schedule['sub_day_last_run'])  # previous date we ran updated when final schedule of the day
        # our compare to sub day here should be is it at least 7 days back from today, since we know we are on the right weekday
        # if are already to this code
        if lr_sub_date + relativedelta(months=-1) <= ctime:
            last_run = get_sched_field_or_none(schedule, 'last_run')
            lrdt = None
            if last_run is not None:
                lrdt = parse_dt_string(last_run)
            if sub_day_freq_type == 'Minutes':
                return minute_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
            if sub_day_freq_type == 'Hours':
                return hourly_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
    return False    # Schedule should not run now


def check_yearly(schedule, ctime):
    # pause check off time of day regardless so do it first
    should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
    if not should_we_run_pause_check:
        # print('pause check return')
        return should_we_run_pause_check

    # we need to check that we are in the right month and day from spec_date
    spec_date = get_sched_field_or_none(schedule, 'spec_date')
    if spec_date is None:
        # we must have spec date for yearly so we know what day we should be running
        return False
    # we are here so we know we have a spec date so parse it
    spec_date = parse_dt_string(spec_date)
    if ctime.month != spec_date.month or ctime.day != spec_date.day:
        # we don't match the day and month so return false and run nothing else
        return False
    # if no sub day we just check hour/minute of the required spec time or sub day sched
    last_run = get_sched_field_or_none(schedule, 'last_run')
    if 'sub_day_freq_type' not in schedule or schedule['sub_day_freq_type'] == 'None':
        if last_run is not None:
            lr = parse_dt_string(last_run).strftime('%Y-%m-%d')
            tdy = ctime.strftime('%Y-%m-%d')
            if lr == tdy:
                # we aren't doing sub day, we are right day of week, but last run is today so we don't run again
                return False
        return spec_time_check(schedule, ctime)

    if schedule['sub_day_freq_type'] == 'Hours' or schedule['sub_day_freq_type'] == 'Minutes':  # We have a sub day schedule
        # print('in sub day')
        sub_day_start = get_sched_field_or_none(schedule, 'sub_day_start_time')
        sub_day_end = get_sched_field_or_none(schedule, 'sub_day_end_time')
        sub_day_stop_sched = get_sched_field_or_none(schedule, 'sub_day_stop_schedule')
        sub_day_freq_interval = get_sched_field_or_none(schedule, 'sub_day_freq_interval')
        sub_day_freq_type = schedule['sub_day_freq_type']
        if 'sub_day_last_run' not in schedule or schedule['sub_day_last_run'] is None:
            schedule['sub_day_last_run'] = datetime.strftime(ctime+relativedelta(years=-1), '%Y-%m-%dT%H:%M:%S%z')
        lr_sub_date = parse_dt_string(schedule['sub_day_last_run'])  # previous date we ran updated when final schedule of the day
        # our compare to sub day here should be is it at least 7 days back from today, since we know we are on the right weekday
        # if are already to this code
        if lr_sub_date + relativedelta(years=-1) <= ctime:
            last_run = get_sched_field_or_none(schedule, 'last_run')
            lrdt = None
            if last_run is not None:
                lrdt = parse_dt_string(last_run)
            if sub_day_freq_type == 'Minutes':
                return minute_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
            if sub_day_freq_type == 'Hours':
                return hourly_sub_day_check(lrdt, sub_day_freq_interval, sub_day_start, sub_day_end, sub_day_stop_sched, schedule, ctime)
    return False    # Schedule should not run now


def check_spec_date_time(schedule, ctime):
    # print(datetime.strptime(schedule['spec_date'], '%Y-%m-%dT%H:%M:%S%z').date().strftime('%m-%d'))
    # print(ctime.strftime('%m-%d'))
    # print(datetime.strptime(schedule['spec_time'], '%H:%M:%S%z').time().strftime('%H:%M'))
    # print(ctime.strftime('%H:%M'))
    # pause check off time of day regardless so do it first
    should_we_run_pause_check = run_sched_with_pause(schedule, ctime)
    if not should_we_run_pause_check:
        return should_we_run_pause_check
    spec_date = get_sched_field_or_none(schedule, 'spec_date')
    if spec_date is None:
        return False
    # we are here so we know we have a spec date so parse it
    spec_date = parse_dt_string(spec_date)
    if ctime.month == spec_date.month and ctime.day == spec_date.day:
        last_run = get_sched_field_or_none(schedule, 'last_run')
        if last_run is not None:
            lr = parse_dt_string(last_run).strftime('%Y-%m-%d')
            tdy = ctime.strftime('%Y-%m-%d')
            if lr >= tdy:
                # we already ran today
                return False
        return spec_time_check(schedule, ctime)
    return False


def check_to_run(schedule, ctime):
    if schedule['freq_type'] == 'Minutes':
        return check_minutes(schedule, ctime)
    if schedule['freq_type'] == 'Hours':
        return check_hours(schedule, ctime)
    if schedule['freq_type'] == 'Daily':
        return check_daily(schedule, ctime)
    if schedule['freq_type'] == 'Weekly':
        return check_weekly(schedule, ctime)
    if schedule['freq_type'] == 'Monthly':
        return check_monthly(schedule, ctime)
    if schedule['freq_type'] == 'Monthly_Weekly':
        return check_monthly_weekly(schedule, ctime)
    if schedule['freq_type'] == 'Yearly':
        return check_yearly(schedule, ctime)
    if schedule['freq_type'] == 'Specific_Date_and_Time':
        return check_spec_date_time(schedule, ctime)


json_out = {"SortedSchedulesToRun": {
    "Daily": [],
    "Hours": [],
    "Minutes": [],
    "Monthly": [],
    "Specific_Date_and_Time": [],
    # "Specific_Time_Daily": [],
    "Weekly": [],
    "Yearly": [],
    "Yearly-Hours": [],
    "Yearly-Minutes": [],
    "Daily-Hours": [],
    "Daily-Minutes": [],
    # "Daily-Specific_Time": [],
    "Weekly-Hours": [],
    "Weekly-Minutes": [],
    # "Weekly-Specific_Time": [],
    "Monthly-Hours": [],
    "Monthly-Minutes": [],
    # "Monthly-Specific_Time": [],
}}


# adding cmdline ability to pull schedules of endpoint to test/evaluate
if args.endpoint_id is not None:
    print('evaluating schedules for an endpoint to test validity...')
    e_scheds = get_endpoint_schedules(args)
    # print('Evaluating the following schedules for Endpoint ID: '+args.endpoint_id)
    # print(e_scheds)
    current_time = datetime.now(tz=datetime.utcnow().astimezone().tzinfo)
    if check_scheduler_lock(current_time, args):
        exit('Schedule already ran in this minute window')
    update_scheduler_lock(current_time, args)

    print()
    for s in e_scheds:
        print('Evaluating schedule with current time: '+str(current_time))
        print(s)

       
        if check_to_run(s, current_time):
            print('Schedule would run now')
        else:
            print('Schedule would NOT run')
        print()
else:
    if args.input is None:
        json_in = json.load(sys.stdin)
    else:
        with open(args.input, 'r') as fp:
            json_in = json.load(fp)
    schedules = []  #set default empty here
    if 'schedule' not in json_in:
        # changing script to get schedules itself but take current time from bw for synchrosity bw needs to pass env though
        schedules = get_active_schedules(args)
    else:
        schedules = json_in['schedule']
#    current_time = datetime.strptime(json_in['current_run_time'], '%Y-%m-%dT%H:%M:%S.%f%z')
    current_time = parse_dt_string(json_in['current_run_time'])
    # TODO test the below and if none lets set to current time just so we are a bit more robust on at
    # least returning the schedules, even if bw would fail down stream without it having it set.
    # current_time = parse_dt_string(json_in['current_run_time'])
    # lock check, it seems bw garbage collection sometimes stacks threads to be in same minute
    # so here we check a last run for the whole scheduler to the minute, if this run is in same
    # minute as last, it just writes empty schedule list and exits
    # if not, then it updates last run in table and goes on as normal
    if check_scheduler_lock(current_time, args):
        sys.stdout.write(json.dumps(json_out))
        exit(0)
    update_scheduler_lock(current_time, args)
    # print(schedules)
    for s in schedules:
        # print(s)
        if check_to_run(s, current_time):
            # fix ups for dumb bw xml parsing
            s['active'] = 1
            if get_sched_field_or_none(s, 'sub_freq_interval') is None:
                s['sub_freq_interval'] = 0
            if get_sched_field_or_none(s, 'sub_day_stop_schedule') is not None:
                s['sub_day_stop_schedule'] = 1
            else:
                s['sub_day_stop_schedule'] = 0
            if get_sched_field_or_none(s, 'spec_date') is not None:
                s['spec_date'] = parse_dt_string(s['spec_date']).date().strftime('%Y-%m-%d')
            else:
                s.pop('spec_date', None)
            if get_sched_field_or_none(s, 'spec_time') is not None:
                s['spec_time'] = parse_dt_string(s['spec_time']).time().strftime('%H:%M:%S')
            else:
                s['spec_time'] = '00:00:00'
            if get_sched_field_or_none(s, 'sub_day_start_time') is not None:
                s['sub_day_start_time'] = parse_dt_string(s['sub_day_start_time']).date().strftime('%H:%M:%S')
            else:
                s['sub_day_start_time'] = '00:00:00'
            if get_sched_field_or_none(s, 'sub_day_end_time') is not None:
                s['sub_day_end_time'] = parse_dt_string(s['sub_day_end_time']).date().strftime('%H:%M:%S')
            else:
                s['sub_day_end_time'] = '00:00:00'
            # fix last run so stupid bw doesn't puke
            if get_sched_field_or_none(s, 'last_run') is not None:
                s['last_run'] = parse_dt_string(s['last_run']).date().strftime('%Y-%m-%dT%H:%M:%S')
            else:
                s.pop('last_run', None)
            # fix last files so stupid bw doesn't puke
            if get_sched_field_or_none(s, 'last_files_found') is not None:
                s['last_files_found'] = parse_dt_string(s['last_files_found']).date().strftime('%Y-%m-%dT%H:%M:%S')
            else:
                s.pop('last_files_found', None)
            if get_sched_field_or_none(s, 'pause_start') is not None:
                s['pause_start'] = parse_dt_string(s['pause_start']).date().strftime('%Y-%m-%dT%H:%M:%S')
            else:
                s.pop('pause_start', None)
            if get_sched_field_or_none(s, 'pause_end') is not None:
                s['pause_end'] = parse_dt_string(s['pause_end']).date().strftime('%Y-%m-%dT%H:%M:%S')
            else:
                s.pop('pause_end', None)

            # Monthly_Weekly frequency type can be packed into Monthly for output so lets change it
            if s['freq_type'] == 'Monthly_Weekly':
                s['freq_type'] = 'Monthly'

            if get_sched_field_or_none(s, 'sub_day_freq_type')is not None:
                json_out['SortedSchedulesToRun'][s['freq_type']+'-'+s['sub_day_freq_type']].append({"schedule": s})
            else:
                s['sub_day_freq_interval'] = 0
                json_out['SortedSchedulesToRun'][s['freq_type']].append({"schedule": s})

    if args.output is None:
        sys.stdout.write(json.dumps(json_out))
        with open('/opt/archive/oasis/logs/filterschedule.log', "a+") as log:
            log.write("\nHostname : " + str(socket.gethostname()) + " BW Run Time: "+str(current_time)+' : Python Log Write Time: '+str(datetime.now())+' Schedule Key : ' + args.schedule_type + ' : ' + json.dumps(json_out)+"\n")
    else:
        with open(args.output, "w") as out:
            out.write(json.dumps(json_out))
