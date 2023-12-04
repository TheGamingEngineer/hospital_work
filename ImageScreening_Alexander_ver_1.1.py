import re 
import pydicom
import os
import numpy as np
import pandas as pd
import sys



## Functions ##
#def collect_img_metadata(path, national_code):
def collect_img_metadata(path,national_code):
    output_file=open(national_code + "_list_of_IDs_and_dates.txt","w")
    ex_ID_images = []
    image_dates = []
    missing_image_dates=[] #for gathering files with missing series-, acquisition-, and study dates
    wrong_name_format=[] #for gathering files with incorrect name format
    missing_meta=[] #for gathering files with missing metadata
    PatID_issue=[] # patient ID issues in directory path
    ExID_issue=[] # examination ID issues in directory path
    names_view=[]
    IDdate_view=[]
    file_count=0  # for assessing the percentage of images with issues
    #single_count=0
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
                    Pat_ID=ds.PatientName
                    if Pat_ID!="":
                        if not re.match('ch[0-9]{4}',str(Pat_ID)) and not re.match('slo[0-9]+',str(Pat_ID)):
                            Pat_string=file + " (" + str(Pat_ID) + ")"
                            PatID_issue.append(Pat_string)
                    
                    # Get examination ID
                    ex_ID = str(ds.PatientID)
                    
                    if ex_ID!="":
                        if not re.match('ch[0-9]{4}[A-Z,a-z]',str(ex_ID)) and not re.match('slo[0-9]+[A-Z,a-z]',str(ex_ID)):
                            Ex_string = file + " (" + str(ex_ID) + ")"
                            ExID_issue.append(Ex_string)
                    
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
                        image_dates.append(str(pd.to_datetime(date)))
                    else:
                        missing_image_dates.append(root + "/" + file)
                        
                    if Pat_ID!="" and ex_ID!="" and date!="":
                        IDdate_view.append([Pat_ID,ex_ID,str(pd.to_datetime(date))])
                    
                    """
                    # count the number of examinations with only one scanning
                    if len(files)==1:
                        single_count+=1
                    """
                    
                    """
                    # for checking the ID's and date of certain patiets/examinations
                    if ex_ID in (): # write in the parenthesis with the examination ID's that you want to check
                        output_file.write("patient_ID" + '\t' + "examination_ID" + '\t' + "date" + '\n')
                    """
                    output_file.write(str(Pat_ID) + '\t' + str(ex_ID) + '\t' + str(date) + '\n')
                elif len(extension) == 0 and file[0] != '.' and file!="DICOMDIR": #this is done to also be able to read images with no extension (CZ)
                    file_count+=1

                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                        
                    except:
                        missing_meta.append(root + "/" + file)
                        next

                    #sys.exit()
                    if national_code=="CZ":
                        Pat_ID=str(ds.PatientName).split('^')[0]
                    else:
                        Pat_ID=str(ds.PatientName)
                    
                    if Pat_ID!="":
                        if not re.match('ATTAS[-,_][0-9]{4}',Pat_ID) and not re.match('ATTAS[-,_][0-9]{5}',Pat_ID):
                            Pat_string=file + " (" + str(Pat_ID) + ")"
                            PatID_issue.append(Pat_string)
                        
                    # Get examination ID
                    ex_ID = ds.PatientID
                    
                    if ex_ID!="":
                        if not re.search('ATTAS[-,_][0-9]{4}[A-Z,a-z]',ex_ID) and not re.search('ATTAS[-,_][0-9]{5}[A-Z,a-z]',ex_ID):
                            Ex_string = file + " (" + str(ex_ID) + ")"
                            ExID_issue.append(Ex_string)
                            
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
                        image_dates.append(str(pd.to_datetime(date)))
                    else:
                        missing_image_dates.append(root + "/" + file)
                    if Pat_ID!="" and ex_ID!="" and date!="":
                        IDdate_view.append([Pat_ID,ex_ID,str(pd.to_datetime(date))])
                    """
                    # count the number of examinations with only one scanning
                    if len(files)==1:
                        single_count+=1
                    """
                    """
                    # for checking the ID's and date of certain patiets/examinations
                    if ex_ID in (): # write in the parenthesis with the examination ID's that you want to check
                        output_file.write("patient_ID" + '\t' + "examination_ID" + '\t' + "date" + '\n')
                    """
                    output_file.write(Pat_ID + '\t' + ex_ID + '\t' + date + '\n')
                # do screening for dicom tags (Simon has another script for checking patient sensitive information)

                #check image date - it must also be present for this project
                #acquisition_date = series_date = study_date, these three variables should be the same. We only need information
                #from one of them to know the image date, so it is fine is only one variable is available and the others have missing values
                
    return ex_ID_images, image_dates, missing_image_dates, file_count, wrong_name_format, missing_meta, PatID_issue, ExID_issue, IDdate_view

