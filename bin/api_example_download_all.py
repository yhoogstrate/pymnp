#!/usr/bin/env python


from tqdm import tqdm
from pymnp.pymnp import *
import sys


def main():
    app = mnpscrape()
    app.login()
    
    f = 0
    
    for sample in tqdm(app.update_samples(detailed=False)):
        
        if len(sys.argv) <= 1 or (sample._name.find(sys.argv[1]) > -1):
            sample.get_detailed_info(app)
            
            for workflow in sample._workflows:
                #if workflow._workflow_name_short == "brain_v12.8-S":

                if sample._workflows[workflow]['jobs'] is not None:
                    for job in sample._workflows[workflow]['jobs'].values():
                        if job.is_downloadable():
                            job.download(app)

        else:
            f += 1
    
    print("Excluded by filter: "+str(f))



main()


