import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta
import logging

import config
import datetime_util

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

tod_sheet = 'https://docs.google.com/spreadsheets/d/1L-G-QUQvQcdsfOgPoRdg47alHnHToJjLq0KGqCFLA_w/edit?usp=sharing'

sheet_name = config.sheet_name
# sheet_name = config.test_sheet

sheet = None
df = None
google_client = None

row_offset = 3
col_offset = 1


async def load_sheet():
    global sheet
    global df
    global google_client

    logging.info("logging in to google service account")

    credentials = ServiceAccountCredentials.from_json_keyfile_name("creds.json",
                                                                   scopes)  # access the json key you downloaded earlier
    google_client = gspread.authorize(credentials)  # authenticate the JSON key with gspread
    logging.info('opening sheet {}'.format(sheet_name))
    document = google_client.open(sheet_name)  # open sheet
    logging.info("google sheet opened!")
    try:
        sheet = document.get_worksheet(0)  # replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    except Exception as e:
        logging.info("An exception occured opening the google sheet: {}".format(e))

    data = sheet.get_all_values()

    data.pop(0) # remove an empty row at the top of the sheet
    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)



async def reload_sheet():
    global sheet
    global df

    document = google_client.open(sheet_name)
    try:
        sheet = document.get_worksheet(0)  # replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1
    except Exception as e:
        logging.info("An exception occured opening the google sheet: {}".format(e))

    data = sheet.get_all_values()

    data.pop(0)  # remove an empty row at the top of the sheet
    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)

async def update_sheet(mob_alias, time_of_death):
    global df
    hq = None

    # check for regular mob name in the sheet already
    test = get_all_mobs_as_list()
    for mob in test:
        if mob_alias.lower() == mob.lower():
            hq = False
            real_name = mob

    if hq is None:
        # check for nickname of mob
        aliases = open('alias.txt', 'r')
        for line in aliases.readlines():
            items = line.split(',')
            mob = items[0].strip()
            real_name = items[1].strip()
            if mob_alias.lower() == mob.lower():
                if len(items) > 2:
                    hq = True
                else:
                    hq = False
                break
        aliases.close()

    if hq is None:
        raise Exception('Invalid mob name')
    else:
        update_helper(real_name, time_of_death, hq)

    await reload_sheet()


def update_helper(mob, time_of_death, is_HQ):
    notes = get_col_by_mob('Day/Notes', mob)
    row = get_row_of_mob(mob)

    if mob in config.HQ_NMs:
        if is_HQ or notes == "":
            notes = 'Day 1'
        else:
            # if the ToD is before the first window, do not update the day
            logging.info(f'time of death {time_of_death}')
            if datetime_util.get_datetime_from_str(time_of_death) > get_first_window(mob):
                day = int(notes.split(' ')[1]) + 1
                notes = 'Day ' + str(day)

    # logging.info('update helper mob {} tod {} hq {}'.format(mob, time_of_death, is_HQ))
    sheet.update_cell(row + row_offset, get_col_of_TOD() + col_offset, time_of_death)

    # logging.info('notes {}'.format(notes.strip()))
    if notes.strip() != '':
        sheet.update_cell(row + row_offset, get_col_of_notes() + col_offset, notes)

def get_last_window(mob):
    tod = get_col_by_mob('ONLY TOUCH', mob)
    if tod.strip() != '':
        tod = datetime_util.get_datetime_from_str(tod)

        max_respawn_time = get_col_by_mob('max respawn', mob)
        max_hours, max_minutes, max_seconds = max_respawn_time.split(':')
        last_window = tod + timedelta(hours=int(max_hours), minutes=int(max_minutes))
        return last_window


def get_first_window(mob):
    tod = get_col_by_mob('ONLY TOUCH', mob)
    if tod.strip() != '':
        tod = datetime_util.get_datetime_from_str(tod)
        min_respawn_time = get_col_by_mob('min respawn time', mob)
        min_hours, min_minutes, min_seconds = min_respawn_time.split(':')
        first_window = tod + timedelta(hours=int(min_hours), minutes=int(min_minutes))
        # logging.info(f'first window {first_window}')
        return first_window
def get_sheet_dataframe():
    return df

def get_col_by_mob(col_to_get, mob):
    row = get_row_of_mob(mob)
    col = get_col_containing(col_to_get)
    return df.iloc[row, col]

def get_all_mobs_as_list():
    mobs = df['NM']
    mobs = mobs.tolist()
    return [x for x in mobs if x.strip() != '']

def get_all_cols_as_list():
    cols = df.columns.values.tolist()
    return [x for x in cols if x != '']
def get_col_containing(label):
    for i, x in enumerate(df.columns):
        if label.lower() in x.lower():
            return i
    return 0

def get_col_of_TOD():
    for i, s in enumerate(df.columns.tolist()):
        if '(ONLY TOUCH THIS)' in s:
            return i

def get_col_of_notes():
    for i, s in enumerate(df.columns.tolist()):
        if 'Notes' in s:
            return i

def get_row_of_mob(mob):
    for i, s in enumerate(df['NM']):
        if mob == s:
            return i
    return 0
def get_notes(mob):
    row = get_row_of_mob(mob)
    col = get_col_of_notes()
    return df.iat[row, col]

