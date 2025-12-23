# LEDs-get-crazy
A tiny python program for Raspberry Pi and other SBCs to easily manage and interact with LED strips or LED matrices locally or over a network, configurable using yaml.

## Idea/Concept

This is a minimalistic UDP/Neopixel interface that allows other programs or devices to control LED strips/matrices by simply sending byte arrays over UDP.

Additionally, it can be used to manage one or more LED strips or LED matrices and patch them together to create a single, bigger canvas. Other programs only need to know about the the total size of the canvas to interact with the LEDs. It does some rate limiting and automatic buffer-flushing to reduce the load on the SBC even when there's a lot of traffic incoming (\*cough\* at a hacker conference, for example).

### Protocol

The protocol is really simple. The UDP interface listens on a port (default 54321) and waits for datagrams consisting of byte arrays. Each three bytes represent a single pixel (RGB). To illuminate the first pixel in red, simply send a UDP datagram consisting of `\xff\x00\x00`. Send more bytes to illuminate more pixels.

## Requirements

- Tested on Raspberry Pi 4 Model B
- Linux operating system with systemd (tested on Raspbian, Bullseye, Bookworm and Trixie)
- Tested with Python >= 3.7.0

## Installation

1. Customize `config.yaml` to your needs. The file contains a few comments to help you get started. Also there's a fully-fledged example in `config.full-example.yaml`.
2. Simply run `./setup.sh` (no sudo) to install all the requirements needed and optionally setup a systemd service when asked.
3. The service will immediately be started if the configuration is valid. You can check the status using `systemctl status ledsgc`. If you didn't setup a systemd service, simply run `sudo ./start-interface.sh` to start the program.
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

## To-Do / Known Issues

- [ ] Fix layout_rotate function (canvas.py, Sections class)
- [ ] Fix the layout_reverse function (canvas.py, Section class)
- [ ] Add a layout_mirror option (canvas.py, Section class)
- [ ] Validation of the yaml configuration, proper error handling and defaults (config.py)
- [ ] Improve text generation (hard breaks) and handling of unknown characters (text.py)
- [ ] Better reset handling instead of trusting the python garbage collector (interface.py)
- ~~[ ] Fix permission issues of the system user (only runs as root currently)~~ wont fix, not possible when using rpi_ws281x lib with DMA