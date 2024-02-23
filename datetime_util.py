from datetime import datetime, timezone, timedelta
import pytz

def get_datetime_from_str(date_str):
    time = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
    #logging.info('time gotten from string      ', time)
    time = time.replace(tzinfo=pytz.timezone('US/Eastern'))
    #logging.info('time after replacing timezone', time)
    return time

def get_time_btw_dates(first_date, second_date):
    return first_date - second_date

def get_current_time():
    now = datetime.now()
    actual_time = get_datetime_from_str('{}/{}/{} {}:{}:{}'.format(str(now.month), str(now.day), str(now.year), str(now.hour), str(now.minute), str(now.second)))
    return actual_time

def get_12_hour_time_from_date(date):
    return date.strftime("%I:%M %p")