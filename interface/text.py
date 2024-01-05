'''
A cannibalized version of the textgen-plugin I wrote. I decided to make a basic version for on-screen status updates.
This code shouldn't be changed for experiments, in order not to break status messages and kill the interface.
'''

import os, time
import json

class Text:

    def __init__(self, font='smol'):

        self.set_canvas_width()
        self.set_canvas_height()
        self.num_pixels = self.canvas_width * self.canvas_height
        self.pixels = [(0, 0, 0)] * self.num_pixels

        # Intermediate steps
        self.array_text = []           # List of lists of 0s and 1s
        self.array_colored = []        # List of lists of RGBW tuples
        self.array_rgbw = self.pixels  # List of RGBW tuples, clipped to canvas height

        self.set_font(font)
        self.set_background()
        self.set_foreground()

        self.set_offset()
        self.set_spacing()
        self.set_text()

    def _load_font_data(self):
        try:
            with open(self.font_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Font file not found: {self.font_path}")
            return None

    def set_font(self, font):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        self.font_path = os.path.join(base_path, 'fonts', f'{font}.json')
        self.font_data = self._load_font_data()

    def set_canvas_width(self, width=48):
        self.canvas_width = width

    def set_canvas_height(self, height=24):
        self.canvas_height = height

    def set_background(self, r=0, g=0, b=0):
        self.background = (r, g, b)

    def set_foreground(self, r=255, g=255, b=255):
        self.foreground = (r, g, b)

    def set_offset(self, x=0, y=0):
        self.offset_x = x
        self.offset_y = y

    def set_spacing(self, x=1, y=1):
        self.spacing_x = x
        self.spacing_y = y

    def set_v_scroll(self, scroll=0):
        self.v_scroll = scroll

    def set_text(self, text='n/a'):
        self.text = text

    def text_to_array(self):
        # Initialize a list to hold the rows of the canvas
        dynamic_canvas = []

        offset_x = self.offset_x
        offset_y = self.offset_y
        letter_height = len(next(iter(self.font_data.values())))  # Get the height of a letter

        for word in self.text.split(' '):
            word_length = sum(len(self.font_data[char][0]) if char in self.font_data else 0 for char in word) + (len(word) - 1) * self.spacing_x

            # Check if the word fits in the current line, if not, move to the next line
            if offset_x + word_length > self.canvas_width:
                offset_y += letter_height + self.spacing_y
                offset_x = self.offset_x # Reset the x offset to initial value

            # Ensure the dynamic canvas has enough rows for the current line
            while len(dynamic_canvas) < offset_y + letter_height:
                dynamic_canvas.append([0] * self.canvas_width)

            for char in word:
                if char in self.font_data:
                    letter = self.font_data[char]
                    for i, row in enumerate(letter):
                        # Ensure the dynamic canvas has enough rows for the current line
                        while len(dynamic_canvas) <= offset_y + i:
                            dynamic_canvas.append([0] * self.canvas_width)

                        for j, pixel in enumerate(row):
                            if offset_x + j < self.canvas_width:  # Check horizontal bounds
                                dynamic_canvas[offset_y + i][offset_x + j] = pixel

                    offset_x += len(letter[0]) + self.spacing_x  # Move to the next character position and add default spacing

            offset_x += 2  # Space after each word
       
        # Ensure dynamic_canvas has at least the minimum height of canvas_height
        init_height = len(dynamic_canvas)
        while len(dynamic_canvas) < self.canvas_height or len(dynamic_canvas) < init_height + self.offset_y:
            dynamic_canvas.append([0] * self.canvas_width)

        # Calculate the total and scrollable heights
        self.total_height = len(dynamic_canvas)
        self.scrollable_height = max(0, self.total_height - self.canvas_height)

        return dynamic_canvas

    def bool_to_color(self, array_text):
        array_colored = []
        # Iterate array_text and convert 0s and 1s to RGBW tuples
        for row in array_text:
            for pixel in row:
                if pixel == 1:
                    array_colored.append(self.foreground)
                else:
                    array_colored.append(self.background)

        return array_colored

    def clip_array(self, array_colored):
        start_pixel = 0
        end_pixel = start_pixel + self.canvas_height * self.canvas_width
        return array_colored[start_pixel:end_pixel]

    def output(self):
        # text_to_array uses defaults or beforehand specified values
        self.array_text    = self.text_to_array()                   # List of lists of 0s and 1s
        self.array_colored = self.bool_to_color(self.array_text)    # List of RGB tuples
        self.array_rgb     = self.clip_array(self.array_colored)    # List of RGB tuples, offset according to v_scroll, clipped to canvas size

        return self.array_rgb