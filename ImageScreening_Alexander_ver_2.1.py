import re 
import pydicom
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys  
from datetime import datetime ## call computer date for output-file
from io import BytesIO ## for exporting images into the report


## Functions ##
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
    image_type_counting={"SIJ":0,
                        "Cervical Spine":0,
                        "Lumbar Spine":0,
                        "Thoracic Spine":0,
                        "other":0}
    date_image_counting={}
    
    # modifying pattern recognition for the ID's of each nation
    pat_pattern=''
    ex_pattern=''
    if national_code=="CH":
        pat_pattern='ch[0-9]{4}'
        ex_pattern='ch[0-9]{4}[A-Z,a-z]'
    elif national_code=="CZ":
        pat_pattern='ATTAS[-,_][0-9]{4}'
        ex_pattern='ATTAS[-,_][0-9][A-Z,a-z]'
    elif national_code=="IS":
        pat_pattern=''
        ex_pattern=''
    elif national_code=="SI":
        pat_pattern='slovenia[0-9]{1,3}'
        ex_pattern='slovenia[0-9]{1,3}[a-z]'
    
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
                    
                    #counting patient ID's in images to calculate diagnosis group images
                    if Pat_ID not in image_counting:
                        image_counting[str(Pat_ID)]=1
                    else:
                        image_counting[str(Pat_ID)]+=1
                    if pat_pattern!='':
                        if not re.match(pat_pattern,Pat_ID):
                            PatID_issue.append(root + "/" + file)
                    
                    # Get examination ID
                    ex_ID = str(ds.PatientID)
                    
                    if ex_pattern!='':
                        if not re.match(ex_pattern,ex_ID):
                            ExID_issue.append(root + "/" + file)
                        
                    #counting the what part of the body has been examined
                    if "BodyPartExamined" in ds.dir():
                        if ds.BodyPartExamined in ("LSPINE","LSSPINE","L SPINE"):
                            image_type_counting["Lumbar Spine"]+=1
                        elif ds.BodyPartExamined in ("CSPINE","C SPINE","CSPINE "):
                            image_type_counting["Cervical Spine"]+=1
                        elif ds.BodyPartExamined in ("TSPINE","T SPINE"):
                            image_type_counting["Thoracic Spine"]+=1
                        elif ds.BodyPartExamined in ("SACROILIAC JNTS","SAKROILIAK","COCCYX","PELVIS","MR Ileo-Sacra...","MR Lendenwirb..","MR Becken"):
                            image_type_counting["SIJ"]+=1
                        else:
                            image_type_counting["other"]+=1
                    
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
                    
                    
                elif len(extension) == 0 and file[0] != '.' and file!="DICOMDIR": #this is done to also be able to read images with no extension (CZ)
                    file_count+=1

                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                        
                    except:
                        missing_meta.append(root + "/" + file)
                        next
                    # Czech include ^ as part of their patient ID's in the images
                    if national_code=="CZ":
                        Pat_ID=str(ds.PatientName).split('^')[0]
                    else:
                        Pat_ID=str(ds.PatientName)
                    
                    #counting patient ID's in images to calculate diagnosis group images
                    if Pat_ID not in image_counting:
                        image_counting[str(Pat_ID)]=1
                    else:
                        image_counting[str(Pat_ID)]+=1
                    
                    if pat_pattern!='':
                        if not re.match(pat_pattern,Pat_ID):
                            PatID_issue.append(root + "/" + file)
                    
                    # Get examination ID
                    ex_ID = str(ds.PatientID)
                    
                    if ex_pattern!='':
                        if not re.match(ex_pattern,ex_ID):
                            ExID_issue.append(root + "/" + file)
                    
                    if ex_ID=="":
                        ExID_issue.append(root + "/" + file)
                    # counting what part of the body has been examined
                    if "BodyPartExamined" in ds.dir():
                        if ds.BodyPartExamined in ("LSPINE","LSSPINE","L SPINE"):
                            image_type_counting["Lumbar Spine"]+=1
                        elif ds.BodyPartExamined in ("CSPINE","C SPINE","CSPINE "):
                            image_type_counting["Cervical Spine"]+=1
                        elif ds.BodyPartExamined in ("TSPINE","T SPINE"):
                            image_type_counting["Thoracic Spine"]+=1
                        elif ds.BodyPartExamined in ("SACROILIAC JNTS","SAKROILIAK","COCCYX","PELVIS"):
                            image_type_counting["SIJ"]+=1
                        else:
                            image_type_counting["other"]+=1
                    
                    
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
                        
                    # Gather images over time
                    if date!="":
                        if str(pd.to_datetime(date)) in date_image_counting:
                            date_image_counting[str(pd.to_datetime(date))]+=1
                        else:
                            date_image_counting[str(pd.to_datetime(date))]=1
                    # Gather ID and date combinations
                    if Pat_ID!="" and ex_ID!="" and date!="":
                        IDdate_view.append([Pat_ID,ex_ID,str(pd.to_datetime(date))])


                # do screening for dicom tags (Simon has another script for checking patient sensitive information)

                #check image date - it must also be present for this project
                #acquisition_date = series_date = study_date, these three variables should be the same. We only need information
                #from one of them to know the image date, so it is fine is only one variable is available and the others have missing values
                
    return ex_ID_images, image_dates, missing_image_dates, file_count, wrong_name_format, missing_meta, PatID_issue, ExID_issue, IDdate_view, image_counting, image_type_counting, date_image_counting

