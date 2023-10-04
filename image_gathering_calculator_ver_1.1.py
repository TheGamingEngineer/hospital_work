#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 12:42:38 2022

@author: alexanderandersen
"""
import re
import numpy as np
import pandas as pd
from datetime import datetime
#from sys import exit
# list of strings describing the full paths to the individual metadata files
## that would be evaluated. 

meta=["/home/alexanderandersen/2_wave/metadata/SL/SL_image_metadata_eurospa_imaging_second_wave.xlsx"]  

for x in meta:
    # open the given metadata files
    try:
        if ".csv" in x:
            metadata=pd.read_csv(x,sep=";")
        if ".xlsx" in x:
            metadata=pd.read_excel(x)
    except IOError:
        print(x," could not be opened")
        next
        
    # extract patient ID 
    if "{" in metadata.patient_id[0]:
        metadata=metadata[1:]
    try:
        patient_ID=np.unique(metadata.patient_id)
    except:
        patient_ID=[]
        for ID in metadata.patient_id:
            if ID not in patient_ID:
                patient_ID+=[ID]
    
    # get country of origin for file naming
    if len(re.findall("/[A-Z]{2}/",x))>0:
        origin=re.search("/[A-Z]{2}/",x).group()[1:3]
    else:
        origin="all"
    if "SL" not in x:
        if "second_wave_part_3" in x:
            origin+="_batch_3_"
        elif "second_wave" in x and "CH" in x:
            origin+="_"+x.split("second_wave_")[1].split("_")[0]+"_"
        elif "second_wave" in x and "CZ" in x:
            origin+="_"+x.split("second_wave_")[1].split("_")[0]+"_"
        elif "teplate" in x and "CZ" in x:
            origin+="_"+x.split("teplate_")[1].split("_")[0]+"_"
        elif "CZ" in x and "corr" in x:
            origin+="_"+x.split("/CZ/")[1].split("_")[0].split("/")[1]+"_"
        elif "CZ" in x and "part 4" in x:
            origin+="_batch_4_"
        elif "CZ" in x and "Plzen" in x:
            origin+="_plzen_"
        elif "CZ" in x and "5" in x:
            origin+="_batch_5_"
        else:
            origin+="_"
    else:
        origin+="_"
    origin+=datetime.now().strftime('%Y%m%d')
    
    # naming the output-files
    filename=origin+".xlsx"
    print("currently working on: ",filename)
    variables=list(metadata.columns)
    if "patient" in variables[-1] and "patient" in variables[-2]:
        variables=variables[:-2]
    if "Unnamed" in variables[-1] and "Unnamed" in variables[-2]:
        variables=variables[:-2]
        
    # makes the column header for the output files
    output_header=[variables[0],variables[3],"start_date_of_first_bdmard"]+variables[4:]
    
    # make the content matrix of the output file
    output_data=[]

    # go through the metadata files and single out the necessary information
    for y in patient_ID:
        # subselect the dataset for a single patient
        pat_meta=metadata[metadata["patient_id"]==y]
        
        # get the number of examinations of each type for a given patient
        var_list=[]
        for z in variables[4:]:
            var_list+=[sum(pat_meta[z].fillna(0))]
        
        # the start_date_of_first_bdmard is set to be the earliest examination date
        date=min(pat_meta["image_date"])
        date=pd.to_datetime(str(date))
        date=str(date).split(" ")[0] #this gives a prettier date format
        
        # the latest diagnosis for the patient is chosen as the current diagnosis
        latest=max(pat_meta["image_date"])
        diagnosis=list(pat_meta[pat_meta["image_date"]==latest]["diagnosis_group"])[0]
        
        # make the line for the given patient in the output file and insert it into the output data matrix
        patient_line=[y,diagnosis,date]+var_list
        output_data.append(patient_line)
    # make the dataframe using the matrix and write it into file
    df=pd.DataFrame(output_data,columns=output_header)
    df.to_excel(filename,index=False)