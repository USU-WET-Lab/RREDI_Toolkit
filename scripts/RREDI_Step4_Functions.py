### Haley Canham                                                             ###
### November 2022                                                            ###
### Updated September 2025 RREDI V2                                          ###
### Identifying and flagging of events influenced by diurnal fluctuations    ###

## import libraries
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates


def DiurnalFlag(workingPath, events):
    diurnalflag = []
    # read in flow file
    flowpath = '{}\\workingfiles\\RREDI_PreProcessing\\Q_I_PreProcessed.csv'.format(workingPath)

    flow = pd.read_csv(flowpath, parse_dates=['date']) #, date_parser=(lambda x: datetime.strptime(x, "%m/%d/%Y %H:%M:%S")))

    #make hourly flow - smooth out 15min variabilty
    flow_hourly = flow.resample('60min', on='date').mean()
    flow_hourly = flow_hourly.reset_index()

    # loop through to identify events inflenced by diurnal cycling
    for event in range(0,len(events)):

        tally = []
        tally_withinevent = []

        eventstart = events['FlowStartDate'][event]
        # eventstart = datetime.strptime(eventstart, '%Y-%m-%d %H:%M:%S')
        eventend = events['FlowEndDate'][event]
        # eventend = datetime.strptime(eventend, '%Y-%m-%d %H:%M:%S')

        windowStart = eventstart - timedelta(days = 4)
        windowEnd = eventend + timedelta(days =4)

        flow_event = flow_hourly[(flow_hourly['date'] >= eventstart) & (flow_hourly['date'] <= eventend)]
        flow_window = flow_hourly[((flow_hourly['date'] >= windowStart) & (flow_hourly['date'] <= eventstart)) |
                           ((flow_hourly['date'] <= windowEnd) & (flow_hourly['date'] >= eventend))]
        # flow_window = flow_hourly[(flow_hourly['date'] >= windowStart) & (flow_hourly['date'] <= windowEnd)]
        # print(flow_window)

        # event_start_mag = events['flow start mag (cms)'][event]
        # event_end_mag = events['flow end mag (cms)'][event]
        event_amplitude = flow_event['flow'].max() - flow_event['flow'].min()

        daily_min = flow_window.groupby([flow_window['date'].dt.date])['flow'].min()
        daily_max = flow_window.groupby([flow_window['date'].dt.date])['flow'].max()
        amplitude = daily_max - daily_min
        amplitude_avg = amplitude.mean() #can find the average without include in the event?
        amplitude_10 = amplitude_avg*0.2
        for i in amplitude:
            if ((i <= amplitude_avg+amplitude_10) & (i>= amplitude_avg-amplitude_10)):
                tally.append(1)
        # check if there is any diurnal within event itself, and throw those out
        daily_min_withinevent = flow_window.groupby([flow_event['date'].dt.date])['flow'].min()
        daily_max_withinevent = flow_window.groupby([flow_event['date'].dt.date])['flow'].max()
        amplitude_withinevent = daily_max_withinevent-daily_min_withinevent
        for i in amplitude_withinevent: # check if there is any diurnal within event itself
            if ((i <= amplitude_avg+amplitude_10) & (i>= amplitude_avg-amplitude_10)):
                tally_withinevent.append(1)

        if (sum(tally)>= 3): #in a diurnal cycling period
            if (event_amplitude < 3*amplitude_avg): # or (sum(tally_withinevent) >=2): #if event less than x times the average amplitude, then throw away
                diurnalflag.append(1)
                # print(amplitude_avg)
                # print('is this diurnal???')

                #plot
                fig, ax = plt.subplots()
                ax.plot(flow_window['date'], flow_window['flow'], color = 'blue', label = 'Amplitude:{}'.format(round(amplitude_avg,2)))
                ax.plot(flow_event['date'], flow_event['flow'], color = 'red', label = 'Amplitude:{}'.format(round(event_amplitude,2)))

                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                plt.xticks(rotation = 45)
                ax.set_ylabel('Flow')
                # ax.set_title(watershed_str)
                ax.legend()
                fig.tight_layout()

                plt.savefig('{}\\workingfiles\\RREDI_Step4\\Diurnal\\throwaways\\Event_{}.png'.format(workingPath, event))

                # plt.show()
                plt.close(fig)
            else:
                diurnalflag.append(0)
                # plot
                fig, ax = plt.subplots()
                ax.plot(flow_window['date'], flow_window['flow'], color='blue', label = 'Amplitude:{}'.format(round(amplitude_avg,2)))
                ax.plot(flow_event['date'], flow_event['flow'], color='green', label = 'Amplitude:{}'.format(round(event_amplitude,2)))

                # date_form = DateFormatter("%m-%d-%y")
                # ax.xaxis.set_major_formatter(date_form)
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                plt.xticks(rotation = 45)
                ax.set_ylabel('Flow')
                # ax.set_title(watershed_str)
                ax.legend()

                fig.tight_layout()

                plt.savefig('{}\\workingfiles\\RREDI_Step4\\Diurnal\\keepers\\Event_{}.png'.format(workingPath, event))
                # plt.show()
                plt.close(fig)
        else:
            diurnalflag.append(0)

    # events['diurnalflag'] = diurnalflag
    # events_diurnal = events[events['diurnalflag'] != 1]
    # events_diurnal = events_diurnal.reset_index(drop = True)

    return diurnalflag
