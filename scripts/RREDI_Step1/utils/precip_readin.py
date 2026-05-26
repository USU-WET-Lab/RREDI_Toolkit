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
import csv
import numpy as np
import os

from utils.matrix_convert_precip import MatrixConversionP
# from utils.helpers import get_calculation_numbers

def date_2_wy_num(date): ## start here. Need to consider before and after 10/1 seperatly
    # updated 19May26 to simplify and start precip wy day accounting at 0 instead of 1 - Haley C
    # need todetermine if leap year
    if date.month >= 10:
        the_year = date.year
    else:
        the_year = date.year - 1
    wy = the_year + 1
    base_day = datetime.strptime('10/1/{}'.format(the_year), '%m/%d/%Y')
    base_day = base_day.date()
    wy_days = []

    if bool(((wy) % 400 == 0) or (((wy) % 100 != 0) and ((wy) % 4 == 0))):  # if true, then a leap year
        year_length = 366
        # print('a leap year')
    else:
        year_length = 365
        # print('not a leap year')

    for i in range(0, year_length):
        wy_days.append(base_day + timedelta(days=i))
    the_wy_date = wy_days.index(date)
            
    return the_wy_date

def make_precip_data(column_number):
       
    # # open and read precipitation .csv

    the_pathP = '{}\\user_input_files\\Precipitation'.format(os.getcwd())
    list_pathP = os.listdir(the_pathP)
    pathP = '{}\\user_input_files\\Precipitation\\{}'.format(os.getcwd(),list_pathP[0])


    precip_csv = pd.read_csv(pathP)
    # print(precip_csv)
    
    s_datesP = []
    e_datesP = []
    
    StormID = precip_csv['StormID'].tolist()
    DurationP = precip_csv['Duration'].tolist()
    MagP = precip_csv['Magnitude'].tolist()
    Intensity_S_P = precip_csv['StormIntensity'].tolist()
    Intensity_15_P = precip_csv['PeakIntensity'].tolist()
    # print(DurationP)
    
    # convert datetime to python readable
    for i in precip_csv['Start']:
        DateS_P = datetime.strptime(i,'%d-%b-%Y %H:%M:%S')
        s_datesP.append(DateS_P)
    
    for i in precip_csv['End']:
        DateE_P = datetime.strptime(i,'%d-%b-%Y %H:%M:%S')
        e_datesP.append(DateE_P)
    
    # create dataframe
    dataP = pd.DataFrame(list(zip(StormID, s_datesP, e_datesP, DurationP, MagP, Intensity_S_P, Intensity_15_P)),
                         columns = ['StormID', 'start', 'end', 'duration', 'magnitude', 'stormIntensity','intervalIntensity'])
    
    # remove storms where duration = 0
    dataP = dataP.loc[dataP['duration'] != 0]
 
    # remove storms where interval intensity equals threshold
    Ithresh = 0.1 #5 used in Grizzly Creek 
    dataP = dataP.loc[dataP['intervalIntensity'] >= Ithresh]
    # print(dataP)
    
    #reset dataframe numbering
    dataP = dataP.reset_index(drop=True)
    # print(dataP)
        
    # read precip data start year
    year = dataP['start'][0].year
    if dataP['start'][0].month < 10:
        year = year -1 ## want the year the water year starts in (not the acual wy number)
    year = year + column_number # so this is the year the wy starts (wy - 1)
    # print(year)   
    wy_year = year +1
    
    start_wy_date = '10/1/{}'.format(year)
    start_wy_date = datetime.strptime(start_wy_date,'%m/%d/%Y')
    end_wy_date = '9/30/{}'.format(year+1)
    end_wy_date = datetime.strptime(end_wy_date,'%m/%d/%Y')
    # print(start_wy_date, end_wy_date)
    
    # splice data frame to get only storms within that wy 
    dataP_wy = dataP.loc[dataP['start'].between(start_wy_date, end_wy_date)]
    # print(dataP_wy)
    
    #match storms with wy dates and make lists
    
    # wystart = []
    wystart_year=[]

    for i in dataP_wy['start']:
        i = i.date()
        day = date_2_wy_num(i)
        wystart_year.append(day)

    # wystart.append(wystart_year)
    # print('wystart:',wystart_year)
    
    #MAKE End list
    # wyend = []
    wyend_year = []
    
    for i in dataP_wy['end']:
        i=i.date()
        day = date_2_wy_num(i)
        wyend_year.append(day)
        
    # wyend.append(wyend_year)
    # print('wyend:',wyend_year)
            
    # make all other lists!
    PStormID_year = dataP_wy['StormID'].tolist()
    Pduration_year = dataP_wy['duration'].tolist()
    Pmag_year = dataP_wy['magnitude'].tolist()
    PsInt_year = dataP_wy['stormIntensity'].tolist()
    P15minInt_year = dataP_wy['intervalIntensity'].tolist()
    
    
    return wystart_year, wyend_year, PStormID_year, Pduration_year, Pmag_year, PsInt_year, P15minInt_year, wy_year
