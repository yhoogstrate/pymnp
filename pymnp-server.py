#!/usr/bin/env python

from pymnp.pymnp import *

from flask import Flask, render_template
from tqdm import tqdm
#from run import *


webapp = Flask(__name__)
app = mnpscrape()
app.login()


@webapp.route('/')
def index():
    return render_template('index.html',
        nsamples=app._n_samples,
        posts=app.get_samples(),
        wfs=classifierWorkflows.get_workflows()
        )


def subsample(app, k):
    sslice = {}
    
    i = 0
    for key in app._samples:
        if i < k:
            sslice[key] = []
        
        for ss in app._samples[key]:
            if i < k:
                sslice[key].append(ss)
            i += 1
    
    return sslice


@webapp.route('/scrape')
def scrape():
    app.update_samples()
    
    k = 4
    app._samples = subsample(app, k)
    app._n_samples = k
    
    
    for s in tqdm(app):
        s.get_detailed_info(app)

    # save
    # https://www.digitalocean.com/community/tutorials/python-pickle-example
    
    return render_template('scrape.html', posts=[]) # trigger that updating has completed


@webapp.route("/sample/<int:sample_id>:<sample_idat>/job/<int:job_id>/remove_job")
def delete_job(sample_id, sample_idat, job_id):
    print(sample_id)
    print(sample_idat)
    print(job_id)
    
    sample = app.get_sample(str(sample_id), str(sample_idat))
    
    print(sample)
    
    job = sample.get_job(int(job_id))
    
    print(job)
    
    job.remove(app)
    
    return "going to invoke delete command " + str(sample_id) + " -- " + str(job_id)



@webapp.route("/sample/<int:sample_id>:<sample_idat>/workflow/<int:workflow_id>/execute_job")
def execute_job(sample_id, sample_idat, workflow_id):
    print(sample_id)
    print(sample_idat)
    print(workflow_id)
    
    sample = app.get_sample(str(sample_id), str(sample_idat))
    print(sample)
    
    workflow = classifierWorkflows.get(workflow_id)
    print(workflow)
    
    sample.execute_workflow(app, workflow)
    
    return 'execting job'


@webapp.route("/sample/<int:sample_id>:<sample_idat>/refresh")
def refresh(sample_id, sample_idat):
    print(sample_id)
    print(sample_idat)
    
    sample = app.get_sample(str(sample_id), str(sample_idat))
    print(sample)
    
    sample.get_detailed_info(app)
    
    return 'done refreshing'
    
    

