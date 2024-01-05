# LEDs-get-crazy
A Python program for Raspberry Pi and other SBCs to easily manage and interact with LED strips or LED matrices locally or over a network, configurable using yaml.

## Idea/Concept

This repository is the heart of the project as it contains a UDP/Neopixel interface that provides a neat abstraction between the hardware (or the Neopixel library) and various other software components.

It can be used to manage one or more LED strips or LED matrices and patch them together to create a single, bigger canvas. But you can use it with a single LED strip or matrix as well. Other programs then just need to know about the simple protocol and about the total size of the canvas to interact with the LEDs. It supports rate limiting and automatic buffer-flushing to reduce the load on the SBC even when there's a lot of traffic incoming (\*cough\* at a hacker conference, for example).

### Protocol

The protocol couldn't be simpler. The UDP interface listens on a port (default 54321) and expects byte arrays. Each three bytes represent a single pixel (RGB). To illuminate the first pixel in red, simply send a UDP datagram consisting of `\xff\x00\x00`.

## Requirements

- Linux operating system with **systemd** (tested on Raspbian, Debian Bullseye, yet to test on Bookworm)
- Python >= 3.7.0

## Installation

1. Customize `config.yaml` to your needs. The file contains a few comments to help you get started. Also there's a fully-fledged example in `config.full-example.yaml`.
2. Simply run `sudo ./setup-systemd.sh` to install all the requirements needed and setup the systemd service.
3. The service will immediately be started if the configuration is valid. You can check the status using `systemctl status ledsgc`.
4. Send some UDP data to `127.0.0.1:54321`!

## Usage

Netcat examples:

```bash
echo -ne '\xff\x00\x00\x00\xff\x00\x00\x00\xff' | nc -u 127.0.0.1 54321
```
```bash
cat /dev/urandom | nc -u 127.0.0.1 54321
```

Python examples:

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b'\xff\x00\x00\x00\xff\x00\x00\x00\xff', ('127.0.0.1', 54321))
```