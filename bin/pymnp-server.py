#!/usr/bin/env python

from pymnp.pymnp import *

from flask import Flask, render_template
from tqdm import tqdm
from run import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.config['SAMPLES'] = []


@app.route('/')
def index():
    return render_template('index.html', posts=app.config['SAMPLES'])


@app.route('/scrape')
def scrape():
    
    
    user, pwd = get_config()
    x_auth, cookie = login(user, pwd)
    cookie = cookie
    
    n_samples = get_sample_count(cookie, x_auth)
    #print("n_samples", n_samples)
    
    app.config['SAMPLES'] = get_samples(cookie, x_auth, n_samples * 2)[0:5]
    
    n = len(app.config['SAMPLES'])
    for i in tqdm(range(n)):
        sample = app.config['SAMPLES'][i]
        app.config['SAMPLES'][i] = scrape_sample(cookie, x_auth, sample['ID'])
    
    print(app.config['SAMPLES'])
    
    return render_template('scrape.html', posts=[])
