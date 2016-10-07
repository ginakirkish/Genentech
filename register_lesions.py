#!/usr/bin/env python
from subprocess import check_call, check_output
import pandas as pd
import argparse 
import os

def main(prev_ratio, yr4_ratio, threshold, subthr):
    subject = os.path.basename(yr4_ratio).split("-")[0]
    mse = os.path.basename(yr4_ratio).split("-")[1].split("_")[0]

    # rigid transforms
    prev2_ratio = subject+'_prevTO%s_ratio_brain.nii.gz' %mse
    prev2_matrix = subject+'_prevTO%s_transform.mat' %mse
    prev = os.path.basename(prev_ratio).split("_")[1]
    lesion_paths = {"yr0": '/data/henry6/alyssa/lesions_reg/manual_lesions/baseline/'+subject+'_yr0_lesions.nii.gz',
                    "yr1": "/data/henry8/alyssa/lesions_reg/get_yr1_lesions/"+subject+"_yr1_lesions.nii.gz",
                    "yr2": "/data/henry8/alyssa/lesions_reg/get_yr2_lesions/"+subject+"_yr2_lesions.nii.gz",
                    "yr3": "/data/henry8/alyssa/lesions_reg/get_yr3_lesions/"+subject+"_yr3_lesions.nii.gz",
                    "yr4": "/data/henry8/alyssa/lesions_reg/get_yr4_lesions/"+subject+"_yr4_lesions.nii.gz",
                    "yr5": "/data/henry8/alyssa/lesions_reg/get_yr5_lesions/"+subject+"_yr5_lesions.nii.gz"
                   }
    prev_les = lesion_paths[prev]
    prev2_les = subject+'_prevTO%s_lesions.nii.gz' %mse

    check_call(['flirt', '-dof', '6', "-searchrx", "-180", "180", "-searchry", "-180", "180", "-searchrz", "-180", "180", '-in', prev_ratio,'-ref', yr4_ratio, '-omat', prev2_matrix, '-out', prev2_ratio])
    check_call(['flirt', '-interp', 'nearestneighbour', '-in', prev_les, '-ref', yr4_ratio, '-applyxfm', '-init', prev2_matrix, '-out', prev2_les])

    # warp images
    prev2_warp = subject+'_prevTO%s_warp.nii.gz' %mse
    prev2_warped_ratio = subject+'_prevTO%s_warped_ratio.nii.gz' %mse
    prev2_warped_les = subject+'_prevTO%s_warped_lesions.nii.gz' %mse

    check_call(['/opt/src/freeware/Slicer/Slicer-4.1-svn-co-20121002/Slicer-4.1-linux_x86_64-build/Slicer-build/lib/Slicer-4.1/cli-modules/BRAINSDemonWarp', "-e", '--registrationFilterType', 'Demons', '-O', prev2_warp, '-o', prev2_warped_ratio, '-f', yr4_ratio, '-m', prev2_ratio]) #, '--interpolationMode', 'BSpline'
    check_call(['WarpImageMultiTransform', '3', prev2_les, prev2_warped_les, '-R', yr4_ratio, prev2_warp, '--use-NN'])

    # subtraction
    sub = subject+'_{mse}_SUB_prevTO{mse}.nii.gz'.format(mse=mse)
    sub_masked = subject+'_{mse}_SUB_prevTO{mse}_wm.nii.gz'.format(mse=mse)
    wm_mask_ero = subject+'_wm_mask_pero.nii.gz'

    print("THIS IS PREV:::::::")
    print(prev)

    if prev == "yr0":
        bad_wm_mask = '/data/henry6/alyssa/rhel7_fsl5.0.8_cb_sienax/yr0_sienax/'+subject+'/I_wm_mask.nii.gz'
    #print("WHY AREN'T I ELSEING???")
    else:
        print("I AM ELSING!!!")
        bad_wm_mask = "/data/henry8/alyssa/"+prev+"_sienax/"+subject+'/I_wm_mask.nii.gz'              
        wm_mask = "/data/henry8/alyssa/"+prev+"_sienax/wm_segs/"+subject+'_I_wm_mask.nii.gz'
        print(os.path.join(os.path.dirname(wm_mask), "I_stdmaskbrain_seg.nii.gz"))
        print(os.path.dirname(wm_mask))
        print(wm_mask)
        check_call(["fslmaths", os.path.join(os.path.dirname(bad_wm_mask), "I_stdmaskbrain_seg.nii.gz"),
                "-thr", "3", "-bin", wm_mask])
        print("SAVED WM MASK SUCCESSFULLY")
        check_call(['/data/henry6/alyssa/scripts/mask_erosion.py', wm_mask])
    check_call(['fslmaths', yr4_ratio, '-sub', prev2_ratio, sub])
    check_call(['flirt', '-interp', 'nearestneighbour', '-in', wm_mask[:-7]+'_pero.nii.gz', '-ref', yr4_ratio, '-applyxfm', '-init', prev2_matrix, '-out', wm_mask_ero])
    check_call(['fslmaths', sub, '-mas', wm_mask_ero, '-thr', subthr, '-bin', sub_masked])

    # clean and get final lesions
    yr4_les = subject+'_%s_lesions.nii.gz' %mse
    
    check_call(['fslmaths', sub_masked, '-add', prev2_warped_les, '-bin', yr4_les]) #, '-add', prev2_les
    check_call(['/data/henry6/alyssa/scripts/mask_dilation.py', yr4_les])
    check_call(['/data/henry6/alyssa/scripts/mask_erosion.py', yr4_les[:-7]+'_pdil.nii.gz'])
    check_call(['fslmaths', yr4_ratio, '-thr', threshold, '-mas', yr4_les[:-7]+'_pdil_pero.nii.gz', '-bin', yr4_les])
    check_call(['/data/henry6/alyssa/scripts/lesion_mask_erosion.py', yr4_les])
    check_call(['mv', yr4_les[:-7]+'_pero.nii.gz', yr4_les])
    check_call(['rm', yr4_les[:-7]+'_pdil.nii.gz', yr4_les[:-7]+'_pdil_pero.nii.gz'])

    return yr4_les

    print("FINISHED SUCCESSFULLY")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prev_ratio", help="last found ratio")
    parser.add_argument("new_ratio", help="current ratio to segment")
    parser.add_argument("threshold", help="intensity threshold")
    parser.add_argument("subthr", help="threshold for longitudinal subtraction")
    args = parser.parse_args()
    main(args.prev_ratio, args.new_ratio, args.threshold, args.subthr)