use = "SI";

########################################
### Initiate the output report file ####
########################################
print("Initiating Report File.")
times=datetime.now().strftime('%Y%m%d') # saves date of run for file-naming
Times=datetime.now().strftime('%d/%m-%Y') # saves date of run for header-naming

output_file_name= use + "_" + times + ".html" # naming the output inconsistency file after the national two-letter code and the time of the run

output_file=open(output_file_name,"w") # opens the file for writing

# writing the headline of the report
FILE_HEADER="<html>\n<head>\n<title> \n" + output_file_name 
FILE_1ST_HEADER="\ </title>\n</head> <body><h1><div style='text-align:center'> <u>EuroSpA Imaging Report for " 
VARIABLE= use + " (" + Times + ")</u></div><br />"
FILE_2ND_HEADER="<h2><div style='text-align:center'>Screening Results of Images and Metadata-file \n</div></body></html>"

output_file.write(FILE_HEADER + output_file_name + FILE_1ST_HEADER + VARIABLE + FILE_2ND_HEADER) 

output_file.write("<br /><br />")


############################################
### Read image metadata from Dicom files ###
############################################
print("Setting paths to images and metadata-file.")
#get images and metadata from Schweitzerland
if(use=="CH") : 
    # set image directory
    images_root_path = "/home/alexanderandersen/2_wave/images/CH/" #pointing path where images are stored (both XRay and MR)
    
    # set and adjust metadata for reading
    excel_metadata_CH = pd.read_csv("/home/alexanderandersen/2_wave/metadata/CH/xray_mri_metadata_second_wave_Exer_20220324_MAIN.csv", sep=";") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_CH.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    
    img_metadata_image_date_list=[]
    for x in excel_metadata_CH.image_date[1:]:
        if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
            img_metadata_image_date_list.append(str(pd.to_datetime(x)))
            
    name="CH" # saves name for file naming 
    excel_metadata=excel_metadata_CH

#get images and metadata from Czech Republic
elif use=="CZ" : 
    # set image directory
    images_root_path = "/home/alexanderandersen/2_wave/images/CZ/corrected part 3" #pointing path where images are stored (both XRay and MR)
    
    # set and adjust metadata for reading
    excel_metadata_CZ = pd.read_excel("/home/alexanderandersen/2_wave/metadata/CZ/Template_image_metadata_eurospai_imaging_second_wave_part_3_MAIN.xlsx") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_CZ.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    #img_metadata_image_date_list = np.unique(str(excel_metadata_CZ.image_date[1:])) #generate a list of image dates that exist in the metadata excel file
    
    img_metadata_image_date_list=[]
    for x in excel_metadata_CZ.image_date[1:]:
        if str(pd.to_datetime(x)) not in img_metadata_image_date_list:
            img_metadata_image_date_list.append(str(pd.to_datetime(x)))
    
    name="CZ" #saves name for file naming 
    excel_metadata=excel_metadata_CZ

