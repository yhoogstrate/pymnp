#!/bin/bash


if [ ! -d ".venv" ] 
then
    virtualenv -p /usr/bin/python3 .venv
fi

source .venv/bin/activate
pip install .

