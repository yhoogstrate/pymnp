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
    
    k = 200
    app._samples = subsample(app, k)
    app._n_samples = k
    
    
    for s in tqdm(app):
        s.get_detailed_info(app)

    # save
    # https://www.digitalocean.com/community/tutorials/python-pickle-example
    
    return render_template('scrape.html', posts=[]) # trigger that updating has completed
