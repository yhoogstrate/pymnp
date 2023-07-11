#!/usr/bin/env python


from tqdm import tqdm
from pymnp.pymnp import *



def main():
    app = mnpscrape()
    app.login()
    
    for sample in tqdm(app.update_samples()):
        for workflow in sample._workflows:
            #print(workflow)
            #print(sample._workflows[workflow])
        
            if sample._workflows[workflow]['jobs'] is not None:
                for job in sample._workflows[workflow]['jobs'].values():
                    if job.is_downloadable():
                        job.download(app)



main()



"""

import requests
import math
import shutil
import os




def get_config():
    user = False
    pwd = False
    
    with open('config.txt', 'r') as fh:
        for line in fh:
            line = line.strip().split("=",1)
            
            if len(line) == 2 and line[0] == "user":
                user = line[1]
            
            elif len(line) == 2 and line[0] == "pwd":
                pwd = line[1]
    
    return user, pwd


def login(user, pwd):
    print("[login]")
    response1 = requests.post('https://www.molecularneuropathology.org/api-v1/authenticate', json = {"email":user,"password":pwd} )
    print("x-auth:" + response1.json()['X-AUTH-TOKEN'])


    response2 = requests.post('https://www.molecularneuropathology.org/authenticate', data = {"email":user,"password":pwd} )
    print("cookie: " + response2.headers['Set-Cookie'])
    
    return response1.json()['X-AUTH-TOKEN'], response2.headers['Set-Cookie']


def get_sample_count(cookie, x_auth_token):
    
    print({'Cookie': cookie})
    
    response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/count', headers={'Cookie': cookie,
     'Content-Type':'application/json',
     'X-AUTH-TOKEN': x_auth_token})
    
    print(response)
    
    print("\n ---\n")
    
    print(response.headers)
    
    print(" -- ")
    
    out = ""
    for _ in response.iter_lines():
        out += _.decode('utf-8')
    
    return(int(out))



def get_samples(cookie, x_auth_token, n):
    
    response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/list/'+str(n)+'/0', headers={'Cookie': cookie,
        'Content-Type':'application/json',
        'X-AUTH-TOKEN': x_auth_token})
    
    print(response)
    out = response.json()
    
    #print("found: "+str(len(out))+ " samples")
    
    return out


def scrape_sample(cookie, x_auth_token, sid):
    response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/details/'+str(sid), headers={'Cookie': cookie,
        'Content-Type':'application/json',
        'X-AUTH-TOKEN': x_auth_token})
    
    out = response.json()



    return out



def download(cookie, x_auth_token, fid, filename_out):
    with requests.get("https://www.molecularneuropathology.org/api-v1/workflow-run-dowload-complete/" + str(fid),
     headers={'Cookie': cookie,
     'Accept': 'application/zip',
        'X-AUTH-TOKEN': x_auth_token}, stream=True) as r:
        with open(filename_out, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)



def main():
    app = mnpscrape()
    app.login()
    app.get_samples()
    
    for s in tqdm(app):
        s.get_detailed_info(app)
    
    # user, pwd = get_config()
    # print("logging in with: "+ user)
    
    # x_auth, cookie = login(user, pwd)
    # cookie = cookie
    
    
    

    # n_samples = get_sample_count(cookie, x_auth)
    
    # print("n-samples: " + str(n_samples))
    
    # #n_pages = int(math.ceil(float(n_samples) / 20.0 ))

    # #print("n-samples: " + str(n_samples) + "  over " + str(n_pages)+ " pages")
    
    # samples = get_samples(cookie, x_auth, n_samples * 2)
    # for sample in tqdm(samples):
        # #print(sample)
        # #print(sample['ID'])
        
        # sample_data = scrape_sample(cookie, x_auth, sample['ID'])
        # if 'EXECUTED-WORKFLOWS' not in sample_data:
            # print ("warning - odd sample" + sample['IDAT'] + " " + sample['SAMPLE-NAME'])
        # else:
            # for wf in sample_data['EXECUTED-WORKFLOWS']:
                # fn = "cache/sample_"+str(sample['ID'])+"__"+sample['IDAT']+"__"+sample['SAMPLE-NAME'].replace(" ","_")+"__executed-workflow_"+str(wf['ID'])+"__"+wf['WORKFLOW-NAME']+".zip"
                # if not os.path.exists(fn):
                    # download(cookie, x_auth , wf['ID'], fn)
    

main()



"""



