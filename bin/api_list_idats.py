#!/usr/bin/env python


from tqdm import tqdm
from pymnp.pymnp import *



def main():
    app = mnpscrape()
    app.login()
    
    for sample in tqdm(app.update_samples(False)):
        print(sample._idat + "__" + sample._name)



main()


