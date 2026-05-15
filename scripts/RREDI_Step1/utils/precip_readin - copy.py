# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 12:31:52 2021

@author: Haley Canham
"""
# Purpose: to read in specified precip.csv and output a list of precip events exceeding a specified threshold organized by wy for the entire POR entered 
#### create a new folder like the user_input_files but for preci to be able to specify the file to be used in this run.

# output: list containing a list of precip events for each wy


    
# import libraries

import pandas as pd
from datetime import datetime, timedelta

from utils.matrix_convert import MatrixConversion


# open and read precipitation .csv
precip_csv = pd.read_csv('D:/Wildfire/FunctionalFlows/func-flow-master - WildfireFlowBased/func-flow-master/user_input_files/Precipitation/Precip_15min_forFFC_Twitchell.csv')

datetimes = []

precip_inc = precip_csv['precip'].tolist()
# intensity = precip_csv['intensity'].tolist()

#convert datetime to python readable
for i in precip_csv['datetime']:
    Datetime = datetime.strptime(i,'%m/%d/%Y %H:%M')
    datetimes.append(Datetime)

#create datetime precip dataframe    
data = pd.DataFrame(list(zip(datetimes,precip_inc)),columns = ['date', 'Precip_inc'])
# print(data)

# accumulate daily precip
data = data.set_index('date')
data_daily = data.resample('D').sum()
print(data_daily)

# #caluclate precipitation intensity
# intensity = []

# count = 0
# for i in data['Datetime']:
#     intensity.append(None)
#     if count == 0:
#         intensity[-1] = 0
#     else:
#         intensity_inc = data['Precip_inc'][count]/((data['Datetime'][count] - data['Datetime'][count-1]).total_seconds()/3600) #in depth/hr
#         intensity[-1] = intensity_inc
#     count = count + 1

#create dataframe with datetime and precip
# data_intensity = pd.DataFrame(list(zip(datetimes,intensity)),columns = ['Datetime', 'Intensity'])
# print(data_intensity)

# #make 15 min time series
# starttime = data['Datetime'][0]
# print(starttime)
# count_rows = data.shape[0]
# endtime = data['Datetime'][count_rows-1]
# print(endtime)

# length_15mins = int((endtime - starttime).total_seconds()/60/60*4)+1


# #this is slow method - need to make it faster
# fullDatetime = []
# count2 = 0
# for i in range(0,length_15mins):
#     if count2 == 0:
#         fullDatetime.append(starttime)
#     else:
#         time_inc = fullDatetime[-1]+timedelta(minutes=15)
#         fullDatetime.append(time_inc)
#     count2 = count2+1
    
# # fullDatetime = [datetime.strftime('%Y-%m-%d %H:%M:%S') for datetime in range(starttime, endtime), timedelta(minutes=15)]

# # print(fullDatetime) 
# fulldatetime_df = pd.DataFrame(list(zip(fullDatetime)),columns=['Datetime'])
# # print(fulldatetime_df)
# full_data = pd.merge_asof(fulldatetime_df,data, on='Datetime', allow_exact_matches = True)
# # print(full_data)



# start_date = data_daily['date'][0]
    
# # Create precip intensity wy matrix


# matrix = MatrixConversion(
    # data_daily['date'], data_daily['Precip_inc'], start_date)

# #create array of wy timestamps
# timestamp = []
# count2 = 1
# for day in range(1,367): #35136
#     count3 = 0
#     for mins in range (0,96):
#         time = count2 + count3
#         timestamp.append(time)
#         count3 = count3 + (1/24/4)
#     count2 = count2+1
# # print(timestamp)

# print(len(timestamp))




# specify precip intensity event threshold
thresh_intensity = 2 #mm/hr

# event identificaiton loop
p_events = [] #bg list of precipitation events

count3 = 0
# for column in precip_matrix
   



# return preciplist

  