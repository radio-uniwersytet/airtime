#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import arrow

from sys import exit,argv
import configparser, os

import airtime
import googleschedule

config = configparser.ConfigParser()
try:
	config.read_file(open(argv[1]))
except (FileNotFoundError,IndexError):
	print("Usage: {} config.cfg".format(argv[0]))
	exit(1)

week_day = {
    'piątek': '5',
    'poniedziałek': '1',
    'sobota': '6',
    'niedziela': '6',
    'czwartek': '4',
    'wtorek': '2',
    'środa': '3'
}

a_calendar = airtime.Schedule(
	user = config['Airtime']['User'],
	password = config['Airtime']['Password'],
	url = config['Airtime']['Url']
)
g_calendar = googleschedule.Schedule(
	key = config['GoogleSchedule']['Key'],
	keyfile = config['GoogleSchedule']['Keyfile']
)
# first step is to remove all future shows from today

# we need a list of show that start 15m from now
todays_shows_start = arrow.now().shift(minutes=15)
# and ends before midnight
todays_shows_end = arrow.now().ceil('day')

for event in a_calendar.event_feed(todays_shows_start,todays_shows_end):
	# if somebody scheduled some audio file within block, we won't touch it
	if event['percent'] != 0:
		print("Show {} is not empty, skipping deletion.".format(event['title']))
		continue
	# then we delete it
	print("Deleting show {}".format(event['title']))
	a_calendar.delete_show(event['id'])

# we access google api, and for each row in spreadsheet
for show in g_calendar.get_csv():
	# skipping if show is NOT planned
	if show['Ramówka'] != 'Tak':
		continue

	# skipping if show is not scheduled for today
	if week_day[show['Dzień tygodnia']] != arrow.now().strftime("%w"):
		continue

	# we creating time object from current time, but we changing hours and min
	show['Godzina rozp.'] = arrow.now().replace(
		hour=int(show['Godzina rozp.'].split(':')[0]),
		minute=int(show['Godzina rozp.'].split(':')[1]),
		second=0
	)

	# now we can decide whatever show was in the past or it is close to emission
	if arrow.now().shift(minutes = 5) > show['Godzina rozp.']:
		print("Skipping adding {} because it is too close to emission or in the past.".format(show['Nazwa audycji']))
		continue

	# we adding duration to start time to obtain end datetime
	show['Godzina zako.'] = show['Godzina rozp.'].shift(minutes=int(show['Czas trwania (min)']))

	# finally we are sending to Aritime API requests to add show
	print("Adding: {} - {} - {}".format(show['Nazwa audycji'],show['Godzina rozp.'],show['Godzina zako.']))
	a_calendar.add_show(
		show['Nazwa audycji'],
		show['Link do zapowiedzi'],
		'radio',
		show['Osoby biorące udział w audycji'],
		show['Godzina rozp.'],
		show['Godzina zako.']
	)
