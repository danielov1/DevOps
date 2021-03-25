#! /usr/bin/env python

import xlrd ## pip install xlrd==1.2.0, This version supported xlsx files
from xlrd import open_workbook
from datetime import time
import requests
import sys
import json
from datetime import datetime
from pytz import timezone
import datetime
import pytz


class Arm(object):
    def __init__(self, StartDate, EndDate, startTime, endTime, RotationName, RotationID, Name, User):
        self.StartDate = StartDate
        self.EndDate = EndDate
        self.startTime = startTime
        self.endTime = endTime
        self.RotationName = RotationName
        self.RotationID = RotationID
        self.Name = Name
        self.User = User

    def Arm(self):
        return[self.StartDate, self.EndDate, self.startTime, self.endTime, self.RotationName, self.RotationID, self.Name, self.User]

## function that change TZ
def change_time(m_date, m_time):
    time_zone = timezone('Asia/Jerusalem')
    my_time = m_date + " " + m_time
    changed_time = time_zone.localize(datetime.datetime.strptime(my_time, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.utc)

    changed_time = str(changed_time)
    changed_time = changed_time[:-6]
    split_date = changed_time.split()
    time_split = split_date[1]
    date_split = split_date[0]
    return time_split, date_split

## Open Excel file
loc = 'excelpath'
wb = open_workbook(loc)

## Read from Excel file and call to Class named Arm
for sheet in wb.sheets():
    number_of_rows = sheet.nrows
    number_of_columns = sheet.ncols

    items = []

    rows = []
    for row in range(1, number_of_rows):
        values = []
        for col in range(number_of_columns):
            value  = (sheet.cell(row,col).value)
            values.append(value)
        item = Arm(*values)
        items.append(item)

for item in items:
    start_datels = list(item.Arm())[0]
    end_datels = list(item.Arm())[1]
    start_timels = list(item.Arm())[2]
    end_timels = list(item.Arm())[3]
    rotation_namels = list(item.Arm())[4]
    rotation_IDls = list(item.Arm())[5]
    namels = list(item.Arm())[6]
    userls = list(item.Arm())[7]
    print(start_timels, start_datels)


    ## convert startDate format
    xl_date_start = start_datels
    datetime_date = xlrd.xldate_as_datetime(xl_date_start, 0)
    date_object = datetime_date.date()
    my_startDate = date_object.isoformat()
    my_startDate = str(my_startDate)


    ## convert endDate format
    xl_date_end = end_datels
    datetime_date = xlrd.xldate_as_datetime(xl_date_end, 0)
    date_object = datetime_date.date()
    my_endDate = date_object.isoformat()
    my_endDate = str(my_endDate)


    ## convert startTime format
    s = start_timels 
    s = int(s * 24 * 3600) 
    my_startTime = time(s//3600, (s%3600)//60, s%60) # hours, minutes, seconds
    my_startTime = str(my_startTime)


    ## convert endTime format
    e = end_timels 
    e = int(e * 24 * 3600) 
    my_endTime = time(e//3600, (e%3600)//60, e%60) # hours, minutes, seconds
    my_endTime = str(my_endTime)

    ## convert to UTC TZ
    time_split, date_split = change_time(my_startDate, my_startTime)
    my_startDate = date_split
    my_startTime = time_split

    time_split, date_split = change_time(my_endDate, my_endTime)
    my_endDate = date_split
    my_endTime = time_split

    print(my_startDate, my_startTime)
    print(my_endDate, my_endTime)


    # PATCH call request to Opsgenie
    headers = {
        'Authorization': 'GenieKey <key>,
        'Content-Type': 'application/json',
        }

    data = ' { "name": "'+ rotation_namels +'", "startDate": "'+ my_startDate +'T'+ my_startTime + 'Z", "endDate": "'+ my_endDate +'T'+ my_endTime + 'Z", "type": "daily", "length": 1, "participants": [ { "type": "user", "username": "'+ userls +'" } ] }'

    response = requests.patch('https://api.eu.opsgenie.com/v2/schedules/<schedule>/rotations/'+ rotation_IDls +'', headers=headers, data=data)   
    response_Org = response.text
    sys.stdout.flush()
    response_json = json.loads(response_Org)
    print(response_json)
    print(my_startTime, my_endTime)
