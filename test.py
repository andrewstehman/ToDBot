import datetime_util
import notification_handler
import sheet_handler
import logging
import sys

sheet_handler.load_sheet()

logging.info("getting menu messages: ")
logging.info(notification_handler.get_menu_messages())

date = datetime_util.get_datetime_from_str('8/8/2023 19:01:00')

print("getting 12 hour time from 19:01:00")
print(datetime_util.get_12_hour_time_from_date(date))

# print("printing dataframe of google sheet:")
# print(sheet_handler.df.to_markdown())

notification_handler.queue_all_from_sheet()
for msg in notification_handler.notification_queue:
    print(msg[1])

# logging.log(level=0, msg="test")
#
# logging.info("test message")

# root = logging.getLogger()
# root.setLevel(logging.DEBUG)

# handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# root.addHandler(handler)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - [%(levelname)s] - %(message)s', stream=sys.stdout)


logging.info("testing logger")