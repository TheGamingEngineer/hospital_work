# -*- coding: utf-8 -*-
from datetime import datetime
import pandas as pd
import numpy as np
import sys
## data is the list of paths to the .xlsx files used 
data=["/Users/AAND0774/Downloads/clinical_data_overview_files_20231110/data_CH_2023-11-09.xlsx",
      "/Users/AAND0774/Downloads/clinical_data_overview_files_20231110/data_CZ_2023-11-10.xlsx",
      "/Users/AAND0774/Downloads/clinical_data_overview_files_20231110/data_DK_2023-11-10.xlsx",
      "/Users/AAND0774/Downloads/clinical_data_overview_files_20231110/data_IS_2023-11-10.xlsx",
      "/Users/AAND0774/Downloads/clinical_data_overview_files_20231110/data_SI_2023-11-10.xlsx"]

# a few custom functions used to run it.
def unique(LIST,isolate=False):
    result=[]
    
    if type(LIST)==pd.core.series.Series:
        LIST=LIST.tolist()
    for i in LIST:
        if str(i) not in result:
            result+=[str(i)]
    if len(result)==1 and isolate:
        result=result[0]
    return(result)
        
def emptiness(LIST):
    if type(LIST)==pd.core.series.Series:
        LIST=LIST.tolist()
    LIST=[str(i) for i in LIST]
    empties=LIST.count('nan')+LIST.count('NaT')
    percent=empties/len(LIST)*100
    percent=round(percent,3)
    return(str(percent))

def Class(x):
    # take the uniques of the variable
    x=unique(x)
    # remove any unknown variables from the unique list
    if 'nan' in x:
        x.remove('nan')
    if 'NaT' in x:
        x.remove('NaT')
    
    # if the variabel is empty, the type cannot be determined. 
    if x==[]:
        return("NA")
    
    # isolate all characters present in the variabel
    characters=[]
    for i in x:
        for j in range(len(i)):
            if i[j] not in characters:
                characters+=[i[j]]
    
    alphabet="abcdefghijklmnopqrstuvwxyzæøå"
    
    # if the variabel only has two possible outcome (without unknowns), the variabel is binary
    if len(x)==2:
        return("binary")
    # it might be numeric, integer, or dates, if there are no letters in it and is not binary
    elif not any(y.lower() in alphabet for y in characters):
        # if there are - in the variabel, it might be a date
        if any("-" in i for i in x):
            if all(len(i.split("-"))==3 for i in x):
                return("date")
            else:
                return("categorical")
        else:
            # if there is a "." in any of the numbers, it might be numeric 
            if any("." in i for i in x):
                deci_split=[int(i.split(".")[1]) for i in x if "." in i]
                # if the number after the decimal is different from 0, it is numeric
                if any(i!=0 for i in deci_split):
                    return("numeric")
                else:                    
                    return("integer")
            else:
                return("integer")
    # otherwise, it is either categorical or (free) text based on whether there are spaces in it or not. 
    else:
        if any(" " in y for y in x):
            return("text")
        else:
            return("categorical")
        
def find_nation(X):
    if "CH" in X:
        return "CH"
    elif "SL" in X:
        return "SL"
    elif "CZ" in X:
        return "CZ"
    elif "IS" in X:
        return "IS"
    elif "DK" in X:
        return "DK"

# make the dataframes for the output files 
variables=[]
nations=[]

check_list={}
overview_list={}
empties_list={}
classes_list={}

# go through the files to gather the info about what varables are present and on what level.
for x in data:
    
    # open source files
    file = pd.read_excel(x,sheet_name=None)
    # get the nation
    nation=unique(file["pat"]["country"],isolate=True)
    # makes sure that the national codes are present in each of the tables 
    if nation not in check_list:
        check_list[nation]=[]
    if nation not in overview_list:
        overview_list[nation]={}
    if nation not in empties_list:
        empties_list[nation]={}
    if nation not in classes_list:
        classes_list[nation]={}
    if nation not in nations:
        nations+=[nation]
    # goes through each fan and checks what variables it has on which level
    for key in file:
        # go through each variable in the level
        for col in file[key]:
            check_list[nation]+=[col]
            # if there are actually data in the variabel
            if col not in overview_list[nation]:
                overview_list[nation][col]=[]
            overview_list[nation][col]+=[key]
            # otherwise
            if col not in empties_list[nation]:
                empties_list[nation][col]=[]
            empties_list[nation][col]+=[key + ": " + emptiness(file[key][col]) + "% "]
            if col not in classes_list:
                classes_list[nation][col]=[]
            classes_list[nation][col]+=[Class(file[key][col])]
            # gather the total amount of variables
            if col not in variables:
                variables+=[col]
#sys.exit()
# sort them
nations.sort()
variables.sort()

# make the output dataframes by filling them in from the preseding data.
empty_data={}
for y in nations:
    empty_data[y]=[""]*len(variables)
            
check_list_out=pd.DataFrame(empty_data,index=variables)
overview_list_out=pd.DataFrame(empty_data,index=variables)
empties_list_out=pd.DataFrame(empty_data,index=variables)
classes_list_out=pd.DataFrame(empty_data,index=variables)

# write the information to these dataframes
for x in nations:
    for y in variables:
        if y in check_list[x]:
            check_list_out[x][y]="X"
        if y in overview_list[x]:
            overview_list_out[x][y]=",".join(overview_list[x][y])
        if y in empties_list[x]:
            empties_list_out[x][y]=" | ".join(empties_list[x][y])
        if y in classes_list[x]:
            classes_list_out[x][y]=",".join(classes_list[x][y])

# write the dataframes to file
times=datetime.now().strftime('%Y%m%d')
outputname="EuroSpAI_variabel_overview_" + times + ".xlsx"
with pd.ExcelWriter(outputname) as writer:
    check_list_out.to_excel(writer,sheet_name="checklist",index=True)
    overview_list_out.to_excel(writer,sheet_name="level overview",index=True)
    empties_list_out.to_excel(writer,sheet_name="percent variabel-emptiness",index=True)
    classes_list_out.to_excel(writer,sheet_name="variabel types",index=True)