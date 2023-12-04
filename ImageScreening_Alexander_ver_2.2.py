########################################################
### Importing needed packages for running the script ###
########################################################
import re 
import pydicom
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys  
from datetime import datetime ## call computer date for output-file
from io import BytesIO ## for exporting images into the report

#############################################################
### Define the country/center to be used in the screening ###
#############################################################

use = "sl";
#if trickle_down_filter is true, ID issues in earlier segments does
## not cause new issues in later segments.
trickle_down_filter=True
# possible centers/countries for the use term: 
## "CH exer", "CH insel", "CH USZ", "CH LUKS", "CH kloe", "CH final"
## "CZ (part) 1","CZ (part) 2","CZ (part) 3", "CZ (part) 4", "CZ (part) 5", "CZ Brno","CZ FNKV","CZ Motol","CZ Olomouc", "CZ Plzen"
## "IS", 
## "SL"
#ignores lower-/uppercase (by converting to uppercase later) and spacing, as long as the
## national code and the center code is provided in the use-variable as a string.
use=use.upper() # makes it more userfrendly
###############################################
### Define Functions used during script-run ###
###############################################

#def collect_img_metadata(path, national_code):
def collect_img_metadata(path,national_code):
    #output_file=open(national_code + "_list_of_IDs_and_dates.txt","w")
    ex_ID_images = []
    image_dates = []
    missing_image_dates=[] #for gathering files with missing series-, acquisition-, and study dates
    wrong_name_format=[] #for gathering files with incorrect name format
    missing_meta=[] #for gathering files with missing metadata
    PatID_issue=[] # files with missing patient ID
    ExID_issue=[] # files with missing examination ID
    names_view=[]
    IDdate_view=[]
    file_count=0  # for assessing the percentage of images with issues
    image_counting={}
    
    for root, dirs, files in os.walk(path):
        if len(files) > 0:
            for file in files:
                # Needs to be changed for CZ
                # We analyze files with no suffix
                Pat_ID=""
                ex_ID=""
                name, extension = os.path.splitext(root + "/" + file)
                names_view.append(name)
                if extension == '.dcm':
                    file_count+=1
                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                    except:
                        missing_meta.append(root + "/" + file)
                        next
                    # Get patient ID
                    Pat_ID=str(ds.PatientName)
                    
                    # counting the patients body parts
                    
                    #counting patient ID's in images to calculate diagnosis group images
                    if Pat_ID not in image_counting:
                        image_counting[str(Pat_ID)]=1
                    else:
                        image_counting[str(Pat_ID)]+=1
                    if Pat_ID=='':
                        PatID_issue.append(root + "/" + file)
                    
                    # Get examination ID
                    ex_ID = str(ds.PatientID)
                    
                    if ex_ID=='':
                        ExID_issue.append(root + "/" + file)
                    
                    # Build list of examination IDs
                    ex_ID_images.append(ex_ID)
                    date=""
                    try:
                        date = ds.StudyDate
                    except:
                        None
                    try:
                        date = ds.AcquisitionDate
                    except:
                        None
                    try:
                        date = ds.SeriesDate
                    except:
                        None
                    
                    if date!="":
                        image_dates.append(str(pd.to_datetime(date)).split(" ")[0])
                    else:
                        missing_image_dates.append(root + "/" + file)
                        
                    if Pat_ID!="" and ex_ID!="" and date!="":
                        IDdate_view.append([Pat_ID,ex_ID,str(pd.to_datetime(date)).split(" ")[0]])
                    
                    
                elif len(extension) == 0 and file[0] != '.' and file!="DICOMDIR": #this is done to also be able to read images with no extension (CZ)
                    file_count+=1

                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                        
                    except:
                        missing_meta.append(root + "/" + file)
                        next
                    # Czech include ^ as part of their patient ID's in the images
                    if "CZ" in national_code:
                        Pat_ID=str(ds.PatientName).split('^')[0]
                    else:
                        Pat_ID=str(ds.PatientName)
                    
                    
                    #counting patient ID's in images to calculate diagnosis group images
                    if Pat_ID not in image_counting:
                        image_counting[str(Pat_ID)]=1
                    else:
                        image_counting[str(Pat_ID)]+=1
                    
                    if Pat_ID=='':
                        PatID_issue.append(root + "/" + file)
                    
                    # Get examination ID
                    ex_ID = str(ds.PatientID)
                    
                    if ex_ID=='':
                        ExID_issue.append(root + "/" + file)
                    
                    if ex_ID=="":
                        ExID_issue.append(root + "/" + file)
                    
                    ex_ID_images.append(ex_ID)
                    date=""
                    try:
                        date = ds.StudyDate
                        # save dates
                    except:
                        None
                    try:
                        date = ds.AcquisitionDate
                    except:
                        None
                    try:
                        date = ds.SeriesDate
                    except:
                        None
                    
                    if date!="":
                        image_dates.append(str(pd.to_datetime(date)).split(" ")[0])
                    else:
                        missing_image_dates.append(root + "/" + file)
                        
                    # Gather ID and date combinations
                    if Pat_ID!="" and ex_ID!="" and date!="":
                        IDdate_view.append([Pat_ID,ex_ID,str(pd.to_datetime(date)).split(" ")[0]])


                # do screening for dicom tags (Simon has another script for checking patient sensitive information)

                #check image date - it must also be present for this project
                #acquisition_date = series_date = study_date, these three variables should be the same. We only need information
                #from one of them to know the image date, so it is fine is only one variable is available and the others have missing values
                
    return ex_ID_images, image_dates, missing_image_dates, file_count, wrong_name_format, missing_meta, PatID_issue, ExID_issue, IDdate_view, image_counting

# function to ensure that a 1 is present in a cell, so any other result is ignored (used in section 10)
def int_check(element:any):
    try:
        element=int(element)
    except ValueError:
        element=0
    return(element)


# function to calculate the average number of images (used in section 12)
def ave(dict):
    SUM=0
    for key in dict:
        SUM+=dict[key]      # sum(X)
    average=SUM/len(dict)   # sum(X)/n
    return average

# function to calculate standard deviation of the images (used in section 12)   
def std(dict):
    SUM=0
    # calculate average
    for key in dict:
        SUM+=dict[key]
    average=SUM/len(dict)      # average = my
    # calculate standard deviation
    new_sum=0
    for key in dict:
        et=(dict[key]-average) # X-my
        new_sum+=et**2         # sum(X-my)²
    STD=(new_sum/len(dict))    # sum(X-my)²/n 
    STD=STD**0.5               # sqrt(sum(X-my)²/n)
    return(STD)

# function to add value labels to graph (used in section 12)
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i,y[i],y[i])

# function to calculate the three quantiles (used in section 12)
def quantile(LIST):
    length=len(LIST)
    if length>=4:
        one_quarter=LIST[int(length*0.25)]    # 1st quantile
        median=LIST[int(length*0.5)]          # median (2nd quantile)
        three_quarter=LIST[int(length*0.75)]  # 3rd quantile  
    elif length==3:
        one_quarter=LIST[0]    # 1st quantile
        median=LIST[0]          # median (2nd quantile)
        three_quarter=LIST[0]  # 3rd quantile
    else:
        one_quarter="NA"    # 1st quantile
        median="NA"          # median (2nd quantile)
        three_quarter="NA"  # 3rd quantile
    return(one_quarter,median,three_quarter)

# function to find the total amount of images (used in section 12) 
def in_total(dict):
    SUM=0
    for key in dict:
        SUM+=dict[key]
    return(SUM)


############################################
### Read image metadata from Dicom files ###
############################################
print("Setting paths to images and metadata-file.")
#get images and metadata from Schweitzerland
if "CH" in use: 
    if "INSEL" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CH/Insel" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CH/Insel/xray_mri_metadata_second_wave_Insel_20220613_FINAL.csv"
        excel_metadata_CH = pd.read_csv(metadata_path, sep=";") #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CH.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CH  
        
        clinical_data_path="/home/alexanderandersen/2_wave/CH/Insel/clinical_data_Insel_20220601_second_wave_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        
        use="CH_INSEL"
        
    elif "EXER" in use:
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CH/Exer" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CH/Exer/xray_mri_metadata_second_wave_Exer_20220727_FINAL.csv"
        excel_metadata_CH = pd.read_csv(metadata_path, sep=";") #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CH.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CH
        
        clinical_data_path="/home/alexanderandersen/2_wave/CH/Exer/clinical_data_Exer_20220401_second_wave_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        
        use="CH_EXER"
    
    elif "KLOE" in use:
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/images/CH/kloetichuv" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/images/CH/kloetichuv/xray_mri_metadata_kloetichuv_20220909.csv"
        excel_metadata_CH = pd.read_csv(metadata_path, sep=";") #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CH.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CH
        
        clinical_data_path="/home/alexanderandersen/2_wave/images/CH/kloetichuv/clinical_data_kloeti_CHUV_20220801_second_wave.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CH_KLOETICHUV"
    
    elif "LUKS" in use:
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CH/LUKS" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CH/LUKS/xray_mri_metadata_second_wave_LUKS_20220810_FINAL.csv"
        excel_metadata_CH = pd.read_csv(metadata_path, sep=";") #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CH.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CH
        
        clinical_data_path="/home/alexanderandersen/2_wave/CH/LUKS/clinical_data_LUKS_20220801_second_wave_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CH_LUKS"
    
    elif "USZ" in use:
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CH/USZ" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CH/USZ/xray_mri_metadata_second_wave_USZ_20220211_FINAL.csv"
        excel_metadata_CH = pd.read_csv(metadata_path, sep=";") #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde) #generate a list of patient examination IDs that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CH.image_date:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CH
        
        clinical_data_path="/home/alexanderandersen/2_wave/CH/USZ/clinical_data_USZ_20220101_second_wave_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CH_USZ"
        
    elif "FINAL" in use:
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/images/CH/final_mix" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_NEW_final_mix.csv"
        excel_metadata_CH = pd.read_csv(metadata_path, sep=";") #load excel file
        #metadata_path="/home/alexanderandersen/CH_total_metadata_20221005.xlsx"
        #excel_metadata_CH = pd.read_excel(metadata_path)
        img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde) #generate a list of patient examination IDs that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CH.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CH
        
        clinical_data_path="/home/alexanderandersen/2_wave/clinical_data/CH/CH_final_mix_clinical_data.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CH_FINAL_MIX"

