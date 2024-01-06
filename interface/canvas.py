# The canvas is the abstraction for a collection of LED devices
# It's the preprocessor and 'user-facing' part

class Canvas:
    def __init__(self, config):
        self.config = config
        self.bytes_per_pixel = 3
        self.sections = self.init_sections()

    def init_sections(self):
        sections = []
        # Initialize each section as an object
        for row in self.config['leds']['sections_y']:
            for column in row['sections_x']:
                sections.append(Section(column['pin'], column['section_width'], column['section_height'], column['brightness'], column['pixel_order'], column['layout_fix'], column['layout_reverse'], column['layout_rotate']))
        return sections

    def update(self, byte_array):
        total_width_in_bytes = self.config['totals']['canvas_width'] * self.bytes_per_pixel

        # Pad data if it's shorter than expected or truncate if it's longer
        expected_length = total_width_in_bytes * self.config['totals']['canvas_height']
        if len(byte_array) > expected_length:
            byte_array = byte_array[:expected_length]
        if len(byte_array) < expected_length:
            byte_array += bytes(expected_length - len(byte_array))

        section_index = 0
        row_y_offset = 0

        for row in self.config['leds']['sections_y']:
            max_row_height = 0
            for column in row['sections_x']:
                start_x = column.get('offset_x', 0) * self.bytes_per_pixel
                end_x = (column['section_width']) * self.bytes_per_pixel
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


# Each Section represents one physical pin (one LED strip, matrix, or other arrangement)
# and the logic to send processed data to it

class Section:

    def __init__(self, pin, section_width, section_height, brightness=1.0, pixel_order='GRB', layout_fix=True, layout_reverse=False, layout_rotate=0):
        self._handle_imports(pin)
        self.section_width = section_width
        self.section_height = section_height
        self.num_pixels = section_width * section_height
        self.bytes_per_pixel = 3
        self.brightness = brightness
        self.pixel_order = pixel_order
        self.layout_fix = layout_fix
        self.layout_reverse = layout_reverse
        self.layout_rotate = layout_rotate
    
    def _handle_imports(self, pin):
        # Check if the current platform is supported
        try:
            self.board = __import__('board')
            self.neopixel_write = __import__('neopixel_write')
            self.digitalio = __import__('digitalio')
            self.pin = self._init_pin(pin)
        except:
            self.supported = False
            print("WARNING: The UDP interface requires a Raspberry Pi or similar device with GPIO pins. Development/Preview mode only (no board/no neopixel).")

    def _init_pin(self, pin):
        dpin = self.digitalio.DigitalInOut(getattr(self.board, pin))
        dpin.direction = self.digitalio.Direction.OUTPUT
        return dpin

    def rotate_bytearray(self, input_bytearray, degrees):

        # Convert the bytearray into a 2D list
        matrix = []
        for i in range(self.section_height):
            row = []
            for j in range(self.section_width):
                start_index = (i * self.section_width + j) * self.bytes_per_pixel
                end_index = start_index + self.bytes_per_pixel
                value = input_bytearray[start_index:end_index]
                row.append(value)
            matrix.append(row)

        # Rotate the matrix based on the specified degrees
        if degrees == 90:
            rotated_matrix = [[matrix[self.section_height - 1 - j][i] for j in range(self.section_height)] for i in range(self.section_width)]
        elif degrees == 180:
            rotated_matrix = [row[::-1] for row in matrix[::-1]]
        elif degrees == 270:
            rotated_matrix = [[matrix[j][i] for j in range(self.section_height)] for i in range(self.section_width)][::-1]
        else:
            raise ValueError("Unsupported rotation degrees. Only 90, 180, and 270 degrees are supported.")

        # Convert the rotated matrix back into a bytearray
        rotated_bytearray = bytearray()
        for i in range(self.section_width):
            for j in range(self.section_height):
                if degrees == 0 or degrees == 180:
                    rotated_bytearray += rotated_matrix[j][i]
                elif degrees == 90 or degrees == 270:
                    rotated_bytearray += rotated_matrix[i][j]

        return rotated_bytearray
        
    def write(self, data):
        if self.pin:
            # Check if the input bytearray length is valid
            if len(data) != self.num_pixels * self.bytes_per_pixel:
                raise ValueError("Input bytearray/section size mismatch.")

            # Rotate the layout if needed
            if self.layout_rotate > 0:
                data = self.rotate_bytearray(data, self.layout_rotate)

            # Adjust dimensions after rotation
            effective_width = self.section_height if self.layout_rotate in [90, 270] else self.section_width
            effective_height = self.section_width if self.layout_rotate in [90, 270] else self.section_height

            frame = bytearray(self.num_pixels * self.bytes_per_pixel)

            for i in range(self.num_pixels):
                # Calculate row and position in row based on effective dimensions
                row = i // effective_width
                position_in_row = i % effective_width

                # Reverse every alternate row if layout_fix is true
                if self.layout_fix and row % 2 == 1:
                    position_in_row = effective_width - 1 - position_in_row

                data_index = (row * effective_width + position_in_row) * self.bytes_per_pixel

                # Extract color values based on LED type
                r, g, b = data[data_index:data_index+3]

                # Apply brightness calculation
                r = int(r * self.brightness)
                g = int(g * self.brightness)
                b = int(b * self.brightness)

                # Set the color for each pixel
                if self.pixel_order == "RGB":
                    frame[i*self.bytes_per_pixel:i*self.bytes_per_pixel+3] = bytearray([r, g, b])
                elif self.pixel_order == "GRB":
                    frame[i*self.bytes_per_pixel:i*self.bytes_per_pixel+3] = bytearray([g, r, b])

            # Reverse the layout if needed
            # EDIT: whoops, this also inverts colors, fixme
            if self.layout_reverse:
                frame = frame[::-1]
 
            # Send the data to the LED matrix
            try:
                self.neopixel_write.neopixel_write(self.pin, frame)
            except Exception as e:
                print("ERROR: Failed to write to LED matrix. {}".format(e))