#get images and metadata from Slovenia
elif use=="SI" : 
    # set image directory
    images_root_path = "/home/alexanderandersen/2_wave/images/SI/" #pointing path where images are stored (both XRay and MR)
    
    # set and adjust metadata for reading
    excel_metadata_SI = pd.read_excel("/home/alexanderandersen/2_wave/metadata/SI/Template_image_metadata_eurospa_imaging_second_wave (1).xlsx") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_SI.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    img_metadata_image_date_list = np.unique(excel_metadata_SI.image_date[1:]) #generate a list of image dates that exist in the metadata excel file
    name="/home/alexanderandersen/2_wave/metadata/SI/" # saves name for file naming 
    excel_metadata=excel_metadata_SI
    
#get images and metadata from Iceland    
elif use=="IS" : 
    # set image directory
    images_root_path = "/home/alexanderandersen/2_wave/images/IS/" #pointing path where images are stored (both XRay and MR)
    
    # set and adjust metadata for reading
    excel_metadata_IS = pd.read_csv("/home/alexanderandersen/2_wave/metadata/IS/", sep=",") #load excel file
    img_metadata_ex_ID_list = np.unique(excel_metadata_IS.patient_id_abcde[1:]) #generate a list of patient examination IDs that exist in the metadata excel file
    img_metadata_image_date_list = np.unique(excel_metadata_IS.image_date[1:]) #generate a list of image dates that exist in the metadata excel file
    name="/home/alexanderandersen/2_wave/metadata/IS/" # saves name for file naming 
    excel_metadata=excel_metadata_IS 

###############################################################
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

image_type_counting=ex_ID_image_dates_images_list[10] #directory of what body part the images are taken from

date_image_counting=ex_ID_image_dates_images_list[11] #directory of how many images were taken on which date

####################################################################
### Print Image filenames with missing or incorrect Patient ID's ###
####################################################################
print("Processing images with missing or incorrect patient IDs.")
output_file.write("<h2><div style='text-align:center'>#1 Files with missing or incorrect Patient IDs</div></h2><br />")

                  
if len(missing_PatID_list)==0:
    output_file.write("<div style='text-align:center'>No images miss nor have incorrect Patient IDs.</div><br />")
else:
    for i in range(len(missing_PatID_list)):
        if use in missing_PatID_list[i]:
            output_file.write("<div style='text-align:center'>" + missing_PatID_list[i].split(use)[1]+"</div><br />")
        else:
            output_file.write("<div style='text-align:center'>" + missing_PatID_list[i].split("test/")[1]+"</div><br />")
    output_file.write("<br /><div style='text-align:center'><u>Total number of files with missing or incorrect Patient ID's: "+ str(len(missing_PatID_list)) +"</u></div>")

########################################################################
### Print Image filenames with missing or incorrect Examination ID's ###
########################################################################
print("Processing images with missing or incorrect examination IDs.")
output_file.write("<h2><div style='text-align:center'>#2 Files with missing or incorrect Examination IDs</div></h2><br />")

                  
if len(missing_ExID_list)==0:
    output_file.write("<div style='text-align:center'>No images miss nor have incorrect Examination IDs.</div><br />")
else:
    for i in range(len(missing_ExID_list)):
        if use in missing_PatID_list[i]:
            output_file.write("<div style='text-align:center'>" + missing_ExID_list[i].split(use)[1]+"</div><br />")
        else:
            output_file.write("<div style='text-align:center'>" + missing_ExID_list[i].split("test/")[1]+"</div><br />")
    output_file.write("<br /><div style='text-align:center'><u>Total number of files with missing or incorrect Examination ID's: "+ str(len(missing_ExID_list)) +"</u></div>")