#get images and metadata from Czech Republic
elif "CZ" in use:
    if "1" in use:
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/1_skvulp_new" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/Corrected_2ND_wave_teplate_part1_AKBA.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
    
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CZ
        
        #clinical_data_path="/home/alexanderandersen/2_wave/CZ/3_skvulp/data_CZ_2-3-4-wave_20211025.xlsx"
        #excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        clinical_patients=np.unique(np.array(["",""],dtype="object"))
        
        use="CZ_1"

    elif "2" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/images/CZ/2_skvulp" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/images/CZ/2_skvulp/Template_image_metadata_eurospa_imaging_second_wave_part2_AKBA.xlsx"

        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
    
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CZ
        
        #clinical_data_path="/home/alexanderandersen/2_wave/CZ/3_skvulp/data_CZ_2-3-4-wave_20211025.xlsx"
        #excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        clinical_patients=np.unique(np.array(["",""],dtype="object"))
        
        use="CZ_2"
        
    elif "3" in use:
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/3_skvulp" #pointing path where images are stored (both XRay and MR)
    
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/3_skvulp/Template_image_metadata_eurospai_imaging_second_wave_part_3_FINAL.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
    
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CZ
        
        clinical_data_path="/home/alexanderandersen/2_wave/CZ/3_skvulp/data_CZ_2-3-4-wave_20211025.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CZ_3"

    elif "4" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/4_skvulp" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/4_skvulp/template 2nd wave part 4.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
    
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CZ
        
        excel_clinical=pd.read_excel("/home/alexanderandersen/2_wave/CZ/3_skvulp/data_CZ_2-3-4-wave_20211025.xlsx",sheet_name=None)
        excel_clinical_extra=pd.read_excel("/home/alexanderandersen/2_wave/CZ/4_skvulp/data_CZ_20220810_Praha.xlsx",sheet_name=None)
        
        clinical_data_path=["/home/alexanderandersen/2_wave/CZ/3_skvulp/data_CZ_2-3-4-wave_20211025.xlsx","/home/alexanderandersen/2_wave/CZ/4_skvulp/data_CZ_20220810_Praha.xlsx"]
        
        use="CZ_4"
    
    elif "5" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/images/CZ/5_skvulp" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/images/CZ/5_skvulp/template_part5.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
    
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CZ
        
        clinical_data_path="/home/alexanderandersen/2_wave/images/CZ/5_skvulp/data_CZ_20221009_Praha_missing_patients.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
                
        use="CZ_5"
    
    elif "BRNO" in use or "BRUNO" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/Brno" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/Brno/Template_image_metadata_eurospa_imaging_second_wave_Brno_FINAL.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x)))
        excel_metadata=excel_metadata_CZ
        
        clinical_data_path="/home/alexanderandersen/2_wave/CZ/Brno/data_CZ_20220429_Brno_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CZ_BRNO"

    elif "FNKV" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/FNKV" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/FNKV/Template_image_metadata_eurospa_imaging_second_wave_FNKV_FINAL.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x))) 
        excel_metadata=excel_metadata_CZ
        
        clinical_data_path="/home/alexanderandersen/2_wave/CZ/FNKV/data_CZ_20220429_FNKV_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CZ_FNKV"

    elif "OLOMOUC" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/olomouc" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/olomouc/Template_image_metadata_eurospa_imaging_second_wave_Olomouc_FINAL.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x))) 
        excel_metadata=excel_metadata_CZ
        
        clinical_data_path="/home/alexanderandersen/2_wave/CZ/olomouc/data_CZ_20220429_Olomouc_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CZ_OLOMOUC"

    elif "MOTOL" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/Motol" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/Motol/Motol_corr_FINAL.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x))) 
        excel_metadata=excel_metadata_CZ
        
        clinical_data_path="/home/alexanderandersen/2_wave/CZ/Motol/data_CZ_20220810_Motol_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CZ_MOTOL"
        
    elif "PLZEN" in use: 
        # set image directory
        images_root_path = "/home/alexanderandersen/2_wave/CZ/Plzen" #pointing path where images are stored (both XRay and MR)
        
        # set and adjust metadata for reading
        metadata_path="/home/alexanderandersen/2_wave/CZ/Plzen/tabulka studie EUROSPAI oprava.xlsx"
        excel_metadata_CZ = pd.read_excel(metadata_path) #load excel file
        img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
        #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
        
        img_metadata_image_date_list=[]
        for x in excel_metadata_CZ.image_date[1:]:
            if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
                img_metadata_image_date_list.append(str(pd.to_datetime(x))) 
        excel_metadata=excel_metadata_CZ
        
        clinical_data_path="/home/alexanderandersen/2_wave/CZ/Plzen/data_CZ_20220429_Plzen_FINAL.xlsx"
        excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
        
        use="CZ_PLZEN"

#get images and metadata from Slovenia
elif use=="SL" : 
    # set image directory
    images_root_path = "/home/alexanderandersen/2_wave/images/SL/" #pointing path where images are stored (both XRay and MR)
    
    # set and adjust metadata for reading
    metadata_path="/home/alexanderandersen/2_wave/metadata/SL/Template_image_metadata_eurospa_imaging_second_wave (7 - changes 17.4.2023).xlsx"
    
    excel_metadata_SI = pd.read_excel(metadata_path) #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_SI.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    img_metadata_image_date_list = np.unique(excel_metadata_SI.image_date[1:]) #generate a list of image dates that exist in the metadata excel file
    excel_metadata=excel_metadata_SI
    
    #excel_clinical=pd.read_excel("/home/alexanderandersen/2_wave/CZ/3_skvulp/data_CZ_2-3-4-wave_20211025.xlsx",sheet_name=None)
    clinical_data_path="/home/alexanderandersen/2_wave/clinical_data/SL/data_si_20230419_v1.xlsx"
    excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
    
