#!/bin/sh
export FLASK_APP=./src/index.py
source $(pipenv --venv)/Scripts/activate
flask run -h 0.0.0.0