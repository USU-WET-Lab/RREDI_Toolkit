# Rainfall-Runoff Event Detection and Identification (RREDI) toolkit V2 - ReadMe.txt
# Canham, H., Lane, B. (2025). Rainfall-Runoff Event Detection and Identification (RREDI) toolkit V2, HydroShare, 
  https://hydroshare.org/resource/c0b8d3aee3434df88adc1f495b3121f6/

# Utah Water Research Laboratory
# Utah State University

# November 2022 http://www.hydroshare.org/resource/797fe26dfefb4d658b8f8bc898b320de
# Updated January 2024 - Additional operational details and streamline of input file names. Include DiurnalFlaggingFunction.py file.
# Updated August 2025 - RREDI V2 release. RREDI code updated to identify better Step 3 runoff start and end using a large sample of watersheds ~250. Additional documentation (including this readme.txt) included and updated including descriptive figures. Example inputs and outputs from updated code included. 
  https://hydroshare.org/resource/c0b8d3aee3434df88adc1f495b3121f6/
# Updated May 2026 - Github repository created
# Updated 26May2026 - Updates to RREDI scripts inclduing steps 1,2_3, and 4. Updates made to imporove rainfall-runoff event pairing. 

# Contact
	Haley Canham - haley.canham@usu.edu
	Belize Lane - belize.lane@usu.edu
	
# To automate the analysis of post-wildfire rainfall-runoff events across numerous storms and watersheds, the hydrologic time-series analysis Rainfall-Runoff Event Detection and Information (RREDI) toolkit was developed. The RREDI algorithm first uses feature detection and signal processing of storm precipitation and flow data to identify rainfall-runoff events (Step 1). Then each rainfall-runoff event is extracted using 15-minute flow and instantaneous precipitation data and the timing and magnitude of the start, peak, and end of event is extracted (Step 2). These identifiers are then used to calculate a set of event attributes 
including time to peak, response time, duration, volume, and percent rise (Step 3). Erroneous identified rainfall-runoff events are flagged and removed (Step 4). These attributes from the identified rainfall-runoff events can then be analyzed to answer research questions regarding variability in rainfall-runoff patterns within and between watersheds. This algorithm utilizes the open-source Python.
 
# This resource is described in detail in:
	Canham, H. A., Lane, B., Phillips, C. B., and Murphy, B. P. (2025). Leveraging a time-series event separation method to disentangle time-varying hydrologic controls on streamflow- application to wildfire-affected catchments, Hydrologic Earth System Sciences, 29, 27-43, https://doi.org/10.5194/hess-29-27-2025.
	
# This resource references:
	Patterson, N. K., Lane, B., Sandoval-Solis, S., Pasternack, G. B., Yarnell, S. M., Qiu, Y. (2020). A hydrologic feature detection algorithm to quantify seasonal components of flow regimes, Journal of Hydrology, 585, 124787, https://doi.org/10.1016/j.jhydrol.2020.124787.

# This resource supersedes: 
	Canham, H., Lane, B. (2025). Rainfall-Runoff Event Detection and Identification (RREDI) toolkit, HydroShare, 
	http://www.hydroshare.org/resource/797fe26dfefb4d658b8f8bc898b320de
	
#Disclaimer
	RREDI is still in development.

