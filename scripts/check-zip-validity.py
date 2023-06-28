#!/usr/bin/env python

import glob
from tqdm import tqdm
import subprocess

def get_zip_file_corrution_status(fn):
    retcode = subprocess.call(["unzip", "-t", fn],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
    
    return retcode


for fn in tqdm(glob.glob("cache/*.zip")):
    rc = get_zip_file_corrution_status(fn)
    
    if rc != 0:
        print("ERROR:" + "\t" + fn + "\t" + str(rc))


