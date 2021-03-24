#! /usr/bin/env python


import xlrd ## pip install xlrd==1.2.0, This version supported xlsx files
from xlrd import open_workbook
from datetime import time
import requests
import sys
import json


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

## Open Excel file
loc = '~/Desktop/opsgenie/shifts.xlsx'
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
    startDatels = list(item.Arm())[0]
    endDatels = list(item.Arm())[1]
    startTimels = list(item.Arm())[2]
    endTimels = list(item.Arm())[3]
    rotationNamels = list(item.Arm())[4]
    RotationIDls = list(item.Arm())[5]
    namels = list(item.Arm())[6]
    userls = list(item.Arm())[7]


    ## convert startDate format
    xl_date_start = startDatels
    datetime_date = xlrd.xldate_as_datetime(xl_date_start, 0)
    date_object = datetime_date.date()
    my_startDate = date_object.isoformat()
    my_startDate = str(my_startDate)

    ## convert endDate format
    xl_date_end = endDatels
    datetime_date = xlrd.xldate_as_datetime(xl_date_end, 0)
    date_object = datetime_date.date()
    my_endDate = date_object.isoformat()
    my_endDate = str(my_endDate)

    ## convert startTime format
    s = startTimels 
    s = int(s * 24 * 3600) 
    my_startTime = time(s//3600, (s%3600)//60, s%60) # hours, minutes, seconds
    my_startTime = str(my_startTime)

    ##convert endTime format
    e = endTimels 
    e = int(e * 24 * 3600) 
    my_endTime = time(e//3600, (e%3600)//60, e%60) # hours, minutes, seconds
    my_endTime = str(my_endTime)

    ## PATCH call request to Opsgenie
    headers = {
        'Authorization': 'GenieKey <API-Key>',
        'Content-Type': 'application/json',
        }

    data = ' { "name": "'+ rotationNamels +'", "startDate": "'+ my_startDate +'T'+ my_startTime + 'Z", "endDate": "'+ my_endDate +'T'+ my_endTime + 'Z", "type": "daily", "length": 1, "participants": [ { "type": "user", "username": "'+ userls +'" } ] }'

    response = requests.patch('https://api.eu.opsgenie.com/v2/schedules/<Schedule-ID>/rotations/'+ RotationIDls +'', headers=headers, data=data)   
    responseOrg = response.text
    sys.stdout.flush()
    responseJson = json.loads(responseOrg)
    print(responseJson)
