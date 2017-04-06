import gspread
import csv
import os.path
import arrow
import json

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
        sheet_csv = []
        for line in csv.DictReader(sheet_csv_raw.splitlines(), delimiter=','):
            sheet_csv.append(line)

        # convert dates
        week_day = {
            'piątek': '5',
            'poniedziałek': '1',
            'sobota': '6',
            'niedziela': '6',
            'czwartek': '4',
            'wtorek': '2',
            'środa': '3'
        }

        week_day_dates = {}

        for i in range(0,7):
            d = arrow.now().replace(hour=0,minute=0,second=0,microsecond=0).shift(days=i)
            week_day_dates[d.format('d')] = d

        for show in sheet_csv:
            show['Dzień tygodnia'] = week_day[show['Dzień tygodnia']]
            show['Godzina rozp.'] = week_day_dates[show['Dzień tygodnia']].replace(
                hour=int(show['Godzina rozp.'].split(':')[0]),
                minute=int(show['Godzina rozp.'].split(':')[1])
            )
            show['Godzina zako.'] = show['Godzina rozp.'].shift(minutes=int(show['Czas trwania (min)']))
        return sheet_csv
