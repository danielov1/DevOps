#! /usr/bin/env python

import pandas as pd
import numpy as np
import datetime
import calendar
import itertools
import xlsxwriter
import openpyxl
from openpyxl import Workbook
import json
import sys
import requests
import math
import numpy

## List NOC users from opsgenie
noc_manager = <name>
genie_token = <api-teken>

url = "https://api.eu.opsgenie.com/v2/users/?query=skypeUsername=NOC"

payload={}
headers = {
  'Authorization': 'GenieKey '+ genie_token,
}

response = requests.request("GET", url, headers=headers, data=payload)

response_Org = response.text
sys.stdout.flush()
response_json = json.loads(response_Org)
total_count = int(response_json['totalCount'])



## Check what is the current date

now = datetime.datetime.now()
current_year = now.year
current_month = now.month
next_month = current_month + 1

## Check what is the next month

month_num_str = str(next_month)
datetime_object = datetime.datetime.strptime(month_num_str, "%m")
full_month_name = datetime_object.strftime("%B")

## Create file named by the next month name
file_loc = '~/Desktop/opsgenie/'+full_month_name+'.xlsx'


num_days_in_month = calendar.monthrange(current_year, current_month)[1]
next_date = f"'{current_year}-{next_month}-01"
rng = pd.date_range(next_date, periods=num_days_in_month, freq='D')

## Functions for date listing

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(itertools.islice(iterable, n))

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def single(iterable): 
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a = iterable
    return a

## Create date frame for the next month

day = ''
name = ''
user = ''
rotation_id = ''
times = itertools.cycle( ['01:00:00', '09:00:00', '17:00:00'])
rotations = itertools.cycle( ['Night', 'Day', 'Evening'])
empty_one = ''
employees_list = []
fullname_list = []
columns_array = ['Day','StartDate', 'EndDate', 'StartTime', 'EndTime', 'RotationName', 'RotationID', 'Name', 'User','']

for arr_index in columns_array:
    employees_list.append(arr_index)

x = 0
for x in range(total_count):
    fullname_list.append(response_json['data'][x]['fullName'])


dates = list(itertools.chain.from_iterable(itertools.repeat(timestamp.date(), 3) for timestamp in rng))

paired_dates = pairwise(take(num_days_in_month*3, dates))
paired_times = pairwise(take(num_days_in_month*3, times))
paired_rotations = single(take(num_days_in_month*3, rotations))


df = pd.DataFrame([[day, start_date, end_date, start_time, end_time, rotation_name, rotation_id, name, user, empty_one] for (start_date, end_date), (start_time, end_time), (rotation_name) in zip(paired_dates, paired_times, paired_rotations)],
               columns =columns_array)

## Add new columns with emplyees names

x = 0
for x in range(total_count):
    df = df.assign(**{fullname_list[x]: ""})

y = 0
for y in range(num_days_in_month*3):
    if y%3==1:
        df[noc_manager][y] = 'V'
        df['Name'][y] = noc_manager
    elif y%3!=1:
        df[noc_manager][y] = 'X'


## format Date cells to Short Date

df['StartDate'] = pd.to_datetime(df['StartDate'], errors='coerce').dt.strftime('%d/%m/%Y')
df['EndDate'] = pd.to_datetime(df['EndDate'], errors='coerce').dt.strftime('%d/%m/%Y')


## Add rotaion id formula
num_for_rotation = num_days_in_month * 3

i = 0
while i < num_for_rotation:
    i_str = i + 2
    i_str = str(i_str)
    df['Day'][i] = '=TEXT(B'+i_str+',"dddd")'
    df['RotationID'][i] = '=IF(F'+i_str+'="Evening","38fa4389-904e-442a-87d7-36dc0dc554b9",IF(F'+i_str+'="Night","3e558a75-9e32-48a2-8123-46f0aa448154",IF(F'+i_str+'="Day","81510d4f-fc2e-4c08-a436-35bbbb6b5384")))'

    ## List of Employees
    

    username_list = []
    first_name = []
    formula_var = ''
    split_fullname = ''

    formula_temp = ''
    max_if = 0
    loopif = math.ceil(total_count/7)
    innerloopcount = 7
    x = 0
    empty = '""'

    for z in range(loopif): 
        if loopif-z == 1:
            innerloopcount = total_count%7
        formula_temp = ''
        for in_loop in range(innerloopcount):
            x = in_loop + (z*7)

            username_list.append(response_json['data'][x]['username'])
            fullname_list.append(response_json['data'][x]['fullName'])
            
            formula_temp = 'IF(H'+i_str+'=''"'+fullname_list[x]+'"'',''"'+username_list[x]+'"'','+ formula_temp +')'

            formula_temp=formula_temp.replace(",)",",\"\")")
            if(z != 0 and z%7== 0):
                formula_temp = '=' + formula_temp
                break
        formula_var = formula_temp + " & " + formula_var
        formula_var = formula_var[:-1]
    formula_var = '=' + formula_var
    formula_var = formula_var[:-1]
    df['User'][i] = formula_var
    
    i = i + 1

## Write to Excel file

df.to_excel(file_loc, index = False)

