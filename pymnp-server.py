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
    
    # save
    # https://www.digitalocean.com/community/tutorials/python-pickle-example
    
    return render_template('scrape.html', posts=[]) # trigger that updating has completed


@webapp.route('/scrape-list')
def scrape_list():
    app.update_samples_sparse()
    
    
    return render_template('scrape.html', posts=[]) # trigger that updating has completed




@webapp.route("/sample/<int:sample_id>:<sample_idat>/job/<int:job_id>/remove_job")
def delete_job(sample_id, sample_idat, job_id):
    log.info(str(sample_id))
    log.info(str(sample_idat))
    log.info(str(job_id))
    
    try:
        sample = app.get_sample(str(sample_id), str(sample_idat))
    
        log.info(str(sample))
    except:
        log.error("Could not find sample: " + str(sample_id) + " -- " + str(sample_idat) + " -- " + str(job_id))

        return "error - please refresh"
    
    try:
        job = sample.get_job(int(job_id))
        log.info(str(job))
    except:
        sample.get_detailed_info(app)
        log.error("Could not find job: " + str(sample_id) + " -- " + str(sample_idat) + " -- " + str(job_id))

        return "error - please refresh"
    
    try:
        job.remove(app)
    except:
        log.error("Could not remove job: " + str(sample_id) + " -- " + str(sample_idat) + " -- " + str(job_id))
        return "error - please refresh"

    return "done"


@webapp.route("/sample/<int:sample_id>:<sample_idat>/job/<int:job_id>/restart_job")
def restart_job(sample_id, sample_idat, job_id):
    log.info("restarting job " + str(sample_id) + " -- " + str(sample_idat)+ " -- " + str(job_id))
    
    try:
        sample = app.get_sample(str(sample_id), str(sample_idat))
        
        log.info(str(sample))
    except:
        log.error("Could not get sample: " + str(sample_id) + " -- " + str(sample_idat))
    
    try:
        job = sample.get_job(int(job_id))
        
        log.info(str(job))
    except:
        sample.get_detailed_info(app)
        
        log.error("Could not get job: " + str(job_id))
    
    job.restart(app)
    
    return "done restarting: " + str(sample_id) + " -- " + str(job_id)



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
    
    try:
        sample = app.get_sample(str(sample_id), str(sample_idat))

        log.info(str(sample))
    except:
        log.error("Could not find sample: " + str(sample_id) + " -- " + str(sample_idat))

        return "error - please refresh"

    
    sample.get_detailed_info(app)
    
    return 'done refreshing'


@webapp.route("/sample/<int:sample_id>:<sample_idat>/remove_sample")
def remove_sample(sample_id, sample_idat):
    print(sample_id)
    print(sample_idat)
    
    sample = app.get_sample(str(sample_id), str(sample_idat))
    print(sample)
    
    sample.remove(app)
    
    return 'done removing and refreshing'




