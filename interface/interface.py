import os, sys
import time
import socket
import json
from text import Text
from preview import Preview
from canvas import Canvas
import traceback

from utils import bytes_to_rgb


class Interface:
    def __init__(self, config):
        self.config = config.config
        self.canvas = Canvas(self.config)
        self.preview = Preview(config)
        self.rgb_data = [(0,0,0)]
        self.ip = self.get_ip()

    def get_ip(self):
        # Hacky way to get IP address
        sock_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_temp.connect(("1.1.1.1", 53))
        ip = sock_temp.getsockname()[0]
        sock_temp.close()
        return ip

    def status(self, message, onscreen, color):
        # Init text
        text = Text()
        text.set_canvas_width(self.config['totals']['canvas_width'])
        text.set_canvas_height(self.config['totals']['canvas_height'])

        text.set_background(1, 1, 1)
        if color == "red":
            text.set_foreground(20, 0, 0)
        elif color == "green":
            text.set_foreground(0, 20, 0)
        elif color == "white":
            text.set_foreground(10, 10, 10)

        text.set_font('smol')
        text.set_offset(1, 1)
        text.set_text(onscreen)
        rgb_array = text.output()

        print(message)

        # Unpack array and turn it into a bytearray
        byte_array = bytearray()
        for rgb in rgb_array:
            byte_array.extend(rgb)
        self.canvas.update(byte_array)

    def udp_listener(self):
        # Init listener
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.config['udp']['listen_ip'], self.config['udp']['listen_port'])
        sock.bind(server_address)
        #sock.settimeout(self.config['udp']['timeout'])
        print('INFO: Listen on {} UDP port {}'.format(*server_address))

        counter = 0
        last_process_time = 0
        min_interval = 1 / self.config['udp']['fps_hardlimit']

        ipl = self.ip.replace(".", ". ")
        self.status("INFO: Primary interface IP address is " + self.ip, "ready ^-^   " + ipl, "green")

        while True:
            try:
                # Process the next datagram immediately if no pending datagrams
                sock.setblocking(1)
                sock.settimeout(self.config['udp']['timeout'])
                data, address = sock.recvfrom(self.config['totals']['num_pixels'] * 3)

                # Check for any newer datagrams and keep the latest
                while True:
                    try:
                        sock.setblocking(0)
                        data, address = sock.recvfrom(self.config['totals']['num_pixels'] * 3)
                    except socket.error:
                        # No more datagrams, break the loop
                        break

                # Process the most recent datagram if the interval has passed
                current_time = time.time()
                if current_time - last_process_time >= min_interval:
                    #self.rgb_data = bytes_to_rgb(data)
                    #self.preview.update(self.rgb_data)
                    self.canvas.update(data)
                    last_process_time = current_time
                    counter += 1
                
                    if counter % 100 == 0:
                        print("INFO: Processed " + str(counter) + " datagrams so far.")
            except KeyboardInterrupt:
                self.status("INFO: Exited by user interaction.", "exit by user x_x", "red")
                sys.exit(0)
            except socket.timeout:
                self.status("INFO: No signal received for " + str(self.config['udp']['timeout']) + " seconds.", "no signal ä ", "white")
                print("INFO: Processed " + str(counter) + " datagrams since listener is active.")
            except Exception as e:
                self.status("ERROR: " + str(e), "error x_x" + str(e), "red")
                traceback.print_exc()
                break
