"""
Author: Vincent Brubaker-Gianakos
"""

import numpy as np
from sklearn.cluster import KMeans
from scipy.stats import multivariate_normal
from scipy.signal import convolve
from scipy.ndimage import maximum_filter, minimum_filter
import colorsys
from ekstrakto.geometry import line_point_distance
import kdtree

RANDOM_STATE = 42


def get_normalized_pixel_data(image, channel_bit_depth):
    return np.array(image.getdata()) / ((2 ** channel_bit_depth) - 1)


def find_optimal_score_index(scores):
    '''
    Calculate line parameters
    :param scores: list containing scores of
    :return: index of the optimal score (elbow method)
    References:
    https://www.datasciencecentral.com/profiles/blogs/python-implementin
    g-a-k-means-algorithm-with-sklearn
    https://www.linkedin.com/pulse/finding-optimal-number-clusters-k-means-thro
    ugh-elbow-asanka-perera/
    '''
    x0 = 0
    x1 = len(scores) - 1
    y0 = scores[0]
    y1 = scores[-1]
    l0 = [x0, y0]
    l1 = [x1, y1]
    # Include first point for base case, exclude last point because its
    # distance is 0
    points = [[i, scores[i]] for i in range(len(scores))]
    # Calculate the distance of each point to the line
    # spanning the first and last point of points
    distances = [line_point_distance(l0, l1, p) for p in points]
    # Return the index of the longest distance in the distances list
    return max(enumerate(distances), key=(lambda d: d[1]))[0]


def get_optimal_k_means(pixels, n0=1, nf=10):
    n_clusters_range = range(n0, nf)
    k_means = [KMeans(n_clusters=n, random_state=RANDOM_STATE)
               for n in n_clusters_range]
    scores = [k_means[i].fit(pixels).score(pixels)
              for i in range(len(k_means))]
    optimal_score_index = find_optimal_score_index(scores)
    return k_means, optimal_score_index


def get_gaussian_kernel(size, s=1.0):
    if size == 1:
        return np.array([[[1]]])
    assert(size > 1)
    cov = np.identity(3) / s
    rv = multivariate_normal((0.5, 0.5, 0.5), cov)
    grid = np.mgrid[:size, :size, :size].T
    kernel = rv.pdf(grid / (size - 1))
    return kernel


def marr_dog_func(size, s=64):
    '''
    Marr D. , Hildreth E. and Brenner Sydney
    Theory of edge detection207Proc. R. Soc. Lond. B.
    https://doi.org/10.1098/rspb.1980.0020
    '''

    # Marr wavelet approximated by Difference of Gaussians
    k1 = get_gaussian_kernel(size, s)
    k2 = get_gaussian_kernel(size, 1.6 * s)
    return k2 - k1


def cwt_peak_detect_3d(h, widths, tolerance=1.0, func=None):
    if not func:
        func = marr_dog_func
    stack = []
    for w in widths:
        kernel = func(w)  # Wavelet kernel
        h2 = convolve(h, kernel, mode='same')  # Convolve with wavelet
        stack.append(h2)  # Add to stack

    def score_point(idx):
        col = np.array([max(0, s[idx]) for s in stack])
        return np.product(col)

    scored = np.zeros_like(h)
    for idx in np.ndindex(h.shape):
        scored[idx] = score_point(idx)
    return scored


def progressive_peak_find(h, sensitivity=1):
    array = sorted(np.ndenumerate(h), key=lambda a: a[1], reverse=True)
    peaks = set()
    peaks.add(array[0])
    scores = np.zeros_like(h)

    def distance(a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def score_point(idx, value):
        nearest_peak = min(peaks, key=lambda p: distance(p[0], idx))
        dist_to_nearest = distance(nearest_peak[0], idx) / h.shape[0]
        nearest_value = nearest_peak[1]
        s = value / nearest_value
        d = min(sensitivity * dist_to_nearest, 1.0) ** 2
        score = s * d
        if score > scores[nearest_peak[0]]:
            peaks.add((idx, value))
            scores[idx] = s * d

    for idx, value in array[1:]:
        score_point(idx, value)

    scores[array[0][0]] = 1

    return scores


def progressive_peak_find_2(h, distinctness=1.0):
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
    bin_range = np.arange(-1, n_bins + 2) / n_bins
    bins = (bin_range,) * 3
    H, edges = np.histogramdd(pixels, bins)

    #kernel = get_gaussian_kernel((n_bins // 16) * 2 + 1)
    #H = convolve(H, kernel, mode='same')

    coords, values = progressive_peak_find_2(H, distinctness)
    normalized_coords = np.array(coords) / (H.shape[0] - 1)
    return normalized_coords, np.array(values)


def normalized_histogram(pixels, n_bins=31, bias=0):
    bin_range = np.arange(-1, n_bins + 2) / n_bins
    bins = (bin_range,) * 3
    H, edges = np.histogramdd(pixels, bins)
    coords, values = zip(*list(np.ndenumerate(H)))
    return np.array(coords) / (H.shape[0] - 1), values


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
            'hsv': lambda h, l, s: colorsys.rgb_to_hsv(
                *list(get_colorsys('hls', 'rgb')(h, l, s))),
            'yiq': lambda h, l, s: colorsys.rgb_to_yiq(
                *list(get_colorsys('hls', 'rgb')(h, l, s)))
        },
        'hsv': {
            'hsv': lambda h, s, v: (h, s, v),
            'rgb': colorsys.hsv_to_rgb,
            'hls': lambda h, s, v: colorsys.rgb_to_hls(
                *list(get_colorsys('hsv', 'rgb')(h, s, v))),
            'yiq': lambda h, s, v: colorsys.rgb_to_yiq(
                *list(get_colorsys('hsv', 'rgb')(h, s, v)))
        },
        'yiq': {
            'yiq': lambda y, i, q: (y, i, q),
            'rgb': colorsys.yiq_to_rgb,
            'hls': lambda y, i, q: colorsys.rgb_to_hls(
                *list(get_colorsys('yiq', 'rgb')(y, i, q))),
            'hsv': lambda y, i, q: colorsys.rgb_to_hsv(
                *list(get_colorsys('yiq', 'rgb')(y, i, q)))
        }
    }[input_system][output_system]
