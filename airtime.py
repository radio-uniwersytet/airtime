#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import arrow
import requests
import json

class Airtime:
    def __init__(self,user,password,url):
        # start cookies and spying bullshit
        self.session = requests.session()
        # fuck self signed SSL
        self.session.verify = False

        # define our target
        self.url = url

        # become a god
        self.auth = {
            'username': user,
            'password': password,
            'locale': 'en_CA',
            'submit': 'Login'
        }
        r = self.session.post(self.url+"/login", self.auth)
        if "Wrong username or password provided. Please try again." in r.text:
            print("Wrong username or password provided. Please try again")
            return False

        # set up http headers
        self.session.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            'Accept': 'application/json'
        }
    def _strfdelta(self,tdelta, fmt):
        d = {"days": tdelta.days}
        d["hours"], rem = divmod(tdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

class Schedule(Airtime):
        def _random_color(self):
            r = lambda: random.randint(0, 255)
            rgb = [r(),r(),r()]

            luminance = 1 - ( 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])/255
            if (luminance < 0.5):
                font = 0
            else:
                font = 255

            return([
                "{:02x}{:02x}{:02x}".format(rgb[0],rgb[1],rgb[2]),
                "{:02x}{:02x}{:02x}".format(font,font,font),
            ])

        def delete_show(self,id):
                self.session.post(
                    self.url+'/Schedule/delete-show',
                    data={
                        'format': 'json',
                        'id': id
                    }

        )

        def add_show(self,title,url,genere,desc,start,end):
            colors = self._random_color()

            data_dict = {
                'add_show_id': '-1',
                "add_show_instance_id": "-1",
                "add_show_name": title,
                "add_show_url": url,
                "add_show_genre": "radio",
                "add_show_description": desc,
                "add_show_start_date": start.strftime("%Y-%m-%d"),
                "add_show_start_time": start.strftime("%H:%M"),
                "add_show_end_date_no_repeat": end.strftime("%Y-%m-%d"),
                "add_show_end_time": end.strftime("%H:%M"),
                "add_show_duration": self._strfdelta((end-start),"{hours:02d}h {minutes:02d}m"),
                "add_show_timezone": "Europe/Warsaw",
                "add_show_repeats": "0",
                "add_show_linked": "0",
                "add_show_repeat_type": "0",
                "add_show_monthly_repeat_type": "2",
                "add_show_end_date": end.strftime("%Y-%m-%d"),
                "add_show_no_end": "0",
                "add_show_no_end": "1",
                "cb_airtime_auth": "0",
                "cb_custom_auth": "0",
                "custom_username": "",
                "custom_password": "",
                "add_show_record": "0",
                "add_show_rebroadcast": "0",
                "add_show_rebroadcast_date_absolute_1": "",
                "add_show_rebroadcast_time_absolute_1": "",
                "add_show_rebroadcast_date_absolute_2": "",
                "add_show_rebroadcast_time_absolute_2": "",
                "add_show_rebroadcast_date_absolute_3": "",
                "add_show_rebroadcast_time_absolute_3": "",
                "add_show_rebroadcast_date_absolute_4": "",
                "add_show_rebroadcast_time_absolute_4": "",
                "add_show_rebroadcast_date_absolute_5": "",
                "add_show_rebroadcast_time_absolute_5": "",
                "add_show_rebroadcast_date_absolute_6": "",
                "add_show_rebroadcast_time_absolute_6": "",
                "add_show_rebroadcast_date_absolute_7": "",
                "add_show_rebroadcast_time_absolute_7": "",
                "add_show_rebroadcast_date_absolute_8": "",
                "add_show_rebroadcast_time_absolute_8": "",
                "add_show_rebroadcast_date_absolute_9": "",
                "add_show_rebroadcast_time_absolute_9": "",
                "add_show_rebroadcast_date_absolute_10": "",
                "add_show_rebroadcast_time_absolute_10": "",
                "add_show_rebroadcast_date_1": "",
                "add_show_rebroadcast_time_1": "",
                "add_show_rebroadcast_date_2": "",
                "add_show_rebroadcast_time_2": "",
                "add_show_rebroadcast_date_3": "",
                "add_show_rebroadcast_time_3": "",
                "add_show_rebroadcast_date_4": "",
                "add_show_rebroadcast_time_4": "",
                "add_show_rebroadcast_date_5": "",
                "add_show_rebroadcast_time_5": "",
                "add_show_rebroadcast_date_6": "",
                "add_show_rebroadcast_time_6": "",
                "add_show_rebroadcast_date_7": "",
                "add_show_rebroadcast_time_7": "",
                "add_show_rebroadcast_date_8": "",
                "add_show_rebroadcast_time_8": "" ,
                "add_show_rebroadcast_date_9": "",
                "add_show_rebroadcast_time_9": "",
                "add_show_rebroadcast_date_10": "",
                "add_show_rebroadcast_time_10": "",
                "add_show_hosts_autocomplete": "",
                "add_show_background_color": colors[0],
                "add_show_color": colors[1]
            }

            data = { 'format': 'json' }

            i = 0
            for (name,value) in data_dict.items():
                data["data[{}][name]".format(i)] = name
                data["data[{}][value]".format(i)] = value
                i = i + 1

            r = self.session.post(self.url+'/Schedule/add-show',data=data).text
            if "Cannot schedule overlapping shows" in r:
                print("Cannot schedule overlapping shows")

            return

        def event_feed(self,start,end):
            data = {
                  'format': 'json',
                  'start': '@'+str(start.timestamp),
                  'end': '@'+str(end.timestamp),
                  'cachep': str(arrow.now().timestamp)
            }
            result = self.session.post(self.url+"/Schedule/event-feed",data=data).json()
            return result['events']
