#!/bin/bash

PROJECT_DIR=$(realpath "$CURRENT_DIR"/..)

echo "Check if sudo is installed..."
if ! command -v sudo &> /dev/null
then
    echo "ERROR: Sudo needs to be installed for this script to work"
    exit
fi

sudo apt update
sudo apt -y upgrade

echo "Check if python 3 is installed..."
if ! command -v python3 &> /dev/null
then
    sudo apt -y install python3
    if ! command -v python3 &> /dev/null
    then
        echo "ERROR: Python 3 could not be installed"
        exit
    fi
fi

sudo apt -y install python3-pip
sudo apt -y install python3-venv

# Enable RPi features
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint disable_raspi_config_at_boot 0

# Create a new user 'ledsgc' if it doesn't exist
if ! id "ledsgc" &>/dev/null; then
    sudo useradd --system --shell /bin/false ledsgc
fi

# Add the user to the gpio group
sudo adduser ledsgc gpio

# Give the user access rights to the folder
ledsgc_group=$(id -gn ledsgc)
sudo chgrp -R "$ledsgc_group" "$PROJECT_DIR"
sudo chmod -R 770 "$PROJECT_DIR"

# Create a Python virtual environment
cd $PROJECT_DIR
python -m venv venv
# Install Python dependencies
venv/bin/pip install -r requirements.txt

sudo find "$PROJECT_DIR" -type d -exec sudo chmod 750 {} +
sudo find "$PROJECT_DIR" -type f -exec sudo chmod 640 {} +

# Make the scripts executable again
find "$PROJECT_DIR" -type f -name "*.sh" -exec sudo chmod +x {} \;