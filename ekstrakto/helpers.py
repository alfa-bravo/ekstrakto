"""
Author: Vincent Brubaker-Gianakos
"""

import numpy as np
import kdtree


def get_normalized_pixel_data(image, channel_bit_depth):
    return np.array(image.getdata()) / ((2 ** channel_bit_depth) - 1)


def progressive_peak_find(h, distinctness=1.0):
    array = sorted(np.ndenumerate(h), key=lambda a: a[1], reverse=True)
    peaks = dict()
    peaks[array[0][0]] = array[0][1]
    visited = kdtree.create([array[0][0]])
    for idx, value in array[1:]:
        nearest_visited, d = visited.search_nn(idx)
        d = d / h.shape[0]
        if d > distinctness:
            peaks[idx] = value
        visited.add(idx)
    ordered_peaks = sorted(peaks.items(), key=lambda p: p[1], reverse=True)
    coords, values = zip(*ordered_peaks)
    return coords, values


def peak_find_3d(pixels, n_bins=19, distinctness=1.0):
    bin_range = np.linspace(0, 1, n_bins)
    bins = (bin_range,) * 3
    H, edges = np.histogramdd(pixels, bins)
    coords, values = progressive_peak_find(H, distinctness)
    normalized_coords = np.array(coords) / (H.shape[0] - 1)
    return normalized_coords, np.array(values)


def normalized_histogram(pixels, n_bins=31, bias=0):
    bin_range = np.arange(-1, n_bins + 2) / n_bins
    bins = (bin_range,) * 3
    H, edges = np.histogramdd(pixels, bins)
    coords, values = zip(*list(np.ndenumerate(H)))
    return np.array(coords) / (H.shape[0] - 1), values


def rgb_to_hex_color(r, g, b):
    r, g, b = np.clip(r, 0, 255), np.clip(g, 0, 255), np.clip(b, 0, 255)
    return f'#{r:02X}{g:02X}{b:02X}'