################################################
### Print Image filenames with missing dates ###
################################################
print("Processing images with missing dates.")
output_file.write("<h2><div style='text-align:center'>#3 Files with missing dates</div></h2><br />")

                  
if len(missing_dates_list)==0:
    output_file.write("<div style='text-align:center'>No images miss dates.<br /> Every image has either Series-, Acquisition-, and/or Study dates.</div><br />")
else:
    for i in range(len(missing_dates_list)):
        if use in missing_dates_list[i]:
            output_file.write("<div style='text-align:center'>" + missing_dates_list[i].split(use)[1]+"</div><br />")
        else:
            output_file.write("<div style='text-align:center'>" + missing_dates_list[i].split("test/")[1]+"</div><br />")
    output_file.write("<br /><div style='text-align:center'><u>Total number of files with missing dates: "+ str(len(missing_dates_list)) +"</u></div>")

#######################################################################################
### Print Examination ID inconsistencies between image metadata and excel metadata  ###
#######################################################################################
print("Processing Examination ID inconsistencies")
output_file.write("<h2><div style='text-align:center'>#4 Examination ID inconsistencies between images and metadata</div></h2><br />")            
#find what examination IDs are not in the image excel metadata, but are present in the images
#could be because this patient examination was not included in the excel metadata
in_img_not_in_metadata = []
for ex_ID in ex_ID_images_list:
    if (not ex_ID in img_metadata_ex_ID_list):
        in_img_not_in_metadata.append(ex_ID)
in_img_not_in_metadata=np.unique(in_img_not_in_metadata)
output_file.write("<h3><div style='text-align:center'>Examination ID's not found in Metadata file:</div></h3><br />")
for i in range(0,len(in_img_not_in_metadata),4):
    sub_set=in_img_not_in_metadata[i:i+4]
    output_file.write("<div style='text-align:center'>"+', '.join(str(x) for x in sub_set) + "</div>")          
output_file.write("<br /><div style='text-align:center'><u>Total number of missing IDs: " + str(len(in_img_not_in_metadata)) + "</u></div><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")

#find what examination IDs are present in the images but not in the image excel metadata
#this most likely occurs if the images were not uploaded in the server, i.e. missing images
in_metadata_not_in_img = []
for ex_ID in img_metadata_ex_ID_list:
    if (not ex_ID in ex_ID_images_list):
        in_metadata_not_in_img.append(ex_ID)
in_metadata_not_in_img=np.unique(in_metadata_not_in_img)
output_file.write("<h3><div style='text-align:center'>Examination ID's not found in images:</div></h3><br />")
for i in range(0,len(in_metadata_not_in_img),4):
    sub_set=in_metadata_not_in_img[i:i+4]
    output_file.write("<div style='text-align:center'>" + ', '.join(str(x) for x in sub_set) + "</div>")            
output_file.write("<br /><div style='text-align:center'><u>Total number of missing IDs: " + str(len(in_metadata_not_in_img)) + "</div></u><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")
                  
#########################################
## comparing ID's and date to metadata ##
#########################################
print("Processing ID and date inconsistencies.")
output_file.write("<h2><div style='text-align:center'>#5 ID and date inconsistencies between images and metadata</div></h2><br />")            
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
        EXCEL_metadata[x][2]=str(pd.to_datetime(EXCEL_metadata[x][2]))

#now we run through all of the ID's and dates from the files and compare them to the metadata
IDdate_not_in_metadata=[]
for line in IDdate:
    if line not in EXCEL_metadata and line not in IDdate_not_in_metadata:
        IDdate_not_in_metadata.append(line)
output_file.write("<h3><div style='text-align:center'>ID's and dates not found in Metadata file:</div></h3><br />")
output_file.write("<u><div style='text-align:center'>Patient ID - Examination ID - Date</div></u>")
for i in range(0,len(IDdate_not_in_metadata)):
    sub_set=IDdate_not_in_metadata[i]
    output_file.write("<div style='text-align:center'>" + ' - '.join(str(x) for x in sub_set) + "</div>")         
output_file.write("<br /><div style='text-align:center'><u>Total number of mismatching ID-date's: " + str(len(IDdate_not_in_metadata)) + "</u></div><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")

