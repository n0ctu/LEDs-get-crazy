#!/bin/bash

PROJECT_DIR=$(realpath $(dirname "$0"))

# Consent
cat << "EOF"
 _     _____ ____                   _                              
| |   | ____|  _ \ ___    __ _  ___| |_    ___ _ __ __ _ _____   _ 
| |   |  _| | | | / __|  / _` |/ _ \ __|  / __| '__/ _` |_  / | | |
| |___| |___| |_| \__ \ | (_| |  __/ |_  | (__| | | (_| |/ /| |_| |
|_____|_____|____/|___/  \__, |\___|\__|  \___|_|  \__,_/___|\__, |
                         |___/                               |___/ 
EOF
echo
echo "This script will set up all the requirements for the UDP interface to run, including the creation of a new low-privileged user and an auto-starting systemd service."
echo "It will modify the file permissions for $PROJECT_DIR. Is this the right folder?"
echo
read -p "Press any key to continue ... "

echo "Check if sudo is installed..."
if ! command -v sudo &> /dev/null
then
    echo "ERROR: Sudo needs to be installed for this script to work"
    exit
fi

#sudo apt update
#sudo apt -y upgrade

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
sudo chmod +x "$PROJECT_DIR"/setup-systemd.sh
sudo chmod +x "$PROJECT_DIR"/start-interface.sh

# Define systemd service files for the interface and web components
INTERFACE_SERVICE="[Unit]
Description=LEDs-get-crazy UDP interface
After=network.target

[Service]
Type=simple
User=ledsgc
Group=ledsgc
ExecStart=$(pwd)/start-interface.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"

# Write the service file
echo "$INTERFACE_SERVICE" | sudo tee /etc/systemd/system/ledsgc.service &> /dev/null

# Reload systemd to recognize new services
sudo systemctl daemon-reload

# Enable the services to start on boot
sudo systemctl enable ledsgc.service
echo "Systemd service 'ledsgc.service' has been set up and enabled."
