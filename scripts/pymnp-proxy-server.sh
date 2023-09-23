#!/bin/bash

source .venv/bin/activate

export FLASK_APP=./pymnp-proxy-server.py
export FLASK_DEBUG=1

flask run