# Contents
	ReadMe.txt -> read me file for resource
	ExampleFiles -> Folder containing all example input and output files for RREDI toolkit scripts. 
	 Example files are from USGS 11098000 and watershed summarized AORC precipitation data. 
		Streamflow_daily_data.csv -> Daily streamflow file. Retrieved and formatted from USGS 11098000. Note file formatting.
		Streamflow_instant_data.csv -> Instantaneous streamflow file. Retrieved and formatted from USGS 11098000. Note file formatting.
		Precipitation_data.csv -> Precipitation file. Retrieved from AORC Precipidation Gridded Data Product (https://registry.opendata.aws/noaa-nws-aorc/). 
 		 Summarized for watershed. Formatted as a single timestamp series of interpolated 0.1 mm precipitation depth. Note file formatting.
		Storms
			StormGenerator_output.csv -> Output file from StormGenerator.py
			Magnitude -> Folder contains .csv files for incremental cumulative magnitude for each storm from StormGenerator.py. 
			Intensity -> Folder contains .csv files for incremental 60-min intensity for each storm from StormGenerator.py.
		RREDI_PreProcessing
			P_storms_PreProcessed -> Output precipitation file from RREDI_dataPrep.py.
			Q_D_PreProcessed -> Output daily streamflow file from RREDI_dataPrep.py.
			Q_I_PreProcessed -> Output instantaneous (15-minute) streamflow file from RREDI_dataPrep.py.
		RREDI_Step1
			RREDI_Step1_output.csv -> Output file from RREDI Step 1.
			Plots -> Folder containing output annual wy plots from RREDI Step 1.
		RREDI_Step2_3
			RREDI_Step2_3_output.csv -> Output file from RREDI Step 2_3.
			Plots -> Folder containing output plots of each identified rainfall-runoff event.
		RREDI_Step4
			RREDI_Step4_output.csv -> Output file from RREDI Step 4. Final output of RREDI toolkit.
		DefaultOutputsFolder -> Folder (empty) where script outputs will be written to.
		
	RREDI_Scripts_V2 -> RREDI toolkit version 2 released Sep2025. Folder contains all RREDI toolkit code (python)
		requirements.py -> RREDI toolkit V2 virtual environment python library requirements.
		StormGenerator.py -> Script to create storms using a specified storm gap from a precipitation record.
		RREDI_dataPrep.py -> Script for preparing streamflow and storm input files for RREDI. Primary function is ensuring matching and overlapping 
			data period of records.
		RREDI_Step1 -> Folder containing RREDI Step 1 Event Pair Identification Code. Code structure adapted from Patterson et al. (2020).
		RREDI_Step2_3.py -> Script to complete RREDI Step 2 Event timing and Step 3 Event metrics calculation.
		RREDI_Step2_3_Functions.py -> Script containing support functions for RREDI_Step_2_3.py.
		RREDI_Step4.py -> Script to complete RREDI Step 4 Event Flagging.
		RREDI_Step4_Functions.py -> Script containing support functions for RREDI_Step4.py.
	
	RREDI_Steps.png -> Figure showing 4 RREDI toolkit Steps. Adapted from Canham et al. (2025) Figure 2.
	RREDI_EventMetrics_example.png -> Figure showing example event metrics calculated by the RREDI toolkit Step 3. Adapted from Canham et al. (2025) Figure 3.
	RREDI_RainfallRunoffEvents_examples.png -> Figure showing RREDI toolkit example identified rainfall-runoff events. Adapted from Canham et al. (2025) Figure 3.
	
	RREDI_archived -> Archived versions of RREDI toolkit 
		RREDI_V1 -> RREDI toolkit version released November 2022. Leveraged by Canham, et al. (2025) and Canham & Lane (in review). 
		
# To use the RREDI toolkit - requirements and tips
	RREDI is developed to automate the identification and attributions of rainfall-runoff events using feature detection and signal processing
	 of timeseries. RREDI performs well in un-altered watersheds with distinct rainfall-runoff events and has been applied in watersheds of varying size across the 
	 western US. 
	Data Requirements: An overlapping daily and instantaneous streamflow and instantaneous precipitation timeseries are need. Recommended the period of record is 
	 greater than one year in duration. Data with extended gaps will lead to errors. Streamflow data with values <1 will lead to errors, recommend adding 1 to 
	 streamflow values to ensure no values <1.
	Software requirements: Python and a python GUI. Note, that the files contained in this repository are the original scripts, and some prior knowledge of 
	python is recommended to run the RREDI toolkit. 
	Python Library Requirements -> The list of libraries used to run RREDI toolkit V2 is included. It is not guaranteed that other versions of libraries will 
	 not lead to error.
	User required changes to the code: Updates to file structure lines may be needed in the provided scripts. Some knowledge of python is recommended.
	Tips: Ensure exact file formatting otherwise code will not run.	File paths will need to be specified and changed for each sub step along the way. - Update 
	 coming in the future.
	Running using scripts as is and example data: Outputs will be written to ExampleFiles/DefaultOutputsFolder except where specifically noted.

# RREDI toolkit steps - Quick Start
	Data PreProcessing
		1. Obtain daily and instantaneous (15-miunte used here) streamflow timeseries data. Ensure there are no extended missing gaps and streamflow values are 
		 >1. Consider adding 1 to streamflow data to ensure no values <1. Streamflow data formatting must follow example files Streamflow_daily_data.csv 
		 and Streamflow_instant_data.csv.  
		2. Obtain precipitation measurements for overlapping period of record. Precipitation records should be used in instantaneous format, with a timestamp for 
		 each increment of measurement as in example file Precpitation_data.csv. Rain gage or summarize precipitation data from other sources may be used. 
		3. Run StormGenerator.py to create storms from precipitation data. User must specify a storm gap, default is 3 hours. 
			Parameters: 
				stormgaps is the minimum allowable temporal gap between storms (hrs), default is 3. 
				I_int is the intensity increment (mins), default is 60. 
				tip is the precipitation depth increment (mm). Default is 0.1mm.
			Input: Precipitation_data.csv 
			Outputs: StormGenerator_output.csv, Magnitude and Intensity folders.  
		4. Run RREDI_dataPrep.py to create storm, daily and instantaneous streamflow timeseries with matching period of records. 
			Inputs: Streamflow_daily_data.csv, Streamflow_instant_data.csv, StormGenerator_output.csv
			Outputs: P_storms_PreProcessed.csv, Q_D_PreProcessed.csv, Q_I_PreProcessed.csv
	
	RREDI toolkit
	RREDI Step 1: Event Pair Identification
		Follow the steps to use the code within the RREDI_Step1 folder. This code structure is adapted from Patterson et al. (2020).
		1. Copy and paste Q_D_PreProcessed.csv into RREDI_Step1//user_input_files
		2. Copy and paste P_storms_PreProcessed.csv into RREDI_Step1//user_input_files//Precipitation
		3. Run main.py. When prompted:
			a. Select 9. Upload Files
			b. Select file.
			c. Select the default (enter) for all other parameters. No changes to the default parameters need to be made regardless of watershed as the
 			 functions this parameter influences are not used in the RREDI toolkit. See Patterson et al. (2020) for more information. The primary modified
			 functionality from Patterson et al. (2020) is the fall flush algorithm.
			Outputs: RREDI_Step1//RREDI_Step1.csv, RREDI_Step1//post_processedFiles//Boxplots//WYxxxx.png where xxxx is the year.
				NOTE: Outputs will be written directly within RREDI_Step1 folder where specifically noted. Not in the ExampleFiles/DefaultOutputsFolder.
		4. IMPORTANT: Before running again with a new watershed/data, delete streamflow and precipitation data input files from RREDI_Step1//user_input_files 
		 and RREDI_Step1//user_input_files//Precipitation, respectively. The script pulls the first precipitation file avaliable, leaving other files in the
 		 RREDI_Step1//user_input_files//Precipitation may lead to error.
	
	RREDI Step 2: Event timing and Step 3: Event metrics calculations 
		These two RREDI toolkit steps are combined into one set of scripts for ease of use. This step takes in the instantaneous (15-min) streamflow, storms files, 
		 and output file RREDI_Step1.csv from RREDI Step 1.
		1. Run RREDI_Step2_3.py. Ensure script is referencing the correct file structure to point to the input files. Ensure that the correct file structure is also
 		 used in RREDI_Step2_3_Functions.py as well, although this script is not manually run. 
			Parameters: 
				seasons start month (1-12), including winter, melt, and summer season start months. If no melt season exists, start melt == start summer. 
				 Defaults are: winter 11, melt 5, summer 5 (no melt season default)
 			Input: RREDI_Step1.csv, Streamflow_instant_data.csv, StormGenerator_output.csv, Intensity and Magnitude folder files
			Output: RREDI_Step2_3.csv, wyxxxx_countyy.png rainfall-runoff event plots where xxxx is the wy and yy is the wys event number. 
	
	RREDI Step 4: Event flagging
		This step takes in the output from RREDI Step 2_3. 
		1. Run RREDI_Step4.py. Ensure script is referencing the correct file structure to point to the input files. Ensure that the correct file structure is also
 		 used in RREDI_Step4_Functions.py as well, although this script is not manually run. This is the final output of RREDI toolkit.
			Input: RREDI_Step2_3.csv
			Output: RREDI_Step4.csv
	
# RREDI toolkit updates
	RREDI toolkit V2 - Sep25
		Changes to RREDI Step 1 have been made to improve RREDI Step 2: Event timing performance for the start and end of rainfall-runoff event identification.
		Start: Altered the default start value and the change in slope detection values
			Altered to default to the minimum hourly flow between peak and storm start. Then find the next value after the min where slope increases for two timesteps 
			 >1. If not found, then search for when slope starts increasing by 5% of (peak-min). Altered to find the timestep prior to the change in slope 
			 (slope change t-1). If a super flashy event with no rise and only a peak, start is peak-1
		End: Altered the order of end searched for, altered some parameters
			Id the min value between peak and end. Search for end from when flow < 50% of peak-rise (for all seasons) to end of window. 
			End is: first local min below seasonal falling threshold. If no local min found, end is: where falling slope is greater than -1 (values between 0 and -1) 
			 below seasonal falling threshold. If nothing found, find falling slope that is 5% of (peak-start) (included for small events). If a no rise event, 
			 (where slope = 0 for several (5) timesteps and peak-start = <0.1, end is timestep after peak. If nothing found, find first local min.
			End is flagged if: identified end is also the last in the window, if there are flow values between peak and end >peak flow value

# Future plans
	Main wrapper script or GUI - so that everything can be run together and not individually. 
	File path unification for simplicity and ease of transferability between users.
