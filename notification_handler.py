import pytz
import config
from datetime import datetime, timedelta
import asyncio
import time
import config
import datetime_util
import sheet_handler
import pandas as pd

notification_queue = []
minutes_to_alert_before = [60, 30, 5]
last_menu_notification = None
async def test_notifications():
    print(config.guilds)
    queue_all_from_sheet()
    while True:
        for guild in config.guilds:
            if guild.name == config.test_guild:
                for channel in guild.text_channels:
                    print(guild.name, channel.name)
                    if channel.name == 'test-channel':
                        await channel.send('test message')
        await asyncio.sleep(300)

def get_notifications_to_send():
    global notification_queue
    global last_menu_notification
    # print('notification queue - {}'.format(str(notification_queue)))
    messages = []
    now = datetime_util.get_current_time()

    if ((last_menu_notification is None or last_menu_notification.date() < now.date())
        and (now.hour == 8 and now.minute <= 5)):
        last_menu_notification = now
        messages.append(get_menu_messages())

    for notification in notification_queue:
        notification_timestamp = notification[0]
        notification_message = notification[1]
        now = datetime_util.get_current_time()

        if now > notification_timestamp:
            messages.append(notification_message)

    return messages

def get_menu_messages():
    messages = ['Here is today\'s menu (all times in EST):']
    windows = []
    mobs = sheet_handler.get_all_mobs_as_list()
    now = datetime_util.get_current_time()
    todays_date = now.date()

    for mob in mobs:
        if is_open_window(mob):
            messages.append('{} is in window now!'.format(mob))
        elif is_before_window(mob):
            first_window = sheet_handler.get_first_window(mob)
            first_window_date = first_window.date()
            first_window = datetime_util.get_12_hour_time_from_date(first_window)

            if first_window_date == (now + timedelta(days=1)).date():
                is_tomorrow = True
            elif first_window_date == todays_date:
                is_tomorrow = False
            else:
                continue

            if first_window.endswith('PM'):
                is_afternoon = True
            else:
                is_afternoon = False

            windows.append((is_tomorrow, is_afternoon, first_window, mob))


    windows = sorted(windows)

    for tuple in windows:
        is_tomorrow = tuple[0]
        first_window = tuple[2]
        mob = tuple[3]

        if mob in config.HQ_NMs:
            hq_day = sheet_handler.get_col_by_mob('Day/Notes', mob)
            mob = mob + ' ' + hq_day

        if is_tomorrow:
            messages.append('{} opens tomorrow at {}!'.format(mob, first_window))
        else:
            messages.append('{} opens at {}!'.format(mob, first_window))

    return '\n'.join(messages)



def update_messages_for_mob(mob):
    global notification_queue

    remove_notifications_for_mob(mob)
    queue_messages_for_mob(mob)

def add_notification_to_queue(timestamp, message):
    notification_queue.append((timestamp, message))

def get_messages_for_mob(tod, mob):
    messages = []
    hours, minutes, seconds = sheet_handler.get_col_by_mob('min respawn', mob).split(':')

    for period in minutes_to_alert_before:
        first_window = tod + timedelta(hours=int(hours), minutes= int(minutes))
        timestamp = first_window - timedelta(minutes=period)
        message = ''

        if period == 60:
            message = '@here 1 hour'
        else:
            message = str(period) + ' minutes'

        if mob in config.HQ_NMs:
            hq_day = sheet_handler.get_col_by_mob('Day/Notes', mob)
            message = message + ' until ' + mob + ' ' + hq_day + ' first window!'
        else:
            message = message + ' until ' + mob + ' first window!'

        messages.append((timestamp, message))

    return messages

def is_before_window(mob):
    first_window = sheet_handler.get_first_window(mob)
    now = datetime_util.get_current_time()
    if first_window is not None:
        return  now < first_window
    return False

def is_open_window(mob):
    now = datetime_util.get_current_time()
    first_window = sheet_handler.get_first_window(mob)
    last_window = sheet_handler.get_last_window(mob)
    if first_window is not None and last_window is not None:
        return now > first_window and now < last_window
    return False

def is_past_window(mob):
    last_window = sheet_handler.get_last_window(mob)
    # print(last_window > datetime_util.get_current_time())
    if last_window is not None:
        return datetime_util.get_current_time() > last_window
    return True
def queue_messages_for_mob(mob):
    tod = sheet_handler.get_col_by_mob('ONLY TOUCH', mob)
    # print(tod)
    if tod.strip() != '':
        try:
            tod = datetime_util.get_datetime_from_str(tod)

            if not is_past_window(mob):

                messages = get_messages_for_mob(tod, mob)
                now = datetime_util.get_current_time()

                for message in messages:
                    message_timestamp = message[0]
                    message_content = message[1]
                    if message_timestamp > now:
                        add_notification_to_queue(message_timestamp, message_content)
        except Exception as e:
            print('An error occured while queuing messages for mob {} - Probably an invalid ToD format'.format(mob))
            print(str(e))

def queue_all_from_sheet():
    global notification_queue
    notification_queue = []
    mobs = sheet_handler.get_all_mobs_as_list()

    for mob in mobs:
        queue_messages_for_mob(mob)

    # print(notification_queue)

def remove_notifications_for_mob(mob):
    global notification_queue
    # only keep messages not containing the mob. access message by using x[1]
    notification_queue = [x for x in notification_queue if mob.lower() not in x[1].lower()]
