#!/usr/bin/env python
#from brain_cluster import ucsf_grid_job
# from hlab_pytools.launch_ipcluster import ucsf_grid_job
import numpy as np
import pandas as pd
import argparse
import os
from subprocess import check_call

def get_thr(date):
    if date < 20050402: #china basin
        threshold = 300
        scanner = 'china basin original'
    elif (date >= 20090301) and (date <= 20091001): #china basin after update
        threshold = 435
        scanner = 'china basin first upgrade'
    elif (date > 20091001) or np.isnan(date): #china basin another update
        threshold = 424
        scanner = 'china basin second upgrade'
    else:
        threshold = 400
        scanner = 'miscellaneous (CHECK THIS..)'
    return threshold, scanner

def find_previous(tp, df):
    checking = range(1, int(tp))[::-1]
    for c in checking:
        prev = str(c)
        if not np.isnan(df[prev].values[0]):
            break
    return prev, df[prev].values[0]

if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("ratios", nargs="+")
    args = parser.parse_args()

    dates = "/data/pelletier1/genentech/csv_xlsx/cb_scan_dates_withyr89_TEST.csv"
    df = pd.read_csv(dates)

    threshloc = "/data/pelletier1/genentech/csv_xlsx/average_threshold_genentech_yr89.csv"
    df2_raw = pd.read_csv(threshloc)

    df2 = df2_raw.copy()
    df2.insert(1, "id", df2.msid)
    df2.insert(2,"mse", df2.msid)
    df2['id'] = df2['id'].apply(lambda x: 'ms%s' % x[2:].split('+')[0].zfill(4))
    df2['mse'] = df2['mse'].apply(lambda x: 'mse%s' % x[2:].split('+')[0].zfill(4))

    logfile = open("processing_log.txt", "w")
    print("logfile open")
    logfile.write("starting log...\n")

    UHOH_noprev = []
    for ratio in args.ratios:
        if len(ratio.split('_'))>2:
	        continue
	    #print("starting new ratio")
    	#print(ratio)
        subject = os.path.basename(ratio).split("-")[0]
        print(subject)
        mse = os.path.basename(ratio).split("_")[0].split('-')[1]
        print(mse)
        logfile.write(subject+"\n")

        if os.path.exists(subject+"_"+mse+'_lesions.nii.gz'):
            print("NEW LESION MASK ALREADY EXISTS")
            #logfile.write(subject, "already exists; skipping processing\n")
            continue




        tp = "8"
        if len(subject)<6:
            logfile.write("uhoh...zeropad??\n")
            print("UHOH")
            print("renaming with zero pad")
            subject = subject[0:2]+subject[2:].zfill(4)
            logfile.write(subject+' <-- zeropadded subject\n')
            #logfile.write(subject)
        try:
            prev, prevdate = find_previous(tp, df[df.msid == subject])
        except:
            UHOH_noprev.append(subject)
            logfile.write("missing a previous timepoint in the spreadsheet\n")
            continue

        ratio_paths = {"6": "/data/henry6/esha/Old_Files/T2T1_Ratio_Zscores/Yr5/calculating_ratios/"+subject+"_yr5_ratio_brain.nii.gz",
                       "5": "/data/henry6/esha/Old_Files/T2T1_Ratio_Zscores/Yr4/calculating_ratios/"+subject+"_yr4_ratio_brain.nii.gz",
                       "4": "/data/henry6/esha/Old_Files/T2T1_Ratio_Zscores/Yr3/calculating_ratios/"+subject+"_yr3_ratio_brain.nii.gz",
                       "3": '/data/henry6/esha/Old_Files/EPIC_Yr2/LST_files/ratio/'+subject+'_yr2_ratio_brain.nii.gz',
                       "2": '/data/henry6/esha/Old_Files/T2T1_Ratio_Zscores/Yr1/calculating_ratios/'+subject+'_yr1_ratio_brain.nii.gz',
                       "1": '/data/henry6/esha/Old_Files/EPIC_Baseline/LST_files/ratio_brain/'+subject+'_yr0_ratio_brain.nii.gz'
                      }


        #scandate = "Skyra"
        '''
        if not os.path.exists('/data/henry6/alyssa/rhel7_fsl5.0.8_cb_sienax/yr0_sienax/'+subject):
            logfile.write("no baseline lesions\n")
            # continue
        '''

        print("WTF")
        if len(ratio.split('-')[0]) < 6:
            logfile.write("uhoh...zeropadding again...\n")
            ratio = subject + '-'+ratio.split('-')[1]

        if os.path.exists(ratio) and os.path.exists(ratio_paths[prev]):
            #threshold = df2.avethresh[df2.msid == subject+'+AC0-'+mse].values[0]
            threshold = df2.avethresh[df2.id == subject].values[0]
            print(threshold)
            print(threshold)
            #gina calculated the qb3 threshold
            thr2, scandate = get_thr(prevdate)
            subthr = threshold - thr2 + 150
            print("processing now...")
            print (ratio)
            print(ratio_paths[prev])
            #pid = check_call(["./register_lesions.py", ratio_paths[prev], ratio, str(threshold), str(subthr)], quiet=True)
            pid = check_call(["/data/pelletier1/genentech/scripts/register_lesions.py", ratio_paths[prev], ratio, str(threshold), str(subthr)])
            logfile.write("F/U Yr%s was acquired on %s so %i threshold was used\nPrevious timepoint was acquired on %s so %i subtraction threshold was used\n" %(str(int(tp)-1), scandate, threshold, prevdate, subthr))
        else:
            logfile.write("missing a ratio\n")
            if not os.path.exists(ratio):
                logfile.write("missing later timepoint\n")
            elif not os.path.exists(ratio_paths[prev]):
                logfile.write("missing earlier timepoint\n")
                logfile.write("prev = "+prev+': '+ratio_paths[prev]+'\n')
            else:
                logfile.write("what??\n")
    logfile.close()
    
    print("NO PREVIOUS FOUND:")
    print(UHOH_noprev)

