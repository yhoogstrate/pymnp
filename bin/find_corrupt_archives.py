#!/usr/bin/env python

import glob
from tqdm import tqdm
import subprocess
import os


for zipfile in tqdm(glob.glob("cache/*/*.zip")):
    result = subprocess.run(['unzip', '-t', zipfile], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    if result.returncode != 0:
        print(zipfile)
        print("-----")
        print(result.stdout.decode('utf-8'))
        print("-----")
        print(result.stderr.decode('utf-8'))
        print("-----")
        print("")
        
        os.remove(zipfile)


