import os, sys
import time
import socket
import json
from text import Text
from preview import Preview
from canvas import Canvas

from utils import bytes_to_rgb


class Interface:
    def __init__(self, config):
        self.config = config.config
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
        #status(canvas, "INFO: Web interface IP address is " + ip, "ready ^-^  " + ipl, "green")

        # Initialize the canvas
        canvas = Canvas(self.config)

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
                    #update_leds(canvas, data)
                    self.rgb_data = bytes_to_rgb(data)
                    #self.preview.update(self.rgb_data)
                    last_process_time = current_time
                    counter += 1
                
                    if counter % 100 == 0:
                        print("INFO: Received " + str(counter) + " datagrams so far.")
            except KeyboardInterrupt:
                #status("INFO: Aborted by user interaction.", "aborted by user x_x", "red")
                print("graceful exit") # to be replaced
                sys.exit(0)
            except socket.timeout:
                #status("INFO: No signal received for " + str(self.config['udp']['timeout']) + " seconds.", "no signal ä ", "white")
                print("INFO: Received " + str(counter) + " datagrams since listener is active.")
            except Exception as e:
                #status("ERROR: " + str(e), "error x_x" + str(e), "red")
                print("ERROR: " + str(e))
                break
