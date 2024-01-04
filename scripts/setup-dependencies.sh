#!/bin/bash

PROJECT_DIR=$(realpath $(realpath $(dirname "$0"))/..)

echo
echo "STEP 1: Updating your system ..."
sudo apt update
sudo apt -y upgrade

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
echo "STEP 4: Enabling RPi interfaces ..."
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint disable_raspi_config_at_boot 0

echo
echo "STEP 5: Creating system user 'ledsgc' if it not exists yet ..."
if ! id "ledsgc" &>/dev/null; then
    sudo useradd --system --shell /bin/false ledsgc
fi

echo
echo "STEP 6: Adding 'ledsgc' user to the group gpio ..."
sudo adduser ledsgc gpio

echo
echo "STEP 7: Creating venv and installing requirements ..."

cd $PROJECT_DIR
python -m venv venv
venv/bin/pip install -r requirements.txt

echo
echo "STEP 8: Giving 'ledsgc' group access to the program folder ..."
ledsgc_group=$(id -gn ledsgc)
sudo chgrp -R "$ledsgc_group" "$PROJECT_DIR"
sudo find "$PROJECT_DIR" -type d -exec sudo chmod 750 {} +
sudo find "$PROJECT_DIR" -type f -exec sudo chmod 640 {} +
find "$PROJECT_DIR" -type f -name "*.sh" -exec sudo chmod +x {} \;

echo