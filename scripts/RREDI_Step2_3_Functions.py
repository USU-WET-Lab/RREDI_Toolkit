## Haley Canham                                                             ###
## August 2022                                                              ###
### Updated September 2025 RREDI V2                                         ###
### Functions for RREDI step 2 and 3                                        ###

# import
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
from scipy.signal import argrelextrema
import numpy as np


def read_flow_file(workingPath):

    flow_path = '{}\\workingfiles\\RREDI_PreProcessing\\Q_I_PreProcessed.csv'.format(workingPath)

    flow_15min = pd.read_csv(flow_path, parse_dates=['date'])
    #
    # flow_Fdata = flow_csv['flow'].tolist()
    # datetime_Fdata = flow_csv['date'].tolist()
    #
    # #read dates
    # # datetime_Fdata = []
    # # for i in flow_csv['date']:
    # #     date = datetime.strptime(i, '%m/%d/%Y %H:%M:%S')
    # #     datetime_Fdata.append(date)
    # flow_15min = pd.DataFrame(list(zip(datetime_Fdata, flow_Fdata)),
    #                               columns=['datetime', 'flow'])
    # flow_15min['flow'] = pd.to_numeric(flow_15min['flow'])

    # calculate slope1 and slope2
    slope1 = []
    for i in range(len(flow_15min.index)):
        if i == 0:
            slope1.append(0)
        else:
            slope1.append(flow_15min['flow'][i] - flow_15min['flow'][i - 1])
    flow_15min['slope1'] = slope1

    slope2 = []
    for i in range(len(flow_15min.index)):
        if bool(i == 0 or i == 1):
            slope2.append(0)
        else:
            slope2.append(slope1[i] - slope1[i - 1])
    flow_15min['slope2'] = slope2

    return flow_15min


def hourly_flow(flow_15min):
    Fdata_hourly = flow_15min.resample('60min', on='date').mean()

    # calculate Slope1 - use hourly series
    slope1 = []
    for i in range(len(Fdata_hourly.index)):
        if i == 0:
            slope1.append(0)
        else:
            slope1.append(Fdata_hourly['flow'][i] - Fdata_hourly['flow'][i - 1])
    Fdata_hourly['slope1'] = slope1

    # calculate slope2 - use hourly series
    slope2 = []
    for i in range(len(Fdata_hourly.index)):
        if bool(i == 0 or i == 1):
            slope2.append(0)
        else:
            slope2.append(slope1[i] - slope1[i - 1])
    Fdata_hourly['slope2'] = slope2

    Fdata_hourly = Fdata_hourly.reset_index()

    return Fdata_hourly

def wy_num_2_date_v2(wy_number, year):
    # print('wy_number', wy_number, year)
   # determine if leap year
    if bool((year % 400 == 0) or ((year % 100 != 0) and (year % 4 == 0))):
        # then leap year
        # print('its a leap year!')
        wy_numbers = list(range(0, 366))
    else:
        # not leap year
        # print('its not leap year :/')
        wy_numbers = list(range(0, 365))
    if wy_number > 91:  # after Dec 31
        base_year = year -1 # add a year to make it the water year?
    else:
        base_year = year
    base_day = datetime.strptime('10/1/{}'.format(base_year), '%m/%d/%Y')

    the_date = base_day + timedelta(days = wy_number)

    # the_date = datetime.strftime(the_date, '%m/%d/%Y')
    # print('the date', the_date)

    return the_date

