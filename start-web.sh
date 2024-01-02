#!/bin/bash

# Activate the virtual environment
source $(dirname $0)/venv/bin/activate

# Start the web component
python $(dirname $0)/webapp.py
