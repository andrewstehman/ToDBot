import re
import pytz
from datetime import datetime, timedelta

import config
import datetime_util


def ingest_message(message):
    content = message.content[5:]
    #content = message[5:]

    return parse_message(content)

def parse_message(content):

    pattern = r'^(.*?)(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(am|pm)?\s*(\w{3})?\s*([+-]\d{1,2})?'

    match = re.search(pattern, content)

    mob = match.group(1).strip()

    # Extract the hours, minutes, and seconds (if present)
    hours = int(match.group(2))
    minutes = int(match.group(3))
    seconds = int(match.group(4) or 0)

    # Convert the hours to 24-hour format if necessary
    if match.group(5) == 'pm' and hours < 12:
        hours += 12
    if match.group(5) == 'am' and hours == 12:
        hours = 0

    # Get the timezone abbreviation from the match, or assume Eastern Standard Time
    tz_abbrev = match.group(6) or 'EST'
    after_eastern = int(match.group(7) or 0)

    input_time = datetime_util.get_current_time()
    input_time = input_time.replace(hour=hours, minute=minutes, second=seconds)
    print('time before adjusting for timezone', input_time)
    input_time = input_time - timedelta(hours=after_eastern)
    print('time after adjusting for timezone', input_time)

    if input_time > datetime.now(pytz.timezone('US/Eastern')):
        input_time = input_time - timedelta(days=1)

    print('day adjusted time', input_time)

    # Format the time
    time_of_death = input_time.strftime(config.date_format)

    return mob, time_of_death
