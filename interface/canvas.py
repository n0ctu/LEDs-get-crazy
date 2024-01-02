import board
import neopixel

# Check if the current platform is supported
try:
    pass
except:
    print("WARNING: The UDP interface requires a Raspberry Pi or similar device with GPIO pins. Development/Preview mode only (no board/no neopixel).")

class Canvas:
    def __init__(self, config):
        self.config = config.config
        self.sections = self.init_sections()
        
    def init_sections(self):
        sections = {}
        # Initialize each section with a NeoPixel object
        for row in self.config['leds']['sections_y']:
            for column in row['sections_x']:
                pin = getattr(board, column['pin'])
                num_pixels = column['section_width'] * column['section_height']
                pixel_order = neopixel.GRB if column['pixel_order'] == 'GRB' else neopixel.RGB
                sections[column['name']] = neopixel.NeoPixel(pin, num_pixels, brightness=column['brightness'], auto_write=column['auto_write'], pixel_order=pixel_order)
        return sections

    def update(self, rgb_data):
        row_y_offset = 0
        for row in self.config['leds']['sections_y']:
            max_row_height = 0
            for column in row['sections_x']:
                start_x = column.get('offset_x', 0)
                end_x = start_x + column['section_width']
                start_y = row_y_offset + column.get('offset_y', 0)
                end_y = start_y + column['section_height']
                section_data = [rgb_row[start_x:end_x] for rgb_row in rgb_data[start_y:end_y]]
                
                # Send the data to the LED matrix
                self.send_to_matrix(column['name'], section_data)
                
                max_row_height = max(max_row_height, column['section_height'])

            row_y_offset += max_row_height

    def send_to_matrix(self, section_name, data):
        matrix = self.sections[section_name]
        for y, row in enumerate(data):
            for x, color in enumerate(row):
                matrix_index = y * len(row) + x
                matrix[matrix_index] = color
        matrix.show()