# and here, we look into if there are any examinations that are recorded in metadata, but are not present in the files.
metadata_not_in_IDdate=[]
for line in EXCEL_metadata:
    if line not in IDdate and line not in metadata_not_in_IDdate:
        metadata_not_in_IDdate.append(line)
        
if re.match('{',metadata_not_in_IDdate[0][0]):
    metadata_not_in_IDdate=metadata_not_in_IDdate[1:]
output_file.write("<h3><div style='text-align:center'>ID's and dates not found in Images:</div></h3><br />")
output_file.write("<u><div style='text-align:center'>Patient ID - Examination ID - Date</div></u>")
for i in range(0,len(metadata_not_in_IDdate)):
    sub_set=metadata_not_in_IDdate[i]
    output_file.write("<div style='text-align:center'>" + ' - '.join(str(x) for x in sub_set) + "</div>")          
output_file.write("<br /><div style='text-align:center'><u>Total number of mismatching ID-date's: " + str(len(metadata_not_in_IDdate)) + "</div></u><br />")
output_file.write("<div style='text-align:center'>######################################################################################################</div><br />")

#########################################
### checking binary data in metadata ####
#########################################
print("Processing possible non-binary results in binary variables from the metadata file")
output_file.write("<h2><div style='text-align:center'>#6 Evaluation of Non-Binary Results in Binary Variables in the Metadata</div></h2><br />")            

EXCEL_BI_metadata=excel_metadata.loc[:,["xray_sij",
                                        "xray_cervical_spine",
                                        "xray_lumbar_spine",
                                        "mri_sij",
                                        "mri_sij_STIR_semi_coronal",
                                        "mri_sij_T1_semi_coronal",
                                        "mri_cervical_spine",
                                        "mri_thoracic_spine",
                                        "mri_lumbar_spine"]].values.tolist()[1:]
                                        #"patient_has_no_relevant_radiograph",
                                        #"patient_has_no_relevant_mri"]].values.tolist()[1:]
ID_codes=[x for x in excel_metadata.patient_id_abcde[1:]]

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
output_file.write("<h2><div style='text-align:center'>#7 Examinations in the Metadata without Any examinations</div></h2><br />")    

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
output_file.write("<h2><div style='text-align:center'>#8 Examinations in the Metadata with Conflicting Examination Types</div></h2><br />")    

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

#################################################################
### counting AxSpA and PsA patients, examinations, and images ###
#################################################################
print("Processing patients, examiantions and images per diagnosis group")
output_file.write("<h2><div style='text-align:center'>#9 Number of Patients, Examinations and Images per Diagnosis group</div></h2><br />")            

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
        else:
            ex_archieve_other.append(ex)
            if pat not in patient_archieve_other:
                patient_archieve_other.append(pat)
    
    # if the entry is not even a string, it cannot be registered as a diagnosis group
    else:
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
output_file.write("<li>Diagnosis grouping for images has been done using the patient IDs from the images (key='PatientName') as a bridge to the metadata file. 0's can be caused either by lack of images in that diagnosis group or due to incorrectly matched Patient ID's</li>")
output_file.write("<li>Registration of diagnosis groups ignores case-sensitivity. Instances of 'Other' can be caused by misspelling of the diagnosis group, lack of diagnosis group or another diagnosis group being registered. </li>")
    
#####################################################################################################    
### schematic for MRI- and X-ray examinations, as well as images sorted on what has been examined ###    
#####################################################################################################    
print("Processing MRI- and X-ray examinations and images.")
output_file.write("<h2><div style='text-align:center'>#10 Overview of Image Type and Examined Body Part for Examinations and Images</div></h2><br />")    

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

for i in range(len(EXCEL_BI_metadata)):
    for j in range(len(BI_names)):
        if type(EXCEL_BI_metadata[i][j])!=float and int(EXCEL_BI_metadata[i][j])==1:
            BI_header[BI_names[j]]+=int(EXCEL_BI_metadata[i][j])

            
examination_data_header=["X-ray examinations","MRI examinations","SUM","# Images"] 
examination_data_row=["SIJ","Cervical spine","Lumbar spine","SIJ STIR semi coronal","SIJ T1 semi coronal","Thoracic spine","Other","SUM"]
                         