def end_event(Fpeak_mag, Fpeak_date, Fevent_start_mag, storm_end, flow_ending, falling_thresh, falling_slope, falling, endflags):
    # default to the end of the window, replace with something better if found
    # Fevent_end = flow_ending['date'].iloc[-1]
    # Fevent_end_mag = flow_ending['flow'].iloc[-1]
    # print(flow_ending)
    endflags.append(0)
    Fevent_end_index = flow_ending['flow'].idxmin()
    if pd.isna(Fevent_end_index):
        Fevent_end = flow_ending['date'].iloc[-1]
        Fevent_end_mag = flow_ending['flow'].iloc[-1]
        endflags.pop()
        endflags.append(1)
    else:
        # print(Fevent_end_index)
        Fevent_end = flow_ending['date'][Fevent_end_index]
        Fevent_end_mag = flow_ending['flow'].min()
        endflags.pop()
        endflags.append(0)

    # splice df to below falling threshold
    flow_ending_belowthresh = flow_ending[flow_ending['flow'] < (Fpeak_mag - ((Fpeak_mag - Fevent_start_mag) * falling_thresh))]
    flow_ending_belowthresh = flow_ending_belowthresh.reset_index()
    # print(flow_ending_belowthresh)

    # check that flow_ending_belowthresh not empty
    if len(flow_ending_belowthresh) > 1:
        if len(flow_ending_belowthresh) > 3:
            for f in range(flow_ending_belowthresh.index[0], flow_ending_belowthresh.index[-4]):
                # find first local minimum - current slope is (-) and next slope is (+ or 0)
                if ((flow_ending_belowthresh['slope1'][f] < 0) and (flow_ending_belowthresh['slope1'][f + 1] >= 0)
                        and (flow_ending_belowthresh['slope1'][f + 2] >= 0) and (flow_ending_belowthresh['slope1'][f + 4] >= 0)
                        and (flow_ending_belowthresh['flow'][f] < flow_ending_belowthresh['flow'][f+1:].max())
                        # and ((Fevent_end == flow_ending['date'][Fevent_end_index]) or (Fevent_end == flow_ending['date'].iloc[-1]))
                ):
                    Fevent_end = flow_ending_belowthresh['date'][f]
                    Fevent_end_mag = flow_ending_belowthresh['flow'][f]
                    print('local min found')
                    endflags.pop()
                    endflags.append(0)

                    # check that no flow values higher than peak, if there are flag event to be thrown out
                    flow_ending_between_check_df = flow_ending[flow_ending['date'].between(Fpeak_date, flow_ending_belowthresh['date'][f])]
                    flow_ending_between_check = flow_ending_between_check_df['flow'].max()
                    if (Fpeak_mag < flow_ending_between_check):
                        # defualt to end and flag
                        Fevent_end = flow_ending['date'].iloc[-1]
                        Fevent_end_mag = flow_ending['flow'].iloc[-1]
                        # replace flag this situation
                        endflags.pop()
                        endflags.append(1)
                    break

        for f in range(flow_ending_belowthresh.index[1], flow_ending_belowthresh.index[-1]):
            # # slope becomes shallow enough (opposite of start rise) and keeps falling
            if ((flow_ending_belowthresh['slope1'][f] >= -1) and (flow_ending_belowthresh['slope1'][f] <= 0)
                    and (flow_ending_belowthresh['slope1'][f+1] <= 0) and (flow_ending_belowthresh['slope1'][f-1] <= 0)
                    and (Fevent_end == flow_ending['date'].iloc[-1])):
                Fevent_end = flow_ending_belowthresh['date'][f]
                Fevent_end_mag = flow_ending_belowthresh['flow'][f]
                print('slope thresh used')
                endflags.pop()
                endflags.append(0)

                # check that no flow values higher than peak, if there are flag event to be thrown out
                flow_ending_between_check_df = flow_ending[flow_ending['date'].between(Fpeak_date, flow_ending_belowthresh['date'][f])]
                flow_ending_between_check = flow_ending_between_check_df['flow'].max()
                if (Fpeak_mag < flow_ending_between_check):
                    # defualt to end and flag
                    Fevent_end = flow_ending['date'].iloc[-1]
                    Fevent_end_mag = flow_ending['flow'].iloc[-1]
                    # replace flag this situation
                    endflags.pop()
                    endflags.append(1)
                break

        for f in range(flow_ending_belowthresh.index[1], flow_ending_belowthresh.index[-1]):
            # # slope becomes shallow enough (opposite of start rise) and keeps falling
            if ((flow_ending_belowthresh['slope1'][f] >= ((Fpeak_mag - Fevent_start_mag) * -0.05))
                    and (((Fpeak_mag - Fevent_start_mag) * -0.05) > -1) and (((Fpeak_mag - Fevent_start_mag) * -0.05) < 0)
                    and (flow_ending_belowthresh['slope1'][f] <= 0)
                    and (flow_ending_belowthresh['slope1'][f+1] <= 0) and (flow_ending_belowthresh['slope1'][f-1] <= 0)
                    and (Fevent_end == flow_ending['date'].iloc[-1])):
                Fevent_end = flow_ending_belowthresh['date'][f]
                Fevent_end_mag = flow_ending_belowthresh['flow'][f]
                print('slope -0.05 thresh used')
                endflags.pop()
                endflags.append(0)

                # check that no flow values higher than peak, if there are flag event to be thrown out
                flow_ending_between_check_df = flow_ending[flow_ending['date'].between(Fpeak_date, flow_ending_belowthresh['date'][f])]
                flow_ending_between_check = flow_ending_between_check_df['flow'].max()
                if (Fpeak_mag < flow_ending_between_check):
                    # defualt to end and flag
                    Fevent_end = flow_ending['date'].iloc[-1]
                    Fevent_end_mag = flow_ending['flow'].iloc[-1]
                    # replace flag this situation
                    endflags.pop()
                    endflags.append(1)
                break

        for f in range(flow_ending_belowthresh.index[0], flow_ending_belowthresh.index[-1]):
            # for no rise events, make sure to keep end close
            if (flow_ending_belowthresh['slope1'][f:f+5].mean() == 0) and ((Fpeak_mag - Fevent_start_mag)/Fpeak_mag < 0.1):
                Fevent_end = flow_ending_belowthresh['date'][f]
                Fevent_end_mag = flow_ending_belowthresh['flow'][f]
                endflags.pop()
                endflags.append(0)
                print('no rise event')
                endflags.pop()
                endflags.append(0)

                # check that no flow values higher than peak, if there are flag event to be thrown out
                flow_ending_between_check_df = flow_ending[flow_ending['date'].between(Fpeak_date, flow_ending_belowthresh['date'][f])]
                flow_ending_between_check = flow_ending_between_check_df['flow'].max()
                if (Fpeak_mag < flow_ending_between_check):
                    # defualt to end and flag
                    Fevent_end = flow_ending['date'].iloc[-1]
                    Fevent_end_mag = flow_ending['flow'].iloc[-1]
                    # replace flag this situation
                    endflags.pop()
                    endflags.append(1)
                break
    elif ((len(flow_ending_belowthresh) <= 1) and (len(flow_ending) >= 2)):
        for f in range(flow_ending.index[0], flow_ending.index[-2]):
            # find first local minimum - current slope is (-) and next slope is (+ or 0)
            if ((flow_ending['slope1'][f] < 0) and (flow_ending['slope1'][f + 1] >= 0)
                    and (flow_ending['slope1'][f + 2] >= 0)
                    and (flow_ending['flow'][f] < flow_ending['flow'][f + 1:].max())
                    and (Fevent_end == flow_ending['date'].iloc[-1])):
                Fevent_end = flow_ending['date'][f]
                Fevent_end_mag = flow_ending['flow'][f]
                print('local min not below thresh found')
                endflags.pop()
                endflags.append(0)

                # check that no flow values higher than peak, if there are flag event to be thrown out
                flow_ending_between_check_df = flow_ending[flow_ending['date'].between(Fpeak_date, flow_ending['date'][f])]
                flow_ending_between_check = flow_ending_between_check_df['flow'].max()
                if (Fpeak_mag < flow_ending_between_check):
                    # defualt to end and flag
                    Fevent_end = flow_ending['date'].iloc[-1]
                    Fevent_end_mag = flow_ending['flow'].iloc[-1]
                    # replace flag this situation
                    endflags.pop()
                    endflags.append(1)
                break

    # check that end is not greater than peak
    if Fevent_end_mag > Fpeak_mag:
        Fevent_end = flow_ending['date'].iloc[-1]
        Fevent_end_mag = flow_ending['flow'].iloc[-1]
        endflags.pop()
        endflags.append(1)

    # check that min found is not just flat afterwards through the end of the window
    # print(flow_ending)
    # print(Fevent_end_index)
    # print(flow_ending.loc[Fevent_end_index:])
    # print(flow_ending['flow'].loc[Fevent_end_index:])
    # print(flow_ending['flow'].loc[Fevent_end_index:].min())
    # print(flow_ending['flow'].loc[Fevent_end_index:].max())

    # check that no flow values higher than peak, if there are flag event to be thrown out
    flow_ending_between_check_df = flow_ending[flow_ending['date'].between(Fpeak_date, Fevent_end)]
    flow_ending_between_check = flow_ending_between_check_df['flow'].max()
    if (Fpeak_mag < flow_ending_between_check):
        # defualt to end and flag
        Fevent_end = flow_ending['date'].iloc[-1]
        Fevent_end_mag = flow_ending['flow'].iloc[-1]
        # replace flag this situation
        endflags.pop()
        endflags.append(1)

    # if the end is the last, flag bc essentially no end found
    if Fevent_end == flow_ending['date'].iloc[-1]:
        # flag this situation
        endflags.pop()
        endflags.append(1)

    print('End at: ', Fevent_end, Fevent_end_mag, endflags[-1])

    return Fevent_end, Fevent_end_mag, endflags