use = "IS";
############################################
### Read image metadata from Dicom files ###
############################################
if(use=="CH") : 
    images_root_path = "/home/alexanderandersen/2_wave/images/test/" #pointing path where images are stored (both XRay and MR)
elif use=="CZ" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/CZ/corrected part 3/" #pointing path where images are stored (both XRay and MR)
elif use=="SI" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/SI/" #pointing path where images are stored (both XRay and MR)
elif use=="IS" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/IS/" #pointing path where images are stored (both XRay and MR

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
missing_dates_list_unabrigded=ex_ID_image_dates_images_list[2]

file_amount=ex_ID_image_dates_images_list[3] # get the number of parsed files

name_issue=ex_ID_image_dates_images_list[4] # get the unique files that don't have the right naming format.
name_issue_unabrigded=ex_ID_image_dates_images_list[4]

no_metadata=ex_ID_image_dates_images_list[5] # get the uniqie files that don't have metadata to them
no_metadata_unabrigded=ex_ID_image_dates_images_list[5]

PatID_dir_issue=ex_ID_image_dates_images_list[6] # 

ExID_dir_issue=ex_ID_image_dates_images_list[7] #

IDdate=ex_ID_image_dates_images_list[8] #
sys.exit()
############################################
### Read image metadata from excel files ###
############################################

if(use=="CH") : 
    excel_metadata_CH = pd.read_csv("/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_Exer_20220324_MAIN.csv", sep=";") #load excel file
    excel_metadata_CH = pd.read_csv("/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_Insel_20220616.csv", sep=",") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    
    img_metadata_image_date_list=[]
    for x in excel_metadata_CH.image_date[1:]:
        if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
            img_metadata_image_date_list.append(str(pd.to_datetime(x)))
            
    name="/home/alexanderandersen/2_wave/1_skvulp/metadata/CH/xray_mri_metadata_second_wave_Exer_20220324_AKBA.xls" # saves name for file naming 
    excel_metadata=excel_metadata_CH

elif use=="CZ" : 
    excel_metadata_CZ = pd.read_excel("/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospa_imaging_second_wave_FNHK.xlsx") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
    
    img_metadata_image_date_list=[]
    for x in excel_metadata_CZ.image_date[1:]:
        if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
            img_metadata_image_date_list.append(str(pd.to_datetime(x)))
    
    name="/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospa_imaging_second_wave_part2_AKBA.xlsx.xlsx" #saves name for file naming 
    excel_metadata=excel_metadata_CZ

elif use=="SI" : 
    excel_metadata_SI = pd.read_excel("/home/alexanderandersen/2_wave/metadata/SI/Template_image_metadata_eurospa_imaging_second_wave_SI_AKBA.xlsx") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_SI.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    img_metadata_image_date_list = np.unique(excel_metadata_SI.image_date[1:]) #generate a list of image dates that exist in the metadata excel file
    name="/home/alexanderandersen/2_wave/metadata/SI/" # saves name for file naming 
    excel_metadata=excel_metadata_SI
    
elif use=="IS" : 
    excel_metadata_IS = pd.read_csv("/home/alexanderandersen/2_wave/metadata/IS/", sep=",") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_IS.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    img_metadata_image_date_list = np.unique(excel_metadata_IS.image_date[1:]) #generate a list of image dates that exist in the metadata excel file
    name="/home/alexanderandersen/2_wave/metadata/IS/" # saves name for file naming 
    excel_metadata=excel_metadata_IS    
#img_metadata_image_date_list = pd.to_datetime(img_metadata_image_date_list.astype(str),dayfirst=True).values #change dates to correct format 
#img_metadata_image_date_list = pd.to_datetime(img_metadata_image_date_list.astype(int).astype(str))

########################################################################
### Print inconsistencies between image metadata and excel metadata  ###
########################################################################
"""
#find what image dates are in the DICOM metadata but not in the image excel metadata
#this can be because the image dates written in the excel file are wrong, or a wrong image was uploaded that does not
#correspond to the one describe in the excel file
in_dicom_not_in_metadata = []
for img_date in image_dates:
    if (not img_date in img_metadata_image_date_list):
        in_dicom_not_in_metadata.append(img_date)

#find what image dates are in the image excel metadata but not in the DICOM metadata
#this most likely occurs if the images were not uploaded in the server, i.e. missing images
in_metadata_not_in_dicom = []
for img_date in img_metadata_image_date_list:
    if (not img_date in image_dates ):
        in_metadata_not_in_dicom.append(img_date)
"""

