#!/usr/bin/env python

"""
Author: Vincent Brubaker-Gianakos
"""

import json
from argparse import *
from PIL import Image
from functools import reduce
from scipy.cluster.hierarchy import *
from scipy.cluster.vq import *
import colorsys

def get_normalized_pixel_data(image, channel_depth):
    data = image.getdata()
    scale = 1.0 / (2 ** channel_depth)
    return [[c * scale for c in list(p)] for p in data]


def get_average(values):
    length = len(values)
    scale = 1.0 / length
    number_of_components = len(values[0])
    return reduce(lambda p, avg: [avg[c] + scale * p[c] for c in range(number_of_components)], values)


def calculate_dominant_colors(pixels, k):
    m = 3
    z = centroid(pixels)
    clusters = fcluster(z, k * m, criterion='maxclust')
    colors = []
    color_clusters = [[] for n in range(k * m)]
    for e in zip(clusters, pixels):
        index = e[0] - 1
        color = e[1]
        color_clusters[index].append(color)
    color_clusters.sort(key=len, reverse=True)
    color_clusters = color_clusters[0:k]
    for cluster in color_clusters:
        colors.append(get_average(cluster))
    return colors


def calculate_dominant_colors2(pixels, k):
    codebook, distortion = kmeans(pixels, k)
    return codebook


def clamp(x, lo, hi):
    return min(max(x, lo), hi)


def rgb_to_hex_color(r, g, b):
    r, g, b = clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255)
    return '#{:02X}{:02X}{:02X}'.format(r, g, b)


def get_colorsys(input_system, output_system):
    return {
        'rgb': {
            'rgb': lambda r, g, b: (r, g, b),
            'hls': colorsys.rgb_to_hls,
            'hsv': colorsys.rgb_to_hsv,
            'yiq': colorsys.rgb_to_yiq
        },
        'hls': {
            'hls': lambda h, l, s: (h, l, s),
            'rgb': colorsys.hls_to_rgb,
            'hsv': lambda h, l, s: colorsys.rgb_to_hsv(*list(get_colorsys('hls', 'rgb')(h, l, s))),
            'yiq': lambda h, l, s: colorsys.rgb_to_yiq(*list(get_colorsys('hls', 'rgb')(h, l, s)))
        },
        'hsv': {
            'hsv': lambda h, s, v: (h, s, v),
            'rgb': colorsys.hsv_to_rgb,
            'hls': lambda h, s, v: colorsys.rgb_to_hls(*list(get_colorsys('hsv', 'rgb')(h, s, v))),
            'yiq': lambda h, s, v: colorsys.rgb_to_yiq(*list(get_colorsys('hsv', 'rgb')(h, s, v)))
        },
        'yiq': {
            'yiq': lambda y, i, q: (y, i, q),
            'rgb': colorsys.yiq_to_rgb,
            'hls': lambda h, s, v: colorsys.rgb_to_hls(*list(get_colorsys('yiq', 'rgb')(y, i, q))),
            'hsv': lambda h, s, v: colorsys.rgb_to_hsv(*list(get_colorsys('yiq', 'rgb')(y, i, q)))
        }
    }[input_system][output_system]

