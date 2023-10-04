#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 10:45:25 2022

@author: alexanderandersen
"""

from datetime import datetime
import re
import pandas as pd
import numpy as np
import sys
typen="clinical"
if typen=="clinical":
    # clinical data
    path=["/home/alexanderandersen/2_wave/clinical_data/CH/CH_final_mix_clinical_data.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CH/clinical_data_Exer_20220401_second_wave_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CH/clinical_data_Insel_20220601_second_wave_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CH/clinical_data_kloeti_CHUV_20220801_second_wave.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CH/clinical_data_LUKS_20220801_second_wave_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CH/clinical_data_USZ_20220101_second_wave_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_2-3-4-wave_20211025.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20211025_part_1.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20220429_Brno_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20220429_FNKV_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20220429_Olomouc_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20220429_Plzen_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20220810_Motol_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20220810_Praha.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/CZ/data_CZ_20221009_Praha_missing_patients.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/DK/DK_clinical_data.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/IS/clinical_20230420_IMGIS.xlsx",
          "/home/alexanderandersen/2_wave/clinical_data/SL/data_si_20230419_v1.xlsx"] # list of strings with full paths to the file with metadata or clinical data
elif typen=="metadata":
    # metadata
    path=["/home/alexanderandersen/2_wave/metadata/CH/scqm_xray_mri_metadata_20211215.csv",
          "/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_final_mix_20220930.csv",
          "/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_Exer_20220727_FINAL.csv",
          "/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_Insel_20220613_FINAL.csv",
          "/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_kloetichuv_20220825.csv",
          "/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_LUKS_20220810_FINAL.csv",
          "/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_USZ_20220211_FINAL.csv",
          "/home/alexanderandersen/2_wave/metadata/CZ/Corrected_2ND_wave_teplate_part1_AKBA.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/Motol_corr_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/Plzen FINAL 20092022.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/template 2nd wave part 4.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospa_imaging_second_wave_Brno_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospa_imaging_second_wave_FNKV_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospa_imaging_second_wave_Olomouc_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospa_imaging_second_wave_part2_AKBA_20220915.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospai_imaging_second_wave_part_3_FINAL.xlsx",
          "/home/alexanderandersen/2_wave/metadata/CZ/template_part5.xlsx",
          "/home/alexanderandersen/2_wave/metadata/DK/Image_metadata_second_wave_dk_1_skvulp.xlsx",
          "/home/alexanderandersen/2_wave/metadata/IS/metadata_island_images_first_wave_all.xlsx",
          "/home/alexanderandersen/2_wave/metadata/SL/SL_image_metadata_eurospa_imaging_second_wave.xlsx"]

## OBS: 
### 1) make sure that all of the file types that you use are of the same type (either .csv or .xlsx)
### 2) if using .xlsx, make sure that all of the sheet names in the file match with what you want to gather in those sheets (especially for clinical data)
### 2.5) for clinical data, make sure that the sheet names are "med" (for treatment), "pat" (for patient), "vis" (for visit), and nsaid (for NSAID's)
### 3) make sure that the files that you want to gather from are sorted into the correct file type folder and national subfolder (for example ../metadata/CH/.. for a metadata file from Schwitzerland)

#################################################
#### DONT CHANGE THINGS BELOW THIS LINE !!! #####
#################################################
def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

def rename_bdmard(d):
    renames={"MEDICINE_ALLOPURINOL" : "allopurinol",
             "otezla" : "apremilast",
             "cya" : "ciclosporin",
             "aza" : "azathioprine",
             "szs" : "sulfasalazine",
             "lef" : "leflunomide",
             "mtx" : "methotrexate",
             "azath" : "azathioprine",
             "aza" : "azathioprine",
             "szs" : "sulfasalazine",
             "NODRUG":"nodrug",
             "NON_BIOLOGIC":"nonbiologic"}
    for key in renames:
        if key in unique(d):
            d=d.replace(key,renames[key])
    return d

def rename_reason(string):
    temp=string.split(",")
    pre_proc=[]
    for x in temp:
        if "WITHDRAWN_" in x:
            pre_proc.append(x.split("WITHDRAWN_")[1].lower())
            pre_proc.append(np.nan)
    output=",".join(pre_proc)
    return output
    
def bdmard(string):
    bdMARDS=["abatacept","adalimumab","amgevita",
             "anakinra","baricitinib","belimumab",
             "benepali","certolizumab","erelzi",
             "etanercept","flixabi","golimumab",
             "guselkumab","hyrimoz","imraldi",
             "inflectra","infliximab","ixekizumab",
             "mycophenolat","otezla","biologic_other",
             "project_medicine","remsima","rituximab",
             "rixathon","ruxience","sarilumab",
             "secukinumab","tocilizumab",
             "tofacitinib","upadacitinib","ustekinumab","zessly"]
    if "_" in string and string.lower() not in ["biologic_other","project_medicine"]:
        temp=string.split("_")
    else:
        temp=[string]
    for x in temp:
        if x in bdMARDS:
            return True
        else:
            return False

def unique(LIST):
    result=[]
    for i in LIST:
        if type(i)!=pd.core.series.Series:
            use=i
        else:
            use=list(i)[0]
        
        if type(use)!=list:
            if use not in result:
                result.append(use)
        else:
            for x in use:
                if x not in result:
                    x.append(x)
    return result

def date_adjust(date,make_str=False):
    if type(date)!=float:
        date=str(date)
    else:
        if np.isnan(date):
            return np.nan
        else:
            date=str(date)
    if "-" in str(date):
        date=date.split("-")
        if len(date)==2 and len(date[0])==4: # if only year and month is given, then we assume that it is the first of the month 
            date.append("01") # asume that it is the first of the month
        elif len(date)==1 and len(date[0])==4: # if only the year is given, then we assume that it is new years day
            date.append("07") # assume the date is in July
            date.append("01") # assume that it is the first of the month
        elif len(date) not in [1,2,3] or len(date[0]) not in [4,8]: # otherwise, the date is too faulty to process
            return np.nan
        if ":" in date[2]:
            date[2]=date[2].split(" ")[0]
        date="".join(date)
    if date=="NaN" or date=="NaT" or date=="MISSING":
        return np.nan
    elif "." in date:
        date=date.split(".")[0]
    date=int(date)
    if make_str:
        date=str(date)
        temp=[date[0:4],date[4:6],date[6:]]
        date="-".join(temp)
        return date
    else:
        return str(date)
    
def df_binarize(df):
    for col in df.columns:
        if True in list(df[col]):
            df[col]=df[col].replace([True],int(1))
        if "True" in list(df[col]):
            df[col]=df[col].replace(["True"],int(1))
        if "pos" in list(df[col]):
            df[col]=df[col].replace(["pos"],int(1))
        if False in list(df[col]):
            df[col]=df[col].replace([False],int(0))
        if "False" in list(df[col]):
            df[col]=df[col].replace(["False"],int(0))
        if "neg" in list(df[col]):
            df[col]=df[col].replace(["neg"],int(0))
    return df

def one_more_day(date):
    # unifies the date input
    DATE=date
    date=str(date)
    if "-" in date:
        date=date.split("-")
        if ":" in date[2]:
            date[2]=date[2].split(" ")[0]
    else:
        date=[date[0:4],date[4:6],date[6:8]]
    
    
    # converts each part of the date to an integer
    for i in range(len(date)):
        date[i]=int(date[i])
    ### read the metadata file ###
    
    # calculate date
    date[2]+=1 # add one more day
    # there are 31 days in january, march, may, july, august and october, so month turnover after the 31th
    if date[1] in [1,3,5,7,8,10] and date[2]>=32:
        date[2]=1
        date[1]+=1
    # there are 30 days in april, june, september and november, so month turnover after the 30th
    elif date[1] in [4,6,9,11] and date[2]>=31:
        date[2]=1
        date[1]+=1
    # after the december 31, both month and year turnover
    elif date[1]==12 and date[2]>=32:
        date[0]+=1
        date[1]=1
        date[2]=1
    # february month turnover depends on the year
    elif date[1]==2:
        if not is_integer(date[0]/4) and date[2]>=29:
            date[1]+=1
            date[2]=1
        elif is_integer(date[0]/4) and date[2]>=30:
            date[1]+=1
            date[2]=1
    # convert back to standard format
    for i in range(len(date)):
        date[i]=str(date[i])
        if i in [1,2] and len(date[i])==1:
            date[i]="0"+date[i]
    # return the date as the same format as was inputted
    if "-" in str(DATE):
        sep="-"
    else:
        sep=""
    output=sep.join(date)
    return output

def adjust_dateframe(d):
    start="drug_start_date"
    stop="drug_stop_date"
    pat="patient_id"
    row="row_id"
    patients=unique(d["patient_id"])
    bdMARDS=["abatacept","adalimumab","amgevita",
             "anakinra","baricitinib","belimumab",
             "benepali","certolizumab","erelzi",
             "etanercept","flixabi","golimumab",
             "guselkumab","hyrimoz","imraldi",
             "inflectra","infliximab","ixekizumab",
             "mycophenolat","otezla","biologic_other",
             "project_medicine","remsima","rituximab",
             "rixathon","ruxience","sarilumab",
             "secukinumab","tocilizumab",
             "tofacitinib","upadacitinib","ustekinumab","zessly"]
    for x in range(len(d)):
        d[start][x]=date_adjust(d[start][x])
        d[stop][x]=date_adjust(d[stop][x])
    D=d[d["drug_name"].isin(bdMARDS)]
    patients=np.unique(D["patient_id"])
    for patient in patients:
        df=D[D[pat]==patient]
        df=df.sort_values(start,ascending=True)
        Keys=[]
        for x in df[row]:
            Keys.append(x)
        for x in range(len(Keys)):
            if x+1==len(Keys):
                break
            if np.isnan(float(df[df[row]==Keys[x]][stop])) or np.isnan(float(df[df[row]==Keys[x+1]][start])):
                continue
            if int(df[df[row]==Keys[x]][stop])<int(df[df[row]==Keys[x+1]][start]):
                new_date=list(df.loc[df[row]==Keys[x+1],start])[0]
                d.loc[d[row]==Keys[x],stop]=date_adjust(new_date,make_str=True)
    return d
    
def criteria_remapping(d):
    a1="asas_criteria_1_back_pain"
    a2="asas_criteria_2_arthritis"
    a3="asas_criteria_3_enthesitis"
    a4="asas_criteria_4_uveitis"
    a5="asas_criteria_5_dactylitis"
    a6="asas_criteria_6_psoriasis"
    a7="asas_criteria_7_ibd"
    a8="asas_criteria_8_response_to_nsaids"
    a9="asas_criteria_9_family_history"
    a10="asas_criteria_10_hla_b27"
    a11="asas_criteria_11_elevated_crp"
    a12="asas_criteria_12_mri_sacroiliitis"
    a13="asas_criteria_13_xray_sacroiliitis"
    
    ny1="new_york_criteria_1_low_back_pain"
    ny2="new_york_criteria_2_lumbar_spine_motion"
    ny3="new_york_criteria_3_chest_expansion"
    ny4="new_york_criteria_4_sacroiilitis"
    
    c1a="caspar_criteria_1a_psoriasis_current"
    c1b="caspar_criteria_1b_psoriasis_history"
    c1c="caspar_criteria_1c_psoriasis_family"
    c2="caspar_criteria_2_nail_symptoms"
    c3="caspar_criteria_3_igmrf_neg"
    c4="caspar_criteria_4_dactylitis"
    c5="caspar_criteria_5_xray_changes"
    
    criteria=[a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,a13,
              ny1,ny2,ny3,ny4,c1a,c1b,c1c,c2,c3,c4,c5]
    
    patients=unique(d["vis"]["patient_id"])
    
    for key in d:
        if key!="pat":
            for patient in patients:
                for x in criteria:
                    if x in list(d[key].keys()):
                        record=unique(d[key][x][d[key]["patient_id"]==patient])
                        if x not in list(d["pat"].keys()) or np.isnan(unique(d["pat"][x][d[key]["patient_id"]==patient])).all():
                            if x not in list(d["pat"].keys()):
                                d["pat"][x]=np.nan
                            if any(item not in [0,0.0,1,1.0] for item in list(d["pat"][x][d[key]["patient_id"]==patient])):
                                if 1 in record or 1.0 in record:
                                    d["pat"][x][d[key]["patient_id"]==patient]=1
                                elif 0 in record or 0.0 in record:
                                    d["pat"][x][d[key]["patient_id"]==patient]=0
            for x in criteria:
                if x in list(d[key].keys()):
                    d[key]=d[key].drop(x,axis=1)
            
    
## map_drugs ##"country"
def map_drugs(treatment,nsaid,patient):
    for x in nsaid["row_id"]:
        if list(nsaid["patient_id"][nsaid["row_id"]==x])[0] in list(np.unique(patient["patient_id"])):
            new=pd.DataFrame({"patient_id":[list(nsaid["patient_id"][nsaid["row_id"]==x])[0]],
                              "drug_name":["nsaid"],
                              "drug_start_date":[list(nsaid["date"][nsaid["row_id"]==x])[0]],
                              "drug_stop_date":[one_more_day(list(nsaid["date"][nsaid["row_id"]==x])[0])],
                              "country":[list(nsaid["country"][nsaid["row_id"]==x])[0]],
                              "source":[list(nsaid["source"][nsaid["row_id"]==x])[0]]})
            treatment=pd.concat([treatment,new])
    INDEX=pd.Index([n for n in range(len(treatment))])
    treatment=treatment.set_index(INDEX)
    return treatment

def asas_cal(d):
    newd=[]
    a1="asas_criteria_1_back_pain"
    a2="asas_criteria_2_arthritis"
    a3="asas_criteria_3_enthesitis"
    a4="asas_criteria_4_uveitis"
    a5="asas_criteria_5_dactylitis"
    a6="asas_criteria_6_psoriasis"
    a7="asas_criteria_7_ibd"
    a8="asas_criteria_8_response_to_nsaids"
    a9="asas_criteria_9_family_history"
    a10="asas_criteria_10_hla_b27"
    a11="asas_criteria_11_elevated_crp"
    a12="asas_criteria_12_mri_sacroiliitis"
    a13="asas_criteria_13_xray_sacroiliitis"
    
    for x in list(d["row_id"]):
        asas_list=[d[a1][d["row_id"]==x],d[a2][d["row_id"]==x],d[a3][d["row_id"]==x],
                   d[a4][d["row_id"]==x],d[a5][d["row_id"]==x],d[a6][d["row_id"]==x],
                   d[a7][d["row_id"]==x],d[a8][d["row_id"]==x],d[a9][d["row_id"]==x],
                   d[a10][d["row_id"]==x],d[a11][d["row_id"]==x],d[a12][d["row_id"]==x],
                   d[a13][d["row_id"]==x]]
        asas_sum=0
        asas_NA=0
        for i in range(len(asas_list)):
            if not np.isnan(list(asas_list[i])[0]) and i<10:
                asas_sum+=list(asas_list[i])[0]
            elif np.isnan(list(asas_list[i])[0]) and i<10:
                asas_NA+=1
        if list(asas_list[11])[0]==1 or list(asas_list[12])[0]==1 and asas_sum>0 or list(asas_list[9])[0]==1 and asas_sum>2:
            newd.append(int(1))
        else:
            if list(asas_list[9])[0]==list(asas_list[11])[0]==list(asas_list[12])[0]==0:
                newd.append(int(0))
            else:
                if list(asas_list[11])[0]==1 or list(asas_list[12])[0]==1:
                    if asas_sum<1 and asas_NA<1 or list(asas_list[9])[0]==1:
                        if asas_sum==1 and asas_NA<=1 or asas_sum==2 and asas_NA<1:
                            newd.append(int(0))
                        else:
                            newd.append(np.nan)
                    else:
                        newd.append(np.nan)
                else:
                    newd.append(np.nan)
    return newd

def new_york_cal(d):
    newd=[]
    ny1="new_york_criteria_1_low_back_pain"
    ny2="new_york_criteria_2_lumbar_spine_motion"
    ny3="new_york_criteria_3_chest_expansion"
    ny4="new_york_criteria_4_sacroiilitis"
    
    for x in list(d["row_id"]):
        noNA=[]
        for i in [d[ny1][d["row_id"]==x],d[ny2][d["row_id"]==x],d[ny3][d["row_id"]==x],d[ny4][d["row_id"]==x]]:
            use=list(i)[0]
            if np.isnan(use):
                noNA.append(0)
            else:
                noNA.append(use)
        if noNA[3]==1 and 1 in noNA[:3]:
            newd.append(1)
        else:
            if noNA[3]==0 or noNA[:3]==[0,0,0]:
                newd.append(0)
            else:
                newd.append(np.nan)
    return newd
           
    
def caspar_cal(d):
    newd=[]
    c1a="caspar_criteria_1a_psoriasis_current"
    c1b="caspar_criteria_1b_psoriasis_history"
    c1c="caspar_criteria_1c_psoriasis_family"
    c2="caspar_criteria_2_nail_symptoms"
    c3="caspar_criteria_3_igmrf_neg"
    c4="caspar_criteria_4_dactylitis"
    c5="caspar_criteria_5_xray_changes"
    
    c11=0
    c12=0               
    c13=0
    for i in list(d["row_id"]):
        if list(d[c1c][d["row_id"]==i])[0]!=np.nan and list(d[c1c][d["row_id"]==i])[0]==1:
            c11=1
        if list(d[c1b][d["row_id"]==i])[0]!=np.nan and list(d[c1b][d["row_id"]==i])[0]==1:
            c12=1
        if list(d[c1a][d["row_id"]==i])[0]!=np.nan and list(d[c1a][d["row_id"]==i])[0]==1:
            c13=1
        c1=max([c11,c12,c13])
        c_list=[c1,
                list(d[c2][d["row_id"]==i])[0],
                list(d[c3][d["row_id"]==i])[0],
                list(d[c4][d["row_id"]==i])[0],
                list(d[c5][d["row_id"]==i])[0]]
        
        casp_sum=0
        casp_NA=0
        for x in c_list: 
            if not np.isnan(x):
                casp_sum+=x
            else:
                casp_NA+=1
        if casp_sum>2:
            newd.append(1)
        else:
            if casp_sum+casp_NA>2:
                newd.append(np.nan)
            else:
                newd.append(0)
    return newd
            
def NY_4ab_adjust(d):
    ny4="new_york_criteria_4_sacroiilitis"
    ny4a="new_york_criteria_4a_xray_sacroiliitis_bilat"
    ny4b="new_york_criteria_4b_xray_sacroiliitis_unilat"
    if ny4a in d.keys() and ny4b in d.keys():
        if ny4 not in list(d.keys()):
            d[ny4]=np.nan
        for i in list(d["patient_id"]):
            if is_integer(list(d[ny4a][d["patient_id"]==i])[0]) or is_integer(list(d[ny4b][d["patient_id"]==i])[0]):
                if 1 in [list(d[ny4a][d["patient_id"]==i])[0],list(d[ny4b][d["patient_id"]==i])[0]]:
                    d[ny4][d["patient_id"]==i]=1
                elif 0 in [list(d[ny4a][d["patient_id"]==i])[0],list(d[ny4b][d["patient_id"]==i])[0]]:
                    d[ny4][d["patient_id"]==i]=0

    
def basdai_cal(d,basdai_1 = "basdai_1_fatigue",
               basdai_2 = "basdai_2_pain_spinal",
               basdai_3 = "basdai_3_pain_joints",
               basdai_4 = "basdai_4_tender",
               basdai_5 = "basdai_5_stiffness_severity",
               basdai_6 = "basdai_6_stiffness_duration"):
    if len(list(d[basdai_1]))==1 and np.isnan(list(d[basdai_1])[0]):
        return [np.nan for x in range(len(d))]
    if len(list(d[basdai_2]))==1 and np.isnan(list(d[basdai_2])[0]):
        return [np.nan for x in range(len(d))]
    if len(list(d[basdai_3]))==1 and np.isnan(list(d[basdai_3])[0]):
        return [np.nan for x in range(len(d))]
    if len(list(d[basdai_4]))==1 and np.isnan(list(d[basdai_4])[0]):
        return [np.nan for x in range(len(d))]
    if len(list(d[basdai_5]))==1 and np.isnan(list(d[basdai_5])[0]):
        return [np.nan for x in range(len(d))]
    if len(list(d[basdai_6]))==1 and np.isnan(list(d[basdai_6])[0]):
        return [np.nan for x in range(len(d))]
    
    na_count={"all":[],"1-4":[],"5-6":[]}
    for x in list(d["row_id"]):
        count=0
        count14=0
        count56=0
        if np.isnan(list(d[basdai_1][d["row_id"]==x])[0]):
            count+=1
            count14+=1
        if np.isnan(list(d[basdai_2][d["row_id"]==x])[0]):
            count+=1
            count14+=1
        if np.isnan(list(d[basdai_3][d["row_id"]==x])[0]):
            count+=1
            count14+=1
        if np.isnan(list(d[basdai_4][d["row_id"]==x])[0]):
            count+=1
            count14+=1
        if np.isnan(list(d[basdai_5][d["row_id"]==x])[0]):
            count+=1
            count56+=1
        if np.isnan(list(d[basdai_6][d["row_id"]==x])[0]):
            count+=1
            count56+=1
        na_count["all"].append(count)
        na_count["1-4"].append(count14)
        na_count["5-6"].append(count56)
    
    basdai_out=[]
    for x in range(len(d)):
        count=np.nan
        if na_count["all"][x]==0:
            count=d[basdai_1][x]+d[basdai_2][x]+d[basdai_3][x]+d[basdai_4][x]
            count+=(d[basdai_5][x]+d[basdai_6][x])/2
            count=count/5
        elif na_count["all"][x]==1 and na_count["1-4"][x]==1:
            count=d[basdai_1][x]+d[basdai_2][x]+d[basdai_3][x]+d[basdai_4][x]
            count+=(d[basdai_5][x]+d[basdai_6][x])/2
            count=count/5
        elif na_count["all"][x]==1 and na_count["5-6"][x]==1:
            count=d[basdai_1][x]+d[basdai_2][x]+d[basdai_3][x]+d[basdai_4][x]
            count+=d[basdai_5][x]+d[basdai_6][x]
            count=count/5
        basdai_out.append(round(count,8))
    return basdai_out


def add_BDSN(d):
    drug="drug_name"
    pat="patient_id"
    start="drug_start_date"
    row="row_id"
    patients=unique(d[pat])
    d["bio_drug_series_number"]=np.nan
    bdMARDS=["abatacept","adalimumab","amgevita",
             "anakinra","baricitinib","belimumab",
             "benepali","certolizumab","erelzi",
             "etanercept","flixabi","golimumab",
             "guselkumab","hyrimoz","imraldi",
             "inflectra","infliximab","ixekizumab",
             "mycophenolat","otezla","biologic_other",
             "project_medicine","remsima","rituximab",
             "rixathon","ruxience","sarilumab",
             "secukinumab","tocilizumab",
             "tofacitinib","upadacitinib","ustekinumab","zessly"]
    D=d[d[drug].isin(bdMARDS)]
    for patient in patients:
        df=D[D[pat]==patient]
        df=df.sort_values(start,ascending=True)
        Keys=[]
        for x in df[row]:
            Keys.append(x)
        if len(Keys)>=1:
            for i in range(len(Keys)):
                d.loc[d.row_id==Keys[i],"bio_drug_series_number"]=int(i)+1
    return d

def basfi_rename(d):
    basfi={"basfi_1":"basfi_1_socks",
           "basfi_2":"basfi_2_pen",
           "basfi_3":"basfi_3_shelf",
           "basfi_4":"basfi_4_chair",
           "basfi_5":"basfi_5_floor",
           "basfi_6":"basfi_6_standing",
           "basfi_7":"basfi_7_steps",
           "basfi_8":"basfi_8_shoulder",
           "basfi_9":"basfi_9_activities_demanding",
           "basfi_10":"basfi_10_activities_day"}
    if all(value in list(d.keys()) for value in list(basfi.keys())):
        for i in list(basfi.keys()):
            d.rename(columns = {i:basfi[i]},inplace = True)
            
    

def readability(dataframe):
    readings=pd.read_excel("/home/alexanderandersen/2_wave/slice_selection_second_wave_overview_all_patientsv1.3.xlsx",sheet_name=None)
    readabilities={}
    for key in readings:
        if all(y in list(readings[key].columns) for y in ["patient_id_abcde","dummy_for_readable"]):
            for x in readings[key]["patient_id_abcde"]:
                if len(list(readings[key]["dummy_for_readable"][readings[key]["patient_id_abcde"]==x]))!=0:
                    readabilities[x]=list(readings[key]["dummy_for_readable"][readings[key]["patient_id_abcde"]==x])[0]
    readability_out=[]
    for x in dataframe["patient_id_abcde"]:
        if x in list(readabilities.keys()):
            readability_out.append(readabilities[x])
        else:
            readability_out.append("")
    return readability_out
    
times=datetime.now().strftime('%Y%m%d')

### read the metadata file ###==str
file_types=[]
for x in range(len(path)):
    if re.search("\.[a-z]{3,4}",path[x]).group() not in file_types:
        file_types.append(re.search("\.[a-z]{3,4}",path[x]).group())

if ".xlsx" in file_types and ".csv" not in file_types:
    full_content={}
elif ".csv" in file_types and ".xlsx" not in file_types:    
    full_content=pd.DataFrame()

if typen=="clinical":
    full_content={}
elif typen=="metadata":    
    full_content=pd.DataFrame()
    national=[]
    sources=[]
    describe={}

for x in range(len(path)):
    nation=re.search("/[A-Z]{2}",path[x]).group()[1:3]
    filename=path[x].split("/")[-1]
    print("Currently working on",filename,"....")
    if "metadata" in path[x] or typen=="metadata":
        datatype="metadata"
    elif "clinical" in path[x] or typen=="clinical":
        datatype="clinical"
        
    output_filename="total_" + datatype + "_" + times + ".xlsx"
    ### read the metadata file ###
    if ".csv" in path[x]:
        metadata_file = pd.read_csv(path[x], sep=";")
        if len(metadata_file.columns)==1:
            metadata_file = pd.read_csv(path[x], sep=",")
    elif ".xlsx" in path[x]:
        metadata_file = pd.read_excel(path[x],sheet_name=None)
    else:
        next
    
    ### removes the header for every file and sheet and add source variable
    if typen=="clinical":
        nsaid_check=False
        if "nsaid" in metadata_file.keys():
            nsaid_check=True
        for key in metadata_file:
            if "weight_kg" in metadata_file[key].keys():
                metadata_file[key].rename(columns={"weight_kg":"weight"},inplace=True)
            if "year_sx_onset" in metadata_file[key].keys():
                metadata_file[key].rename(columns={"year_sx_onset":"year_of_symptoms_onset"},inplace=True)
            if "spa_cohort" in metadata_file[key].keys():
                metadata_file[key].rename(columns={"spa_cohort":"spa_cohort_cz"},inplace=True)
            if "patient_pga" in metadata_file[key].keys():
                metadata_file[key].rename(columns={"patient_pga":"patient_global_score"},inplace=True)
            NY_4ab_adjust(metadata_file[key])
            basfi_rename(metadata_file[key])
            criteria_remapping(metadata_file)
            if "{" in str(metadata_file[key].iloc[0][0]):
                metadata_file[key]=metadata_file[key][1:]
            if key not in full_content.keys():
                full_content[key]=pd.DataFrame()
            metadata_file[key]=metadata_file[key].assign(source=filename)
            metadata_file[key]["country"]=nation
            full_content[key]=pd.concat([full_content[key],metadata_file[key]])
             
    elif typen=="metadata":
        if type(metadata_file)==dict:
            sheetname=list(metadata_file.keys())[0]
            metadata_file=metadata_file[sheetname]
        if x!=0 and "{" in metadata_file.iat[0,0]:
            for x in list(metadata_file.keys()):
                if x not in describe.keys() and "Unnamed:" not in x:
                    describe[x]=metadata_file[x][0]
            metadata_file=metadata_file[1:]
            
        metadata_file=metadata_file.assign(source=filename)
        metadata_file["country"]=nation
        
        full_content=pd.concat([full_content,metadata_file])
        
        

#sys.exit()  

###post-pooling processing###
        
if typen=="clinical":
    print("currently processing clinical data...")
    print("updating row ID, binarize binary variables and resetting index ....")
    for key in full_content:
        full_content[key]=df_binarize(full_content[key])
        full_content[key]["row_id"]=[n for n in range(len(full_content[key]))]
        full_content[key]=full_content[key].reset_index(drop=True)
        
    print("mapping drugs ....")
    full_content["med"]=map_drugs(full_content["med"],full_content["nsaid"],full_content["pat"])
    full_content["med"]["row_id"]=[n for n in range(len(full_content[key]))]
    
    print("renaming drugs ....")
    full_content["med"]["drug_name"]=rename_bdmard(full_content["med"]["drug_name"])

    print("adjusting dates ....")
    for key1 in full_content:
        for key2 in full_content[key1]:
            if "date" in str(key2):
                for i in range(len(full_content[key1][key2])):
                    full_content[key1][key2][i]=date_adjust(full_content[key1][key2][i])
    
    print("adjusting date-frames ....")                    
    full_content["med"]=adjust_dateframe(full_content["med"])
    for key in full_content:
        for key2 in full_content[key]:
            if "date" in str(key2):
                for i in range(len(full_content[key][key2])):
                    full_content[key][key2][i]=date_adjust(full_content[key][key2][i],make_str=True)
    
    print("adds bio_drug_series_number ....")
    full_content["med"]=add_BDSN(full_content["med"])
    
    print("calculates output variables ....")
    full_content["vis"]["basdai"]=basdai_cal(full_content["vis"])
    full_content["pat"]["caspar_criteria"]=caspar_cal(full_content["pat"])
    full_content["pat"]["new_york_criteria"]=new_york_cal(full_content["pat"])
    full_content["pat"]["asas_criteria"]=asas_cal(full_content["pat"])
    
    print("fill in date of first and last visits")
    pid=unique(full_content["pat"]["patient_id"])
    for x in pid:
        if "NaT" in str(full_content["pat"][full_content["pat"]["patient_id"]==x]["date_of_first_visit"]):
            if len(full_content["vis"][full_content["vis"]["patient_id"]==x]["visit_date"])!=0:
                first_date=min(full_content["vis"][full_content["vis"]["patient_id"]==x]["visit_date"])
                full_content["pat"][full_content["pat"]["patient_id"]==x]["date_of_first_visit"]=first_date
        if "NaT" in str(full_content["pat"][full_content["pat"]["patient_id"]==x]["date_of_last_visit"]):
            if len(full_content["vis"][full_content["vis"]["patient_id"]==x]["visit_date"])!=0:
                last_date=max(full_content["vis"][full_content["vis"]["patient_id"]==x]["visit_date"])
                full_content["pat"][full_content["pat"]["patient_id"]==x]["date_of_last_visit"]=last_date
    
    print("remove unused variabel and reorganize ....")
    for key in full_content:
        for x in ["Unnamed: 0","X30","patient_id2","nraxSpA","new_york_criteria_4a_xray_sacroiliitis_bilat","new_york_criteria_4b_xray_sacroiliitis_unilat"]:
            if x in full_content[key].keys():
                full_content[key]=full_content[key].drop(x,axis=1)
    for key in full_content:
        last=["country","source"]
        if key=="pat":
            first=["row_id","patient_id","year_of_birth","year_of_diagnosis","year_of_symptoms_onset","diagnosis_group","hla_b27","gender","height","date_of_first_visit","date_of_last_visit"]
            last=["registry_name","data_cut_date"]+last
        elif key=="med":
            first=["row_id","patient_id","drug_name","drug_start_date","drug_stop_date","drug_discont_reason","bio_drug_series_number"]
        elif key=="vis":
            first=["row_id","patient_id","crp","weight","visit_date"]
        middle=[]
        for key2 in full_content[key]:
            if key2 not in first and key2 not in last:
                middle.append(key2)
        middle=natural_sort(middle)
        full=first+middle+last
        full_content[key]=full_content[key].reindex(columns=full)
    
    
    
if typen=="metadata":
    print("adjusting date ....")
    full_content["row_id"]=[n for n in range(len(full_content))]
    for key in full_content:
        if "date" in str(key):
            for i in range(len(full_content[key])):
                full_content[key][full_content["row_id"]==i]=date_adjust(list(full_content[key][full_content["row_id"]==i])[0])
    
    print("adjusting diagnosis group ....")
    for i in range(len(full_content["diagnosis_group"])):
        temp=list(full_content["diagnosis_group"][full_content["row_id"]==i])[0]
        if type(temp)!=float:
            full_content["diagnosis_group"][full_content["row_id"]==i]=temp.lower()
        else:
            full_content["diagnosis_group"][full_content["row_id"]==i]=""
    print("dropping pointless variables ....")
    full_content=full_content.drop("row_id",axis=1)
    for key in full_content:
        temp=unique(full_content[key])
        if len(temp)==1 and np.isnan(temp[0]):
            full_content=full_content.drop(key,axis=1)

    print("inserting new variables for the sake of the reviewer ....")
    full_content["excluded_during_slices_selection"]=""
    describe["excluded_during_slices_selection"]="{0,1}"
    
    full_content["scan_plain_STIR"]=""
    describe["scan_plain_STIR"]="{0,1}"
    
    full_content["scan_plain_T1"]=""
    describe["scan_plain_T1"]="{0,1}"
    
    full_content["readability"]=readability(full_content)
    describe["readability"]="{0,1}"
    
    print("remove unused variabel and reorganize ....")
    for x in full_content.keys():
        if "Unnamed:" in x:
            full_content=full_content.drop(x,axis=1)
            #del describe[x]
    
    print("adding national code and source-file names ....")
    full_content=full_content.reindex(columns=[col for col in full_content if col not in ["country","source"]]+["country","source"])
    if "country" not in describe.keys():
        describe["country"]="{CH,CZ,DK,SL,etc}"
    if "source" not in describe.keys():
        describe["source"]="{text}"
    

#sys.exit()
### write content to file ###
print("currently writing output-files ....")
sys.exit()
if typen=="metadata":
    output_filename=datatype + "_" + times + ".xlsx"
    print("writing",output_filename)
    Describe=pd.DataFrame(describe,index=[0])
    FULL=pd.concat([Describe,full_content.loc[:]]).reset_index(drop=True)
    with pd.ExcelWriter(output_filename) as writer:
        FULL.to_excel(writer,sheet_name="main",index=False)
    
    countries=unique(full_content["country"])
    for i in countries:
        output_filename=datatype + "_"+ i +"_" + times + ".xlsx"
        print("writing",output_filename)
        curr_country=full_content[full_content["country"]==i]
        curr_country=pd.concat([Describe,curr_country[:]]).reset_index(drop=True)
        with pd.ExcelWriter(output_filename) as writer:
            curr_country.to_excel(writer,sheet_name="main",index=False)

elif typen=="clinical":   
    countries=unique(full_content["pat"]["country"])
    sheets=["pat","med","vis"]
    for x in countries:
        for y in sheets:
            sub_select=full_content[y][full_content[y]["country"]==x]
            sub_select=sub_select.reset_index(drop=True)
            sub_select["row_id"]=[n for n in range(len(sub_select))]
            for i in range(0,len(sub_select),5000):
                sub_file=y+"_"+x+"_"+str(i)+".xlsx"
                if i==0:
                    sub_file=y+"_"+x+".xlsx"
                print("writing",sub_file)
                with pd.ExcelWriter(sub_file) as writer:
                    if i+5000<len(sub_select):
                        sub_select[i:i+5000].to_excel(writer,sheet_name=y,index=False)
                    else:
                        sub_select[i:].to_excel(writer,sheet_name=y,index=False)
    for y in sheets:
        full_content[y]["row_id"]=[n for n in range(len(full_content[y]))]
        for i in range(0,len(full_content[y]),5000):
            sub_file=y+"_"+str(i)+".xlsx"
            if i==0:
                sub_file=y+".xlsx"
            print("writing",sub_file)
            with pd.ExcelWriter(sub_file) as writer:
                if i+5000<len(full_content[y]):
                    full_content[y][i:i+5000].to_excel(writer,sheet_name=y,index=False)
                else:
                    full_content[y][i:].to_excel(writer,sheet_name=y,index=False)
    
print("All Done.")    