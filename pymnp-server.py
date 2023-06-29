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
    
    #app._samples = subsample(app, 15)
    #app._n_samples = 15
    
    
    for s in tqdm(app):
        s.get_detailed_info(app)

    
    return render_template('scrape.html', posts=[]) # trigger that updating has completed
