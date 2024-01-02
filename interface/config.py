import os
import yaml

# Config Loader
class Config:
    def __init__(self, path='../config.yaml'):
        config_path = os.path.join(os.path.dirname(__file__), path)
        self.config = self.load_config(config_path)
        self.calculate_totals()

    def load_config(self, path):
        with open(path, 'r') as file:
            return yaml.safe_load(file)

    def calculate_totals(self):
        max_width = 0
        max_height = 0

        # Iterate over each row
        for row in self.config['leds']['sections_y']:
            row_width = 0
            row_height = 0

            # Iterate over each column within the row
            for column in row['sections_x']:
                # Calculate the total width and height with offsets
                width_with_offset = column.get('offset_x', 0) + column['section_width']
                height_with_offset = column.get('offset_y', 0) + column['section_height']

                # Update the maximum width and height for the row
                row_width += width_with_offset
                row_height = max(row_height, height_with_offset)

            # Update the maximum canvas size
            max_width = max(max_width, row_width)
            max_height += row_height

        print("INFO: Total canvas size is {} x {} px".format(max_width, max_height))

        self.config['totals'] = {
            'num_pixels': max_width * max_height,
            'canvas_width': max_width,
            'canvas_height': max_height
        }