import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

tod_sheet = 'https://docs.google.com/spreadsheets/d/1L-G-QUQvQcdsfOgPoRdg47alHnHToJjLq0KGqCFLA_w/edit?usp=sharing'
sheet_name = "Copy of SpikeFlail ToDs"

sheet = None
df = None
google_client = None

row_offset = 3
col_offset = 1


def load_sheet():
    global sheet
    global df
    global google_client

    credentials = ServiceAccountCredentials.from_json_keyfile_name("creds.json",
                                                                   scopes)  # access the json key you downloaded earlier
    google_client = gspread.authorize(credentials)  # authenticate the JSON key with gspread
    sheet = google_client.open(sheet_name)  # open sheet

    sheet = sheet.get_worksheet(0)  # replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1


    data = sheet.get_all_values()

    data.pop(0) # remove an empty row at the top of the sheet
    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)



def reload_sheet():
    global sheet
    global df

    sheet = google_client.open(sheet_name)
    sheet = sheet.get_worksheet(0)

    data = sheet.get_all_values()

    data.pop(0)  # remove an empty row at the top of the sheet
    headers = data.pop(0)

    df = pd.DataFrame(data, columns=headers)

def update_sheet(mob_alias, time_of_death):
    print('mob {} tod {}'.format(mob_alias, time_of_death))
    hq = None
    # check for regular mob name in the sheet already
    for i, s in enumerate(df['NM']):
        if mob_alias.lower() == s.lower():
            hq = False
            real_name = s

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

    if hq is None:
        raise Exception('Invalid mob name')
    else:
        update_helper(real_name, time_of_death, hq)

    reload_sheet()


def update_helper(mob, time_of_death, is_HQ):
    notes = get_notes(mob)
    row = get_row_of_mob(mob)

    if mob in ['Fafnir', 'Turtle', 'Behe']:
        if is_HQ or notes == "":
            notes = 'Day 1'
        else:
            day = int(notes.split(' ')[1]) + 1
            notes = 'Day ' + str(day)

    print('update helper mob {} tod {} hq {}'.format(mob, time_of_death, is_HQ))
    sheet.update_cell(row + row_offset, get_col_of_TOD() + col_offset, time_of_death)

    print('notes {}'.format(notes.strip()))
    if notes.strip() != '':
        sheet.update_cell(row + row_offset, get_col_of_notes() + col_offset, notes)


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
