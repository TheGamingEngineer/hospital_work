#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 10:23:37 2022

@author: alexanderandersen
"""
####################################################
######### importing the necessary packages #########
####################################################

import pydicom
import os
from datetime import datetime ## call computer date for output-file
import re
from os.path import exists

###########################################################################
######### Setting paths to images and the changes to ######################
######### patient ID (Pat_ID), examination ID (ex_ID), and date ###########
######### OBS: if only one of these are to be changed,write "" in ######### 
######### the position of the other lists #################################
###########################################################################

# list of the paths to the folders (examinations) with images that need renaming
path=["/home/alexanderandersen/2_wave/images/SL/sl291/sl291b/",
      "/home/alexanderandersen/2_wave/images/SL/sl291/sl291f/"]

Pat_ID=[""] # the new patient ID's (leave "" in position, if no changes should be made to it)

ex_ID=[""] # the new examination ID's (leave "" in postition, if no changes should be made to it)

date=["20210418","20191205"] # the new dates (leave "" in position, if no changes should be made to it)

##################################################################
########### here runs the script. DO NOT CHANGE IT !!! ###########
##################################################################
##################################################################
######### Initiating the log file recording the changing #########
##################################################################
times=datetime.now().strftime('%Y%m%d') # saves date of run for file-naming
Times=datetime.now().strftime('%H:%M %d/%m-%Y') # saves date of run for header-naming

output_file_name= "ID-Date_renaming-log_" + times + ".txt" # naming the output inconsistency file after the national two-letter code and the time of the run

print("Initiating Report File:",output_file_name) #reporting the report to be made to the data analyst

if exists(output_file_name):
    output_file=open(output_file_name,'a+')
else:
    output_file=open(output_file_name,'w')

######################################################################################################################
######### If the ID- and/or date list is too short in comparison to the list of paths, the rest is filled in #########
######################################################################################################################
if len(Pat_ID)==0 or len(Pat_ID)<len(path):
    for x in range(len(path)-len(Pat_ID)):
        Pat_ID.append("")

if len(ex_ID)==0 or len(ex_ID)<len(path):
    for x in range(len(path)-len(ex_ID)):
        ex_ID.append("")

if len(date)==0 or len(date)<len(path):
    for x in range(len(path)-len(date)):
        date.append("")

output_file.write("Initial Time of Changes: " + Times + '\n')
archive=[]
##################################################################################
######### Running loops over the files in the folder sof the given paths #########
##################################################################################
for x in range(len(path)):
    print("Currently working on:" + path[x])
    nation=re.search("/[A-Z]{2}",path[x]).group()[1:3]
    output_file.write('\n' + "Changes to images in: " + 
                      nation + 
                      path[x].split(nation)[1] + '\n')
    for root, dirs, files in os.walk(path[x]):
        if len(files) > 0: #only work for directories with files in it
            
            for file in files:
                # Needs to be changed for CZ
                # We analyze files with no suffix
                name, extension = os.path.splitext(root + file)
                
                if extension == '.dcm':
                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                    except:
                        next
                    if Pat_ID[x]!="":    
                        ds.PatientName=Pat_ID[x]
                        output_file.write("Patient ID's (DicomKey:PatientName) changed to " + Pat_ID[x]  + "for file:" + name + extension + '\n')
                    if ex_ID[x]!="":
                        ds.PatientID=ex_ID[x]
                        output_file.write("Examination ID's (DicomKey:PatientID) changed to " + ex_ID[x]  + "for file:" + name + extension + '\n')
                    if date[x]!="":
                        ds.SeriesDate=date[x]   
                        output_file.write("Date (DicomKey:SeriesDate) changed to " + date[x] + "for file:" + name + extension + '\n')
                    if path[x][-1]!="/":
                        FILE=root+"/"+file
                    else:
                        FILE=root+file
                    ds.save_as(FILE)
                    archive.append(ds)
                    print("file saved:",FILE)
                elif len(extension)==0 and file[0]!='.' and file!="DICOMDIR": #this is done to also be able to read images with no extension (CZ)
                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)    
                    except:
                        next
                    # Czech include ^ as part of their patient ID's in the images
                    if Pat_ID[x]!="":    
                        ds.PatientName=Pat_ID[x]
                        output_file.write("Patient ID's (DicomKey:PatientName) changed to " + Pat_ID[x]  + " for file:" + name + extension + '\n')
                    if ex_ID[x]!="":
                        ds.PatientID=ex_ID[x]
                        output_file.write("Examination ID's (DicomKey:PatientID) changed to " + ex_ID[x]  + " for file:" + name + extension + '\n')
                    if date[x]!="":
                        ds.SeriesDate=date[x]   
                        output_file.write("Date (DicomKey:SeriesDate) changed to " + date[x] + " for file:" + name + extension + '\n')
                    if path[x][-1]!="/":
                        FILE=root+"/"+file
                    else:
                        FILE=root+file
                    ds.save_as(FILE)
                    archive.append(ds)
                    print("file saved:",FILE)
        output_file.write('\n')

output_file.write("###################################################################\n\n")
output_file.close()
print("all done!")