#get images and metadata from Iceland    
elif use=="IS" : 
    # set image directory
    images_root_path = "/home/alexanderandersen/2_wave/images/IS/" #pointing path where images are stored (both XRay and MR)
    
    # set and adjust metadata for reading
    metadata_path="/home/alexanderandersen/2_wave/metadata/IS/metadata_island_images_first_wave_all.xlsx"
    excel_metadata_IS = pd.read_excel(metadata_path) #load excel file    
    img_metadata_ex_ID_list = np.unique(excel_metadata_IS.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    img_metadata_image_date_list = []
    for x in excel_metadata_IS.image_date:
        if type(x)==int:
            img_metadata_image_date_list.append(x)
    #img_metadata_image_date_list = np.unique(excel_metadata_IS.image_date[1:]) #generate a list of image dates that exist in the metadata excel file
    excel_metadata=excel_metadata_IS 
    
    clinical_data_path="/home/alexanderandersen/2_wave/clinical_data/IS/clinical_20230420_IMGIS.xlsx"
    excel_clinical=pd.read_excel(clinical_data_path,sheet_name=None)
    
    clinical_patients=np.unique(np.array(["",""],dtype="object"))
    
    
########################################
### Initiate the output report file ####
########################################

times=datetime.now().strftime('%Y%m%d') # saves date of run for file-naming
Times=datetime.now().strftime('%d/%m-%Y') # saves date of run for header-naming

# naming the output inconsistency file after the national two-letter code and the time of the run
if trickle_down_filter==True:
    output_file_name= use + "_" + times + "_FILTERED.html" 
else:
    output_file_name= use + "_" + times + ".html" 

print("Initiating Report File:",output_file_name) #reporting the report to be made to the data analyst

output_file=open(output_file_name,"w") # opens the file for writing

# writing the headline of the report
FILE_HEADER="<html>\n<head>\n<title> \n" + output_file_name 
FILE_1ST_HEADER="\ </title>\n</head> <body><h1><div style='text-align:center'> <u>EuroSpA Imaging Report for " 
VARIABLE= use + " (" + Times + ")</u></div><br />"
FILE_2ND_HEADER="<h2><div style='text-align:center'>Screening Results of Images and Metadata-file \n</div></body></html>"

output_file.write(FILE_HEADER + output_file_name + FILE_1ST_HEADER + VARIABLE + FILE_2ND_HEADER) 

output_file.write("<br /><br /></h2>")

output_file.write("<div style='text-align:center'>path to images: " + images_root_path + "</div>")

if type(excel_clinical)==dict:    
    output_file.write("<div style='text-align:center'>metadata-file used: " + metadata_path + "</div>")
    output_file.write("<div style='text-align:center'>clinical data file used: " + clinical_data_path + "</div>" + "<br /><br />")
else:
    output_file.write("<div style='text-align:center'>metadata-file used: " + metadata_path + "</div>" + "<br /><br />")
############################################################
### Information gathering from the images to be screened ###
############################################################
print("Gathering data from images.")
ex_ID_image_dates_images_list = collect_img_metadata(images_root_path,use) #run previous function to get a tuple consisting of two lists: The first with examination IDs in all images, the second with all image dates

ex_ID_images_list = ex_ID_image_dates_images_list[0] #extract unique examination IDs
ex_ID_count = len(ex_ID_images_list) #get amount of unique examination IDs

#image_dates = ex_ID_image_dates_images_list[1] #extract unique image dates 
image_dates_tmp = ex_ID_image_dates_images_list[1] #extract unique image dates
image_dates=[]
#image_dates = pd.to_datetime(image_dates) #change dates to correct format 
for x in pd.to_datetime(image_dates_tmp):
    image_dates.append(str(x))

missing_dates_list = ex_ID_image_dates_images_list[2] # get the unique files for which dates are not given

file_amount=ex_ID_image_dates_images_list[3] # get the number of parsed files

name_issue=ex_ID_image_dates_images_list[4] # get the unique files that don't have the right naming format.
name_issue_unabrigded=ex_ID_image_dates_images_list[4]

no_metadata=ex_ID_image_dates_images_list[5] # get the uniqie files that don't have metadata to them
no_metadata_unabrigded=ex_ID_image_dates_images_list[5]

missing_PatID_list=ex_ID_image_dates_images_list[6] # get the files that miss patient ID's

missing_ExID_list=ex_ID_image_dates_images_list[7] # get the files that miss examination ID's

IDdate=ex_ID_image_dates_images_list[8] #

image_counting=ex_ID_image_dates_images_list[9] # directory of patient ID's from images used in image-diagnosis group summary


####################################################################
### Print Image filenames with missing or incorrect Patient ID's ###
####################################################################
print("Processing images with missing patient IDs.")
output_file.write("<h2><div style='text-align:center'>#1 Files with missing Patient IDs</div></h2><br />")

                  
if len(missing_PatID_list)==0:
    output_file.write("<div style='text-align:center'>No images lack Patient IDs.</div><br />")
else:
    for i in missing_PatID_list:
        output_file.write("<div style='text-align:center'>" + i.split(images_root_path)[1]+"</div><br />")

    output_file.write("<br /><div style='text-align:center'><u>Total number of files with missing or incorrect Patient ID's: "+ str(len(missing_PatID_list)) +"</u></div>")

########################################################################
### Print Image filenames with missing or incorrect Examination ID's ###
########################################################################
print("Processing images with missing examination IDs.")
output_file.write("<h2><div style='text-align:center'>#2 Files with missing Examination IDs</div></h2><br />")

                  
if len(missing_ExID_list)==0:
    output_file.write("<div style='text-align:center'>No images lack Examination IDs.</div><br />")
else:
    for i in missing_ExID_list:
        output_file.write("<div style='text-align:center'>" + i.split(images_root_path)[1]+"</div><br />")

    output_file.write("<br /><div style='text-align:center'><u>Total number of files with missing or incorrect Examination ID's: "+ str(len(missing_ExID_list)) +"</u></div>")

################################################
### Print Image filenames with missing dates ###
################################################
print("Processing images with missing dates.")
output_file.write("<h2><div style='text-align:center'>#3 Files with missing dates</div></h2><br />")

                  
if len(missing_dates_list)==0:
    output_file.write("<div style='text-align:center'>No images lack dates.<br /> Every image has either Series-, Acquisition-, and/or Study dates.</div><br />")
else:
    for i in missing_dates_list:
        output_file.write("<div style='text-align:center'>" + i.split(images_root_path)[1]+"</div><br />")
            
    output_file.write("<br /><div style='text-align:center'><u>Total number of files with missing dates: "+ str(len(missing_dates_list)) +"</u></div>")

#######################################################################################
### Print patient ID inconsistencies between image metadata and excel metadata  ###
#######################################################################################
print("Processing patient ID inconsistencies")
output_file.write("<h2><div style='text-align:center'>#4 Patient ID inconsistencies between images and metadata</div></h2><br />")            
#find what patient IDs are not in the image excel metadata, but are present in the images
#could be because this patient  was not included in the excel metadata
pat_ID_images_list=list(image_counting.keys())

pat_ID_metadata_list=list(np.unique(excel_metadata.patient_id[1:]))
                  
pat_in_img_not_in_metadata = []
for pa_ID in pat_ID_images_list:
    if (not pa_ID in pat_ID_metadata_list):
        pat_in_img_not_in_metadata.append(pa_ID)
pat_in_img_not_in_metadata=np.unique(pat_in_img_not_in_metadata)
output_file.write("<h3><div style='text-align:center'>Patient ID's not found in Metadata file:</div></h3><br />")
for i in range(0,len(pat_in_img_not_in_metadata),4):
    sub_set=pat_in_img_not_in_metadata[i:i+4]
    output_file.write("<div style='text-align:center'>"+', '.join(str(x) for x in sub_set) + "</div>")          
output_file.write("<br /><div style='text-align:center'><u>Total number of missing IDs: " + str(len(pat_in_img_not_in_metadata)) + "</u></div><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")

#find what patient IDs are present in the images but not in the image excel metadata
#this most likely occurs if the images were not uploaded in the server, i.e. missing images
pat_in_metadata_not_in_img = []
for pa_ID in pat_ID_metadata_list:
    if (not pa_ID in pat_ID_images_list and "{" not in pa_ID):
        pat_in_metadata_not_in_img.append(pa_ID)
pat_in_metadata_not_in_img=np.unique(pat_in_metadata_not_in_img)
output_file.write("<h3><div style='text-align:center'>Patient ID's not found in images:</div></h3><br />")
for i in range(0,len(pat_in_metadata_not_in_img),4):
    sub_set=pat_in_metadata_not_in_img[i:i+4]
    output_file.write("<div style='text-align:center'>" + ', '.join(str(x) for x in sub_set) + "</div>")            
output_file.write("<br /><div style='text-align:center'><u>Total number of missing IDs: " + str(len(pat_in_metadata_not_in_img)) + "</div></u><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")
      

#######################################################################################
### Print Examination ID inconsistencies between image metadata and excel metadata  ###
#######################################################################################
print("Processing Examination ID inconsistencies")
output_file.write("<h2><div style='text-align:center'>#5 Examination ID inconsistencies between images and metadata</div></h2><br />")            
#find what examination IDs are not in the image excel metadata, but are present in the images
#could be because this patient examination was not included in the excel metadata
ex_in_img_not_in_metadata = []
for ex_ID in ex_ID_images_list:
    if trickle_down_filter==True:
        if ex_ID not in img_metadata_ex_ID_list and ex_ID[:-1] not in pat_in_img_not_in_metadata:
            ex_in_img_not_in_metadata.append(ex_ID)
    else:
        if ex_ID not in img_metadata_ex_ID_list:
            ex_in_img_not_in_metadata.append(ex_ID)
ex_in_img_not_in_metadata=np.unique(ex_in_img_not_in_metadata)
output_file.write("<h3><div style='text-align:center'>Examination ID's not found in Metadata file:</div></h3><br />")
for i in range(0,len(ex_in_img_not_in_metadata),4):
    sub_set=ex_in_img_not_in_metadata[i:i+4]
    output_file.write("<div style='text-align:center'>"+', '.join(str(x) for x in sub_set) + "</div>")          
output_file.write("<br /><div style='text-align:center'><u>Total number of missing IDs: " + str(len(ex_in_img_not_in_metadata)) + "</u></div><br />")
if trickle_down_filter==True:
    output_file.write("<br /><div style='text-align:center'><u> Examination ID's for missing patients have not been accounted for. </u></div><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")

#find what examination IDs are present in the images but not in the image excel metadata
#this most likely occurs if the images were not uploaded in the server, i.e. missing images
ex_in_metadata_not_in_img = []
for ex_ID in img_metadata_ex_ID_list:
    if trickle_down_filter==True:
        if ex_ID not in ex_ID_images_list and "{" not in ex_ID and ex_ID[:-1] not in pat_in_metadata_not_in_img:
            ex_in_metadata_not_in_img.append(ex_ID)
    else:
        if ex_ID not in ex_ID_images_list and "{" not in ex_ID:
            ex_in_metadata_not_in_img.append(ex_ID)
ex_in_metadata_not_in_img=np.unique(ex_in_metadata_not_in_img)
output_file.write("<h3><div style='text-align:center'>Examination ID's not found in images:</div></h3><br />")
for i in range(0,len(ex_in_metadata_not_in_img),4):
    sub_set=ex_in_metadata_not_in_img[i:i+4]
    output_file.write("<div style='text-align:center'>" + ', '.join(str(x) for x in sub_set) + "</div>")            
output_file.write("<br /><div style='text-align:center'><u>Total number of missing IDs: " + str(len(ex_in_metadata_not_in_img)) + "</div></u><br />")
if trickle_down_filter==True:
    output_file.write("<br /><div style='text-align:center'><u> Examination ID's for missing patients have not been accounted for. </u></div><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")
                  
#########################################
## comparing ID's and date to metadata ##
#########################################
print("Processing ID and date inconsistencies.")
output_file.write("<h2><div style='text-align:center'>#6 ID and date inconsistencies between images and metadata</div></h2><br />")            
# first off, we convert the dataframe to a list of list to make it esasier to iterate over 
EXCEL_metadata=excel_metadata.loc[:,["patient_id","patient_id_abcde","image_date"]].values.tolist()
# then we convert every element in the list of lists into string
for x in range(len(EXCEL_metadata)):
    if type(EXCEL_metadata[x][2])==float and not np.isnan(EXCEL_metadata[x][2]):
        EXCEL_metadata[x][2]=str(int(EXCEL_metadata[x][2]))
    elif type(EXCEL_metadata[x][2])==int or type(EXCEL_metadata[x][2])!=str:
        EXCEL_metadata[x][2]=str(EXCEL_metadata[x][2])


# convert all dates from metadata to the same format as those taken from images
for x in range(len(EXCEL_metadata)):
    if EXCEL_metadata[x][2]!="{yyyymmdd}" and EXCEL_metadata[x][2]!=" etc}": 
        EXCEL_metadata[x][2]=str(pd.to_datetime(EXCEL_metadata[x][2])).split(" ")[0]

#now we run through all of the ID's and dates from the files and compare them to the metadata
IDdate_not_in_metadata=[]
for line in IDdate:
    if line not in EXCEL_metadata and line not in IDdate_not_in_metadata:
        if trickle_down_filter==True:
            if line[0] not in pat_in_img_not_in_metadata and line[1] not in ex_in_img_not_in_metadata:
                IDdate_not_in_metadata.append(line)
        else:
            IDdate_not_in_metadata.append(line)
output_file.write("<h3><div style='text-align:center'>ID's and dates not found in Metadata file:</div></h3><br />")
output_file.write("<u><div style='text-align:center'>Patient ID - Examination ID - Date</div></u>")

IDdate_not_in_metadata_new=[]
for i in range(0,len(IDdate_not_in_metadata)):
    IDdate_not_in_metadata_new.append(" - ".join(str(x) for x in IDdate_not_in_metadata[i]))

IDdate_not_in_metadata_new.sort()
IDdate_not_in_metadata=IDdate_not_in_metadata_new

for i in range(0,len(IDdate_not_in_metadata)):
    sub_set=IDdate_not_in_metadata[i]
    output_file.write("<div style='text-align:center'>" + sub_set + "</div>")         
output_file.write("<br /><div style='text-align:center'><u>Total number of mismatching ID-date's: " + str(len(IDdate_not_in_metadata)) + "</u></div><br />")
if trickle_down_filter==True:
    output_file.write("<br /><div style='text-align:center'><u> ID-date combinations for missing patients and/or examinations have not been accounted for. </u></div><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")

# and here, we look into if there are any examinations that are recorded in metadata, but are not present in the files.
metadata_not_in_IDdate=[]
for line in EXCEL_metadata:
    if line not in IDdate and line not in metadata_not_in_IDdate:
        if trickle_down_filter==True:
            if line[0] not in pat_in_metadata_not_in_img and line[1] not in ex_in_metadata_not_in_img:
                metadata_not_in_IDdate.append(line)
        else:
            metadata_not_in_IDdate.append(line)
if len(metadata_not_in_IDdate)>0 and re.match('{',metadata_not_in_IDdate[0][0]):
    metadata_not_in_IDdate=metadata_not_in_IDdate[1:]
output_file.write("<h3><div style='text-align:center'>ID's and dates not found in Images:</div></h3><br />")
output_file.write("<u><div style='text-align:center'>Patient ID - Examination ID - Date</div></u>")
for i in range(0,len(metadata_not_in_IDdate)):
    sub_set=metadata_not_in_IDdate[i]
    output_file.write("<div style='text-align:center'>" + ' - '.join(str(x) for x in sub_set) + "</div>")          
output_file.write("<br /><div style='text-align:center'><u>Total number of mismatching ID-date's: " + str(len(metadata_not_in_IDdate)) + "</div></u><br />")
if trickle_down_filter==True:
    output_file.write("<br /><div style='text-align:center'><u> ID-date combinations for missing patients and/or examinations have not been accounted for. </u></div><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")

#########################################
### checking binary data in metadata ####
#########################################
print("Processing possible non-binary results in binary variables from the metadata file")
output_file.write("<h2><div style='text-align:center'>#7 Evaluation of Non-Binary Results in Binary Variables in the Metadata</div></h2><br />")            
if "USZ" not in use and "MOTOL" not in use and "SL" not in use:
    EXCEL_BI_metadata=excel_metadata.loc[:,["xray_sij",
                                            "xray_cervical_spine",
                                            "xray_lumbar_spine",
                                            "mri_sij",
                                            "mri_sij_STIR_semi_coronal",
                                            "mri_sij_T1_semi_coronal",
                                            "mri_cervical_spine",
                                            "mri_thoracic_spine",
                                            "mri_lumbar_spine"]].values.tolist()
                                            #"patient_has_no_relevant_radiograph",
                                            #"patient_has_no_relevant_mri"]].values.tolist()[1:]
    BI_header=["xray_sij",
               "xray_cervical_spine",
               "xray_lumbar_spine",
               "mri_sij",
               "mri_sij_STIR_semi_coronal",
               "mri_sij_T1_semi_coronal",
               "mri_cervical_spine",
               "mri_thoracic_spine",
               "mri_lumbar_spine"]
               #"patient_has_no_relevant_radiograph",
               #"patient_has_no_relevant_mri"]
else: #USZ does not have mri_sij_STIR_semi_coronal or mri_sij_T1_semi_coronal
    EXCEL_BI_metadata=excel_metadata.loc[:,["xray_sij",
                                            "xray_cervical_spine",
                                            "xray_lumbar_spine",
                                            "mri_sij",
                                            "mri_cervical_spine",
                                            "mri_thoracic_spine",
                                            "mri_lumbar_spine"]].values.tolist()[1:]
                                            #"patient_has_no_relevant_radiograph",
                                            #"patient_has_no_relevant_mri"]].values.tolist()[1:]
    BI_header=["xray_sij",
               "xray_cervical_spine",
               "xray_lumbar_spine",
               "mri_sij",
               "mri_cervical_spine",
               "mri_thoracic_spine",
               "mri_lumbar_spine"]
               #"patient_has_no_relevant_radiograph",
               #"patient_has_no_relevant_mri"]


ID_codes=[x for x in excel_metadata.patient_id_abcde]

# removes identifier row if present
if '{0,1}' in EXCEL_BI_metadata[0] or '{' in EXCEL_BI_metadata[0]:
    EXCEL_BI_metadata.pop(0)
    
if '{' in ID_codes[0]:
    ID_codes.pop(0)

remove_lines=['' for x in range(len(BI_header))]

# convert 0/1 to  "" and everything else to "X" to differentiate between binary and non-binary
excel_bi_metadata=[]
for line in EXCEL_BI_metadata:
    excel_bi_metadata.append(["" if str(x)=="1" or str(x)=="0" else "X" for x in line])

# removes lines, where there are only "", since we only want to focus on instances, where there are non-binaries    
while remove_lines in excel_bi_metadata:
    if len(ID_codes)==0:
        break
    INDEX=excel_bi_metadata.index(remove_lines)
    excel_bi_metadata.remove(remove_lines)
    ID_codes.pop(INDEX)
    
    
# if there are instances of non-binary results to binary variables, we continue to make the table    
if excel_bi_metadata!=[]:
    n=len(excel_bi_metadata[0])

    strike_index=[]
    for i in range(n):
        strike=0
        for j in excel_bi_metadata:
            if j[i]=="":
                strike+=1
        if strike==len(excel_bi_metadata):
            strike_index.append(i)

    index_correction=0
    for j in range(len(excel_bi_metadata)):
        index_correction=0
        for n in strike_index:
            excel_bi_metadata[j].pop(n-index_correction)
            index_correction+=1

    for n in reversed(strike_index):
        BI_header.pop(n)
        
    BI_header.insert(0,"EX_ID's")
    
    flat_list = [cell for row in excel_bi_metadata for cell in row]
    row_len = len(excel_bi_metadata[0])
    new_bi = [flat_list[e::row_len] for e in range(row_len)]
    
    for i in range(0,len(new_bi)):
        new_bi[i]=[BI_header[i+1]]+new_bi[i]
    
    res = {"EX_ID's":ID_codes}
    for sub in new_bi:
        res[sub[0]] = sub[1:]

    output_file.write(pd.DataFrame(res).to_html(index=False,justify="center"))
    output_file.write("<li> Only variables with non-binary entries are included</li>")
    output_file.write("<li> Only Examination ID's with non-binary entries are included</li>")
    output_file.write("<li> X marks instances for where an examination ID has a non-binary result for the given variabel</li>")
else: # if there are no instances of non-binary results to binary variables.
    output_file.write("<div style='text-align:center'>All Binary variables have been filled correctly.</div>")


######################################################################################
### Examination IDs in the metadata file that are not given any examination checks ###
######################################################################################
print("Processing possilbe empty examinations.")
output_file.write("<h2><div style='text-align:center'>#8 Examinations in the Metadata without Any examinations</div></h2><br />")    

if "USZ" not in use and "MOTOL" not in use and "SL" not in use:                  
    bi_metadata=excel_metadata.loc[:,["patient_id_abcde",
                                      "xray_sij",
                                      "xray_cervical_spine",
                                      "xray_lumbar_spine",
                                      "mri_sij",
                                      "mri_sij_STIR_semi_coronal",
                                      "mri_sij_T1_semi_coronal",
                                      "mri_cervical_spine",
                                      "mri_thoracic_spine",
                                      "mri_lumbar_spine"]].values.tolist()[1:]
else:
    bi_metadata=excel_metadata.loc[:,["patient_id_abcde",
                                      "xray_sij",
                                      "xray_cervical_spine",
                                      "xray_lumbar_spine",
                                      "mri_sij",
                                      "mri_cervical_spine",
                                      "mri_thoracic_spine",
                                      "mri_lumbar_spine"]].values.tolist()[1:]
empty_list=[]

for line in bi_metadata:
    count=0
    for n in line[1:]:
        if type(n)!=float and int(n)==1:     #if there are examinations for anything, there would be a 1 in a binary variable and we can dismiss this examinations for this purpose
            break
        count+=1
        if count==len(line[1:]):
            empty_list.append(line[0])    #if the line only consist of 0's, it will be reported

if len(empty_list)!=0:
    for i in range(0,len(empty_list),5):
        output_file.write("<div style='text-align:center'>" + ', '.join(str(x) for x in empty_list[i:i+5]) + "</div>") #here, the examinations are reported
else:
    output_file.write("<div style='text-align:center'>No empty examinations were found.</div>")
output_file.write("<br />")

######################################################################################################################
### check whether there are any examinations in the metadata file that contain both X-ray and MRI variable checks. ###
######################################################################################################################
print("Processing possible conflicting examinations.")
output_file.write("<h2><div style='text-align:center'>#9 Examinations in the Metadata with Conflicting Examination Types</div></h2><br />")    

conflict_list=[]
for line in bi_metadata:
    X_flag=False       #red flag for X-ray examinations
    MRI_flag=False     #red flag for MRI examinations
    for n in range(len(line)):
        
        # checking for X-ray examinations
        if n in [1,2,3]:  
            if type(line[n])!=float and int(line[n])==1:
                X_flag=True
        
        # checking for MRI examinations
        if n in [4,5,6,7,8,9]:
            if type(line[n])!=float and int(line[n])==1:
                MRI_flag=True
                
    # if MRI_flag and X_flag are both true, there are both MRI- and X-ray examinations in the same examination.
    if MRI_flag==True and X_flag==True:
        conflict_list.append(line[0]) # gather the examination ID's in a list for compact printing.
            
if len(conflict_list)!=0:
    for i in range(0,len(conflict_list),5):
        output_file.write("<div style='text-align:center'>" + ', '.join(str(x) for x in conflict_list[i:i+5]) + "</div>") # printing out the examination ID's with conflicting examinations.
else:
    output_file.write("<div style='text-align:center'>No problem detected in this section</div>")

##########################################################################################
### Checking that the patients has the right examinations according to their diagnosis ###
##########################################################################################
print("Evaluating examinations according to diagnosis")
output_file.write("<h2><div style='text-align:center'>#10 Necessary examinations to their diagnosis</div></h2>")

# only extracts patient ID, diagnosis groups and MRI for SIJ and spine
diagnosis_eval_metadata=excel_metadata.loc[:,["patient_id",
                                         "diagnosis_group",
                                         "mri_sij",
                                         "mri_cervical_spine",
                                         "mri_thoracic_spine",
                                         "mri_lumbar_spine",
                                         "patient_id_abcde"]].values.tolist()
# single list of patients
patients=np.unique(excel_metadata.patient_id).tolist()

issue_list=[] #here, the issues are recorded for the given patients
temp_issue_list=[]
# go through each patient to each up on their required examinations
for name in patients:
    ex_count=0
    diagnosis_flag="down" # flag used to mark if the examination is met. is down until required examination is met. 
    for line in diagnosis_eval_metadata:
        if line[0]==name and "{" not in line[0]: # some metadata file has {  in the first line as a descriptive line. That is not needed
            ex_count=+1
            diagnosis=line[1] # saves the diagnosis for reporting
            if line[1].lower()=="axspa":
                if int_check(line[2])==1: #AxSpA patients just need a MRI SIJ examination
                    diagnosis_flag="up"
            if line[1].lower()=="psa": #PsA patients needs either a MRI of SIJ or of the whole spine (Cervical, Lumbar, and Thoracic)
                if int_check(line[2])==1 or int_check(line[3])==int_check(line[4])==int_check(line[5])==1:
                    diagnosis_flag="up"
            else:
                #in case only few examinations are given erroneously
                message=line[-1]+"("+diagnosis+")"+" lacks a usable diagnosis group!!!"
                temp_issue_list.append(message)
                
        # if the flag is still down, the patient has not gotten the minimum required for in range(len(nsaid.columns)):
    if diagnosis_flag=="down" and "{" not in name:
        if "axspa" in diagnosis.lower():
            message=name+"("+diagnosis+") lack MRI of the SI-joints."
        elif diagnosis.lower()=="psa":
            message=name+"("+diagnosis+") lack MRI of both the SI-joints and the spine."
        else: # in case the patient does not have a usable diagnosis
            # if the unusable diagnosis have been given only to a few examinations, the given examinations are printed
            if ex_count>len(temp_issue_list):
                for x in temp_issue_list:
                    issue_list.append(x)
            # otherwise, if the unusable diagnosis have been given for the whole patient, the whole patient is printed.
            else:
                message=name+"("+diagnosis+")"+" lacks a usable diagnosis group!!!"
        issue_list.append(message)
                  
if len(issue_list)>0:
    for x in issue_list:
        TEXT="<div style='text-align:center'>" + x + "</div>"
        output_file.write(TEXT)
    output_file.write("<br /><div style='text-align:center'><u>Total number of cases that does not fulfill the inclusion criteria:" + str(len(issue_list)) + "</div></u><br />")
else:
    output_file.write("<div style='text-align:center'>All patients has the minimum required examinations for their diagnosis.</div>")

output_file.write("<li>The check makes sure that the patients has gotten the necessary examinations according to their diagnosis</li>")
output_file.write("<li>AxSpA patient needs to have an MRI of the SI-joints</li>")            
output_file.write("<li>PsA patients needs to have an MRI of the SI-joins and/or of the spine (cervical, lumbar and thoracic)</li>")            

###########################################################################################
### checking whether patient ID's from the metadata file has the required clinical data ###
###########################################################################################
print("Comparing metadata patients to clinical data on patient- and visit-level")
output_file.write("<h2><div style='text-align:center'>#11 Necessary clinical data for the patients.</div></h2><br />")            

metadata_pat=np.unique(excel_metadata.patient_id)                  
no_clin_pat=[]
no_clin_vis=[]
no_clin_all=[]

if type(excel_clinical)==dict:
    pat_pat=np.unique(excel_clinical["pat"].patient_id)
    if "vis" in excel_clinical:
        vis_pat=np.unique(excel_clinical["vis"].patient_id)
    else:
        vis_pat=[]
    for x in metadata_pat:
        if "{" not in x:
            if x not in pat_pat and x in vis_pat:
                no_clin_pat.append(x)
            elif x not in vis_pat and x in pat_pat:
                no_clin_vis.append(x)
            elif x not in pat_pat and x not in vis_pat: 
                no_clin_all.append(x)
    # evaluate clinical data on patient level
    if len(no_clin_pat)!=0:
        for x in no_clin_pat:
            output_file.write("<div style='text-align:center'>" + str(x) + " lacks clinical data on patient level.")
        output_file.write("<br /><div style='text-align:center'><u>Total number of patients without clinical data on patient level: " + str(len(no_clin_pat)) + " </div></u><br />")
    else:
        output_file.write("<br /><div style='text-align:center'><u> All patients with metadata also have clinical data on patient level. </div></u><br />")
    # evaluate clinical data on visit level
    if len(no_clin_vis)!=0:
        if len(vis_pat)==0:
            output_file.write("<br /><div style='text-align:center'><u> No Clinical Visit Data were delivered </div></u><br />")
        else:
            for x in no_clin_vis:
                output_file.write("<div style='text-align:center'>" + str(x) + " lacks clinical data on visit level.")
            output_file.write("<br /><div style='text-align:center'><u>Total number of patients without clinical data on visit level: " + str(len(no_clin_vis)) + " </div></u><br />")
    else:
        output_file.write("<br /><div style='text-align:center'><u> All patients with metadata also have clinical data on visit level. </div></u><br />")
    # evaluate clinical data on both patient- and visit level
    if len(no_clin_all)!=0:
        for x in no_clin_all:
            output_file.write("<div style='text-align:center'>" + str(x) + " lacks clinical data on both patient- and visit level.")
        output_file.write("<br /><div style='text-align:center'><u>Total number of patients without clinical data on both patient- and visit level: " + str(len(no_clin_all)) + " </div></u><br />")
    if len(no_clin_pat)==len(no_clin_vis)==len(no_clin_all)==0:
        output_file.write("<div style='text-align:center'>All patients with image metadata does also have clinical data on patient- and visit-level.")
    
else:
    output_file.write("<div style='text-align:center'>No clinical data present.")


#################################################################################################
### checking whether patient ID's from the metadata file has clinical data on treatment level ###
#################################################################################################
print("Comparing metadata patients to clinical data on treatment level")
output_file.write("<h2><div style='text-align:center'>#12 Summary of patients without clinical data on treatment level.</div></h2><br />")            

metadata_pat=np.unique(excel_metadata.patient_id)                  
no_clin_med=[]

if type(excel_clinical)==dict:
    med_pat=np.unique(excel_clinical["med"].patient_id)
    for x in metadata_pat:
        if x not in med_pat and "{" not in x:
            no_clin_med.append(x)

    if len(no_clin_med)!=0:
        for x in no_clin_med:
            output_file.write("<div style='text-align:center'>" + str(x) + " lacks clinical data on treatment level.")
        output_file.write("<br /><div style='text-align:center'><u>Total number of patients without clinical data on treatment level: " + str(len(no_clin_med)) + " </div></u><br />")
    else:
        output_file.write("<br /><div style='text-align:center'><u> All patients with metadata also have clinical data on treatment level. </div></u><br />")
else:
    output_file.write("<div style='text-align:center'>No clinical data present.")

#################################################################
### counting AxSpA and PsA patients, examinations, and images ###
#################################################################
print("Processing patients, examiantions and images per diagnosis group")
output_file.write("<h2><div style='text-align:center'>#13 Number of Patients, Examinations and Images per Diagnosis group</div></h2><br />")            

patient_archieve_axspa=[]
patient_archieve_psa=[]
patient_archieve_other=[]
ex_archieve_axspa=[]
ex_archieve_psa=[]
ex_archieve_other=[]
for x in range(len(excel_metadata)):
    pat=[excel_metadata.patient_id[x],excel_metadata.diagnosis_group[x]] # patient level diagnosis
    ex=[excel_metadata.patient_id_abcde[x],excel_metadata.diagnosis_group[x]] # examination level diagnosis
    
    # fundamentally, this variable needs to be written as a string. 
    if type(excel_metadata.diagnosis_group[x])==str:
        #gathering only AxSpA ID's
        if excel_metadata.diagnosis_group[x].lower()=="axspa":
            ex_archieve_axspa.append(ex)
            if pat not in patient_archieve_axspa:
                patient_archieve_axspa.append(pat)
    
        #gathering only PsA ID's
        elif excel_metadata.diagnosis_group[x].lower()=="psa":
            ex_archieve_psa.append(ex)
            if pat not in patient_archieve_psa:
                patient_archieve_psa.append(pat)
    
        #gathering ID's on other diagnosis groups
        elif "{" not in excel_metadata.diagnosis_group[x] and "}" not in excel_metadata.diagnosis_group[x]:
            ex_archieve_other.append(ex)
            if pat not in patient_archieve_other:
                patient_archieve_other.append(pat)
    
    # if the entry is not even a string, it cannot be registered as a diagnosis group
    elif "{" not in excel_metadata.diagnosis_group[x] and "}" not in excel_metadata.diagnosis_group[x]:
        ex_archieve_other.append(ex)
        if pat not in patient_archieve_other:
            patient_archieve_other.append(pat)

# counting the number of images per diagnosis group            
image_axspa_count=0            
image_psa_count=0            
image_other_count=0
init_excel_diagnosis_metadata=excel_metadata.loc[:,["patient_id","diagnosis_group"]].values.tolist()[1:]

# init_excel_diagnosis_metadata has alot of duplicate lines, which we need to filter away
excel_diagnosis_metadata=[]
for line in init_excel_diagnosis_metadata:
    if line not in excel_diagnosis_metadata:
        excel_diagnosis_metadata.append(line)

# use the patient IDs as a bridge to count the number of images per diagnosis group
for key in image_counting:
    for line in excel_diagnosis_metadata:
        if line[0]==key:
            if type(line[1])==str and line[1].lower()=="axspa":
                image_axspa_count+=image_counting[key]
            elif type(line[1])==str and line[1].lower()=="psa":
                image_psa_count+=image_counting[key]
            else:
                image_other_count+=image_counting[key]

# calculate the sums 
image_total_count=image_axspa_count+image_psa_count+image_other_count
ex_total=len(ex_archieve_axspa)+len(ex_archieve_psa)+len(ex_archieve_other)
pat_total=len(patient_archieve_axspa)+len(patient_archieve_psa)+len(patient_archieve_other)

# make the dataframe for the table
diagnosis_data_header=["AxSpA","PsA","Other","SUM"]                
diagnosis_data_rows=["Patients","Examinations","Images"]
diagnosis_data=[[len(patient_archieve_axspa),len(patient_archieve_psa),len(patient_archieve_other),pat_total],
                [len(ex_archieve_axspa),len(ex_archieve_psa),len(ex_archieve_other),ex_total],
                [image_axspa_count,image_psa_count,image_other_count,image_total_count]]
                
diagnosis_df=pd.DataFrame(diagnosis_data,columns=diagnosis_data_header,index=diagnosis_data_rows)

output_file.write(diagnosis_df.to_html(justify="center"))

output_file.write("<li>Diagnosis grouping for Patients and Examinations has been done solely based on the metadata-file</li>")            
output_file.write("<li>Diagnosis grouping for images has been done using the patient IDs from the images (key='PatientName') as a bridge to the metadata file. 0's can be caused either by lack of images in that diagnosis group or due to incorrect Patient ID's</li>")
output_file.write("<li>Registration of diagnosis groups ignores case-sensitivity. Instances of 'Other' can be caused by misspelling of the diagnosis group, lack of diagnosis group or another diagnosis group being registered. </li>")

#########################################################
### tabel of images per body part per diagnosis group ###
#########################################################
print("Processing body part examined per diagnosis group.")
output_file.write("<h2><div style='text-align:center'>#14 Number of patients per body part per diagosis group</div></h2><br />")    
if "USZ" not in use and "MOTOL" not in use and "SL" not in use:                
    diagnosis_metadata=excel_metadata.loc[:,["patient_id",
                                             "diagnosis_group",
                                             "xray_sij",
                                             "xray_cervical_spine",
                                             "xray_lumbar_spine",
                                             "mri_sij",
                                             "mri_sij_STIR_semi_coronal",
                                             "mri_sij_T1_semi_coronal",
                                             "mri_cervical_spine",
                                             "mri_thoracic_spine",
                                             "mri_lumbar_spine"]].values.tolist()
else:
    diagnosis_metadata=excel_metadata.loc[:,["patient_id",
                                             "diagnosis_group",
                                             "xray_sij",
                                             "xray_cervical_spine",
                                             "xray_lumbar_spine",
                                             "mri_sij",
                                             "mri_cervical_spine",
                                             "mri_thoracic_spine",
                                             "mri_lumbar_spine"]].values.tolist()
axspa_pat_dict={"SIJ":0,
                  "Cervical Spine":0,
                  "Lumbar Spine":0,
                  "Thoracic Spine":0,
                  "SIJ STIR semi-coronal":0,
                  "SIJ T1 semi-coronal":0,
                  "Spine":0}                  
psa_pat_dict={"SIJ":0,
                  "Cervical Spine":0,
                  "Lumbar Spine":0,
                  "Thoracic Spine":0,
                  "SIJ STIR semi-coronal":0,
                  "SIJ T1 semi-coronal":0,
                  "Spine":0}                  
# get a list of unique patient IDs
patients=np.unique(excel_metadata.patient_id).tolist()

# sorting patient counts per body part per diagnosis group
for name in patients:  
    SIJ_flag="down"
    cervical_flag="down"
    lumbar_flag="down"
    thoracic_flag="down"
    stir_flag="down"
    T1_flag="down"
    spine_flag="down"
    if "USZ" not in use and "MOTOL" not in use and "SL" not in use:
        for line in diagnosis_metadata:
            if line[0]==name and "{" not in line[0]:
                #print(line)
                # in case the patient has AxSpA
                if "axspa" in str(line[1]).lower() or "ax" in str(line[1]).lower():
                    # if the patient has registered SIJ-images
                    if 1 in [int_check(line[2]),int_check(line[5])] and SIJ_flag=="down":
                        axspa_pat_dict["SIJ"]+=1
                        SIJ_flag="up"
                        #   if the patient has registered cervical spine images
                    if 1 in [int_check(line[3]),int_check(line[8])] and cervical_flag=="down":
                        axspa_pat_dict["Cervical Spine"]+=1
                        cervical_flag="up""sl52",
                    # if the patient has registered lumbar spine images
                    if 1 in [int_check(line[4]),int_check(line[10])] and lumbar_flag=="down":
                        axspa_pat_dict["Lumbar Spine"]+=1
                        lumbar_flag="up"
                    # if the patient has registered thoracic spine images
                    if int_check(line[9])==1 and thoracic_flag=="down":
                        axspa_pat_dict["Thoracic Spine"]+=1
                        thoracic_flag="up"
                    # if the pattient has other SIJ images
                    if int_check(line[6])==1 and stir_flag=="down":
                        axspa_pat_dict["SIJ STIR semi-coronal"]+=1
                        stir_flag="up"
                    if int_check(line[7])==1 and T1_flag=="down":
                        axspa_pat_dict["SIJ T1 semi-coronal"]+=1
                        T1_flag="up"
                    if int_check(line[3])==int_check(line[4])==1 and spine_flag=="down":
                        axspa_pat_dict["Spine"]+=1
                        spine_flag="up"
                    if int_check(line[8])==int_check(line[9])==int_check(line[10])==1 and spine_flag=="down":
                        axspa_pat_dict["Spine"]+=1
                        spine_flag="up"
                    # in case the patient has PsA
                elif "psa" in str(line[1]).lower():
                    # if the patient has registered SIJ-images
                    if 1 in [int_check(line[2]),int_check(line[5])] and SIJ_flag=="down":
                        psa_pat_dict["SIJ"]+=1
                        SIJ_flag="up"
                    # if the patient has registered cervical spine images
                    if 1 in [int_check(line[3]),int_check(line[8])] and cervical_flag=="down":
                        psa_pat_dict["Cervical Spine"]+=1
                        cervical_flag="up"
                    # if the patient has registered lumbar spine images
                    if 1 in [int_check(line[4]),int_check(line[10])] and lumbar_flag=="down":
                        psa_pat_dict["Lumbar Spine"]+=1
                        lumbar_flag="up"
                    # if the patient has registered thoracic spine images
                    if int_check(line[9])==1 and thoracic_flag=="down":
                        psa_pat_dict["Thoracic Spine"]+=1
                        thoracic_flag="up"
                    # if the pattient has other SIJ images
                    if int_check(line[6])==1 and stir_flag=="down":
                        psa_pat_dict["SIJ STIR semi-coronal"]+=1
                        stir_flag="up"
                    if int_check(line[7])==1 and T1_flag=="down":
                        psa_pat_dict["SIJ T1 semi-coronal"]+=1
                        T1_flag="up"
                    if int_check(line[3])==int_check(line[4])==1 and spine_flag=="down":
                        psa_pat_dict["Spine"]+=1
                        spine_flag="up"
                    if int_check(line[8])==int_check(line[9])==int_check(line[10])==1 and spine_flag=="down":
                        psa_pat_dict["Spine"]+=1
                        spine_flag="up"
    else:
        for line in diagnosis_metadata:
            if line[0]==name and "{" not in line[0]:
                #print(line)
                # in case the patient has AxSpA
                if "axspa" in str(line[1]).lower() or "ax" in str(line[1]).lower():
                    # if the patient has registered SIJ-images
                    if 1 in [int_check(line[2]),int_check(line[5])] and SIJ_flag=="down":
                        axspa_pat_dict["SIJ"]+=1
                        SIJ_flag="up"
                        #   if the patient has registered cervical spine images
                    if 1 in [int_check(line[3]),int_check(line[6])] and cervical_flag=="down":
                        axspa_pat_dict["Cervical Spine"]+=1
                        cervical_flag="up"
                    # if the patient has registered lumbar spine images
                    if 1 in [int_check(line[4]),int_check(line[8])] and lumbar_flag=="down":
                        axspa_pat_dict["Lumbar Spine"]+=1
                        lumbar_flag="up"
                    # if the patient has registered thoracic spine images
                    if int_check(line[7])==1 and thoracic_flag=="down":
                        axspa_pat_dict["Thoracic Spine"]+=1
                        thoracic_flag="up"
                    if int_check(line[3])==int_check(line[4])==1 and spine_flag=="down":
                        axspa_pat_dict["Spine"]+=1
                        spine_flag="up"
                    if int_check(line[6])==int_check(line[7])==int_check(line[8])==1 and spine_flag=="down":
                        axspa_pat_dict["Spine"]+=1
                        spine_flag="up"
                    # in case the patient has PsA
                elif "psa" in str(line[1]).lower():
                    # if the patient has registered SIJ-images
                    if 1 in [int_check(line[2]),int_check(line[5])] and SIJ_flag=="down":
                        psa_pat_dict["SIJ"]+=1
                        SIJ_flag="up"
                    # if the patient has registered cervical spine images
                    if 1 in [int_check(line[3]),int_check(line[6])] and cervical_flag=="down":
                        psa_pat_dict["Cervical Spine"]+=1
                        cervical_flag="up"
                    # if the patient has registered lumbar spine images
                    if 1 in [int_check(line[4]),int_check(line[8])] and lumbar_flag=="down":
                        psa_pat_dict["Lumbar Spine"]+=1
                        lumbar_flag="up"
                    # if the patient has registered thoracic spine images
                    if int_check(line[7])==1 and thoracic_flag=="down":
                        psa_pat_dict["Thoracic Spine"]+=1
                        thoracic_flag="up"
                    # if the pattient has other SIJ images
                    if int_check(line[3])==int_check(line[4])==1 and spine_flag=="down":
                        psa_pat_dict["Spine"]+=1
                        spine_flag="up"
                    if int_check(line[6])==int_check(line[7])==int_check(line[8])==1 and spine_flag=="down":
                        psa_pat_dict["Spine"]+=1
                        spine_flag="up"
# make the header and rows for the table
diagnosis_data_header=["AxSpA","PsA","SUM"]  
diagnosis_data_rows=["SIJ",
                     "Cervical Spine",
                     "Lumbar Spine",
                     "Thoracic Spine",
                     "SIJ STIR semi-coronal",
                     "SIJ T1 semi-coronal",
                     "Spine"]                  
diagnosis_data=[[axspa_pat_dict["SIJ"],psa_pat_dict["SIJ"],axspa_pat_dict["SIJ"]+psa_pat_dict["SIJ"]],
                [axspa_pat_dict["Cervical Spine"],psa_pat_dict["Cervical Spine"],axspa_pat_dict["Cervical Spine"]+psa_pat_dict["Cervical Spine"]],
                [axspa_pat_dict["Lumbar Spine"],psa_pat_dict["Lumbar Spine"],axspa_pat_dict["Lumbar Spine"]+psa_pat_dict["Lumbar Spine"]],
                [axspa_pat_dict["Thoracic Spine"],psa_pat_dict["Thoracic Spine"],axspa_pat_dict["Thoracic Spine"]+psa_pat_dict["Thoracic Spine"]],
                [axspa_pat_dict["SIJ STIR semi-coronal"],psa_pat_dict["SIJ STIR semi-coronal"],axspa_pat_dict["SIJ STIR semi-coronal"]+psa_pat_dict["SIJ STIR semi-coronal"]],
                [axspa_pat_dict["SIJ T1 semi-coronal"],psa_pat_dict["SIJ T1 semi-coronal"],axspa_pat_dict["SIJ T1 semi-coronal"]+psa_pat_dict["SIJ T1 semi-coronal"]],
                [axspa_pat_dict["Spine"],psa_pat_dict["Spine"],axspa_pat_dict["Spine"]+psa_pat_dict["Spine"]]]    

diagnosis_df=pd.DataFrame(diagnosis_data,columns=diagnosis_data_header,index=diagnosis_data_rows)

output_file.write(diagnosis_df.to_html(justify="center"))

output_file.write("<li>Diagnosis grouping for patients has been done using the metadata file. 0's can be caused either by no patients having that given diagnosis, having the diagnosis group seriously misspelled (as it ignores casing) or no diagnosis group being given for the patient.</li>")
output_file.write("<li>A patient can have more than one body part examined, so a sum of each column would not tell much.</li>")
output_file.write("<li>The sum column sums up the patients from both diagnosis groups that have gotten the same body part examined. None of the numbers in the sum column cells can be higher than the total number of patients in the metadata file.</li>")
output_file.write("<li>The 'Spine'-row is an accumulate check based on either a X-ray examination of the Cervical and Lumbar spine or a MRI examination of the Cervical, Lumbar and Thoracic spine. If both or all checks for the individual examination type is positive, it will be checked as an examination of the entire spine as well as the individual spinal parts</li>")

#####################################################################################################    
### schematic for MRI- and X-ray examinations, as well as images sorted on what has been examined ###    
#####################################################################################################    
print("Processing MRI- and X-ray examinations and images.")
output_file.write("<h2><div style='text-align:center'>#15 Overview of Image Type and Examined Body Part for Examinations and Images</div></h2><br />")    
if "USZ" not in use and "MOTOL" not in use and "SL" not in use:
    EXCEL_BI_metadata=excel_metadata.loc[:,["xray_sij",
                                            "xray_cervical_spine",
                                            "xray_lumbar_spine",
                                            "mri_sij",
                                            "mri_sij_STIR_semi_coronal",
                                            "mri_sij_T1_semi_coronal",
                                            "mri_cervical_spine",
                                            "mri_thoracic_spine",
                                            "mri_lumbar_spine"]].values.tolist()[1:]
    BI_header={"xray_sij":0,
           "xray_cervical_spine":0,
           "xray_lumbar_spine":0,
           "mri_sij":0,
           "mri_sij_STIR_semi_coronal":0,
           "mri_sij_T1_semi_coronal":0,
           "mri_cervical_spine":0,
           "mri_thoracic_spine":0,
           "mri_lumbar_spine":0}
    BI_names=["xray_sij",
              "xray_cervical_spine",
              "xray_lumbar_spine",
              "mri_sij",
              "mri_sij_STIR_semi_coronal",
              "mri_sij_T1_semi_coronal",
              "mri_cervical_spine",
              "mri_thoracic_spine",
              "mri_lumbar_spine"]
else:
    EXCEL_BI_metadata=excel_metadata.loc[:,["xray_sij",
                                            "xray_cervical_spine",
                                            "xray_lumbar_spine",
                                            "mri_sij",
                                            "mri_cervical_spine",
                                            "mri_thoracic_spine",
                                            "mri_lumbar_spine"]].values.tolist()[1:]
    BI_header={"xray_sij":0,
           "xray_cervical_spine":0,
           "xray_lumbar_spine":0,
           "mri_sij":0,
           "mri_cervical_spine":0,
           "mri_thoracic_spine":0,
           "mri_lumbar_spine":0}
    BI_names=["xray_sij",
              "xray_cervical_spine",
              "xray_lumbar_spine",
              "mri_sij",
              "mri_cervical_spine",
              "mri_thoracic_spine",
              "mri_lumbar_spine"]


# Gathers the number of examinations of the various types from the metadata file
for i in range(len(EXCEL_BI_metadata)):
    for j in range(len(BI_names)):
        if type(EXCEL_BI_metadata[i][j])!=float and int(EXCEL_BI_metadata[i][j])==1:
            BI_header[BI_names[j]]+=int(EXCEL_BI_metadata[i][j])

# calculates the whole spine counts
BI_header["xray_spine"]=0
BI_header["mri_spine"]=0
BI_names.append("xray_spine")
BI_names.append("mri_spine")

if "USZ" not in use and "MOTOL" not in use and "SL" not in use:
    for line in EXCEL_BI_metadata:
        if int_check(line[1])==int_check(line[2])==1:
            BI_header["xray_spine"]+=1
        if int_check(line[6])==int_check(line[7])==int_check(line[8])==1:
            BI_header["mri_spine"]+=1
else:
    for line in EXCEL_BI_metadata:
        if int_check(line[1])==int_check(line[2])==1:
            BI_header["xray_spine"]+=1
        if int_check(line[4])==int_check(line[5])==int_check(line[6])==1:
            BI_header["mri_spine"]+=1

if "USZ" not in use and "MOTOL" not in use and "SL" not in use:            
    examination_data_header=["X-ray examinations","MRI examinations","SUM"] 
    examination_data_row=["SIJ","Cervical spine","Lumbar spine","SIJ STIR semi coronal","SIJ T1 semi coronal","Thoracic spine","SUM","Spine"]
                         
    X_sum=BI_header["xray_sij"]+BI_header["xray_cervical_spine"]+BI_header["xray_lumbar_spine"]
    MRI_sum=BI_header["mri_cervical_spine"]+BI_header["mri_lumbar_spine"]+BI_header["mri_sij_STIR_semi_coronal"]+BI_header["mri_sij_T1_semi_coronal"]
    TOTAL_SUM=X_sum+MRI_sum
    examination_data=[[BI_header["xray_sij"],BI_header["mri_sij"],BI_header["xray_sij"] + BI_header["mri_sij"]],
                      [BI_header["xray_cervical_spine"],BI_header["mri_cervical_spine"],BI_header["xray_cervical_spine"] + BI_header["mri_cervical_spine"]],
                      [BI_header["xray_lumbar_spine"],BI_header["mri_lumbar_spine"],BI_header["xray_lumbar_spine"] + BI_header["mri_lumbar_spine"]],
                      ["-",BI_header["mri_sij_STIR_semi_coronal"],BI_header["mri_sij_STIR_semi_coronal"]],
                      ["-",BI_header["mri_sij_T1_semi_coronal"],BI_header["mri_sij_T1_semi_coronal"]],
                      ["-",BI_header["mri_thoracic_spine"],BI_header["mri_thoracic_spine"]],
                      [X_sum,MRI_sum,TOTAL_SUM],
                      [BI_header["xray_spine"],BI_header["mri_spine"],BI_header["xray_spine"] + BI_header["mri_spine"]]]
else:
    examination_data_header=["X-ray examinations","MRI examinations","SUM"] 
    examination_data_row=["SIJ","Cervical spine","Lumbar spine","Thoracic spine","SUM","Spine"]
                         
    X_sum=BI_header["xray_sij"]+BI_header["xray_cervical_spine"]+BI_header["xray_lumbar_spine"]
    MRI_sum=BI_header["mri_cervical_spine"]+BI_header["mri_lumbar_spine"]
    TOTAL_SUM=X_sum+MRI_sum
    examination_data=[[BI_header["xray_sij"],BI_header["mri_sij"],BI_header["xray_sij"] + BI_header["mri_sij"]],
                      [BI_header["xray_cervical_spine"],BI_header["mri_cervical_spine"],BI_header["xray_cervical_spine"] + BI_header["mri_cervical_spine"]],
                      [BI_header["xray_lumbar_spine"],BI_header["mri_lumbar_spine"],BI_header["xray_lumbar_spine"] + BI_header["mri_lumbar_spine"]],
                      ["-",BI_header["mri_thoracic_spine"],BI_header["mri_thoracic_spine"]],
                      [X_sum,MRI_sum,TOTAL_SUM],
                      [BI_header["xray_spine"],BI_header["mri_spine"],BI_header["xray_spine"] + BI_header["mri_spine"]]]             

ex_df=pd.DataFrame(examination_data,columns=examination_data_header,index=examination_data_row)

output_file.write(ex_df.to_html(justify="center"))
output_file.write("<li>the SUM-column only sums over the examinations and not the images</li>")
output_file.write("<li>the # Images-column does not discriminate between X-ray and MRI images</li>")
output_file.write("<li>the # Images-column uses the key 'BodypartExamined' to sort them based on keywords seen in the given key across images.</li>")                      
output_file.write("<li>The 'Spine'-row is an accumulate check based on either a X-ray examination of the Cervical and Lumbar spine or a MRI examination of the Cervical, Lumbar and Thoracic spine. If both or all checks for the individual examination type is positive, it will be checked as an examination of the entire spine as well as the individual spinal parts</li>")
    
############################################################
### Graphic overview of the number of images per patient ###
############################################################
print("Processing images summary in graphic form.")
output_file.write("<h2><div style='text-align:center'>#16 Graphic Summary of the Images</div></h2>")    

# making strings with the patient ID's and image counts for the patients        
Patients=sorted(image_counting.keys())
img_count=[image_counting[x] for x in Patients] 

# calculates quantiles for the image counts
QUANTILES=quantile(sorted(img_count))

# adjust graph-width according to number of patients
width=len(Patients)*0.25

# here we make the graph for image summary
plt.figure(figsize=(width,6)) # image size. 
plt.xticks(ticks=range(len(Patients)),labels=Patients,rotation=90) # adds the patient ID's to the x-axis vertically for ease of reading
plt.bar(Patients,height=img_count) # the barplot
addlabels(Patients,img_count) # adds the values of each image count to the bars 
plt.xlabel("Patient ID") 
plt.ylabel("Number of Images")
# adds minor statistics to the graph as additional information
info_text='\n'.join(["".join(("Total # of images: ",str(in_total(image_counting)))),
                             "".join(("Average: ",str(ave(image_counting)))),
                             "".join(("std: ",str(std(image_counting)))),
                             "".join(("1st quantile: ",str(QUANTILES[0]))),
                             "".join(("median: ",str(QUANTILES[1]))),
                             "".join(("3rd quantile: ",str(QUANTILES[2]))),
                             "".join(("Max.: ",str(max(img_count)))),
                             "".join(("Min.: ",str(min(img_count))))])

# adjust placement of the statistics text-box based on the width of the plot
if width<10:
    plt.figtext(0.95,0.25,info_text,fontsize='large',bbox=dict(boxstyle='round',facecolor='wheat',alpha=0.5))    
else:
    plt.figtext(0.135,0.6,info_text,fontsize='large',bbox=dict(boxstyle='round',facecolor='wheat',alpha=0.5))    

# converts the graph as an image to binary in order to insert it into the report
svg_file=BytesIO() 
plt.savefig(svg_file,format='svg') #saves the graph in binary
svg_file.seek(0)
svg_data=svg_file.getvalue().decode() # retrieve the saved data
svg_data='<svg' + svg_data.split('<svg')[1] #strip the xml header to make sure the image is showing

output_file.write("<li>The number of images for each patient is written on the top of each bar</li>")
output_file.write("<li>The Patient ID's are taken from the images and hence disregards the metadata file entirely</li>")
output_file.write("<li>Lack of images can be due to missing Patient ID for the images. </li>")

output_file.write(svg_data)


output_file.close()
sys.stdout.write("The report for " + use + " is ready as " + output_file_name)

        