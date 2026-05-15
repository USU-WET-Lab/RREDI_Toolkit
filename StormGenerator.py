### Haley Canham                                                            ###
### August 2022                                                             ###
### Updated September 2025 RREDI V2                                         ###
### Convert precipitation rain gage timestamp tips to storms                ###
### Calculate running 15-min intensity, peak 15-min intensity, cum depth    ###

## import libraries
import pandas as pd
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import os

current_directory = os.getcwd()
os.chdir('..')
workingPath = os.getcwd()
print(workingPath)

# variables
stormgaps = [3]# Min temporal gap allowed between storms, units = hrs
I_int = 60 # storm intensity interval, units = minutes
tip = 0.1 # rainfall magnitude in each tip, unit = mm, #0.1mm for AORC, 0.245mm (0.01in) for tipping RG

# read rain gage timestamp tip file
data_filename = '{}\\ExampleFiles\\Precipitation_data.csv'.format(workingPath)
data = pd.read_csv(data_filename, header=None)

# make storm output files
filepath_storms = '{}\\ExampleFiles\\DefaultOutputsFolder\\Storms'.format(workingPath)
os.mkdir(filepath_storms)

for stormgap in stormgaps:
    print('Start ', stormgap, ' at ', datetime.now())

    filepath_mag = '{}\\ExampleFiles\\DefaultOutputsFolder\\Storms\\Magnitude'.format(workingPath)
    os.mkdir(filepath_mag)
    filepath_int = '{}\\ExampleFiles\\DefaultOutputsFolder\\Storms\\Intensity'.format(workingPath)
    os.mkdir(filepath_int)

    # create timestamp of tips
    timestamps = []
    for i in range(0,len(data[0])):
        the_datetime = data[0][i] +" "+ data[1][i]
        timestamps.append(datetime.strptime(the_datetime, '%m-%d-%Y %H:%M:%S'))
    # print(timestamps)

    # identify individual storms and make StormID
    # calculate time steps between tips
    dt_tips = []
    for i in range(0,len(timestamps)):
        if i != len(timestamps)-1:
            dt_tips.append((timestamps[i+1] - timestamps[i]).total_seconds()/60/60) #difference in hours
        else:
            dt_tips.append(0)

    # make dataframe
    df = pd.DataFrame(list(zip(timestamps, dt_tips)), columns=['timestamps', 'dt_tips'])
    # print(df)

    # identify breaks greater than storm gap
    storm_breaks = df.index[df['dt_tips']>stormgap].tolist()
    # print(df['timestamps'][len(df['timestamps'])-1])
    storm_breaks.append(len(df['timestamps'])-1)
    # print(storm_breaks, len(storm_breaks))

    stormIDs = list(range(1,len(storm_breaks)+1))
    # print(stormIDs, len(stormIDs))

    # Calculate storm start, stop, depth, and duration
    starts = []
    ends = []
    durations = []
    magnitudes = []

    for i in stormIDs:
        # print(i)
        if i == 1:
            index = i-1
            start = df['timestamps'][0]
            end = df['timestamps'][storm_breaks[index]]
            # print(storm_breaks[index])
            magnitude = (storm_breaks[index]+1)*tip # number of tips*tip #in mm

        elif i == len(stormIDs)+1:
            print('got in here at: ', i)
            index = i-1
            start = df['timestamps'][storm_breaks[index]+1]
            end = df['timestamps'].iloc[-1]
            magnitude = ((len(df['timestamps']) - storm_breaks[index])-1)*tip #in mm

        else:
            index= i-1
            start = df['timestamps'][storm_breaks[index-1]+1]
            end = df['timestamps'][storm_breaks[index]]
            magnitude = (storm_breaks[index] - storm_breaks[index-1])*tip # in mm

        duration = (end - start).total_seconds() / 60 / 60  # in hours

        # print('StormID: ', i)
        # print('start: ', start)
        starts.append(start)
        # print('end: ', end)
        ends.append(end)
        # print('duration: ', duration)
        durations.append(duration) #hrs
        # print('magnitude: ', magnitude)
        magnitudes.append(magnitude) #mm
    # print(starts)
    storms = pd.DataFrame(list(zip(stormIDs, starts, ends, durations, magnitudes)), columns = ['StormID', 'Start', 'End', 'Duration', 'Magnitude'])
    # print(storms)

    # calucalate peak rainfall intensity over moving window of specific interval
    I_int = I_int/60 # convert to hours
    dt = 2.7833e-04 #1 second intervals (units = hours)
    win_step = 0.0167/10 # 10-second intensity calculation step

    intensities = []
    time = []
    storm_ints = []
    peak_ints = []

    for i in storms.index:
        StormID = i +1
        # print('stormID: ', StormID)
        if storms['Duration'][i] <= I_int:
            if storms['Duration'][i] == 0:
                storm_int = 'NaN'
            else:
                storm_int = storms['Magnitude'][i]/storms['Duration'][i] #mm/hr
            peak_Int = 'NaN'
        else:
            storm_int = storms['Magnitude'][i]/storms['Duration'][i] #mm/hr

            #windowing for peak 15-min intensity
            # for each storm interpolate time difference and magnitude
            # get start and stop of df index
            if StormID == 1:
                # print('got in here')
                start_index = 0
                end_index = timestamps.index(timestamps[storm_breaks[i]])
            elif StormID == len(storms['StormID']):
                # print('got in here')
                start_index = timestamps.index(timestamps[storm_breaks[i-1]+1])
                end_index = timestamps.index(timestamps[-1])

            else:
                start_index = timestamps.index(timestamps[storm_breaks[i-1]+1])
                end_index = timestamps.index(timestamps[storm_breaks[i]])

            # print('start index: ', start_index)
            # print('end index: ', end_index)

            indices = list(range(start_index, end_index+1))
            # print(indices)
            mag_times = []
            mag_times.append(0)
            for x in indices:
                if x == indices[-1]:
                    break
                else:
                    mag_times.append((timestamps[x+1]-timestamps[x]).total_seconds()/60/60 + mag_times[-1]) #hours

            mag_cum = list(range(len(indices)))
            mag_cum = [mag * tip + tip for mag in mag_cum]

            magnitude_cumulative = pd.DataFrame(list(zip(mag_times, mag_cum)), columns = ['TimeInc', 'DepthInc'])
            # print(magnitude_cumulative)

            # now for the 15-min intensity
            win_halfstep = win_step/2
            time_intensity = []
            intensity_15min = []

            start_intensity = I_int/2
            end_intensity = magnitude_cumulative['TimeInc'].iloc[-1] - (I_int/2)
            # time_intensity.append(start_intensity)

            step = start_intensity
            while step < end_intensity:
                time_intensity.append(step)
                step = step + win_step
            # time_intensity.append(end_intensity)
            # print(time_intensity)

            mag_interp = interp1d(magnitude_cumulative['TimeInc'], magnitude_cumulative['DepthInc'])

            for j in time_intensity:
                win_start = j - I_int/2
                win_end = j + I_int/2

                accumulated_precip = mag_interp(win_end) - mag_interp(win_start) #mm
                Int_15min = accumulated_precip/I_int #mm/hr
                intensity_15min.append(Int_15min)

            intensity = pd.DataFrame(list(zip(time_intensity, intensity_15min)), columns=['TimeInc', 'Intensity'])
            # print(intensity)

            peak_Int = max(intensity['Intensity'])

            # write .csv files

            magnitude_cumulative.to_csv('{}\\magnitude_{}.csv'.format(filepath_mag,StormID), index = False)
            intensity.to_csv('{}\\intensity_{}.csv'.format(filepath_int, StormID), index = False)


        storm_ints.append(storm_int)
        peak_ints.append(peak_Int)

    storms['StormIntensity'] = storm_ints
    storms['PeakIntensity'] = peak_ints
    print(storms)

    # write .csv file
    storms.to_csv('{}\\ExampleFiles\\DefaultOutputsFolder\\Storms\\StormGenerator_output.csv'.format(workingPath), index = False)