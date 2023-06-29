#!/usr/bin/env python


import requests
import math
from tqdm import tqdm
import shutil
import os
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class classifierWorkflowObj:
    _workflow_id = None
    _workflow_name_full = None
    _workflow_name_short = None
    _workflow_version = None
    _workflow_description = None
    
    def __init__(self, cw_id, cw_name, cw_version, cw_description):
        self._workflow_id = cw_id
        self._workflow_name_full = cw_name
        self._workflow_name_short = cw_name.replace("_classifier","").replace("_report","").replace("_research","-R").replace("_sample","-S")
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
    
    def __iter__(self):
        for key in sorted(self._map.keys()):
            yield self._map[key]
    
    def __len__(self):
        return len(self._map)

    def get_workflows(self):
        out = []
        
        for _ in self:
            out.append(_)
        
        return out


classifierWorkflows = classifierWorkflowsObj()
classifierWorkflows.add(classifierWorkflowObj(114, "sarcoma_classifier_v12.2_sample_report", "3.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj(121, "medulloblastoma_classifier_v1.0_sample_report", "3.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj(122, "brain_classifier_v11b4_sample_report", "3.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj(123, "brain_classifier_v12.5_research_report", "1.0", "..." ))
classifierWorkflows.add(classifierWorkflowObj(124, "brain_classifier_v11b4_sample_report", "3.2", "..." ))
classifierWorkflows.add(classifierWorkflowObj(125, "brain_classifier_v11b4_sample_report", "3.3", "..." ))
classifierWorkflows.add(classifierWorkflowObj(126, "brain_classifier_v12.5_sample_report", "1.1", "..." ))
classifierWorkflows.add(classifierWorkflowObj(127, "skin_classifier_v0.1_research_report", "1.0", "..." ))
classifierWorkflows.add(classifierWorkflowObj(130, "brain_classifier_v12.8_sample_report", "1.0", "..." )) # should be unavailable
classifierWorkflows.add(classifierWorkflowObj(131, "brain_classifier_v12.8_sample_report", "1.1", "..." ))




class sample:
    _idat = None
    _id = None
    _name = None
    _created_at = None
    _chip_type = None
    _extraction_type = None
    
    _ext = None
    _workflows = None
    
    def __init__(self, s_idat, s_id, s_name, s_created_at, s_chip_type, s_extraction_type):
        self._idat = s_idat
        self._id = s_id
        self._name = s_name
        self._created_at = s_created_at
        self._chip_type = s_chip_type
        self._extraction_type = s_extraction_type

    def get_detailed_info(self, app):
        response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/details/'+str(self._id), 
                headers={'Cookie': app._response_cookie ,
                 'Content-Type':'application/json',
                 'X-AUTH-TOKEN': app._response_x_auth})
    
        self._ext = response.json()
        self._workflows = {}

        for wd in self._ext['AVAILABLE-WORKFLOWS']:
            cwf = classifierWorkflows.get(wd['ID'])
            
            if cwf in self._workflows:
                raise Exception("Duplicate workflow " + wd['ID'])
            
            self._workflows[cwf] = {'status':'available','jobs':[]}
        
        for wd in self._ext['EXECUTED-WORKFLOWS']:
            cwf = classifierWorkflows.get(wd['WORKFLOW-ID'])
            
            if cwf in self._workflows:
                raise Exception("Duplicate workflow " + wd['WORKFLOW-ID'])
            
            self._workflows[cwf] = {'status':'done','jobs':[]}
        
        for wd in classifierWorkflows:
            if wd not in self._workflows:
                self._workflows[wd] = {'status':'unavailable','jobs':[]}




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
    
    _n_samples = 0
    _samples = {}
    
    
    def get_config(self):
        logging.info("Reading credentials")
        
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
        
        logging.info("Authenticating to the portal")
        self._response_x_auth = requests.post('https://www.molecularneuropathology.org/api-v1/authenticate', json = {"email": self._user,"password": self._pwd} ).json()['X-AUTH-TOKEN']
        self._response_cookie = requests.post('https://www.molecularneuropathology.org/authenticate', data = {"email":self._user,"password":self._pwd} ).headers['Set-Cookie']
        
        # remove from memory, credentials have been used, respones are enough
        self._user = None
        self._pwd = None

        logging.info("Authenticating to the portal: done")
        
        return True


    def get_sample_count(self):
        logging.info("Getting number of samples listed")
        
        response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/count', 
                headers={'Cookie': self._response_cookie,
                 'Content-Type':'application/json',
                 'X-AUTH-TOKEN': self._response_x_auth})
        
        
        out = ""
        for _ in response.iter_lines():
            out += _.decode('utf-8')
        
        
        logging.info("Getting number of samples listed: " + out)
        
        out = int(out)
        
        return out



    def update_samples(self):
        n = self.get_sample_count() # for validation
        
        logging.info("Getting sample overview")
        
        response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/list/'+str(n)+'/0', 
        headers={'Cookie': self._response_cookie ,
                 'Content-Type':'application/json',
                 'X-AUTH-TOKEN': self._response_x_auth})
        
        raw_out = response.json()
        
        i = 0
        for _ in raw_out:
            self.add_sample(sample(_['IDAT'], _['ID'], _['SAMPLE-NAME'], _['CREATED-AT'], _['CHIP-TYPE'], _['EXTRACTION-TYPE']))
            i += 1
        
        if i != n:
            raise Exception(str(n) + " samples expected, only "+str(i)+" provided by the query")
        
        return n

    def add_sample(self, sample_s):
        
        if sample_s._idat in self._samples:
            log.warning("Duplicate -- " + sample_s._idat)
        else:
            self._samples[sample_s._idat] = []
        
        self._samples[sample_s._idat].append(sample_s)
        self._n_samples += 1
    
    
    def __iter__(self):
        for idat in self._samples:
            for s in self._samples[idat]:
                yield s
    
    def get_samples(self):
        out = []
        
        for sample in self:
            out.append(sample)
        
        return out
    
    def __len__(self):
        return self._n_samples





def download_file(cookie, x_auth_token, fid, filename_out):
    with requests.get("https://www.molecularneuropathology.org/api-v1/workflow-run-dowload-complete/" + str(fid),
     headers={'Cookie': cookie,
     'Accept': 'application/zip',
        'X-AUTH-TOKEN': x_auth_token}, stream=True) as r:
        with open(filename_out, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)