def plot_event(workingPath, flow_15min_chunk, flow_hourly_chunk, intensity_true, Fpeak_date, Fpeak_mag, Fevent_start, Fevent_start_mag,
               Fevent_end, Fevent_end_mag, j, count, wy_year, antecedent_storms, storm_summary):
    ## Plot Chuckdata
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(flow_15min_chunk['date'], flow_15min_chunk['flow'], color='wheat', label='15-min Flow')
    ax.plot(flow_hourly_chunk['date'], flow_hourly_chunk['flow'], color='orange', label='Hourly Flow')
    # ax.plot(hour_chunk.index, hour_chunk['slope1'], color = 'lightgray', label = 'Slope1')
    # ax.plot(flow_hourly_chunk['datetime'], flow_hourly_chunk['slope2'], color = 'lightgrey', label = 'Slope2')
    ax.plot(Fevent_start, Fevent_start_mag, '^', color='green')  # , label = 'Start')
    ax.plot(Fpeak_date, Fpeak_mag, '^', color='purple')  # , label = 'Peak')
    ax.plot(Fevent_end, Fevent_end_mag, '^', color='red')  # , label = 'End')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    ax2 = ax.twinx()
    ax2.invert_yaxis()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y %H:%M'))
    ax2.plot(intensity_true['time'], intensity_true['Intensity'], color='blue', label='Precipitation')
    if len(antecedent_storms.index != 0):
        ax2.bar(antecedent_storms['Start'], antecedent_storms['PeakIntensity'], width = 0.07, alpha = 0.5, color = 'lightblue', label = 'Antecedent Precip')

    # ax.set_yscale('log')

    ax.set_ylabel('Flow (cfs)', fontsize=16)
    ax2.set_ylabel("15-min Precip Intensity\n(mm/hr)", fontsize=16)
    plt.gcf().autofmt_xdate()
    # ax.set_title(watershed_str, loc='left')
    ax.set_title('WY{}, Event# = {}'.format(wy_year, count), loc='right')
    # ax.set_ylim(0,200)
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    lines = lines_1 + lines_2
    labels = labels_1 + labels_2
    ax.legend(lines, labels, loc='upper left')
    fig.tight_layout()

    plt.savefig('{}\\workingfiles\\RREDI_Step2_3\\Plots\\wy{}_count{}.png'.format(workingPath, wy_year,count))

    # plt.show()
    plt.close(fig)

    return