#find what examination IDs are not in the image excel metadata, but are present in the images
#could be because this patient examination was not included in the excel metadata
in_img_not_in_metadata = []
for ex_ID in ex_ID_images_list:
    if (not ex_ID in img_metadata_ex_ID_list):
        in_img_not_in_metadata.append(ex_ID)

#find what examination IDs are present in the images but not in the image excel metadata
#this most likely occurs if the images were not uploaded in the server, i.e. missing images
in_metadata_not_in_img = []
for ex_ID in img_metadata_ex_ID_list:
    if (not ex_ID in ex_ID_images_list):
        in_metadata_not_in_img.append(ex_ID)


"""
print("Number of images: ", ex_ID_count)
print("Number of images in metadata file: ", len(img_metadata_ex_ID_list))
"""
#########################################
## comparing ID's and date to metadata ##
#########################################


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
    if EXCEL_metadata[x][2]!="{yyyymmdd}": 
        EXCEL_metadata[x][2]=str(pd.to_datetime(EXCEL_metadata[x][2]))
    
"""
num=0
NUM=0
for line in EXCEL_metadata:
    num=0
    for x in line:
        if type(x)==int or type(x)=="datetime.datetime":
            EXCEL_metadata[NUM][num]=str(x)
        elif type(x)==float and not np.isnan(x):
            EXCEL_metadata[NUM][num]=str(int(x))
        num+=1
    NUM+=1
"""

### counting AxSpA and PsA patients and examinations ###
patient_archieve_axspa=[]
patient_archieve_psa=[]
ex_archieve_axspa=[]
ex_archieve_psa=[]
for x in range(len(excel_metadata)):
    pat=[excel_metadata.patient_id[x],excel_metadata.diagnosis_group[x]] # patient level diagnosis
    ex=[excel_metadata.patient_id_abcde[x],excel_metadata.diagnosis_group[x]] # examination level diagnosis
    
    #gathering only AxSpA data
    if excel_metadata.diagnosis_group[x].lower()=="axspa":
        ex_archieve_axspa.append(ex)
        if pat not in patient_archieve_axspa:
            patient_archieve_axspa.append(pat)
    
    #gathering only PsA data
    elif excel_metadata.diagnosis_group[x].lower()=="psa":
        ex_archieve_psa.append(ex)
        if pat not in patient_archieve_psa:
            patient_archieve_psa.append(pat)


#now we run through all of the ID's and dates from the files and compare them to the metadata
IDdate_not_in_metadata=[]
for line in IDdate:
    if line not in EXCEL_metadata:
        IDdate_not_in_metadata.append(line)
        
# and here, we look into if there are any examinations that are recorded in metadata, but are not present in the files.
metadata_not_in_IDdate=[]
for line in EXCEL_metadata:
    if line not in IDdate:
        metadata_not_in_IDdate.append(line)

#########################################
### checking binary data in metadata ####
#########################################
EXCEL_BI_metadata=excel_metadata.loc[:,["patient_id_abcde",
                                        "xray_sij",
                                        "xray_cervical_spine",
                                        "xray_lumbar_spine",
                                        "mri_sij",
                                        "mri_sij_STIR_semi_coronal",
                                        "mri_sij_T1_semi_coronal",
                                        "mri_cervical_spine",
                                        #"mri_cervical_spine_T1",
                                        "mri_thoracic_spine",
                                        #"mri_thoracic_spine_STIR",
                                        #"mri_thoracic_spine_T1",
                                        "mri_lumbar_spine",
                                        #"mri_lumbar_spine_STIR",
                                        #"mri_lumbar_spine_T1",
                                        "patient_has_no_relevant_radiograph",
                                        "patient_has_no_relevant_mri"]].values.tolist()
BI_header=["patient_id_abcde",
           "xray_sij",
           "xray_cervical_spine",
           "xray_lumbar_spine",
           "mri_sij",
           "mri_sij_STIR_semi_coronal",
           "mri_sij_T1_semi_coronal",
           "mri_cervical_spine",
           #"mri_cervical_spine_T1",
           "mri_thoracic_spine",
           #"mri_thoracic_spine_STIR",
           #"mri_thoracic_spine_T1",
           "mri_lumbar_spine",
           #"mri_lumbar_spine_STIR",
           #"mri_lumbar_spine_T1",
           "patient_has_no_relevant_radiograph",
           "patient_has_no_relevant_mri"]

not_bi=[]
num=0
for line in EXCEL_BI_metadata:
    num=0
    for x in line:
        if num>0 and x not in [1,0]:
            not_bi.append([line[0],BI_header[num]])
        num+=1


