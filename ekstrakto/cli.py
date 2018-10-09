#!/usr/bin/env python

"""
ekstrakto 0002
Author: Vincent Brubaker-Gianakos
Find the dominant colors in an image.
"""

import json
from argparse import *
from PIL import Image

import sys
sys.path.append('../ekstrakto')
from ekstrakto.helpers import *

def show_display(output_colors, image):
    from tkinter import Tk, Canvas
    from PIL import ImageTk
    tk = Tk()
    tk.title('ekstrakto')
    tk.configure(background='black')
    size = (800, 400)
    tk.geometry('{}x{}'.format(size[0], size[1]))
    canvas = Canvas(tk, width=size[0], height=size[1], highlightthickness=0)
    canvas.pack()
    number_of_output_colors = len(output_colors)
    if number_of_output_colors > 0:
        w = size[0] / number_of_output_colors
        h = size[1]
        for i, color in enumerate(output_colors):
            x = w * i
            y = 0
            canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline='')
    else:
        print('Warning: no output colors to display')
    photo_image = ImageTk.PhotoImage(image)
    canvas.create_image(10, 10, image=photo_image, anchor='nw')
    tk.mainloop()


def main(args):
    orig_image = Image.open(args.image)
    image = orig_image.convert('RGB')
    thumbnail_size = (args.max_sample_dimension, args.max_sample_dimension)
    image.thumbnail(thumbnail_size)
    channel_depth = 8  # TODO
    pixels = get_normalized_pixel_data(image, channel_depth)
    analysis_space = args.analysis_color_space.lower()
    output_space = args.output_color_space.lower()
    analysis_cs_func = get_colorsys('rgb', analysis_space)
    output_cs_func = get_colorsys(analysis_space, output_space)
    # Convert RGB to analysis color space
    pixels = list(map(lambda _: analysis_cs_func(*_), pixels))
    dominant_colors = calculate_dominant_colors3(pixels, args.number_of_colors)
    # Convert analysis color space to output color space
    dominant_colors = list(map(lambda _: output_cs_func(*_), dominant_colors))
    # Assuming output colors are in RGB color space!!!
    dominant_colors_fixed = [[int(c * 2**channel_depth) for c in color] for color in dominant_colors]
    output_colors_hex_rgb = [rgb_to_hex_color(*c) for c in dominant_colors_fixed]
    # Limit decimal places
    dominant_colors = list(map(lambda p: [round(c, args.significant_digits) for c in p], dominant_colors))
    print(json.dumps({
        'colors': dominant_colors,
        'format': output_space
    }))
    if args.display:
        show_display(output_colors_hex_rgb, image)

def entrypoint():
    parser = ArgumentParser(description='Extract colors from an image')
    parser.add_argument('image')
    parser.add_argument('--number-of-colors', nargs='?', type=int, default=5)
    parser.add_argument('--max-sample-dimension', nargs='?', type=int, default=64)
    # Analysis color space
    parser.add_argument('--analysis-color-space', nargs='?', default='yiq')
    # Output color space (RGB by default)
    parser.add_argument('--output-color-space', nargs='?', default='rgb')
    parser.add_argument('--significant-digits', nargs='?', type=int, default=16)
    parser.add_argument('--display', action='store_true', default=False)
    parser.add_argument('--test', action='store_true', default=False)
    args = parser.parse_args()
    if args.test:
        from ekstrakto.tests import run_tests
        run_tests(args)
    else:
        main(args)

if __name__ == "__main__":
    entrypoint()