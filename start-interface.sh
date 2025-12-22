#!/bin/bash

echo "Starting interface with command:"
echo "$(dirname $0)/venv/bin/python $(dirname $0)/interface/main.py"

# Start the interface component
$(dirname $0)/venv/bin/python $(dirname $0)/interface/main.py
