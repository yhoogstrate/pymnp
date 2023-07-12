#!/usr/bin/env python


from tqdm import tqdm
from pymnp.pymnp import *



def main():
    app = mnpscrape()
    app.login()
    
    for sample in tqdm(app.update_samples()):
        for workflow in sample._workflows:
            if sample._workflows[workflow]['jobs'] is not None:
                for job in sample._workflows[workflow]['jobs'].values():
                    if job.is_downloadable():
                        job.download(app)



main()


