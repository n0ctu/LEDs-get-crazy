import os
import time
import socket
import json
from text import Text
from preview import Preview

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

    def bytes_to_rgb(self, data):
        # Convert the received bytearray data to a list of RGB tuples
        rgb_data = []
        for i in range(0, len(data), 3):
            rgb_data.append((data[i], data[i+1], data[i+2]))
        return rgb_data  # Should return a list of (R, G, B) tuples

    def udp_listener(self):
        # Init listener
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.config['udp']['listen_ip'], self.config['udp']['listen_port'])
        sock.bind(server_address)
        sock.settimeout(self.config['udp']['timeout'])
        print('INFO: Listen on {} UDP port {}'.format(*server_address))

        counter = 0
        last_process_time = 0
        min_interval = 1 / self.config['udp']['fps_hardlimit']

        ipl = self.ip.replace(".", ". ")
        #status(canvas, "INFO: Web interface IP address is " + ip, "ready ^-^  " + ipl, "green")

        while True:
            try:
                # Process the next datagram immediately if no pending datagrams
                sock.setblocking(1)
                sock.settimeout(self.config['udp']['timeout'])
                data, address = sock.recvfrom(self.config['totals']['total_leds'] * 4)

                # Check for any newer datagrams and keep the latest
                while True:
                    try:
                        sock.setblocking(0)
                        data, address = sock.recvfrom(self.config['totals']['total_leds'] * 4)
                    except socket.error:
                        # No more datagrams, break the loop
                        break

                # Process the most recent datagram if the interval has passed
                current_time = time.time()
                if current_time - last_process_time >= min_interval:
                    #update_leds(canvas, data)
                    self.rgb_data = self.bytes_to_rgb(data)
                    self.preview.update(self.rgb_data)
                    last_process_time = current_time
                    counter += 1
                
                    if counter % 100 == 0:
                        print("INFO: Received " + str(counter) + " datagrams so far.")

            except socket.timeout:
                #status("INFO: No signal received for " + str(self.config['udp']['timeout']) + " seconds.", "no signal ä ", "white")
                print("INFO: Received " + str(counter) + " datagrams since listener is active.")
            except Exception as e:
                #status("ERROR: " + str(e), "error x_x" + str(e), "red")
                break