def event_attribution(j, i, workingPath,pair_Pindex, PStormID, precipmag_total_all, storm_summary,
                                          stormIDs_all, stormstart_all, stormend_all,PeakInt_mag_all, PeakInt_all, pair_startF, pair_endF, flow_15min,
                                          Fdata_hourly, Fpeak_mag_all, Fpeak_all, Fevent_start_all, Fevent_start_mag_all, Fevent_end_all, Fevent_end_mag_all, count, antecedent_precip_all, endflags, melt_start, summer_start, winter_start, seasonflags):

    #### PRECIPITATION
    ## Storm precip (mag and intensity data)
    # Need the storm number from the FFC
    Id = int(PStormID[pair_Pindex[i]])
    print(Id)
    stormIDs_all.append(Id)

    # #Read storm ID intensity and magnitude file
    intensitypath = '{}\\workingfiles\\StormGenerator\\Storms\\Intensity\\intensity_{}.csv'.format(workingPath, Id)
    intensitycsv = pd.read_csv(intensitypath)
    precipmagpath = '{}\\workingfiles\\StormGenerator\\Storms\\Magnitude\\magnitude_{}.csv'.format(workingPath, Id)
    precipmagcsv = pd.read_csv(precipmagpath)

    ## get storm total magnitude
    precipmag_total = precipmagcsv['DepthInc'].iloc[-1]
    precipmag_total_all.append(precipmag_total)

    # #get storm ID start time
    # storm_start = storm_summary['start'][Id-(storm_summary['StormID'][0])]
    storm_start = storm_summary['Start'][Id]#-(storm_summary['StormID'][0])]

    stormstart_all.append(storm_start)

    storm_end = storm_summary['End'][Id] #-(storm_summary['StormID'][0])]
    # storm_end = storm_summary['end'][Id-(storm_summary['StormID'][0])]

    print(storm_start, storm_end)
    stormend_all.append(storm_end)
    stormend_window = storm_end + timedelta(hours = 24)

    if storm_start.month >= 10:
        wy_year = storm_start.year +1
    else:
        wy_year = storm_start.year

    # Make Range_2 datetime format
    timeincrements = []
    for x in intensitycsv['TimeInc']:
        day = 0
        hour = int(x)
        minutes = int(x * 60) - (hour * 60)
        seconds = int(x * 3600) - (hour * 3600 + minutes * 60)
        if hour >= 24:
            day = int(hour / 24)
            hour = hour - (24*day)
        timeinc = "{}:{}:{}".format(hour, minutes, seconds)
        date = datetime.strptime(timeinc, '%H:%M:%S')
        date = date + timedelta(hours=day * 24)
        timeincrements.append(date)
    intensity = pd.DataFrame(list(zip(timeincrements, intensitycsv['Intensity'])),
                             columns=['time', 'Intensity'])

    # #get storm ID start time
    Ptimeactual = []
    for r in range(len(intensity)):
        day = intensity['time'][r].day - 1
        hour = intensity['time'][r].hour
        minute = intensity['time'][r].minute
        second = intensity['time'][r].second
        delta = day * 86400 + hour * 3600 + minute * 60 + second
        storm_next = storm_start + timedelta(seconds=delta)
        Ptimeactual.append(storm_next)
    intensity_true = pd.DataFrame(list(zip(Ptimeactual, intensitycsv['Intensity'])),
                                  columns=['time', 'Intensity'])

    # find peak intensity
    PeakInt_mag = float(intensity_true['Intensity'].max())
    PeakInt_mag_all.append(PeakInt_mag)
    PeakInt_index = intensity_true['Intensity'].idxmax()
    PeakInt = intensity_true['time'][PeakInt_index]
    PeakInt_all.append(PeakInt)

    ## add 0 at start and end of intensity_true
    intensity_true.loc[len(intensity_true.index)] = [intensity_true['time'][len(intensity_true) - 1], 0]
    toprow = pd.DataFrame({'time': intensity_true['time'][0], 'Intensity': 0}, index=[0])
    intensity_true = pd.concat([toprow, intensity_true]).reset_index(drop=True)

    # get antecedent precipitation
    antecedent_window = storm_start - timedelta(days=6)
    antecedent_storms = storm_summary[(storm_summary['Start'] > antecedent_window) & (storm_summary['Start'] < storm_start)]
    # sum total storm mags to be antecedent precip
    if len(antecedent_storms.index) == 0:
        antecedent_precip_all.append(0)
    else:
        antecedent_precip_all.append(antecedent_storms['Magnitude'].sum())

    #### FLOW
    startday_F = pair_startF[i]  # zero based
    year_start = int(storm_start.strftime('%Y'))
    # print('start day', startday_F, 'start year', year_start)
    if int(storm_end.strftime('%m')) == 12 and startday_F > 91:
        year_start = year_start + 1


    Fstart_date = wy_num_2_date_v2(startday_F, year_start) #in date

    # storm_start_date = storm_start.date()
    # storm_start_date = storm_start.strftime('%Y-%m-%d')

    print(storm_start, Fstart_date)
    print(type(storm_start))
    print(type(Fstart_date))

    if Fstart_date >= storm_start- timedelta(days = 2): #if  the flow start date is after the storm start date
        Fstart_date = storm_start - timedelta(days=2) # make Fstart_date at least 2 days prior to storm start


    endday_F = pair_endF[i]  # zero based
    year_end = int(storm_end.strftime('%Y'))
    if int(storm_end.strftime('%m')) == 12 and endday_F > 91:
        year_end = year_end + 1

    Fend_date = wy_num_2_date_v2(endday_F, year_end) # in date

    # storm_end_date = storm_end.date()
    if Fend_date <= storm_end + timedelta(days=15):
        Fend_date = storm_end + timedelta(days=15)

    print('flow start', Fstart_date, 'flow end', Fend_date)

    # chunk 15-min flow
    flow_15min_chunk = flow_15min.loc[flow_15min['date'].between(Fstart_date, Fend_date)]
    # print(flow_15min_chunk)
    # flow_15min_chunk = flow_15min.loc[flow_15min['datetime'].between(Fstart_date, Fend_date)]
    flow_15min_chunk = flow_15min_chunk.reset_index()
    # print(flow_15min_chunk)
    # flow_15min_afterstorm = flow_15min.loc[flow_15min['date'].between(storm_end, Fend_date)]
    # flow_15min_afterstorm = flow_15min_afterstorm.reset_index()
    flow_15min_window = flow_15min.loc[flow_15min['date'].between(storm_start-timedelta(minutes = 60), stormend_window)]
    flow_15min_afterstorm_24 = flow_15min.loc[flow_15min['date'].between(storm_end-timedelta(minutes = 15),stormend_window)]
    flow_15min_duringstorm =flow_15min.loc[flow_15min['date'].between(storm_start-timedelta(minutes = 60), storm_end)]


    # chunk hourly flow
    flow_hourly_chunk = Fdata_hourly.loc[Fdata_hourly['date'].between(Fstart_date, Fend_date)]
    flow_hourly_chunk = flow_hourly_chunk.reset_index()
    flow_hourly_afterstorm = Fdata_hourly.loc[Fdata_hourly['date'].between(storm_end, Fend_date)]
    flow_hourly_afterstorm = flow_hourly_afterstorm.reset_index()
    # flow_hourly_duringstorm = Fdata_hourly.loc[Fdata_hourly['date'].between(storm_start, stormend_window)]
    # flow_hourly_duringstorm = flow_hourly_duringstorm.reset_index()
    # print(storm_start)
    # print(flow_hourly_afterstorm)


    ## Identify peak 15-min datetime and mag after storm end within 24 hours
    # flow_15min_window = flow_15min.loc[flow_15min['date'].between(storm_start+timedelta(minutes=15), stormend_window)]
    # flow_15min_afterstorm_24 = flow_15min.loc[flow_15min['date'].between(storm_end-timedelta(minutes = 15),stormend_window)]
    # flow_15min_duringstorm =flow_15min.loc[flow_15min['date'].between(storm_start+timedelta(minutes = 15), storm_end)]


    if ((len(flow_15min_window) == 0) or (len(flow_15min_afterstorm_24) == 0) #or (len(flow_15min_afterstorm) == 0)
            or (len(flow_15min_chunk) == 0) or (storm_start < flow_15min_chunk.date[0])):
        # print('skipped because not in flow window')
        Fpeak_mag_all.append('NAN')
        Fpeak_all.append('NAN')
        Fevent_start_all.append('NAN')
        Fevent_start_mag_all.append('NAN')
        Fevent_end_all.append('NAN')
        Fevent_end_mag_all.append('NAN')
        endflags.append('NAN')
        seasonflags.append('NAN')

    # elif (len(flow_15min_afterstorm_24) == 0):
    #     # print('skipped becuase not in after storm window')
    #     Fpeak_mag_all.append('NAN')
    #     Fpeak_all.append('NAN')
    #     Fevent_start_all.append('NAN')
    #     Fevent_start_mag_all.append('NAN')
    #     Fevent_end_all.append('NAN')
    #     Fevent_end_mag_all.append('NAN')
    #     endflags.append('NAN')
    #     seasonflags.append('NAN')
    #
    # elif (len(flow_15min_afterstorm) == 0):
    #     # print('skipped becuase not in after storm window')
    #     Fpeak_mag_all.append('NAN')
    #     Fpeak_all.append('NAN')
    #     Fevent_start_all.append('NAN')
    #     Fevent_start_mag_all.append('NAN')
    #     Fevent_end_all.append('NAN')
    #     Fevent_end_mag_all.append('NAN')
    #     endflags.append('NAN')
    #     seasonflags.append('NAN')
    #
    # elif (len(flow_15min_chunk) == 0):
    #     # print('skipped becuase not in after storm window')
    #     Fpeak_mag_all.append('NAN')
    #     Fpeak_all.append('NAN')
    #     Fevent_start_all.append('NAN')
    #     Fevent_start_mag_all.append('NAN')
    #     Fevent_end_all.append('NAN')
    #     Fevent_end_mag_all.append('NAN')
    #     endflags.append('NAN')
    #     seasonflags.append('NAN')

    # elif storm_start < flow_15min_chunk.date[0]: #if the precip event is prior to the flow_15min_chunk
    #     # print('skipped becuase storm event prior to flow window')
    #     Fpeak_mag_all.append('NAN')
    #     Fpeak_all.append('NAN')
    #     Fevent_start_all.append('NAN')
    #     Fevent_start_mag_all.append('NAN')
    #     Fevent_end_all.append('NAN')
    #     Fevent_end_mag_all.append('NAN')
    #     endflags.append('NAN')
    #     seasonflags.append('NAN')

    else:
        # identify local maxes after storm ends
        flow_15min_afterstorm_24['maxs'] = flow_15min_afterstorm_24.iloc[argrelextrema(flow_15min_afterstorm_24.flow.values, np.greater_equal, order=48)[0]]['flow'] #12 hrs *4 15min/hr = 32

        # get the highest of the local maxes
        stormmax = float(flow_15min_duringstorm['flow'].max())
        afterstormmax = float(flow_15min_afterstorm_24['flow'].max())
        # print(stormmax, afterstormmax)
        # print(flow_15min_window)
        #defualt to the highest value during or after storm
        Fpeak_mag = float(flow_15min_window['flow'].max())
        Fpeak_index = flow_15min_window['flow'].idxmax()
        # print(Fpeak_mag, Fpeak_index)
        Fpeak_date = flow_15min_window.loc[Fpeak_index,'date']

        #replace if something better is found
        if flow_15min_afterstorm_24['maxs'].notnull().all():
            Fpeak_index = flow_15min_afterstorm_24['maxs'].first_valid_index()
            Fpeak_date = flow_15min_afterstorm_24['date'][Fpeak_index]
            Fpeak_mag = flow_15min_afterstorm_24['flow'][Fpeak_index]
            if (Fpeak_mag < stormmax) and (len(flow_15min_duringstorm)>0):
                Fpeak_mag = float(flow_15min_duringstorm['flow'].max())
                Fpeak_index = flow_15min_duringstorm['flow'].idxmax()
                Fpeak_date = flow_15min_duringstorm.loc[Fpeak_index,'date']
        elif (flow_15min_afterstorm_24['maxs'].isnull().all()) and (len(flow_15min_duringstorm)>0):
            flow_15min_duringstorm['maxs'] = flow_15min_duringstorm.iloc[argrelextrema(flow_15min_duringstorm.flow.values, np.greater_equal, order=48)[0]]['flow']  # 12 hrs *4 15min/hr = 32
            if afterstormmax >= stormmax:
                Fpeak_mag = float(flow_15min_afterstorm_24['flow'].max())
                Fpeak_index = flow_15min_afterstorm_24['flow'].idxmax()
                Fpeak_date = flow_15min_afterstorm_24.loc[Fpeak_index,'date']
            elif stormmax > afterstormmax:
                if flow_15min_duringstorm['maxs'].notnull().all():
                    Fpeak_index = flow_15min_duringstorm['maxs'].first_valid_index()
                    Fpeak_date = flow_15min_duringstorm['date'][Fpeak_index]
                    Fpeak_mag = flow_15min_duringstorm['flow'][Fpeak_index]
                else:
                    Fpeak_mag = float(flow_15min_duringstorm['flow'].max())
                    Fpeak_index = flow_15min_duringstorm['flow'].idxmax()
                    Fpeak_date = flow_15min_duringstorm.loc[Fpeak_index,'date']

        Fpeak_mag_all.append(Fpeak_mag)
        Fpeak_all.append(Fpeak_date)
        print('Peak at: ', Fpeak_date, Fpeak_mag)

        ## Identify start 15-min datetime and mag by slope2 (2nd derivative exceeding 0.01)
        Fevent_start = storm_start - timedelta(minutes=60)
        Fevent_start_mag = flow_15min_window['flow'].iloc[0]
        # print(Fevent_start, Fevent_start_mag)
        # print(flow_hourly_duringstorm)

        # flow between storm start and peak
        flow_hourly_prepeak = Fdata_hourly.loc[Fdata_hourly['date'].between(storm_start - timedelta(minutes = 60), Fpeak_date)]
        flow_hourly_peakpeak = flow_hourly_prepeak.reset_index(inplace=False)
        flow_15min_prepeak = flow_15min.loc[flow_15min['date'].between(storm_start - timedelta(minutes = 60), Fpeak_date)]
        flow_15min_prepeak = flow_15min_prepeak.reset_index(inplace=False)

        print(flow_hourly_prepeak)
        if len(flow_hourly_prepeak.index) > 0:
            # print(flow_hourly_prepeak)
            # find local min first as the next default
            Fevent_start_min_index = flow_hourly_prepeak['flow'].idxmin()
            Fevent_start = flow_hourly_prepeak['date'][Fevent_start_min_index]
            Fevent_start_mag = flow_hourly_prepeak['flow'].min()

            rise_5 = (Fpeak_mag - flow_hourly_prepeak['flow'].min()) * 0.05

            if rise_5 < 1:
                rise_allowed = rise_5
                # then use rise_5
            else:
                rise_allowed = 1

            for k in range(Fevent_start_min_index, flow_hourly_prepeak.index[-1] + 1):
                if ((k != flow_hourly_prepeak.index[-1])
                        and (k != flow_hourly_prepeak.index[0])
                        and (Fevent_start_mag == flow_hourly_prepeak['flow'].min())
                        and (flow_hourly_prepeak['slope1'][k] >= rise_allowed)):
                        # and (flow_hourly_prepeak['slope1'][k + 1] >= rise_allowed)):
                        Fevent_start = flow_hourly_prepeak['date'][k - 1]
                        Fevent_start_mag = flow_hourly_prepeak['flow'][k - 1]
                        print('start slope consistently > rise allowed', rise_allowed)
                        break

            #
            # # then look through to find changes in slope
            # # print(Fevent_start_min_index, flow_hourly_prepeak.index[-1]+1)
            # for k in range(Fevent_start_min_index,flow_hourly_prepeak.index[-1]+1):
            #     # else look for when slope starts increaseing  with consistent values >1
            #     if ((k != flow_hourly_prepeak.index[-1]) and (k != flow_hourly_prepeak.index[0])
            #             and (Fevent_start_mag == flow_hourly_prepeak['flow'].min()) and (flow_hourly_prepeak['slope1'][k] > 1)
            #             and (flow_hourly_prepeak['slope1'][k+1] > 1)):
            #         Fevent_start = flow_hourly_prepeak['date'][k - 1]
            #         Fevent_start_mag = flow_hourly_prepeak['flow'][k - 1]
            #         print('start slope consistently >1')
            #         break
            #
            #     # else look for when slope starts increasing more than 5% of (peak - minstartflow) - and only continue if start still min
            #     elif ((flow_hourly_prepeak['slope1'][k] > (Fpeak_mag-flow_hourly_prepeak['flow'].min())*0.05)
            #           and (k < flow_hourly_prepeak.index[-1])
            #           and (flow_hourly_prepeak['slope1'][k+1] > (Fpeak_mag-flow_hourly_prepeak['flow'].min())*0.05)
            #           and (k != flow_hourly_prepeak.index[0])
            #           and (Fevent_start_mag == flow_hourly_prepeak['flow'].min())):
            #         Fevent_start = flow_hourly_prepeak['date'][k-1]
            #         Fevent_start_mag = flow_hourly_prepeak['flow'][k-1]
            #         print('start slope >5%')
            #         break

                # else if just a single hour rise at the end (super flashy) - and only continue if start still min
                elif ((k == flow_hourly_prepeak.index[-1])
                      and (k != flow_hourly_prepeak.index[0])
                      and (len(flow_hourly_prepeak) >= 1)
                      and (Fevent_start_mag == flow_hourly_prepeak['flow'].min())
                      and (flow_hourly_prepeak['slope1'][k] > 1)
                      and (flow_hourly_prepeak['slope1'][k-1] < 1)):
                    Fevent_start = flow_hourly_prepeak['date'][k-1]
                    Fevent_start_mag = flow_hourly_prepeak['flow'][k-1]
                    print('single hour only')
                    break

        print('Event start: ', Fevent_start, Fevent_start_mag)


        Fevent_start_all.append(Fevent_start)
        Fevent_start_mag_all.append(Fevent_start_mag)

        ## Identify end hourly datetime and mag
        # make ending eligible df - both after peak and after storm
        flow_ending = flow_hourly_afterstorm.loc[flow_hourly_afterstorm['date'].between(Fpeak_date,Fend_date, inclusive='right')]
        flow_ending = flow_ending.set_index('index')
        # flow_ending = flow_ending.reset_index()


        flow_ending['mins'] = flow_ending.iloc[argrelextrema(flow_ending.flow.values, np.less_equal, order=24)[0]]['flow']  # hrs

        if len(flow_ending) >0:
            if Fpeak_date.month >= melt_start and Fpeak_date.month < summer_start : #melt
                falling_thresh = 0.5 # needs to fall below this thresh from the peak to even consider
                falling_slope = -0.05 # slope1 value that needs to between and 0 (a local min)
                falling = 0.5 # will find the next value that falls below this thresh - dont actually use this
                Fevent_end, Fevent_end_mag, endflags = end_event(Fpeak_mag, Fpeak_date, Fevent_start_mag, storm_end, flow_ending, falling_thresh, falling_slope, falling, endflags)
                seasonflags.append('m')
            elif Fpeak_date.month >= summer_start and Fpeak_date.month < winter_start: #summer
                falling_thresh = 0.5
                falling_slope = -0.05
                falling = 0.95
                Fevent_end, Fevent_end_mag, endflags = end_event(Fpeak_mag, Fpeak_date, Fevent_start_mag, storm_end, flow_ending, falling_thresh, falling_slope, falling, endflags)
                seasonflags.append('s')
            elif Fpeak_date.month >= winter_start or Fpeak_date.month < melt_start: #winter
                falling_thresh = 0.5 #0.25
                falling_slope = -0.05
                falling = 0.75
                Fevent_end, Fevent_end_mag, endflags = end_event(Fpeak_mag, Fpeak_date, Fevent_start_mag, storm_end, flow_ending, falling_thresh, falling_slope, falling, endflags)
                seasonflags.append('w')

            # Fevent_end_all.append(Fevent_end)
            # Fevent_end_mag_all.append(Fevent_end_mag)

            plot_event(workingPath, flow_15min_chunk, flow_hourly_chunk, intensity_true, Fpeak_date, Fpeak_mag, Fevent_start, Fevent_start_mag,
                   Fevent_end, Fevent_end_mag, j, count, wy_year, antecedent_storms, storm_summary)

        else:
            Fevent_end = 'NAN'
            Fevent_end_mag = 'NAN'
            seasonflags.append('NAN')
            endflags.append(1)

        Fevent_end_all.append(Fevent_end)
        Fevent_end_mag_all.append(Fevent_end_mag)

    return  precipmag_total_all, stormIDs_all, stormstart_all, stormend_all, PeakInt_mag_all, PeakInt_all, Fpeak_mag_all, Fpeak_all, Fevent_start_all, Fevent_start_mag_all, Fevent_end_all, Fevent_end_mag_all, antecedent_precip_all, endflags, seasonflags

