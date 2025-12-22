#!/bin/bash

PROJECT_DIR=$(realpath $(realpath $(dirname "$0"))/..)

echo
echo "STEP 1: Updating your system ..."
sudo apt update
sudo apt -y upgrade
sudo rpi-update

echo
echo "STEP 2: Check if python 3 is installed..."
if ! command -v python3 &> /dev/null
then
    sudo apt -y install python3
    if ! command -v python3 &> /dev/null
    then
        echo "ERROR: Python 3 could not be installed"
        exit
    fi
fi
echo "Python 3 found"

echo
echo "STEP 3: Installing or upgrading python3-pip and python3-venv ..."
sudo apt -y install python3-pip python3-venv

echo
echo "STEP 4: Creating venv and installing requirements ..."

cd "${PROJECT_DIR}"
python -m venv venv
sudo chmod +x venv/bin/pip venv/bin/pip3 venv/bin/python venv/bin/python3
venv/bin/pip install -r requirements.txt

echo