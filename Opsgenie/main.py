#! /usr/bin/env python

import pandas as pd
import json
import requests
import sys
from datetime import datetime
from pytz import timezone
import datetime
import pytz

loc = '~/Desktop/opsgenie/shifts.xlsx'
schedule_id = 'c3f9e3b6-d717-424b-8085-5dfad8b4560e'
genie_token = 'f0c1430d-ee72-4dcc-ab49-e76b01d3ec75'

def prefix_time(x):
    x = list(x)
    prefix_zero = x[0]
    prefix_zero = str(prefix_zero)
    if prefix_zero == '0':
        prefix_zero = x[1]
        return prefix_zero
    else:
        x = ''.join(x)
        return x


## Function that convert time from Asia/Jerusalem to UTC

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

## Function that sort Dataframe by Rotation Name and execute PATCH API call that update the schedule

def sort_df(rotation_name, rotation_id):

    user_list = []
    start_date_list = []
    start_time_list = []
    end_date_list = []
    end_time_list = []

    df = pd.read_excel(loc)

    rslt_df = df[df["RotationName"] == rotation_name] 
    df = rslt_df.groupby(['StartDate', 'StartTime', 'EndDate', 'EndTime', 'RotationID', 'Users']).agg(tuple).reset_index()
    # print(df)
    for record in df.to_dict(orient='records'):
        
        start_date_list.append(str(record['StartDate']).split()[0])
        start_time_list.append(str(record['StartTime']))
        end_date_list.append(str(record['EndDate']).split()[0])
        end_time_list.append(str(record['EndTime']))
        user_list.append(str(record['Users']))


    ## Get the first Start Date and the first Start Time

    start_date = start_date_list[0]
    start_time = start_time_list[0]
    prefix_start_time_h = start_time.split(":")[0]
    prefix_start_time_m = start_time.split(":")[1] 
    prefix_start_time_h = prefix_time(prefix_start_time_h)
    prefix_start_time_m = prefix_time(prefix_start_time_m)

    ## Get the last End Date and the last End Start Time

    end_date = end_date_list[-1]
    end_time = end_time_list[-1]
    prefix_end_time_h = end_time.split(":")[0]
    prefix_end_time_m = end_time.split(":")[1] 
    prefix_end_time_h = prefix_time(prefix_end_time_h)
    prefix_end_time_m = prefix_time(prefix_end_time_m)

    ## Convert time and date to UTC

    time_split, date_split = change_time(start_date, start_time)
    my_start_date_split = date_split
    my_start_time_split = time_split

    time_split, date_split = change_time(end_date, end_time)
    my_end_date_split = date_split
    my_end_time_split = time_split
    

    ## Get User List to JSON
    
    user_list_json = {"participants": [{ "type": "user", "username": i} for i in user_list]}
    json.dumps(user_list_json)
    user_list_json = str(user_list_json)
    user_list_json = user_list_json[1:-1]
    user_list_json = user_list_json.replace("'",'"')


    ## PATCH API call that update the schedule
    

    headers = {
        'Authorization': 'GenieKey '+ genie_token,
        'Content-Type': 'application/json',
    }

    data = ' { "name": "'+ rotation_name +'", "startDate": "'+ my_start_date_split +'T'+ my_start_time_split + 'Z", "endDate": "'+ my_end_date_split +'T'+ my_end_time_split + 'Z", "type": "daily", "length": 1, '+ user_list_json + ', "timeRestriction": { "type": "time-of-day", "restriction": { "startHour": '+ prefix_start_time_h +', "endHour": '+ prefix_end_time_h +', "startMin": '+ prefix_start_time_m +', "endMin": '+ prefix_end_time_m +' } } }'
    response = requests.patch('https://api.eu.opsgenie.com/v2/schedules/'+ schedule_id +'/rotations/'+ rotation_id, headers=headers, data=data)

    response_Org = response.text
    sys.stdout.flush()
    response_json = json.loads(response_Org)
    print(response_json)
    

## Read excel file to Dataframe

df = pd.read_excel(loc)
df = df.groupby(['RotationName', 'RotationID']).agg(tuple).reset_index()

## Run function for each Rotation name

for record in df.to_dict(orient='records'):
    rotation_name = (str(record['RotationName']))
    rotation_id = (str(record['RotationID']))
    sort_df(rotation_name, rotation_id)