def yearly_events(j, workingPath, event_ids, storm_summary, flow_15min, Fdata_hourly, stormIDs_all,
                  stormstart_all, stormend_all, precipmag_total_all, PeakInt_mag_all, PeakInt_all, Fevent_start_all, Fevent_start_mag_all,
                  Fpeak_all, Fpeak_mag_all, Fevent_end_all, Fevent_end_mag_all, num_events, wys, wycount, antecedent_precip_all,
                  endflags, melt_start, summer_start, winter_start, seasonflags):

    # flow events
    PStormID = list(map(float, (str(event_ids[12])[1:-1]).split(',')))
    # precip-flow event pairs
    pair_Pindex = list(map(int, (str(event_ids[14])[1:-1]).split(',')))
    pair_startF = list(map(int, (str(event_ids[18])[1:-1]).split(',')))
    pair_endF = list(map(int, (str(event_ids[22])[1:-1]).split(',')))


    count = 0
    for i in range(len(pair_Pindex)): #going through each event pair
        wys.append(wycount)
        print('Event#', count)
        num_events.append(count)


        # call event attribution function for each event pair
        (precipmag_total_all, stormIDs_all, stormstart_all, stormend_all, PeakInt_mag_all, PeakInt_all, Fpeak_mag_all, Fpeak_all,
         Fevent_start_all, Fevent_start_mag_all, Fevent_end_all, Fevent_end_mag_all, antecedent_precip_all, endflags,
         seasonflags) =  event_attribution(j, i,  workingPath,pair_Pindex, PStormID, precipmag_total_all, storm_summary,
                                          stormIDs_all, stormstart_all, stormend_all,PeakInt_mag_all, PeakInt_all, pair_startF, pair_endF, flow_15min,
                                          Fdata_hourly, Fpeak_mag_all, Fpeak_all, Fevent_start_all, Fevent_start_mag_all, Fevent_end_all, Fevent_end_mag_all, count, antecedent_precip_all, endflags, melt_start, summer_start, winter_start, seasonflags)

        count = count + 1
    return stormIDs_all, stormstart_all, stormend_all, precipmag_total_all, PeakInt_mag_all, PeakInt_all, Fevent_start_all, Fevent_start_mag_all, \
           Fpeak_all, Fpeak_mag_all, Fevent_end_all, Fevent_end_mag_all, num_events, wys, antecedent_precip_all, endflags, seasonflags


