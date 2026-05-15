### Haley Canham                                    ###
### October 2022                                    ###
### Updated September 2025 RREDI V2                 ###
## RREDI Step 4                                     ###


# libraries
import pandas as pd
from datetime import datetime, timedelta
from RREDI_Step4_Functions import DiurnalFlag
import os
import shutil


current_directory = os.getcwd()
os.chdir('..')
workingPath = os.getcwd()
print(workingPath)
#

#Read in event attributes .csv file
eventspath = '{}\\ExampleFiles\\RREDI_Step2_3\\RREDI_Step2_3_output.csv'.format(workingPath)

events = pd.read_csv(eventspath, header = None).T
events.columns = events.iloc[0]
events = events[1:]

# Remove NAN events
events = events[events['FlowDuration_h'] != 'NAN']

events = events.reset_index(drop=True)

events['EndingFlag'] = pd.to_numeric(events['EndingFlag'])
events['StormPeakInt_mmh'] = pd.to_numeric(events['StormPeakInt_mmh'])
events['StormTotalPrecip_mm'] = pd.to_numeric(events['StormTotalPrecip_mm'])
events['FlowStartMag'] = pd.to_numeric(events['FlowStartMag'])
events['FlowPeakMag'] = pd.to_numeric(events['FlowPeakMag'])
events['FlowEndMag'] = pd.to_numeric(events['FlowEndMag'])
events['FlowStartDate'] = pd.to_datetime(events['FlowStartDate'])
events['FlowPeakDate'] = pd.to_datetime(events['FlowPeakDate'])
events['FlowEndDate'] = pd.to_datetime(events['FlowEndDate'])
events['StormStartDate'] = pd.to_datetime(events['StormStartDate'])


# add in an actual wy column
events['wy_actual'] = events['StormStartDate'].dt.year
events['storm_start_month'] = events['StormStartDate'].dt.month
for k in range(0,len(events.index)):
    if events['storm_start_month'][k] >= 10:
        events['wy_actual'][k] = events['wy_actual'][k] + 1
events.drop('storm_start_month', axis=1, inplace=True)


# file management
if os.path.isdir('{}\\ExampleFiles\\DefaultOutputsFolder\\Diurnal'.format(workingPath)):
    shutil.rmtree('{}\\ExampleFiles\\DefaultOutputsFolder\\Diurnal'.format(workingPath))
os.mkdir('{}\\ExampleFiles\\DefaultOutputsFolder\\Diurnal'.format(workingPath))
os.mkdir('{}\\ExampleFiles\\DefaultOutputsFolder\\Diurnal\\throwaways'.format(workingPath))
os.mkdir('{}\\ExampleFiles\\DefaultOutputsFolder\\Diurnal\\keepers'.format(workingPath))

# Filtering and flagging!

# Flag duplicated events (keep in dataframe for future if needed)
duplicateflag = [0]*len(events.index)
for i in events.index:
# for i in range(0,len(events.index)):
#     print(i)
    if i != len(events['FlowPeakDate'])-1:
        # locate any other same peak exists later, keep the later one (flag this one)
        if ((events['FlowPeakDate'][i] == events['FlowPeakDate'][i+1])
                or ((events['FlowPeakDate'][i] - timedelta(hours = 1) <= events['FlowPeakDate'][i+1])
                    and (events['FlowPeakDate'][i] + timedelta(hours = 1) >= events['FlowPeakDate'][i+1]))):
            duplicateflag[i] = 1
            # but if the next duplicate event is tiny, keep the earlier larger one
            if (events['StormPeakInt_mmh'][i+1] < 0.5) or (events['StormTotalPrecip_mm'][i+1] < 0.5):
                duplicateflag[i] = 0
                duplicateflag[i+1] = 1
events['duplicateflag'] = duplicateflag

# diurnal filter
DiurnalFlag_list = DiurnalFlag(workingPath, events)
events['DiurnalFlag'] = DiurnalFlag_list

# flag events where peak=start (declining events) (but keep no response 0 events where peak=end
peak_start_flag = [0]*len(events.index)
for v in range(0,len(events.index)):
    if ((events['FlowStartDate'][v] == events['FlowPeakDate'][v])
            or (events['FlowStartDate'][v] + timedelta(hours=1) >= events['FlowPeakDate'][v])
            or ((events['FlowEndMag'][v] >= events['FlowPeakMag'][v]) and (events['FlowPeakMag'][v] != 0))):
        peak_start_flag[v] = 1
events['PeakStartFlag'] = peak_start_flag

# remove flagged events
filtered = events[(events['PeakStartFlag'] == 0) & (events['DiurnalFlag'] == 0) & (events['duplicateflag'] == 0) & (events['EndingFlag'] == 0)]
filtered = filtered.reset_index(drop = True)

# get counts and percent for each flagged instance
duplicate_sum = events['duplicateflag'].sum()
duplicate_percent = round(duplicate_sum/len(events.index)*100)

diurnal_sum = events['DiurnalFlag'].sum()
diurnal_percent = round(diurnal_sum/len(events.index)*100)

peak_start_sum = events['PeakStartFlag'].sum()
peak_start_percent = round(peak_start_sum/len(events.index)*100)

EndingFlag_sum = events['EndingFlag'].sum()
EndingFlag_percent = round(EndingFlag_sum/len(events.index)*100)


#write.csv for the remaining set of events

filtered.to_csv('{}\\ExampleFiles\\DefaultOutputsFolder\\RREDI_Step4_output.csv'.format(workingPath), index=False)

# # events write out
# print('The total number of events found is ', len(events.index))
# print('The number of duplicate events found is ', duplicate_sum, duplicate_percent, '%')
# print('The number of no ending events found is ', EndingFlag_sum, EndingFlag_percent, '%')
# print('The number of start=peak events  is ', peak_start_sum, peak_start_percent, '%')
# print('The number of diurnal events  is ', diurnal_sum, diurnal_percent, '%')
# print('The number of remaining events found is ', len(filtered.index), round(len(filtered.index)/len(events.index)*100), '%')

