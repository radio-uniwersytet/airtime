import gspread
import csv
import os.path

from oauth2client.service_account import ServiceAccountCredentials

class Schedule:
    def __init__(self,key,keyfile):
        # accessing google docs via google API
        feeds = ['https://spreadsheets.google.com/feeds']
        access = ServiceAccountCredentials.from_json_keyfile_name(keyfile, feeds)
        session = gspread.authorize(access)
        doc = session.open_by_key(key)
        self.sheet = doc.get_worksheet(0)
    def get_csv(self):
        # downloading spreadsheet in CSV format
        sheet_csv_raw = self.sheet.export(format='csv').decode(encoding='UTF-8').replace('\r','')

        # parsing CSV into python dictionary
        sheet_csv = csv.DictReader(sheet_csv_raw.splitlines(), delimiter=',')
        return sheet_csv
