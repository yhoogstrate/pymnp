#!/usr/bin/env python


import requests
import math
from tqdm import tqdm
import subprocess
import shutil
import os
import logging
import copy

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
classifierWorkflows.add(classifierWorkflowObj(132, "sarcoma_classifier_v12.3_sample_report", "1.0", "..." ))



class job:
    _id = None
    _status = None
    _workflow = None # rename to _tasks
    _sample = None
    
    def __init__(self, jobid, s_workflow, s_sample):
        self._id = int(jobid)
        self._workflow = s_workflow
        self._sample = s_sample
    
    def get_detailed_info(self, app):
        try:
            response = requests.get('https://www.molecularneuropathology.org/api-v1/workflow-run/'+str(self._id), 
                    headers={'Cookie': app._response_cookie ,
                     'Content-Type':'application/json',
                     'X-AUTH-TOKEN': app._response_x_auth})
            
            self._status = response.json()['TASK-RUNS']
        
        except requests.exceptions.RequestException as e:
            log.warning("Could not get detailed info of sample: " + str(self._id) + " -- second attempt after 3 sec")
            
            time.sleep(3)

            try:
                log.warning("failed updating job "+str(self._id)+" at least once, trying again")
                response = requests.get('https://www.molecularneuropathology.org/api-v1/workflow-run/'+str(self._id), 
                        headers={'Cookie': app._response_cookie ,
                         'Content-Type':'application/json',
                         'X-AUTH-TOKEN': app._response_x_auth})
                
                
                self._status = response.json()['TASK-RUNS']
        
            except requests.exceptions.RequestException as e:
                log.error("Could not get detailed info of sample: " + str(self._id) + " after two https attempts")
    
    def remove(self, app):
        # idsample: "<...>", idworkflowrun: "<...>"} # note in web interface, idsample = string, idworkflowrun = int
        
        self._status = {}
        
        response = requests.post('https://www.molecularneuropathology.org/api-v1/remove-workflow-run',
             headers={'Cookie': app._response_cookie ,
                     'Content-Type':'application/json',
                     'X-AUTH-TOKEN': app._response_x_auth},
         json = {"idsample": str(self._sample._id), "idworkflowrun": int(self._id)} )

        out = str(response.json())
        if out != "Done":
            raise Exception("Error: " + out)
        
        self._sample.get_detailed_info(app) # flush


    def restart(self, app):
        
        self._status = {}
        
        js = {"idsample": str(self._sample._id), "idworkflowrun": int(self._id)}
        
        response = requests.post('https://www.molecularneuropathology.org/api-v1/methylation-sample/restart-workflow',
             headers={'Cookie': app._response_cookie ,
                     'Content-Type':'application/json',
                     'X-AUTH-TOKEN': app._response_x_auth},
         json=js )

        out = str(response.json())
        print(out)
        
        self._sample.get_detailed_info(app) # flush

    def get_file_name(self):
        return "".join([
        "cache/",
        
        str(self._workflow._workflow_name_full),
        "__v",
        str(self._workflow._workflow_version),
        "__",
        str(self._workflow._workflow_id),
        
        "/",

        # sample
        str(self._sample._idat),
        "__",
        str(self._sample._name),
        "__",
        str(self._sample._id),
        "____",
        
        # workflow
        str(self._workflow._workflow_name_full),
        "__v",
        str(self._workflow._workflow_version),
        "__",
        str(self._workflow._workflow_id),
        "____",
        
        # run
        "run-",
        str(self._id),
        ".zip"])

    def is_downloaded(self):
        if os.path.isfile(self.get_file_name()):
            return True
        else:
            return False

    def is_downloadable(self):
        for task in self._status:
            if task['STATUS'] != "complete":
                return False
        
        return not self.is_downloaded()

    def download(self, app):
        fn = self.get_file_name()
        
        path = os.path.dirname(fn)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        
        log.info("Downloading: "+str(self._sample._name[0:25]) + " - " + str(self._workflow._workflow_name_short)[0:20] + "v"+str(self._workflow._workflow_version)+" - " + str(self._id))
        
        with requests.get("https://www.molecularneuropathology.org/api-v1/workflow-run-dowload-complete/" + str(self._id),
         headers={'Cookie': app._response_cookie,
         'Accept': 'application/zip',
            'X-AUTH-TOKEN': app._response_x_auth}, stream=True) as r:
            with open(fn, "wb") as fh:
                shutil.copyfileobj(r.raw, fh)
        
        if not is_valid_zipfile(fn):
            os.remove(fn)
            log.warning("Seems like an invalid file is accessible at the portal. The downloaded file and job will be removed automatically: " + fn)
            self.remove(app)




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
        new_workflows = {}
        #'@todo this._workflows = "updating"
        
        try:
            response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/details/'+str(self._id), 
                headers={'Cookie': app._response_cookie ,
                 'Content-Type':'application/json',
                 'X-AUTH-TOKEN': app._response_x_auth})
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)
        
        self._ext = response.json()

        if 'AVAILABLE-WORKFLOWS' not in self._ext:
            self._ext['AVAILABLE-WORKFLOWS'] = {}
            log.error("incomplete update response: " + str(self._ext))
            
        if 'EXECUTED-WORKFLOWS' not in self._ext:
            self._ext['EXECUTED-WORKFLOWS'] = {}
            log.error("incomplete update response: " + str(self._ext))

        for wd in self._ext['AVAILABLE-WORKFLOWS']:
            cwf = classifierWorkflows.get(wd['ID'])
            
            if cwf in new_workflows:
                log.error("Duplicate workflow " + wd['ID'], " -- in http response?")
                raise Exception("Duplicate workflow " + wd['ID'], " -- in http response?")
            
            new_workflows[cwf] = {'status':'available','jobs':{}}
        
        for wd in self._ext['EXECUTED-WORKFLOWS']: # may contain duplicate entries - one for each finished job
            cwf = classifierWorkflows.get(wd['WORKFLOW-ID'])
            
            if cwf not in new_workflows:
                new_workflows[cwf] = {'status':'done','jobs':{}}
            
            new_workflows[cwf]['jobs'][wd['ID']] = job(wd['ID'], cwf, self)
            new_workflows[cwf]['jobs'][wd['ID']].get_detailed_info(app)
        
        for wd in classifierWorkflows:
            if wd not in new_workflows:
                new_workflows[wd] = {'status':'unavailable','jobs': None}
        
        self._workflows = new_workflows
    
    def get_job(self, job_id): # needs error catching
        for jobs in self._workflows.values():
            print("jobs  ", jobs['jobs'])
            if jobs['jobs'] != None:
                for job in jobs['jobs'].values():
                    print(job)
                    print("jj", job._id, " == ",job_id)
                    if int(job._id) == int(job_id):
                        print("match")
                        return job
            
        raise Exception("job " + str(job_id) + " not found")

    def execute_workflow(self, app, workflow):
        response = requests.post('https://www.molecularneuropathology.org/api-v1/methylation-sample/execute-workflow',
             headers={'Cookie': app._response_cookie ,
                     'Content-Type':'application/json',
                     'X-AUTH-TOKEN': app._response_x_auth},
         json = {"idsample": str(self._id), "idworkflow": int(workflow._workflow_id)} )

        out = str(response.json())
        print(out)
        #if out != "Done":
        #    raise Exception("Error: " + out)
        
        self.get_detailed_info(app) # flush




    def remove(self, app):
        log.info("removing sample: " + str(self._id) + "  --  " + str(self._idat) + " -- " + str(self._name))
        
        response = requests.post('https://www.molecularneuropathology.org/api-v1/remove-sample',
             headers={'Cookie': app._response_cookie ,
                     'Content-Type':'application/json',
                     'X-AUTH-TOKEN': app._response_x_auth},
         json = {"idsample": str(self._id)} )

        try:
            out = str(response.json())
        
            time.sleep(0.25) # 250ms
            #self.get_detailed_info(app)
            app.update_samples_sparse() # automatically reduces size of list
        except:
            raise Exception("Failed removing sample: " + str(self._id))




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
        
        try:
            self._response_x_auth = requests.post('https://www.molecularneuropathology.org/api-v1/authenticate', json = {"email": self._user,"password": self._pwd} ).json()['X-AUTH-TOKEN']
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)
        
        try:
            self._response_cookie = requests.post('https://www.molecularneuropathology.org/authenticate', data = {"email":self._user,"password":self._pwd} ).headers['Set-Cookie']
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)
        
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



    def update_samples(self, detailed = True):
        n = self.get_sample_count() # n used to query list

        self._samples = {} # flush
        self._n_samples = 0
        
        logging.info("Getting sample overview -- n="+str(n))
        
        response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/list/'+str(n)+'/0', 
        headers={'Cookie': self._response_cookie ,
                 'Content-Type':'application/json',
                 'X-AUTH-TOKEN': self._response_x_auth})
        
        raw_out = response.json()
        log.info("update samples: " + str(raw_out)[0:100])
        
        i = 0
        for _ in tqdm(raw_out):
            s = sample(_['IDAT'], _['ID'], _['SAMPLE-NAME'], _['CREATED-AT'], _['CHIP-TYPE'], _['EXTRACTION-TYPE'])
            
            if detailed:
                s.get_detailed_info(self)
            
            self.add_sample(s)
            i += 1
            
            yield s
        
        if i != n:
            raise Exception(str(n) + " samples expected, only "+str(i)+" provided by the query")

    def update_samples_sparse(self):
        """
        updates sample list, without refreshing those already present
        """
        n = self.get_sample_count() # for validation
        #n = 100
        
        logging.info("Getting sample overview")
        
        response = requests.get('https://www.molecularneuropathology.org/api-v1/methylation-samples/list/'+str(n)+'/0', 
        headers={'Cookie': self._response_cookie ,
                 'Content-Type':'application/json',
                 'X-AUTH-TOKEN': self._response_x_auth})
        
        raw_out = response.json()
        
        existing_samples = []
        new_samples = []
        
        for _ in tqdm(raw_out):
            s = self.get_sample(_['ID'], _['IDAT'])
            if s is not None:
                existing_samples.append(s)
            else:
                s = sample(_['IDAT'], _['ID'], _['SAMPLE-NAME'], _['CREATED-AT'], _['CHIP-TYPE'], _['EXTRACTION-TYPE'])
                s.get_detailed_info(self)
                new_samples.append(s)

        i = 0
        
        self._samples = {}
        self._n_samples = 0
        for _ in existing_samples + new_samples:
            self.add_sample(_)
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
    
    def get_sample(self, sample_id, sample_idat):
        if sample_idat in self._samples:
            samples = self._samples[sample_idat]
        
            for s in samples:
                if str(s._id) == str(sample_id):
                    return s
            
        return None
        
    
    def get_samples(self):
        out = []
        
        for sample in self:
            out.append(sample)
        
        return out
    
    def __len__(self):
        return self._n_samples




"""
def download_file(cookie, x_auth_token, fid, filename_out):
    with requests.get("https://www.molecularneuropathology.org/api-v1/workflow-run-dowload-complete/" + str(fid),
     headers={'Cookie': cookie,
     'Accept': 'application/zip',
        'X-AUTH-TOKEN': x_auth_token}, stream=True) as r:
        with open(filename_out, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)
"""

def is_valid_zipfile(zipfile):
    result = subprocess.run(['unzip', '-t', zipfile], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        
    return (result.returncode == 0)


