import datetime_util
import notification_handler
import sheet_handler

sheet_handler.load_sheet()

print(notification_handler.get_menu_messages())

date = datetime_util.get_datetime_from_str('8/8/2023 19:01:00')

print(datetime_util.get_12_hour_time_from_date(date))