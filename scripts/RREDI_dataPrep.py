### Haley Canham                                                            ###
### July 2022                                                               ###
### Updated September 2025 RREDI V2                                         ###
### Ensure that flow data and storm files cover the same wys for RREDI      ###
### Will throw an error in RREDI if not same wys                            ###

## Import libraries
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt

current_directory = os.getcwd()
os.chdir('..')
workingPath = os.getcwd()
print(workingPath)

## Read in all data files
Q_daily_filename = '{}\\workingfiles\\Streamflow_daily_data.csv'.format(workingPath)
Q_instant_filename = '{}\\workingfiles\\Streamflow_instant_data.csv'.format(workingPath)
storms_filename = '{}\\workingfiles\\StormGenerator\\StormGenerator_output.csv'.format(workingPath)

Q_daily = pd.read_csv(Q_daily_filename , parse_dates= ['date'])
Q_instant = pd.read_csv(Q_instant_filename, parse_dates= ['date'])
storms = pd.read_csv(storms_filename, parse_dates= ['Start', 'End'])

# identify the latest start date
starts = []
starts.append(Q_daily.date[0]) # daily start
starts.append(Q_instant.date[0]) # instant start
starts.append(storms.Start[0]) # storms start

start = max(starts)
if start.month >= 10:
    start_wy = start.year +1
else:
    start_wy = start.year
print(start_wy)

# identify the earliest end date
ends = []
ends.append(Q_daily['date'][len(Q_daily)-1])
ends.append(Q_instant['date'][len(Q_instant)-1])
ends.append(storms['End'][len(storms)-1])

end = min(ends)
if end.month >= 10:
    end_wy = end.year +1
else:
    end_wy = end.year
print(end_wy)

# new dataframes with later than the start date and before the end date
storms = storms[storms['Start'] >= start]
Q_daily = Q_daily[Q_daily['date'] >= datetime.strptime('10/1/{}'.format(start_wy-1),'%m/%d/%Y')]
Q_instant = Q_instant[Q_instant['date'] >= datetime.strptime('10/1/{} 00:00:00'.format(start_wy-1),'%m/%d/%Y %H:%M:%S')]

storms = storms[storms['Start'] <= end]
Q_daily = Q_daily[Q_daily['date'] <= datetime.strptime('9/30/{}'.format(end_wy),'%m/%d/%Y')]
Q_instant = Q_instant[Q_instant['date'] <= datetime.strptime('09/30/{} 23:45:00'.format(end_wy),'%m/%d/%Y %H:%M:%S')]

start = datetime.strftime(start,'%m-%d-%Y')
end = datetime.strftime(end, '%m-%d-%Y')

# make sure all timesteps have a value
# Daily: if missing dates and values, replace with NAN
Q_daily = Q_daily.reset_index()
startdate_daily = Q_daily['date'][0]
enddate_daily = Q_daily['date'].iloc[-1]
Dates = pd.date_range(startdate_daily, enddate_daily, freq='d')
print(Dates)

# make sure in the correct input datetime format
daily_dates = []
for i in Q_daily.index:
    daily_dates.append(datetime.strftime(Q_daily['date'][i], '%m/%d/%Y'))
Q_daily['date'] = daily_dates

instant_dates = []
for i in Q_instant.index:
    instant_dates.append(datetime.strftime(Q_instant['date'][i], '%m/%d/%Y %H:%M:%S'))
Q_instant['date'] = instant_dates

storm_dates_start = []
storm_dates_end = []
for i in storms.index:
    storm_dates_start.append(datetime.strftime(storms['Start'][i], '%d-%b-%Y %H:%M:%S'))
    storm_dates_end.append(datetime.strftime(storms['End'][i], '%d-%b-%Y %H:%M:%S'))
storms['Start'] = storm_dates_start
storms['End'] = storm_dates_end

## write PreProcessing .csv files
Q_daily.to_csv('{}\\workingfiles\\RREDI_PreProcessing\\Q_D_PreProcessed.csv'.format(workingPath), index = False)
Q_instant.to_csv('{}\\workingfiles\\RREDI_PreProcessing\\Q_I_PreProcessed.csv'.format(workingPath), index = False)
storms.to_csv('{}\\workingfiles\\RREDI_PreProcessing\\P_storms_PreProcessed.csv'.format(workingPath), index = False)