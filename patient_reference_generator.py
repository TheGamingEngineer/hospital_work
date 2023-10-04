#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 08:39:35 2022

@author: alexanderandersen
"""

import numpy as np
from datetime import datetime
import re
from os.path import exists
import pandas as pd

path=[] # list of strings describing the metadata-files (with paths to them in the same string).


times=datetime.now().strftime('%Y%m%d')
content_history=[]
content_file_history={}
for x in range(len(path)):
    nation=re.search("/[A-Z]{2}",path[x]).group()[1:3]
    filename=path[x].split("/")[-1]
    output_filename=nation + "_patient_reference_" + times + ".xlsx"
    dup_filename=nation + "_duplicates_" + times + ".txt"
    
    ### read the metadata file ###
    if ".csv" in path[x]:
        metadata_file = pd.read_csv(path[x], sep=";")
        if len(metadata_file.columns)==1:
            metadata_file = pd.read_csv(path[x], sep=",")
    elif ".xlsx" in path[x]:
        metadata_file = pd.read_excel(path[x])
    else:
        next
    
    ### make a file for all of the duplicates ###
    dup_file=output_file=open(dup_filename,'w')
    
    ### gahter the patient ID's from the metadata file ###
    if "{" in metadata_file.patient_id[0]:
        pat_id=np.unique(metadata_file.patient_id[1:])
    else:
        pat_id=np.unique(metadata_file.patient_id)
    
    ### make the content for patient ID and the metadata of origin ###
    content=[]
    for n in range(len(pat_id)):
        if pat_id[n] not in content_history:
            content.append([pat_id[n],filename])
            content_history.append(pat_id[n])
            content_file_history[pat_id[n]]=filename
        else:
            dup_file.write(pat_id[n] + " was found in both " + content_file_history[pat_id[n]] + " and " + filename + "." + "\n")
        
    
    ### write content to file ###
    df_source=None
    if exists(output_filename):
        df_source=pd.DataFrame(pd.read_excel(output_filename,sheet_name="main"))
    if df_source is not None:
        df_best=df_source.append(content)
    else:
        df_best=pd.DataFrame([["patient_id","reference"]]).append(pd.DataFrame(content))
        #df_best.columns=[''] * len(df_best.colunms)
    df_best.to_excel(output_filename,sheet_name="main",index=False)
    
        
    
    