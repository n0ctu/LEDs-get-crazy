class Section:
    def __init__(self, pin, section_width, section_height, brightness=1.0, pixel_order='GRB'):
        self._handle_imports()
        if self.supported:
            self.pin = self._init_pin(pin)
        self.section_width = section_width
        self.section_height = section_height
        self.num_pixels = section_width * section_height
        self.brightness = brightness
        self.pixel_order = pixel_order
    
    def _handle_imports(self):
        # Check if the current platform is supported
        try:
            self.board = __import__('board')
            self.neopixel_write = __import__('neopixel_write')
            self.digitalio = __import__('digitalio')
            self.supported = True
        except:
            self.supported = False
            print("WARNING: The UDP interface requires a Raspberry Pi or similar device with GPIO pins. Development/Preview mode only (no board/no neopixel).")

    def _init_pin(self, pin):
        return self.digitalio.DigitalInOut(getattr(self.board, pin))

    def write(self, byte_array):
        if self.supported:
            '''
            To-Do:
            Restructure the data to match the layout of the section
            Calculate the brightness
            Change color order if GRB
            Reverse the whole data if true
            Rotate the whole data if true
            '''

            # Send the data to the LED matrix
            self.neopixel_write.neopixel_write(self.pin, byte_array)


class Canvas:
    def __init__(self, config):
        self.config = config
        self.sections = self.init_sections()

    def init_sections(self):
        sections = []
        # Initialize each section as an object
        for row in self.config['leds']['sections_y']:
            for column in row['sections_x']:
                sections.append(Section(column['pin'], column['section_width'], column['section_height'], column['brightness'], column['pixel_order']))
        return sections

    def update(self, byte_array):
        section_index = 0
        row_y_offset = 0
        bytes_per_pixel = 3 
        total_width_in_bytes = self.config['totals']['canvas_width'] * bytes_per_pixel

        for row in self.config['leds']['sections_y']:
            max_row_height = 0
            for column in row['sections_x']:
                start_x = column.get('offset_x', 0) * bytes_per_pixel
                end_x = (column['section_width']) * bytes_per_pixel
                start_y = row_y_offset + column.get('offset_y', 0)
                end_y = start_y + column['section_height']

                # Extract the section data from the byte array
                section_data = bytearray()
                for y in range(start_y, end_y):
                    row_start_index = y * total_width_in_bytes
                    section_data.extend(byte_array[row_start_index + start_x : row_start_index + start_x + end_x])

                # Send the data to the current section/matrix
                self.sections[section_index].write(section_data)

                section_index += 1
                max_row_height = max(max_row_height, column['section_height'])

            row_y_offset += max_row_height