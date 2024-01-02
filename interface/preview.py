import requests
import json

class Preview:
    def __init__ (self, config):
        self.config = config.config
        self.width = config.config['totals']['canvas_width']
        self.height = config.config['totals']['canvas_height']

    def update(self, rgb_array):
        # Send array of rgb tuples to http server as json
        url = "http://127.0.0.1:" + str(self.config['web']['listen_port']) + "/api/preview"
        # Add canvas width, height and rgb array to payload as json
        payload = json.dumps({"width": self.width, "height": self.height, "rgb_array": rgb_array})
        headers = {"content-type": "application/json"}
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 200:
            return False
        else:
            return True
        
