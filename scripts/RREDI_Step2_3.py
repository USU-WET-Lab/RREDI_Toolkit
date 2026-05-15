## Haley Canham                                                             ###
## August 2022                                                              ###
### Updated September 2025 RREDI V2                                         ###
### Main script to call functions for RREDI Step 2 and 3                    ###

import pandas as pd
from RREDI_Step2_3_Functions import read_flow_file, hourly_flow, yearly_events, write_csv, calculations
import os

current_directory = os.getcwd()
os.chdir('..')
workingPath = os.getcwd()
print(workingPath)

# set variables
# define seasons start. if no melt season, set start melt == start summer
winter_start = 11
melt_start = 5
summer_start = 5

# Call readfiles function
stormspath = '{}\\ExampleFiles\\StormGenerator\\StormGenerator_output.csv'.format(workingPath)
storm_summary = pd.read_csv(stormspath, parse_dates=['Start', 'End'], index_col = ['StormID'])

flow_15min = read_flow_file(workingPath)
# remove nan flow data
flow_15min = flow_15min.loc[flow_15min.flow >= 0]

# generate hourly timeseries
Fdata_hourly = hourly_flow(flow_15min)
# print(Fdata_hourly)

## Read in RREDI_Step1_ouput.csv file
events_path = '{}\\ExampleFiles\\RREDI_Step1\\RREDI_Step1_output.csv'.format(workingPath)
events_csv = pd.read_csv(events_path)
event_prams = events_csv['wy'].tolist()

# define big lists to be created
## Define big lists to be created
Eventcount = []
Fpeak_all = []
Fpeak_mag_all = []
Fevent_start_mag_all = []
Fevent_start_all = []
Fevent_end_all = []
Fevent_end_mag_all = []
stormIDs_all = []
stormstart_all = []
stormend_all = []
PeakInt_all = []
PeakInt_mag_all = []
event_volume_all = []
event_rise_volume_all = []
event_fall_volume_all = []
precipmag_total_all = []
num_events = []
wys = []
antecedent_precip_all = []
endflags = []
seasonflags = []

# loop through all years in daily events file
wycount = 0
for j in range(0,len(events_csv.columns)-1):
    event_ids = events_csv[str(j)].tolist()

    if event_ids[16] == '[]': #the index of the first flow-precip pairs - so if no pairs exist
        # wys.append(wycount)
        # num_events.append('None')
        print('No rainfall-runoff pairs identified this year') #will move on to next year/quit if at the end
    else:
        # Perform RREDI Step 2 Event timing
        stormIDs_all, stormstart_all, stormend_all, precipmag_total_all, PeakInt_mag_all, PeakInt_all, Fevent_start_all, Fevent_start_mag_all, Fpeak_all, Fpeak_mag_all, Fevent_end_all, Fevent_end_mag_all, num_events, wys, antecedent_precip_all, endflags, seasonflags = yearly_events(j, workingPath, event_ids, storm_summary, flow_15min, Fdata_hourly, stormIDs_all, stormstart_all, stormend_all, precipmag_total_all, PeakInt_mag_all, PeakInt_all, Fevent_start_all, Fevent_start_mag_all, Fpeak_all, Fpeak_mag_all, Fevent_end_all, Fevent_end_mag_all, num_events, wys, wycount, antecedent_precip_all, endflags, melt_start, summer_start, winter_start, seasonflags) # call function for each year
    wycount = wycount + 1

# Perform RREDI Step 3 Calcualations
flowduration, timetopeak, timetorecession, rise, storm_start_timetopeak, storm_int_timetopeak = calculations(Fevent_end_all, Fevent_start_all, Fpeak_all, Fevent_start_mag_all, Fpeak_mag_all, stormstart_all, PeakInt_all)

write_csv(workingPath, wys, stormIDs_all, stormstart_all, stormend_all, precipmag_total_all, PeakInt_mag_all, PeakInt_all, Fevent_start_all, Fevent_start_mag_all, Fpeak_all, Fpeak_mag_all, Fevent_end_all, Fevent_end_mag_all, num_events, flowduration, timetopeak, timetorecession, rise, storm_start_timetopeak, storm_int_timetopeak, antecedent_precip_all, endflags, seasonflags)

