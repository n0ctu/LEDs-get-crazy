#!/bin/bash

PROJECT_DIR=$(realpath $(realpath $(dirname "$0"))/..)

# Systemd daemon 'ledsgc.service'
INTERFACE_SERVICE="[Unit]
Description=LEDs-get-crazy UDP interface
After=network.target

[Service]
Type=simple
User=ledsgc
Group=ledsgc
ExecStart=$($PROJECT_DIR)/start-interface.sh
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

sudo systemctl start ledsgc.service
echo "Systemd service 'ledsgc.service' has been started."