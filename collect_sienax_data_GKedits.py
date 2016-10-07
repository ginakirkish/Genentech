#!/usr/bin/env python
from subprocess import check_output, check_call
from getpass import getpass
import nibabel as nib
import numpy as np
from glob import glob
import csv
import os

password = getpass("mspacman password: ")
check_call(["ms_dcm_echo", "-p", password])

folders = sorted(glob("ms*"))

writer = open("genentech_yr89_data.csv", "w")
spreadsheet = csv.DictWriter(writer, 
                             fieldnames=["msid", "Scan Date", "Scan Status",
                                        "vscale", 
                                        "brain vol (u, mm3)",
                                        "WM vol (u, mm3)", 
                                        "GM vol (u, mm3)",
                                        "vCSF vol (u, mm3)",
                                        "cortical vol (u, mm3)",
                                        "lesion vol (u, mm3)", "mseID"])
spreadsheet.writeheader()

for folder in folders:
    msid = "ms%04d" % int(folder.split("-")[0].split("s")[-1])
    mse = folder.split("-")[1]
    print(msid, mse)
    mseid = folder.split("-")[1]
    row = {"msid": msid, "Scan Status": "Skyra", "mseID": mseid}

    output = check_output(["ms_get_phi", "--examID", mseid, "--studyDate", "-p", password])
    for line in output.split("\n"):
        if "StudyDate" in line:
            row["Scan Date"] = line.split()[-1]

    report = os.path.join(folder, "report.sienax")
    with open(report, "r") as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines:
            if line.startswith("VSCALING"):
                row["vscale"] = line.split()[1]
            elif line.startswith("pgrey"):
                row["cortical vol (u, mm3)"] = line.split()[2]
            elif line.startswith("vcsf"):
                row["vCSF vol (u, mm3)"] = line.split()[2]
            elif line.startswith("GREY"):
                row["GM vol (u, mm3)"] = line.split()[2]
            elif line.startswith("WHITE"):
                row["WM vol (u, mm3)"] = line.split()[2]
            elif line.startswith("BRAIN"):
                row["brain vol (u, mm3)"] = line.split()[2]

    lm = os.path.join(folder, "lesion_mask.nii.gz")
    img = nib.load(lm)
    data = img.get_data()
    row["lesion vol (u, mm3)"] = np.sum(data)

    spreadsheet.writerow(row)

writer.close()
