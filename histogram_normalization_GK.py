#!/usr/bin/env python
from subprocess import call
import numpy as np
import nibabel as nib
import os
import sys
import csv
from scipy.stats import linregress 

# does not include noise/background vs foreground differentiation in histogram
# but then again, we're working on brain extracted images
# add i_max and i_min when doing flair to t2

inputs = sys.argv[1:] # ratios
standard = '/data/henry6/alyssa/ratio_hist_norm/baseline/frfse_average.nii.gz'
spreadsheet = csv.writer(open('slopes_and_intercepts.csv', 'wb'))
spreadsheet.writerow(['msid', 'slopes', '1-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-99', 'intercepts', '1-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-99', 'estimated thrs', '1-10', '10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90', '90-99'])

def main(input):
    percentiles = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]
    # percentiles = list(np.arange(30,55,5))

    # standard_data, standard_affine = load(standard)
    # standard_landmarks =  np.percentile(standard_data[standard_data > 0], percentiles)
    
    # all avg: 
    standard_landmarks = [192.23805126, 284.33555389, 312.2577499, 347.74805948, 398.59652187, 456.90221322, 519.25354007, 599.43605854, 752.53323979, 1219.34471393, 3078.63745648]
    # lower lesvols avg: [189.07371796, 277.36542384, 302.84423728, 336.11237, 386.42650312, 444.60373288, 504.58231056, 575.15079959, 696.34415278, 1070.46175473, 2952.08181927]

    input_data, input_affine = load(input)
    # input_data = np.nan_to_num(input_data)
    input_landmarks = np.percentile(input_data[input_data > 0], percentiles)

    slopes = []
    intercepts = []
    thrs = []
    for i in np.arange(len(percentiles)-1):
        standard_pts = standard_landmarks[i:i+2]
        input_pts = input_landmarks[i:i+2]
        slope, intercept, r_value, p_value, std_err = linregress(input_pts,standard_pts)
        thr = (400.0 - intercept)/slope
        slopes.append(slope)
        intercepts.append(intercept)
        thrs.append(thr)
    """
    a = input_data[input_data > 0]
    new = np.zeros(np.shape(a))
    for index, voxel in enumerate(a):
        if voxel < input_landmarks[1]:
            new[index] = slopes[0] * voxel + intercepts[0]
        elif input_landmarks[1] < voxel < input_landmarks[2]:
            new[index] = slopes[1] * voxel + intercepts[1]
        elif input_landmarks[2] < voxel < input_landmarks[3]:
            new[index] = slopes[2] * voxel + intercepts[2]
        elif input_landmarks[3] < voxel < input_landmarks[4]:
            new[index] = slopes[3] * voxel + intercepts[3]
        elif input_landmarks[4] < voxel < input_landmarks[5]:
            new[index] = slopes[4] * voxel + intercepts[4]
        elif input_landmarks[5] < voxel < input_landmarks[6]:
            new[index] = slopes[5] * voxel + intercepts[5]
        elif input_landmarks[6] < voxel < input_landmarks[7]:
            new[index] = slopes[6] * voxel + intercepts[6]
        elif input_landmarks[7] < voxel < input_landmarks[8]:
            new[index] = slopes[7] * voxel + intercepts[7]
        elif input_landmarks[8] < voxel < input_landmarks[9]:
            new[index] = slopes[8] * voxel + intercepts[8]
        elif voxel > input_landmarks[9]:
            new[index] = slopes[9] * voxel + intercepts[9]

    output_data = np.zeros(np.shape(input_data))
    output_data[input_data > 0] = new
    
    for index, landmark in enumerate(input_landmarks):
        output_data[input_data == landmark] = standard_landmarks[index]

    nib.save(nib.Nifti1Image(output_data, input_affine), os.path.basename(input)[:-7]+'_normalized.nii.gz')
    """
    row = [msid, '']
    row += slopes
    row.append('')
    row += intercepts
    row.append('')
    row += thrs
    spreadsheet.writerow(row)

def load(image):
    img = nib.load(image)
    data = np.array(img.get_data())
    affine = img.get_affine()
    return data, affine

for input in inputs:
    msid = os.path.basename(input).split('_')[0]
    print(msid)
    main(input)
