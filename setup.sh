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
echo "This script will set up all the requirements for the UDP interface to run, including the creation of a new low-privileged user and optionally an auto-starting systemd service."
echo "It will modify the file permissions for $PROJECT_DIR. Is this the right folder?"
echo
read -p "Press any key to continue ... "

./setup-dependencies.sh

echo "Do you want to register the systemd daemon 'ledsgc.service'?"
echo
read -p "Press any key to continue ... "

./setup-daemon.sh

