import pydicom
import os
import shutil

## list of strings with paths to the directory/directories that needs to be sorted
## can handle multiple paths sorting simultaneously
directories=["/home/alexanderandersen/2_wave/images/SL"]

for path in directories:
    # works in two root/directory/file loops:
    ## first loop makes the correct folders and moves the files there
    print("file sorting of ",path)
    for root, dirs, files in os.walk(path):
        
        if len(files) > 0: #only work for directories with files in it
            for file in files:
                # Needs to be changed for CZ
                # We analyze files with no suffix
                Pat_ID=""
                ex_ID=""
                name, extension = os.path.splitext(root + "/" + file)
                
                if extension == '.dcm':
                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)
                    except:
                        next
                    
                    # Get patient ID
                    Pat_ID=str(ds.PatientName)
                    
                    # Get examination ID
                    ex_ID = str(ds.PatientID)
                    
                    # cannot make new folders for ID sorting, if an image as no ID
                    if Pat_ID=="":
                        next
                    
                    if ex_ID=="":
                        next
                    
                elif len(extension) == 0 and file[0] != '.' and file!="DICOMDIR": #this is done to also be able to read images with no extension (CZ)
                    # read metadata
                    try:
                        ds = pydicom.dcmread(root + "/" + file)    
                    except:
                        next
                    # Czech include ^ as part of their patient ID's in the images
                    if "CZ" in path:
                        Pat_ID=str(ds.PatientName).split('^')[0]
                    else:
                        Pat_ID=str(ds.PatientName)
                    
                    # Get examination ID
                    ex_ID = str(ds.PatientID)
                    
                    if Pat_ID=="":
                        next
                    
                    if ex_ID=="":
                        next
                #sys.exit()
                # make directories based on the IDs, if the directories does not exist
                if not os.path.exists(path + "/" + Pat_ID):
                    os.makedirs(path + "/" + Pat_ID)
                if not os.path.exists(path + "/" + Pat_ID + "/" + ex_ID):
                    os.makedirs(path + "/" + Pat_ID + "/" + ex_ID)
                
                # unless the file in question already exists in that folder, the file will be moved there
                if not os.path.exists(path + "/" + Pat_ID + "/" + ex_ID + "/" + file):
                    shutil.move(root + "/" + file,path + "/" + Pat_ID + "/" + ex_ID) 
                else:
                    next
    
    ## second loop deletes empty folders and it can handle 10 layers of matroyska dolls    
    print("Removal of empty directories from",path)
    for x in range(11):
        for root, dirs, files in os.walk(path):
            if len(os.listdir(root))==0:
                shutil.rmtree(root)
    print("organization of ",path,": complete")
print("All done.")