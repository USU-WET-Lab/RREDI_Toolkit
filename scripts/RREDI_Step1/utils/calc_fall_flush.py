### Haley Canham                             ###
### Modified from Patterson et al (2020)     ###

import numpy as np
import scipy.interpolate as ip
import matplotlib.pyplot as plt
import pandas as pd
import csv
from scipy.ndimage import gaussian_filter1d
from utils.helpers import find_index, peakdet, replace_nan
from utils.precip_readin import make_precip_data
from params import fall_params as def_fall_params
from utils.helpers import set_user_params



# import precip data matrix - Haley
# from utils.precip_readin import create_precip_matrix

# Purpose: modify original calc_fall_flush.py to identify flow events that are after an identified precip event
# output: list of flow events after each identifed precip event

def calc_fall_flush_timings_durations(flow_matrix, summer_timings, class_number, fall_params=def_fall_params,):
    params = set_user_params(fall_params, def_fall_params)

    max_zero_allowed_per_year, max_nan_allowed_per_year, min_flow_rate, sigma, broad_sigma, wet_season_sigma, peak_sensitivity, peak_sensitivity_wet, max_flush_duration, min_flush_percentage, wet_threshold_perc, peak_detect_perc, flush_threshold_perc, min_flush_threshold, date_cutoff, slope_sensitivity = params.values()
    
    F_peak_dates = []
    wet_dates = []
    durations = []
    mags = []
    dry_dates = []
    finalFEvents = []
    finalP_Sevents = []
    lefts = []
    rights = []
    years = []
    p_index = []
    peakmags = []
    endFdates = []
    pairedpeaks = []
    f_index = []
    finalP15minInt = []
    leftmag = []
    rightmag = []
    finalleftmag = []
    finalrightmag = []
    Pwystart = []
    Pwyend = []
    PStormID = []
    Pduration = []
    Pmag = []
    PsInt = []
    P15minInt = []
    
    # print('made it inside function')

    for column_number, _ in enumerate(flow_matrix[0]):
        print('column number:', column_number)

        wet_dates.append(None)
        durations.append([])
        lefts.append([])
        rights.append([])

        """Check to see if water year has more than allowed nan or zeros"""
        if np.isnan(flow_matrix[:, column_number]).sum() > max_nan_allowed_per_year or np.count_nonzero(flow_matrix[:, column_number] == 0) > max_zero_allowed_per_year or max(flow_matrix[:, column_number]) < min_flow_rate:
            F_peak_dates.append([])
            mags.append([])
            p_index.append([])
            f_index.append([])
            leftmag.append([])
            rightmag.append([])
            peakmags.append([])
            pairedpeaks.append([])
            finalFEvents.append([])
            Pwystart.append([])
            Pmag.append([])
            P15minInt.append([])
            finalP15minInt.append([])
            finalleftmag.append([])
            endFdates.append([])
            finalrightmag.append([])
            PStormID.append([])
            finalP_Sevents.append([])
            print('in the not loop')

        if np.isnan(flow_matrix[:, column_number]).sum() > max_nan_allowed_per_year or np.count_nonzero(flow_matrix[:, column_number] == 0) > max_zero_allowed_per_year or max(flow_matrix[:, column_number]) < min_flow_rate:
            # F_peak_dates.append([])
            # mags.append([])
        # else:
            continue

        """Get flow data"""
        # for one wy
        flow_data = flow_matrix[:, column_number]
        x_axis = list(range(len(flow_data)))

        """Interpolate between None values"""
        flow_data = replace_nan(flow_data)
        # print(flow_matrix)

        # print(flow_data)

        """Return to Wet Season"""
        if class_number == 3 or class_number == 4 or class_number == 5 or class_number == 6 or class_number == 7 or class_number == 8:
            wet_season_filter_data = gaussian_filter1d(flow_data, 6)
        else:
            wet_season_filter_data = gaussian_filter1d(flow_data, wet_season_sigma)
        broad_filter_data = gaussian_filter1d(flow_data, broad_sigma)
        if class_number == 1 or class_number == 2 or class_number == 9:
            slope_detection_data = gaussian_filter1d(flow_data, 7)
        elif class_number == 3 or class_number == 4 or class_number == 5 or class_number == 6 or class_number == 7 or class_number == 8:
            slope_detection_data = gaussian_filter1d(flow_data, 1)
        else:
            slope_detection_data = gaussian_filter1d(flow_data, 4)

        return_date = return_to_wet_date(flow_data, wet_season_filter_data, broad_filter_data, slope_detection_data,
                                         wet_threshold_perc, peak_detect_perc, peak_sensitivity_wet, column_number, slope_sensitivity)
        if return_date:
            wet_dates[-1] = return_date
        broad_filter_data = gaussian_filter1d(flow_data, broad_sigma)

        """Filter noise data with small sigma to find fall flush hump"""
        filter_data = gaussian_filter1d(flow_data, sigma)

        """Fit spline"""
        x_axis = list(range(len(filter_data)))
        spl = ip.UnivariateSpline(x_axis, filter_data, k=3, s=3)

        """Find the peaks and valleys of the filtered data"""
        mean_flow = np.nanmean(filter_data)
        maxarray, minarray = peakdet(spl(x_axis), mean_flow * peak_sensitivity)

        """Find max and min of filtered flow data"""
        max_flow = max(filter_data[20:])
        max_flow_index = find_index(filter_data[20:], max_flow) + 20

        min_flow = min(broad_filter_data[:max_flow_index])

        """If could not find any max and find"""
        if not list(maxarray) or not list(minarray) or minarray[0][0] > max_flow_index:
            F_peak_dates.append([])
            mags.append([])
            p_index.append([])
            f_index.append([])
            leftmag.append([])
            rightmag.append([])
            peakmags.append([])
            pairedpeaks.append([])
            finalFEvents.append([])
            Pwystart.append([])
            Pmag.append([])
            P15minInt.append([])
            finalP15minInt.append([])
            finalleftmag.append([])
            endFdates.append([])
            finalrightmag.append([])
            PStormID.append([])
            finalP_Sevents.append([])

            continue


        """Get flow magnitude threshold from previous summer's baseflow"""
        if column_number == 0:
            wet_date = wet_dates[0]
            baseflow = list(flow_matrix[:wet_date, column_number])
            bs_med = np.nanpercentile(baseflow, 50)
            dry_dates.append(summer_timings[column_number])
        else:
            summer_date = summer_timings[column_number - 1]
            dry_dates.append(summer_timings[column_number])
            if wet_dates[column_number]:
                if wet_dates[column_number] > 20:
                    wet_date = wet_dates[column_number] - 20
                else:
                    wet_date = wet_dates[column_number]
                baseflow = list(flow_matrix[summer_date:, column_number - 1]) + list(flow_matrix[:wet_date, column_number])
            else:
                baseflow = list(flow_matrix[summer_date:, column_number - 1])
            bs_med = np.nanpercentile(baseflow, 50)

        # append summer_timings to create bound for start of dry season events - for wildfire - Haley Canham

        yearlist_startdates = [] #added for wildfire to create yearly list within F_start_dates list - Haley Canham
        yearlist_mags = [] #added
        """Get fall flush peak"""
        counter = 0
        # Only test duration for first half of fall flush peak
        half_duration = int(max_flush_duration/2)
        min_flush_magnitude = 0

        for flow_index in maxarray:

            if counter == 0:
                if flow_index[0] < half_duration and flow_index[0] != 0 and flow_index[1] > broad_filter_data[int(flow_index[0])] and flow_index[1] > min_flush_magnitude and flow_index[0] <= date_cutoff:
                    """if index found is before the half duration allowed"""

                    yearlist_startdates.append(int(flow_index[0]))
                    yearlist_mags.append(flow_index[1])

                elif bool((flow_index[1] - spl(maxarray[counter][0] - half_duration)) / flow_index[1] > flush_threshold_perc or minarray[counter][0] - maxarray[counter][0] < half_duration) and flow_index[1] > broad_filter_data[int(flow_index[0])] and flow_index[1] > min_flush_magnitude and flow_index[0] <= date_cutoff:
                    """If peak and valley is separted by half duration, or half duration to the left is less than 30% of its value"""

                    yearlist_startdates.append(int(flow_index[0]))
                    yearlist_mags.append(flow_index[1])

            elif counter == len(minarray):
                break

            elif bool(minarray[counter][0] - maxarray[counter][0] < half_duration or maxarray[counter][0] - minarray[counter-1][0] < half_duration) and bool(flow_index[1] > broad_filter_data[int(flow_index[0])] and flow_index[1] > min_flush_magnitude and flow_index[0] <= date_cutoff):
                """valley and peak are distanced by less than half dur from either side"""

                yearlist_startdates.append(int(flow_index[0]))
                yearlist_mags.append(flow_index[1])

            elif (spl(flow_index[0] - half_duration) - min_flow) / (flow_index[1] - min_flow) < flush_threshold_perc and (spl(flow_index[0] + half_duration) - min_flow) / (flow_index[1] - min_flow) < flush_threshold_perc and flow_index[1] > broad_filter_data[int(flow_index[0])] and flow_index[1] > min_flush_magnitude and flow_index[0] <= date_cutoff:
                """both side of flow value at the peak + half duration index fall below flush_threshold_perc"""

                yearlist_startdates.append(int(flow_index[0]))
                yearlist_mags.append(flow_index[1])

            counter = counter + 1
        # print(yearlist_startdates)
        # if len(yearlist_startdates) == 0:
        #     yearlist_startdates.append('')
        #     yearlist_mags.append('')
        F_peak_dates.append(yearlist_startdates)
        mags.append(yearlist_mags)
        # print(F_peak_dates)


        """Check to see if last start_date falls behind the max_allowed_date"""

        #remove 0 from F_start_dates for safety
        # print(F_peak_dates)
        # print(F_peak_dates[-1])
        if len(F_peak_dates[-1]) != 0:
            if F_peak_dates[-1][0] == 0:
                F_peak_dates[-1][0] = -9999
                mags[-1][0] = -9999

        # remove -9999 values from list - output a list that only contains events that meet criteria!
        F_peak_dates[-1] = [i for i in F_peak_dates[-1] if i != -9999]
        mags[-1] = [i for i in mags[-1] if i != -9999]

        # print('Peak magnitude = ', mags, 'length=',len(mags))

        # print('Peak date = ', F_start_dates, 'lenght=', len(F_start_dates))

        """Get duration of each fall flush"""
        #for wildfire need to make a new list of year_durations and caluclate the duration of everything in that list
        current_duration, left, right = calc_fall_flush_durations_2(
            filter_data, F_peak_dates[-1])
        durations[-1] = current_duration
        lefts[-1] = left
        rights[-1] = right

        #find mag of start dates (left)
        yearly_leftmag = []
        for i in left:
            yearly_leftmag.append(flow_data[i])
        leftmag.append(yearly_leftmag)

        #find mag of end dates (rights)
        yearly_rightmag = []
        for i in right:
            yearly_rightmag.append(flow_data[i])
        rightmag.append(yearly_rightmag)

        print('made it to calling Precip!')



        # check to see if there is a flow event start (left) that is within 1 day after precip start date to peak flow event (start_date0 - keep those flow dates
        # precip_events, precip_events_mags, precip_data_all = make_precip_data2()
        wystart_year, wyend_year, PStormID_year, Pduration_year, Pmag_year, PsInt_year, P15minInt_year, wy_year = make_precip_data(column_number)

        Pwystart.append(wystart_year)
        Pwyend.append(wyend_year)
        PStormID.append(PStormID_year)
        Pduration.append(Pduration_year)
        Pmag.append(Pmag_year)
        PsInt.append(PsInt_year)
        P15minInt.append(P15minInt_year)


        yearly_finalFdates = []
        yearly_finalP_Sdates = []
        yearly_p_index = []
        yearly_peakmags = []
        yearly_endFdates = []
        yearly_pairedpeaks = []
        yearly_f_index = []

        # print('F_peak_dates',F_peak_dates)
        # print(len(F_peak_dates))
        # print(column_number)
        # print('mags',mags)
        # print('F_peak_dates',F_peak_dates[column_number])

        #find the associated flow event for each storm
        # print(column_number)
        count3 = 0
        for pdate in wystart_year:
            # print('pdate', pdate)
            count4 = 0
            for fdate in left:
                # print('fdate', fdate)
                endF = right[count4]
                # print(F_peak_dates)
                # print(column_number)
                # print(count4)
                # peak_date = F_peak_dates[-1][count4]
                # peakmag = mags[-1][count4]
                peak_date = F_peak_dates[column_number][count4]
                peakmag = mags[column_number][count4]
                # print('fdate:', fdate, 'count4:', count4, 'peakdate:', peak_date)
                if bool(pdate == fdate or pdate+1 == fdate or (pdate > fdate and pdate <= peak_date)): # keep flow date if equal or one day prior to pdate and equal to or less than peak flow date
                    yearly_finalFdates.append(fdate)
                    yearly_finalP_Sdates.append(pdate)
                    yearly_p_index.append(count3)
                    yearly_f_index.append(count4)
                    yearly_peakmags.append(peakmag)
                    yearly_endFdates.append(endF)
                    yearly_pairedpeaks.append(peak_date)
                    print('MATCH!!!!')
                    break
                count4 = count4 + 1
            count3 = count3 + 1

        finalFEvents.append(yearly_finalFdates)
        finalP_Sevents.append(yearly_finalP_Sdates)
        p_index.append(yearly_p_index)
        peakmags.append(yearly_peakmags)
        endFdates.append(yearly_endFdates)
        pairedpeaks.append(yearly_pairedpeaks)
        f_index.append(yearly_f_index)

        #make list of paired storm events 15min intensity
        yearly_finalP15minInt = []
        # for i in p_index[-1]:
        for i in p_index[column_number]:
            yearly_finalP15minInt.append(P15minInt_year[i])

        finalP15minInt.append(yearly_finalP15minInt)

        #make list of paired flow events start (left) and end (right) mags
        yearly_finalleftmag = []
        yearly_finalrightmag = []
        for i in f_index[column_number]:
            yearly_finalleftmag.append(leftmag[column_number][i])
            yearly_finalrightmag.append(rightmag[column_number][i])
        finalleftmag.append(yearly_finalleftmag)
        finalrightmag.append(yearly_finalrightmag)

        # print('Flow Events', lefts)
        # print('Precip Events', precip_events)

        # print('Final Precip Based Flow Event Start Dates', finalEvents)
        # print('Final Precip Based Precip Start Dates', finalPevents)
        # print('P-Index',p_index)

        # print(wystart)
        # print(P15minInt)

        #plot!!
        _plotter(x_axis, flow_data, filter_data, broad_filter_data, F_peak_dates, mags, wet_dates, column_number, left,
                 right, maxarray, minarray, min_flush_magnitude, slope_detection_data, dry_dates, finalFEvents, finalP_Sevents,
                 wystart_year, P15minInt_year, peakmags, endFdates, pairedpeaks, wy_year)

    # #write to csv!!
    years = list(range(0,len(finalFEvents)))

    with open('RREDI_Step1_output.csv','w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerow(['wy'] + years)
        writer.writerow(['FLOW'])
        writer.writerow(['all flow start dates'] + lefts)
        writer.writerow(['all flow peak dates'] + F_peak_dates)
        writer.writerow(['all flow end dates'] + rights)
        writer.writerow(['all flow start magnitudes'] + leftmag)
        writer.writerow(['all flow peak magnitudes'] + mags)
        writer.writerow(['all flow end magnitudes'] + rightmag)
        writer.writerow(['all flow durations'] + durations)
        writer.writerow(['PRECIPITATION'])
        writer.writerow(['all precip event start dates'] + Pwystart)
        writer.writerow(['all precip event magnitudes'] + Pmag)
        writer.writerow(['all precip event 15min Intensity'] + P15minInt)
        writer.writerow(['all precip StormID'] + PStormID)
        writer.writerow(['FLOW - PRECIPITATION PAIRS'])
        writer.writerow(['F-P pair precip index'] + p_index)
        writer.writerow(['F-P pair flow index'] + f_index)
        writer.writerow(['F-P pair precip start dates'] + finalP_Sevents)
        writer.writerow(['F-P pair precip 15min Intensity'] + finalP15minInt)
        writer.writerow(['F-P pair flow start dates'] + finalFEvents)
        writer.writerow(['F-P pair flow start magnitudes'] + finalleftmag)
        writer.writerow(['F-P pair flow peak dates'] + pairedpeaks)
        writer.writerow(['F-P pair flow peak magnitudes'] + peakmags)
        writer.writerow(['F-P pair flow end dates'] + endFdates)
        writer.writerow(['F-P pair flow end magnitudes'] + finalrightmag)

    # clear start_dates to just be the first event so dont have to modify following parts of FFC
    start_dates = []
    # start_dates.append(None)
    for i in F_peak_dates:
        if len(i) != 0:
            start_dates.append(i[0])
        else:
            start_dates.append(None)
    # print(start_dates)

    return start_dates, mags, wet_dates, durations


def calc_fall_flush_durations(flow_data, broad_filter_data, date):

    duration_left = None
    duration_right = None
    duration = None

    if date:
        date = int(date)
        for index_left, flow_left in enumerate(reversed(flow_data[:date])):
            if flow_left < broad_filter_data[date - index_left]:
                duration_left = index_left
                break
        for index_right, flow_right in enumerate(flow_data[date:]):
            if flow_right < broad_filter_data[date + index_right]:
                duration_right = index_right
                break

        if duration_left and duration_right:
            duration = duration_left + duration_right
        else:
            duration = None

    return duration


def calc_fall_flush_durations_2(filter_data, date):
    """Left side sharp"""
    der_percent_threshold_left = 50  # Slope of rising limb (i.e. derivative) must be "sharp"
    flow_percent_threshold_left = 80

    """Right side mellow"""
    der_percent_threshold_right = 30  # Slope of falling limb (i.e. derivative) has lower requirement to be part of flush duration
    flow_percent_threshold_right = 80

    duration = []
    left = []
    right = []

    for i in date:
        duration_i = None
        left_i = 0
        right_i = 0

        if i or i == 0:
            i = int(i)
            _, left_minarray = peakdet(filter_data[:i], 0.01)
            _, right_minarray = peakdet(filter_data[i:], 0.01)

            if not list(left_minarray):
                left_i = 0
            else:
                left_i = int(left_minarray[-1][0])

            if not list(right_minarray):
                right_i = 0
            else:
                right_i = int(i + right_minarray[0][0])

            if i - left_i > 10:
                """create spline, and find derivative"""
                x_axis_left = list(range(len(filter_data[left_i:i])))
                spl_left = ip.UnivariateSpline(
                    x_axis_left, filter_data[left_i:i], k=3, s=3)
                spl_first_left = spl_left.derivative(1)

                """check if derivative value falls below certain threshold"""
                spl_first_left_median = np.nanpercentile(
                    spl_first_left(x_axis_left), der_percent_threshold_left)

                """check if actual value falls below threshold, avoiding the rounded peak"""
                median_left = np.nanpercentile(
                    list(set(filter_data[left_i:i])), flow_percent_threshold_left)

                for index_left, der in enumerate(reversed(spl_first_left(x_axis_left))):
                    if der < spl_first_left_median and filter_data[i - index_left] < median_left:
                        left_i = i - index_left
                        break

            if right_i - i > 10:
                x_axis_right = list(range(len(filter_data[i:right_i])))
                spl_right = ip.UnivariateSpline(
                    x_axis_right, filter_data[i:right_i], k=3, s=3)
                spl_first_right = spl_right.derivative(1)

                spl_first_right_median = abs(np.nanpercentile(
                    spl_first_right(x_axis_right), der_percent_threshold_right))
                median_right = np.nanpercentile(
                    list(set(filter_data[i:right_i])), flow_percent_threshold_right)

                for index_right, der in enumerate(spl_first_right(x_axis_right)):
                    if abs(der) < spl_first_right_median and filter_data[i + index_right] < median_right:
                        right_i = i + index_right
                        break

            if left_i:
                duration_i = int(i - left_i)
            elif not left_i and right_i:
                duration_i = int(right_i - i)
            else:
                duration_i = 0

            duration.append(duration_i)
            right.append(right_i)
            left.append(left_i)

    return duration, left, right


def return_to_wet_date(flow_data, wet_season_filter_data, broad_filter_data, slope_detection_data,
                       wet_threshold_perc, peak_detect_perc, peak_sensitivity_wet, column_number, slope_sensitivity):
    search_index = None
    max_wet_peak_mag = max(broad_filter_data[20:])
    max_wet_peak_index = find_index(broad_filter_data, max_wet_peak_mag)

    if broad_filter_data[:max_wet_peak_index].size == 0:
        return None
    min_wet_peak_mag = min(broad_filter_data[:max_wet_peak_index])
    maxarray_wet, _ = peakdet(
        wet_season_filter_data, peak_sensitivity_wet)

    """Get the derivative of smoothed data for rate of change requirement"""
    x_axis = list(range(len(slope_detection_data)))
    spl = ip.UnivariateSpline(x_axis, slope_detection_data, k=3, s=3)
    spl_first = spl.derivative(n=1)

    """Loop through peaks to find starting point of search"""
    for index, value in enumerate(maxarray_wet):
        if len(maxarray_wet) == 1:
            if maxarray_wet[0][0] == 0:
                search_index = max_wet_peak_index
                break
            else:
                search_index = int(maxarray_wet[0][0])
                break
        else:
            if (maxarray_wet[index][1]-min_wet_peak_mag)/(max_wet_peak_mag-min_wet_peak_mag) > peak_detect_perc:
                search_index = int(maxarray_wet[index][0])
                break
    """Loop backwards from max flow index to beginning, to search for wet season"""
    if not search_index:
        return None
    for index, value in enumerate(reversed(wet_season_filter_data[:search_index])):
        if index == len(wet_season_filter_data[:search_index] - 1):
            return None
        elif (value - min_wet_peak_mag) / (max_wet_peak_mag - min_wet_peak_mag) < wet_threshold_perc and abs(spl_first(search_index - index)) < max_wet_peak_mag/slope_sensitivity:
            """If value percentage falls below wet_threshold_perc"""
            return_date = search_index - index


            return return_date


def _plotter(x_axis, flow_data, filter_data, broad_filter_data, F_peak_dates, mags, wet_dates, column_number,
             left, right, maxarray, minarray, min_flush_magnitude, slope_detection_data, dry_dates, finalFEvents,
             finalP_Sevents, wystart_year, P15minInt_year, peakmags, endFdates, pairedpeaks, wy_year):
    # plt.figure()
    fig, ax = plt.subplots()
    ax.plot(x_axis, flow_data,color = 'orange', label = 'Flow (cms)') #make sure to scale flow_data as needed
    for data in finalP_Sevents[-1]:
        ax.axvline(data, ls = ":", color = 'gray')
    plotallmags = []
    plotallpeakmags = []
    for i in mags[column_number]:
        plotallmags.append(i) # make sure to scale i as needed
    for i in peakmags[column_number]: # make sure to scale i as needed
        plotallpeakmags.append(i)
    ax.plot(F_peak_dates[column_number], plotallmags, '^', color = 'lightgreen', label = 'Flow Peak')
    ax.plot(pairedpeaks[column_number], plotallpeakmags,'^',color = 'darkgreen', label = 'Paired Flow Peak')

    ax2 = ax.twinx()

    if bool(wystart_year):
        ax2.bar(wystart_year, P15minInt_year, color = 'blue', label = '15min Precip Int (mm/hr)', snap = False)
    ax.set_xlabel('WY Day')
    ax.set_ylabel('Flow (cfs)')
    ax2.set_ylabel('Precipitation Intensity (mm/hr)')
    ax2.invert_yaxis()
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    lines = lines_1 + lines_2
    labels = labels_1 + labels_2
    ax2.legend(lines, labels, loc='upper left').set_zorder(2)
    ax.set_title('', loc = 'left')
    #ax.set_title('WY = 2021, Precip = Cinn RG', loc = 'right') #change the name of the RG!!
    ax.set_title('WY{}'.format(wy_year), loc = 'right')
    # ax.set_ylim([0,2])

    plt.savefig('post_processedFiles/Boxplots/WY{}.png'.format(wy_year))