X_sum=BI_header["xray_sij"]+BI_header["xray_cervical_spine"]+BI_header["xray_lumbar_spine"]
MRI_sum=BI_header["mri_cervical_spine"]+BI_header["mri_lumbar_spine"]+BI_header["mri_sij_STIR_semi_coronal"]+BI_header["mri_sij_T1_semi_coronal"]
TOTAL_SUM=X_sum+MRI_sum
image_sum=image_type_counting["SIJ"]+image_type_counting["Cervical Spine"]+image_type_counting["Lumbar Spine"]+image_type_counting["Thoracic Spine"]+image_type_counting["other"]
examination_data=[[BI_header["xray_sij"],BI_header["mri_sij"],BI_header["xray_sij"] + BI_header["mri_sij"],image_type_counting["SIJ"]],
                  [BI_header["xray_cervical_spine"],BI_header["mri_cervical_spine"],BI_header["xray_cervical_spine"] + BI_header["mri_cervical_spine"],image_type_counting["Cervical Spine"]],
                  [BI_header["xray_lumbar_spine"],BI_header["mri_lumbar_spine"],BI_header["xray_lumbar_spine"] + BI_header["mri_lumbar_spine"],image_type_counting["Lumbar Spine"]],
                  ["-",BI_header["mri_sij_STIR_semi_coronal"],BI_header["mri_sij_STIR_semi_coronal"],"-"],
                  ["-",BI_header["mri_sij_T1_semi_coronal"],BI_header["mri_sij_T1_semi_coronal"],"-"],
                  ["-",BI_header["mri_thoracic_spine"],BI_header["mri_thoracic_spine"],image_type_counting["Thoracic Spine"]],
                  ["-","-","-",image_type_counting["other"]],
                  [X_sum,MRI_sum,TOTAL_SUM,image_sum]]
             

ex_df=pd.DataFrame(examination_data,columns=examination_data_header,index=examination_data_row)

output_file.write(ex_df.to_html(justify="center"))
output_file.write("<li>the SUM-column only sums over the examinations and not the images</li>")
output_file.write("<li>the # Images-column does not discriminate between X-ray and MRI images</li>")
output_file.write("<li>the # Images-column uses the key 'BodypartExamined' to sort them based on keywords seen in the given key across images.</li>")                      
    
############################################################
### Graphic overview of the number of images per patient ###
############################################################
print("Processing images summary in graphic form.")
output_file.write("<h2><div style='text-align:center'>#11 Graphic Summary of the Images</div></h2>")    

# function to calculate the average number of images
def ave(dict):
    SUM=0
    for key in dict:
        SUM+=dict[key]      # sum(X)
    average=SUM/len(dict)   # sum(X)/n
    return average

# function to calculate standard deviation of the images    
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

# function to add value labels
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i,y[i],y[i])

# function to calculate the three quantiles
def quantile(LIST):
    length=len(LIST)
    one_quarter=LIST[int(length*0.25)]    # 1st quantile
    median=LIST[int(length*0.5)]          # median (2nd quantile)
    three_quarter=LIST[int(length*0.75)]  # 3rd quantile  
    return(one_quarter,median,three_quarter)

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
plt.figtext(0.15,0.8,"".join(("Average: ",str(ave(image_counting)))),fontsize='large')
plt.figtext(0.15,0.77,"".join(("std: ",str(std(image_counting)))),fontsize='large')
plt.figtext(0.15,0.74,"".join(("1st quantile: ",str(QUANTILES[0]))),fontsize='large')
plt.figtext(0.15,0.71,"".join(("median: ",str(QUANTILES[1]))),fontsize='large')
plt.figtext(0.15,0.68,"".join(("3rd quantile: ",str(QUANTILES[2]))),fontsize='large')
plt.figtext(0.15,0.65,"".join(("Max.: ",str(max(img_count)))),fontsize='large')
plt.figtext(0.15,0.62,"".join(("Min.: ",str(min(img_count)))),fontsize='large')

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

        