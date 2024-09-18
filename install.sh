#!/bin/bash

# if setting up virtualenv/pip causes trouble:
# rm -Rf ~/.cache/pip/ ~/.cache/pip-tools/

if [ ! -d ".venv" ] 
then
    virtualenv -p /usr/bin/python3 .venv
fi

source .venv/bin/activate
pip install .

