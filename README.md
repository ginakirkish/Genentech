# Genentech

Locate Scans
SETUP
423 IS THE NUMBER OF Follow Up Scans on Adams List
99 of them were not on the file system, a third of these have not been retrieved
100 weren't processed because of spacecd /data/pelletier1/genentech/scripts
231 Completed by Alyssa
211 Left for Gina

-  cd /data/pelletier1/genentech/scripts
- del ipython notebook
- Open Genentech_FINAL.ipynb
- Year 8/9 data from adams list and the skyra baseline scans:
                         /data/pelletier1/genentech/csv_xlsx/EPIC _GNE_Y8-9_MRI_List.xlsx

RETRIEVE FROM BILL
 This script checks for all the missing scans from yr8/9 and skyra baseline from mspacman
    - That list was sent to bill to retrieve
    - Once Bill retrieved it, I ran ms_get_scanner_data with the EPIC study flag
    - Copy mse# generated from ms_get_scanner_data into /scratch/henry_temp/PBR/dicom

LOCATE MISSING DATA IN PBR
- Find the 211 scans that alyssa didn't process!
        - Look at the mseID's from adams list and compare it to the mse's in alyssa's list to see which ones have not been completed
           Adams list:  /data/pelletier1/genentech/csv_xlxs/EPIC _GNE_Y8-9_MRI_List.xlsx
        -            Alyssa's list: /data/pelletier1/genentech/csv_xlsx/genentech_cb_and_skyra_data_WITHMSE_FINAL.xlsx
        -
        - Find out what is missing and create the new CSV with all mseID's, columns designate missing versus non-missing!
        -            New Master List: /data/pelletier1/genentech/csv_xlsx/yr89-Gina-notdone_FINAL.xlsx
-
- Make a text file: /data/pelletier1/genentech/missing.txt, that do not have niftis generated in /data/henry7/PBR/subjects/<mse>/nifti

- In terminal run the command to create niftis and ratios in pbr for the missing mseIDs:
      pbr-sge -s /data/pelletier1/genentech/missing.txt --pbrargs "-w nifti"
-       pbr-sge -s /data/pelletier1/genentech/missing.txt --pbrargs "-w ratio"

- After that was completed, this script checks through the file system to see whether PBR has been run on the scans in mspacman
        - /scratch/henry_temp/PBR/dicoms/<mse> for whether pbr has been run to create dicoms
        - /data/henry7/PBR/subject/<mse>/nifti for whether pbr has been run to create niftis
        - /data/henry7/PBR/subject/<mse>/ratio for whether pbr has been run to create ratios

TROUBLE SHOOTING THE MISSING DICOMS, NIFTIS, RATIOS, OH MY!
- Error with original upload - NO DICOMS when running pbr -w dicom
    - ex error message; could not run node: PBR.dicom.a0
    - Check if there are any series in the mspacman website, if there are..try retrieving them by running ms_dcm_qr -t
    - If that doesn't work.. Ask Jason what the problem is
    - If they aren't in mspacman, ask Bill to re-push the exam and run ms_get_scanner_data
- MseID is for a spinal cord scan not a brain scan - NO NIFTI or RATIO when running pbr -w nifti ratio
    - ex error message; Interface MNIAngulation failed to run or could not run node: PBR.ratio.a0
    - Can check using dti_info, (Gina has a script that will do a batch dti_info)
    - Need to retrieve the brain scan with Bill
- Error with ms_pac_man - NO DICOM/NIFTI/RATIO
    - If not all of the DICOMs were brought down that are in the mspacman system
    - Re-run ms_dcm_qr -t

    - If ms_dcm_qr doesn't bring everything down check dti_info on the dicoms folder in /scratch/henry_temp/PBR/dicoms and see if it matches the series descriptions in the mspacman website
    - If you see something missing you can run ms_dcm_qr -t mseID -s <specific series you want>
- The DICOMS that were brought down with the mspacman system are not in the heuristic file
    - ex error message; Interface MNIAngulation failed to run or could not run node: PBR.ratio.a0
    - Need a T1 and a T2/FLAIR in order to create a ratio
    - Talk to Anisha about adding a series name to the heuristic file
-  Error: command 'antsApplyTransforms' could not be found
    - Add to path:
#ANTS
export PATH=/netopt/rhel7/versions/ANTs/1.9/antsbin/bin:$PATH
export ANTSPATH=/data/henry7/software/ak/ #/data/henry6/keshavan/ANTS/antsbin/
export PATH=/netopt/rhel7/versions/ANTs/1.9/ANTs/Scripts:$PATH
- MT files don't match size
    - For now MT is taken out of the pipeline so we shouldn't get this error
    - However, once MT is back we need to discuss with Bill what the correct MT series pair names are

SETUP RATIOS AND T1s

- See Genentech_FINAL script to move ratio scans into: /data/pelletier1/genentech/GKyr89_ratio/all_ratios_renamed/
- Move T1 aligned scans into: /data/pelletier1/genentech/GKyr89_ratio/T1_aligned_renamed

Histogram Normalization

- Run the following command:
- python /data/pelletier1/genentech/scripts/histogram_normalization_GK.py /data/pelletier1/genentech/GKyr89_ratio/all_ratios_renamed/*
- (python 2 for this script)
- This will generate thresholds, to get the average threshold look at the average 40-50 column threshold
- Copy that threshold and save it to a seperate csv: /data/pelletier1/genentech/average_threshold_genentech_yr89.xlxs

Lesion Registration

- Run the following command:
- cd /data/pelletier1/genentech/GKyr89_ratio/all_ratios_renamed/
- python /data/pelletier1/genentech/GKyr89_ratio/all_ratios_renamed/register_lesion_wrapper_TEST.py /data/pelletier1/genentech/GKyr89_ratio/all_ratios_renamed/*
- (you may have to move the files that are called warper into a new folder to run this - but remember to move them back when it's done)
- (you may have to move the skyra BL scans because they do not have any previous lesions masks - but remember to move them back)
- This script will look at old lesion masks and register the new ones to the old and generate a series of files
- For the skyra BL scans the lesions were created this time around and therefore did not need to be registered

SIENAX for Follow Up

- cd /data/pelletier1/genentech/yr8_sienax 

- For non baseline scans you run: python /data/pelletier1/genentech/yr8_sienax
- /run_sienax_y8_GK.py /data/pelletier1/genentech/GKyr89_ratio/all_ratios_renamed/*

SIENAX For Skyra BL

- Antje and Simone edited the lesion masks in Jim
- Esha converted the lesion masks into ROIs
    - mkdir /data/pelletier1/genentech/yr8_sienax/ms****-mse****
    - Grab the aligned T1 image in /data/henry7/PBR/subjects/<mse>/aligned and put it in /data/pelletier1/genentech/yr8_sienax/ms****-mse****
    - Put the lesion mask in (.nii.gz)  in /data/pelletier1/genentech/yr8_sienax/ms****-mse****
    - run the following sienax command in /data/pelletier1/genentech/yr8_sienax/ms****-mse****
    - sienax <T1 brain> -lm <lesion mask ROI> -r -d -o  /data/pelletier1/genentech/yr8_sienax/ms****-mse****

Collect DATA from SIENAX

- cd /data/pelletier1/genentech/yr8_sienax
- (make sure you are using python 2)
- python collect_sienax_data_GKedits.py *
- Data will be saved in a csv called: genentech_yr89_data.csv 
