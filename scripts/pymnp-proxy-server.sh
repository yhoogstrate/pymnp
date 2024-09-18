#!/bin/bash

source .venv/bin/activate

export FLASK_APP=./pymnp-proxy-server.py
export FLASK_DEBUG=1


flask run

# or run to outside world (not recommended)
# flask run --host=0.0.0.0

