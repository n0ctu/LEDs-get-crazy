import os
import yaml

# Config Loader
class Config:
    def __init__(self, path='../config.yaml'):
        config_path = os.path.join(os.path.dirname(__file__), path)
        self.config = self.load_config(config_path)
        self.total_leds = 0
        self.total_canvas_width = 0
        self.total_canvas_height = 0
        self.calculate_totals()

    def load_config(self, path):
        with open(path, 'r') as file:
            return yaml.safe_load(file)

    def calculate_totals(self):
        for section_x in self.config['leds']['sections_x']:
            for section_y in section_x['sections_y']:
                self.total_leds += section_y['canvas_width'] * section_y['canvas_height']
                self.total_canvas_width += section_y['canvas_width']
                self.total_canvas_height += section_y['canvas_height']
        
        self.config['totals'] = {
            'total_leds': self.total_leds,
            'total_canvas_width': self.total_canvas_width,
            'total_canvas_height': self.total_canvas_height
        }