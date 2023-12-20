import datetime_util
import notification_handler
import sheet_handler

sheet_handler.load_sheet()

print("getting menu messages: ")
print(notification_handler.get_menu_messages())

date = datetime_util.get_datetime_from_str('8/8/2023 19:01:00')

print("getting 12 hour time from 19:01:00")
print(datetime_util.get_12_hour_time_from_date(date))

# print("printing dataframe of google sheet:")
# print(sheet_handler.df.to_markdown())

notification_handler.queue_all_from_sheet()
for msg in notification_handler.notification_queue:
    print(msg[1])