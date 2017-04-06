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
todays_shows_end = arrow.now().shift(days=7).ceil('day')

shows = g_calendar.get_csv()

def search_shows(title,start,end,shows):
	for show in shows:
		if show['Nazwa audycji'] != title:
			continue
		if show['Godzina rozp.'] != start:
			continue
		if show['Godzina zako.'] != end:
			continue
		return True
	return False

for event in a_calendar.event_feed(todays_shows_start,todays_shows_end):

	# if somebody scheduled some audio file within block, we won't touch it
	if event['percent'] != 0:
		print("Show {} is not empty, skipping deletion.".format(event['title']))
		continue

	if search_shows(event['title'],event['start'],event['end'],shows):
		print("Show {} is is the same as in schedule, skipping.".format(event['title']))
		continue

	# then we delete it
	print("Deleting show {}".format(event['title']))
	a_calendar.delete_show(event['id'])

# we access google api, and for each row in spreadsheet
for show in shows:
	# skipping if show is NOT planned
	if show['Ramówka'] != 'Tak':
		continue

	# now we can decide whatever show was in the past or it is close to emission
	if arrow.now().shift(minutes = 5) > show['Godzina rozp.']:
		print("Skipping adding {} - {} - {} because it is too close to emission or in the past.".format(show['Nazwa audycji'],show['Godzina rozp.'],show['Godzina zako.']))
		continue

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
