#!/usr/bin/env python

import glob
from tqdm import tqdm
import subprocess
import os
import sys
from pymnp.pymnp import *


files = glob.glob("cache/*/*.zip")
if len(sys.argv) > 1:
    old = len(files)
    files = [_ for _ in files if _.find(sys.argv[1]) != -1]
    new = len(files)
    print("Filtered from "+str(old) + " to " + str(new) + " entries")



for zipfile in tqdm(files):
    result = subprocess.run(['unzip', '-t', zipfile], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
    if not is_valid_zipfile(zipfile):
        print(zipfile)
        os.remove(zipfile)


