"""
ekstrakto 0002
Author: Vincent Brubaker-Gianakos
Find the dominant colors in an image.
"""

import json
from argparse import *
from PIL import Image
import sys
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
        print('Warning: no output colors to display', file=sys.stderr)
    photo_image = ImageTk.PhotoImage(image)
    canvas.create_image(10, 10, image=photo_image, anchor='nw')
    tk.mainloop()


def main(args):
    orig_image = Image.open(args.image)
    image = orig_image.convert('RGB')
    thumbnail_size = (args.max_sample_dimension, args.max_sample_dimension)
    image.thumbnail(thumbnail_size)
    channel_bit_depth = 8  # TODO
    pixels = get_normalized_pixel_data(image, channel_bit_depth)
    top_colors, top_values = peak_find_3d(
        pixels, distinctness=args.distinctness)
    try:
        number_of_colors = int(args.number_of_colors)
        dominant_colors = top_colors[:number_of_colors]
    except ValueError:
        top_values = top_values / np.max(top_values)
        dominant_colors = [c for c, v in zip(top_colors, top_values)
                           if v > args.color_threshold]
    # Assuming output colors are in RGB color space!!!
    dominant_colors_fixed = [[int(c * 2**channel_bit_depth) for c in color]
                             for color in dominant_colors]
    output_colors_hex_rgb = [rgb_to_hex_color(*c)
                             for c in dominant_colors_fixed]
    # Limit decimal places
    dominant_colors = list(map(lambda p: [round(c, args.significant_digits)
                                          for c in p], dominant_colors))
    print(json.dumps({
        'colors': dominant_colors,
        'format': 'rgb'
    }))
    if args.display:
        show_display(output_colors_hex_rgb, image)


def entrypoint():
    parser = ArgumentParser(
        description='Extract colors from an image')
    parser.add_argument(
        'image')
    parser.add_argument(
        '--number-of-colors', nargs='?', default='auto')
    parser.add_argument(
        '--color-threshold', nargs='?', type=float, default=0)
    parser.add_argument(
        '--distinctness', nargs='?', type=float, default=1)
    parser.add_argument(
        '--max-sample-dimension', nargs='?', type=int, default=256)
    parser.add_argument(
        '--significant-digits', nargs='?', type=int, default=16)
    parser.add_argument(
        '--display', action='store_true', default=False)
    parser.add_argument(
        '--test', action='store_true', default=False)
    args = parser.parse_args()
    if args.test:
        from ekstrakto.tests import run_tests
        run_tests(args)
    else:
        main(args)


if __name__ == "__main__":
    entrypoint()