#########################################
### writing inconsistencies into file ###
#########################################

from datetime import datetime ## call computer date for output-file

### save the national two-letter code for the output-file

output_file_prefix=re.search('/[A-Z]{2}/',name).group(0)[1:3] # saves the national two-letter code as the first two letters of the output-file

times=datetime.now().strftime('%Y%m%d_%H-%M-%S') # saves date of run for file-naming

output_file_name= output_file_prefix + "_image_project_issues_" + times + ".txt" 			# naming the output inconsistency file after the national two-letter code and the time of the run
output_file_summary_name= output_file_prefix + "_image_project_issues_summary_" + times + ".txt"	# naming the summary inconsistency file after the national two letter code and the time of the run
output_file_unique_name= output_file_prefix + "_image_project_issues_unique_cases_" + times + ".txt"	# naming the summary inconsistency file after the national two letter code and the time of the run

output_file=open(output_file_name,"w") # opens the file for writing
summary_file=open(output_file_summary_name,"w") # opens the summary file for writing
unique_file=open(output_file_unique_name,"w")
# write header to file
output_header=["issue","issue_code","value","description"] # makes the header
output_file.write('\t'.join(output_header)+'\n') 

#write header for summary file
summary_header=["type","count","%"]
summary_file.write('\t'.join(summary_header)+'\n')

incon=[in_img_not_in_metadata,
       in_metadata_not_in_img,
       np.unique(missing_dates_list),
       np.unique(no_metadata),
       np.unique(PatID_dir_issue),
       np.unique(ExID_dir_issue),
       IDdate_not_in_metadata,
       metadata_not_in_IDdate,
       not_bi] 	# list of inconsistencies to be written (abrigded)

incon_unabrigded=[in_img_not_in_metadata,
       in_metadata_not_in_img,
       missing_dates_list,
       no_metadata,
       PatID_dir_issue,
       ExID_dir_issue,
       IDdate_not_in_metadata,
       metadata_not_in_IDdate,
       not_bi] 	# list of inconsistencies to be written (unabrigded)

incon_descript=["examination ID found in images, but not in metadata",
		"examination ID found in metadata, but not in images",
		"missing series-,acquisition-, and study dates",
        "missing Dicom metadata",
        "incorrect patient ID in image",
        "incorrect examination ID in image",
        "examination not found in metadata, but found in files",
        "examination not found in files, but found in metadata",
        "non-binary value for binary variable"] 	# inconsistency descriptions



n=0 			#count issue type code
issue_numb=1 		#count number of issues
incon_descript_nr=0 	#provides the issues related to the entry

summ=[]
for line in incon:
    for x in line:
        summ.append(" ".join([str(x),incon_descript[incon_descript_nr]]))
    incon_descript_nr+=1   
    
summ_unique=[]
for x in summ:
    if x not in summ_unique:
        summ_unique.append(x)

incon_descript_nr=0        
for line in incon:
	for x in line:
		issue="issue." + str(issue_numb)
		output_file.write(issue + '\t' + str(n+1) + '\t' + str(x) + '\t' + incon_descript[incon_descript_nr] + '\n')
		issue_numb+=1
	n+=1
	incon_descript_nr+=1		
output_file.close()

count=0
for line in incon_unabrigded:
    issue_entries_nr=len(line)  										# summarizes the number of entries with that specific issue 
    if issue_entries_nr!=0:
        issue_entries_percentage=(len(line)/file_amount)*100							# summarizes the percentage of entries that have this issue
        summary_file.write(incon_descript[count] + '\t' + str(issue_entries_nr) + '\t' + str(round(issue_entries_percentage,3)) + '\n') # writes this summary to file
        print(incon_descript[count], '\t', str(issue_entries_nr), '\t', str(round(issue_entries_percentage,3)))
    count+=1
summary_file.close()
		
for line in summ_unique:
    unique_file.write(line + '\n')
unique_file.close()
print("number of images/files screened: ",file_amount)
print("number of AxSpA patients: ",len(patient_archieve_axspa))
print("number of PsA patients: ",len(patient_archieve_psa))
print("number of AxSpA examinations: ",len(ex_archieve_axspa))
print("number of PsA examinations: ",len(ex_archieve_psa))
###########################################
"""
print("In images, but not in image metadata file")
print(in_img_not_in_metadata)
print("In image metadata file, but not in images")
print(in_metadata_not_in_img)
print("In DICOM metadata file, but not in image metadata")
print(in_dicom_not_in_metadata)
print("In image metadata file, but not in DICOM metadata")
print(in_metadata_not_in_dicom)
"""