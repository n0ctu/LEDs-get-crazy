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
echo "This script will guide you through the setup of the UDP interface."

allowed_base=0
case "${PROJECT_DIR}" in
  /home/*|/opt/*|/srv/*|/server/*|/data/*) allowed_base=1 ;;
esac
if [ "${allowed_base}" -ne 1 ]; then
  echo -e "\033[31mERROR: Installation is not under an allowed base path (/home, /opt, /srv, /server, /data): ${PROJECT_DIR}\033[0m"
  echo "Please move the project folder to an allowed location and run this script from there again."
  exit 1
fi

if [[ "$EUID" -eq 0 && $PROJECT_DIR == /home/* ]]; then 
    echo
    echo -e "\033[31mERROR: If this folder is located in your home directory, run this script without 'sudo' or 'su'! This makes sure you will still own all files created during setup.\033[0m"
    exit 1
fi

if ! command -v sudo &> /dev/null
then
    echo
    echo -e '\033[31mERROR: Sudo needs to be installed for this script to work\033[0m'
    exit 1
fi

echo
echo "This will install missing dependencies and applies changes to $PROJECT_DIR. Is this the right folder?"

while true; do
    read -p "Type 'y' to continue, or 'n' to skip: " user_choice

    if [ "$user_choice" = "y" ]; then
        sudo chmod +x scripts/setup-dependencies.sh
        ./scripts/setup-dependencies.sh
        break
    elif [ "$user_choice" = "n" ]; then
        echo "Dependency installation skipped."
        break
    else
        echo "Invalid input. Please type 'y' or 'n'."
    fi
done

echo
echo "Do you want to setup the systemd daemon 'ledsgc.service'?"
echo "This makes the UDP interface automatically start on boot and run in the background."

while true; do
    read -p "Type 'y' to install, or 'n' to skip: " user_choice

    if [ "$user_choice" = "y" ]; then
        sudo chmod +x scripts/setup-daemon.sh
        ./scripts/setup-daemon.sh
        break
    elif [ "$user_choice" = "n" ]; then
        echo "Daemon installation skipped."
        break
    else
        echo "Invalid input. Please type 'y' or 'n'."
    fi
done

echo
echo "All done. Run this script again if you want to change thigns. Bye!"
read -p "Press any key to exit ..."