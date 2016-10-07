#!/usr/bin/env python
#from brain_cluster import ucsf_grid_job
from subprocess import check_call
from glob import glob
import os

# run: cd /data/pelletier1/genentech/yr8_sienax, python run_sienax_y8_GK.py /data/pelletier1/genentech/ratios/GKyr89_ratio/all_ratios_renamed/*

lesions = sorted(glob("/data/pelletier1/genentech/GKyr89_ratio/all_ratios_renamed/ms????_[!p]*_lesions.nii.gz"))
super_outdir = "/data/pelletier1/genentech/yr8_sienax/"
UHOH = []
for lesion in lesions:
    msid = os.path.basename(lesion).split("_")[0]
    mse = os.path.basename(lesion).split("_")[1]
    print(lesion)

    T1_brain_path = os.path.join("/data/pelletier1/genentech/GKyr89_ratio/T1_aligned_renamed", msid + "-" + mse + "-brain.nii.gz")
    if not os.path.exists(T1_brain_path):
        UHOH.append(T1_brain_path)
        print("UH OH")
        print(T1_brain_path)
        continue
    else:
        print("...processing")
 

    outdir = os.path.join(super_outdir, msid)
    print(outdir, "name of outdir")

    if not os.path.exists(outdir):

        os.mkdir(outdir)
        r2std = os.path.join(outdir, os.path.basename(T1_brain_path))
        check_call(["fslreorient2std", T1_brain_path, r2std])
        pid = check_call(["sienax", T1_brain_path, "-lm", lesion, "-r", "-d","-o", outdir])
                         #"-B", "-f 0.1",
                         #"-o", outdir])
    #-B is for BET, 
    #print(pid)
    #print msid, mse, pid"""
print(UHOH, "did not find T1 brain path")
