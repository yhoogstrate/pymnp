#!/usr/bin/env python


import requests
import math
from tqdm import tqdm
import shutil
import os


class classifierWorkflowObj:
    _workflow_id = None
    _workflow_name = None
    _workflow_version = None
    _workflow_description = None
    
    def __init__(self, cw_id, cw_name, cw_version, cw_description):
        self._workflow_id = cw_id
        self._workflow_name = cw_name
        self._workflow_version = cw_version
        self._workflow_description = cw_description
        

class classifierWorkflowsObj:
    _map = {}
    
    def add(self, c):
        self._map[c._workflow_id] = c
    
    def get(self, w_id):
        if not w_id in self._map:
            raise Exception("unknown workflow: " + str(w_id))
        else:
            return self._map[w_id]


classifierWorkflows = classifierWorkflowsObj()
classifierWorkflows.add(classifierWorkflowObj( 114, "sarcoma_classifier_v12.2_sample_report", "3.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 121, "medulloblastoma_classifier_v1.0_sample_report", "3.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 122, "brain_classifier_v11b4_sample_report", "3.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 123, "brain_classifier_v12.5_research_report", "1.0", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 124, "brain_classifier_v11b4_sample_report", "3.2", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 125, "brain_classifier_v11b4_sample_report", "3.3", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 126, "brain_classifier_v12.5_sample_report", "1.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 127, "skin_classifier_v0.1_research_report", "1.0", "..." ))
classifierWorkflows.add(classifierWorkflowObj( 131, "brain_classifier_v12.8_sample_report", "1.1", "..." ))




class sample:
    pass


# most elegant way would be to have this class in four states:
# - uninitialized
# - credentials loaded (blocks everything except login)
# - logged in (blocks loading credentials)
# - error
class mnpscrape:
    _user = None
    _pwd = None
    
    _response1 = None # x-auth-token
    _response2 = None # cookie
    
    _samples = None
    
    
    def get_config(self):
        with open('config.txt', 'r') as fh:
            for line in fh:
                line = line.strip().split("=",1)
                
                if len(line) == 2 and line[0] == "user":
                    self._user = line[1]
                
                elif len(line) == 2 and line[0] == "pwd":
                    self._pwd = line[1]

        if self._user is None or self._pwd is None:
            raise Exception("config error")
        
        return True


    def login(self):
        self.get_config()
        
        print("[login]")
        self._response1 = requests.post('https://www.molecularneuropathology.org/api-v1/authenticate', json = {"email": self._user,"password": self._pwd} )
        print("x-auth:" + self._response1.json()['X-AUTH-TOKEN'])


        self._response2 = requests.post('https://www.molecularneuropathology.org/authenticate', data = {"email":self._user,"password":self._pwd} )
        print("cookie: " + self._response2.headers['Set-Cookie'])
        
        # remove from memory, credentials have been used, respones are enough
        self._user = None
        self._pwd = None
        
        return True


    def get_sample_count(self):
        
        print({'Cookie': cookie})
        
        response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/count', headers={'Cookie': cookie,
         'Content-Type':'application/json',
         'X-AUTH-TOKEN': x_auth_token})
        
        
        out = ""
        for _ in response.iter_lines():
            out += _.decode('utf-8')
        
        return(int(out))



    def get_samples(self):
        n = self.get_sample_count() + 2 # for validation
        
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



def download_file(cookie, x_auth_token, fid, filename_out):
    with requests.get("https://www.molecularneuropathology.org/api-v1/workflow-run-dowload-complete/" + str(fid),
     headers={'Cookie': cookie,
     'Accept': 'application/zip',
        'X-AUTH-TOKEN': x_auth_token}, stream=True) as r:
        with open(filename_out, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)





