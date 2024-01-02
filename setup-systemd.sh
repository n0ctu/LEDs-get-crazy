#!/bin/bash

echo "This script will set up all requirements for this software to run, including the creation of new low-privileged users and systemd services for the Matrix Interface and Web components to start with the system."
read -p "Press any key to continue... "

echo "Check if python 3 is installed..."
if ! command -v python3 &> /dev/null
then
    apt install python3
    if ! command -v python3 &> /dev/null
    then
        echo "Python 3 could not be installed"
        exit
    fi
fi

echo "Check if venv is installed..."
if ! command -v python3 -m venv &> /dev/null
then
    pip install virtualenv
    if ! command -v python3 -m venv &> /dev/null
    then
        echo "Virtualenv could not be installed"
        exit
    fi
fi

# Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Make the start scripts executable
chmod +x $(pwd)/start-web.sh
chmod +x $(pwd)/start-interface.sh

# Create a new user 'matrix' if it doesn't exist
if ! id "matrix" &>/dev/null; then
    useradd -r -M -s /bin/false matrix
fi

matrix_group=$(id -gn matrix)

sudo chgrp -R "$matrix_group" $(pwd)/webapp
sudo chgrp "$matrix_group" $(pwd)/start-web.sh

sudo chmod -R 775 $(pwd)/webapp
sudo chmod 775 $(pwd)/start-web.sh

# Define systemd service files for the interface and web components
INTERFACE_SERVICE="[Unit]
Description=Matrix UDP Interface
After=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=$(pwd)/start-interface.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"

WEB_SERVICE="[Unit]
Description=Matrix Web Interface
After=network.target

[Service]
Type=simple
User=matrix
Group=matrix
ExecStart=$(pwd)/start-web.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target"

# Write the service files
echo "$INTERFACE_SERVICE" | sudo tee /etc/systemd/system/matrix-interface.service &> /dev/null
echo "$WEB_SERVICE" | sudo tee /etc/systemd/system/matrix-web.service &> /dev/null

# Reload systemd to recognize new services
systemctl daemon-reload

# Enable the services to start on boot
systemctl enable matrix-interface.service
systemctl enable matrix-web.service

echo "Systemd services for Matrix Interface and Web have been set up and enabled."

systemctl start matrix-interface.service
systemctl start matrix-web.service

echo "Matrix Interface and Web services have been started."