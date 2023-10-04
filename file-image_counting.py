#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 07:52:02 2022

@author: alexanderandersen
"""
import os
import pydicom

use = "all";
############################################
### Read image metadata from Dicom files ###
############################################
if(use=="CH") : 
    images_root_path = "/home/alexanderandersen/2_wave/images/CH/" #pointing path where images are stored (both XRay and MR)
elif(use=="CH_insel") : 
    images_root_path = "/home/alexanderandersen/2_wave/images/test/"
elif use=="CZ" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/CZ/corrected part 3/" #pointing path where images are stored (both XRay and MR)
elif use=="CZ_Brno" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/CZ/Other centers/Brno2"
elif use=="CZ_FNKV" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/CZ/Other centers/FNKV"
elif use=="SL" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/SL/" #pointing path where images are stored (both XRay and MR)
elif use=="IS" : 
    images_root_path = "/home/alexanderandersen/2_wave/images/IS/" #pointing path where images are stored (both XRay and MR)

if use!="all":
    file_count=0
    dcm_count=0
    other_count=0
    body_parts=[]
    pydi_keys=[]
    for root, dirs, files in os.walk(images_root_path):
        if len(files) > 0:
            for file in files:
                name, extension = os.path.splitext(root + "/" + file)
                if extension == '.dcm':
                    file_count+=1
                    dcm_count+=1
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                    except:
                        next
                    if "BodyPartExamined" in ds.dir() and ds.BodyPartExamined not in body_parts:
                        body_parts.append(ds.BodyPartExamined)
                    for i in ds.keys():
                        if i not in pydi_keys:
                            pydi_keys.append(i)
                elif len(extension) == 0 and file[0] != '.' and file!="DICOMDIR": #this is done to also be able to read images with no extension (CZ)
                    file_count+=1
                    other_count+=1
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                    except:
                        next
                    if "BodyPartExamined" in ds.dir() and ds.BodyPartExamined not in body_parts:
                        body_parts.append(ds.BodyPartExamined)
                    for i in ds.keys():
                        if i not in pydi_keys:
                            pydi_keys.append(i)
else:
    image_root_path=["/home/alexanderandersen/2_wave/images/CH/",
                     "/home/alexanderandersen/2_wave/images/test/",
                     "/home/alexanderandersen/2_wave/images/CZ/corrected part 3/",
                     "/home/alexanderandersen/2_wave/images/CZ/Other centers/Brno2",
                     "/home/alexanderandersen/2_wave/images/CZ/Other centers/FNKV",
                     "/home/alexanderandersen/2_wave/images/SI/",
                     "/home/alexanderandersen/2_wave/images/IS/"]
    file_count=0
    dcm_count=0
    other_count=0
    body_parts=[]
    pydi_keys=[]
    for i in image_root_path:
        for root, dirs, files in os.walk(i):
            if len(files) > 0:
                for file in files:
                    name, extension = os.path.splitext(root + "/" + file)
                    if extension == '.dcm':
                        file_count+=1
                        dcm_count+=1
                        try:
                            ds = pydicom.dcmread(root + "/" + file)
                        except:
                            next
                        if "BodyPartExamined" in ds.dir() and ds.BodyPartExamined not in body_parts:
                            body_parts.append(ds.BodyPartExamined)
                        """
                        if "PatientBirthDate" in ds.dir():
                            print("PatientBirthDate: ",ds.PatientBirthDate)
                        if "EthnicGroup" in ds.dir():
                            print("EthnicGroup: ",ds.EthnicGroup)
                        """
                        if "OtherPatientNames" in ds.dir():
                            print("OtherPatientNames: ",ds.OtherPatientNames)
                        
                        """
                        if "PixelAspectRatio" in ds.dir():
                            print("PixelAspectRatio: ",ds.PixelAspectRatio)
                        if "GridAspectRatio" in ds.dir():
                            print("GridAspectRatio: ",ds.GridAspectRatio)
                        for i in ds.dir():
                            if i not in pydi_keys:
                                pydi_keys.append(i)
                        """
                    elif len(extension) == 0 and file[0] != '.' and file!="DICOMDIR": #this is done to also be able to read images with no extension (CZ)
                        file_count+=1
                        other_count+=1
                        try:
                            ds = pydicom.dcmread(root + "/" + file)
                        except:
                            next
                        if "BodyPartExamined" in ds.dir() and ds.BodyPartExamined not in body_parts:
                            body_parts.append(ds.BodyPartExamined)
                        """
                        if "PatientBirthDate" in ds.dir():
                            print("PatientBirthDate: ",ds.PatientBirthDate)
                        if "EthnicGroup" in ds.dir():
                            print("EthnicGroup: ",ds.EthnicGroup)
                        """
                        if "OtherPatientNames" in ds.dir():
                            print("OtherPatientNames: ",ds.OtherPatientNames)
                        """
                        if "PixelAspectRatio" in ds.dir():
                            print("PixelAspectRatio: ",ds.PixelAspectRatio)
                        if "GridAspectRatio" in ds.dir():
                            print("GridAspectRatio: ",ds.GridAspectRatio)
                        for i in ds.dir():
                            if i not in pydi_keys:
                                pydi_keys.append(i)
                        """

print("number of files/images for",use,":",file_count)
print("of which ",dcm_count," has the .dcm extension.")
print("and ",other_count," has the alternative extension.")
print("Body Parts found:",body_parts)
print("keys in images:",pydi_keys)