def calculations(Fevent_end_all, Fevent_start_all, Fpeak_all, Fevent_start_mag_all, Fpeak_mag_all, stormstart_all, PeakInt_all):
    flowduration = []
    timetopeak= []
    timetorecession = []
    rise = []
    storm_start_timetopeak = []
    storm_int_timetopeak = []

    for i in range(len(Fpeak_all)):
        if ((Fpeak_all[i] != 'NAN') and (Fevent_end_all[i] != 'NAN')):
            flowduration.append(((Fevent_end_all[i] - Fevent_start_all[i]).total_seconds()) / 3600)
            timetopeak.append(((Fpeak_all[i] - Fevent_start_all[i]).total_seconds()) / 3600)
            timetorecession.append(((Fevent_end_all[i] - Fpeak_all[i]).total_seconds()) / 3600)
            if Fevent_start_mag_all[i] != 0:
                rise.append(((Fpeak_mag_all[i] - Fevent_start_mag_all[i]) / Fevent_start_mag_all[i]) * 100)
            else:
                rise.append(0)
            storm_start_timetopeak.append(((Fpeak_all[i] - stormstart_all[i]).total_seconds()) / 3600)
            storm_int_timetopeak.append(((Fpeak_all[i] - PeakInt_all[i]).total_seconds()) / 3600)
        else:
            flowduration.append('NAN')
            timetopeak.append('NAN')
            timetorecession.append('NAN')
            rise.append('NAN')
            storm_start_timetopeak.append('NAN')
            storm_int_timetopeak.append('NAN')
    return flowduration, timetopeak, timetorecession, rise, storm_start_timetopeak, storm_int_timetopeak


