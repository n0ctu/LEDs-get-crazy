# LEDs-get-crazy
A Python program for Raspberry Pi and other SBCs to easily manage and interact with LED strips or LED matrices over a network, configurable using yaml.

## Idea/Concept

This repository is the heart of the project as it contains a UDP/Neopixel interface that provides a neat abstraction between the hardware (or the Neopixel library) and various other software components.

It can be used to manage one or more LED strips or LED matrices and patch them together to create a single, bigger canvas. Other programs then just need to know about the simple protocol and about the total size of the canvas to interact with the LEDs. It supports rate limiting and automatic buffer-flushing to reduce the the load on the SBC even when there's a lot of traffic incoming (\*cough\* at a hacker conference, for example).

The interface needs to run on a supported platform and demands special privileges to access hardware pins. Thus, the setup script can be used to create a corresponding user and a systemd service to handle everything without needing root privileges.

### Protocol

The protocol couldn't be simpler. The UDP interface listens on a port (default 54321) and expects byte arrays. Each three bytes represent a single pixel (RGB). To illuminate the first pixel in red, simply send a UDP datagram containing `\xff\x00\x00`.

## Requirements

- Linux operating system with systemd (tested on Raspbian, Debian Bullseye, yet to test on Bookworm)
- Python 3.7 or newer

## Installation

1. Customize `config.yaml` to your needs. The file contains a few comments to help you get started. Also there's a fully fledged example configuration in `config.full-example.yaml`.
2. Simply run `sudo ./setup-systemd.sh` to install all requirements and the systemd service.
3. The service will immediately be started if the configuration is valid. You can check the status using `systemctl status ledsgc`.
4. Send some UDP data to `127.0.0.1:54321`! E.g. `echo -ne '\xff\x00\x00' | nc -u`