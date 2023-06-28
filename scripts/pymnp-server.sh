#!/bin/bash

source .venv/bin/activate

export FLASK_APP=mnpweb
export FLASK_ENV=development

flask run