def write_csv(workingPath,wys, storm_IDs_all, stormstart_all, stormend_all, precipmag_total_all, PeakInt_mag_all, PeakInt_all, Fevent_start_all, Fevent_start_mag_all,
          Fpeak_all, Fpeak_mag_all, Fevent_end_all, Fevent_end_mag_all, num_events, flowduration, timetopeak, timetorecession, rise,
              storm_start_timetopeak, storm_int_timetopeak, antecedent_precip_all, endflags, seasonflags):
    with open('{}\\workingfiles\\RREDI_Step2_3\\RREDI_Step2_3_output.csv'.format(workingPath), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['WY'] + wys)
        writer.writerow(['YearlyEventNumber'] + num_events)
        writer.writerow(['FLOW'])
        writer.writerow(['FlowStartDate'] + Fevent_start_all)
        writer.writerow(['FlowPeakDate'] + Fpeak_all)
        writer.writerow(['FlowEndDate'] + Fevent_end_all)
        writer.writerow(['FlowStartMag'] + Fevent_start_mag_all)
        writer.writerow(['FlowPeakMag'] + Fpeak_mag_all)
        writer.writerow(['FlowEndMag'] + Fevent_end_mag_all)
        writer.writerow(['PRECIPITATION'])
        writer.writerow(['StormID'] + storm_IDs_all)
        writer.writerow(['StormStartDate'] + stormstart_all)
        writer.writerow(['StormEndDate'] + stormend_all)
        writer.writerow(['StormPeakIntDate'] + PeakInt_all)
        writer.writerow(['StormPeakInt_mmh'] + PeakInt_mag_all)
        writer.writerow(['StormTotalPrecip_mm'] + precipmag_total_all)
        writer.writerow(['AntecedentPrecip_mm'] + antecedent_precip_all)
        writer.writerow(['CALCULATIONS'])
        writer.writerow(['FlowDuration_h'] + flowduration)
        writer.writerow(['FlowTimeToPeak_h'] + timetopeak)
        writer.writerow(['FlowTimeToEnd_h'] + timetorecession)
        writer.writerow(['FlowRise_%'] + rise)
        writer.writerow(['StormStartToFlowPeak_h'] + storm_start_timetopeak)
        writer.writerow(['StormMaxIntToFlowPeak_h'] + storm_int_timetopeak)
        # writer.writerow(['flow event volume (m3)'] + event_volume_all)
        # writer.writerow(['flow event volume rise (m3)'] + event_rise_volume_all)
        # writer.writerow(['flow event volume fall (m3)'] + event_fall_volume_all)
        writer.writerow(['FLAGS'])
        writer.writerow(['EndingFlag'] + endflags)
        writer.writerow(['SeasonFlag'] + seasonflags)

