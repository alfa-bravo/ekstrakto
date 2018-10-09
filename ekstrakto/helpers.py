"""
Author: Vincent Brubaker-Gianakos
"""

from functools import reduce
from scipy.cluster.hierarchy import *
from scipy.cluster.vq import *
from sklearn.cluster import KMeans

import colorsys
from ekstrakto.geometry import collapse_closest_points, line_point_distance


def get_normalized_pixel_data(image, channel_depth):
    data = image.getdata()
    scale = 1.0 / (2 ** channel_depth)
    return [[c * scale for c in list(p)] for p in data]


def get_average(values):
    length = len(values)
    scale = 1.0 / length
    number_of_components = len(values[0])
    initial = [0.0 for _ in range(number_of_components)]
    return reduce(lambda avg, p: [avg[c] + scale * p[c] for c in range(number_of_components)], values, initial)


def _calculate_dominant_colors(pixels, labels, k):
    colors = []
    color_clusters = [[] for _ in range(k)]
    for e in zip(labels, pixels):
        index = e[0]
        color = e[1]
        color_clusters[index].append(color)
    color_clusters.sort(key=len, reverse=True)
    color_clusters = color_clusters[0:k]
    for cl in color_clusters:
        e = get_average(cl)
        colors.append(e)
    return colors


def calculate_dominant_colors(pixels, k):
    z = centroid(pixels)
    clusters = fcluster(z, k, criterion='maxclust')
    clusters = [c - 1 for c in clusters] # Convert 1 index to 0
    return _calculate_dominant_colors(pixels, clusters, k)


def calculate_dominant_colors2(pixels, k):
    codebook, distortion = kmeans(pixels, k)
    return codebook


def find_optimal_score_index(scores):
    '''
    Calculate line parameters
    :param scores: list containing scores of
    :return: index of the optimal score (elbow method)
    References:
    https://www.datasciencecentral.com/profiles/blogs/python-implementing-a-k-means-algorithm-with-sklearn
    https://www.linkedin.com/pulse/finding-optimal-number-clusters-k-means-through-elbow-asanka-perera/
    '''
    x0 = 0
    x1 = len(scores) - 1
    y0 = scores[0]
    y1 = scores[-1]
    l0 = [x0, y0]
    l1 = [x1, y1]
    # Include first point for base case, exclude last point because its distance is 0
    points = [[i, scores[i]] for i in range(len(scores))]
    # Calculate the distance of each point to the line
    # spanning the first and last point of points
    distances = [line_point_distance(l0, l1, p) for p in points]
    # Return the index of the longest distance in the distances list
    return max(enumerate(distances), key=(lambda d: d[1]))[0]


def get_optimal_k_means(pixels, n0=1, nf=10):
    n_clusters_range = range(n0, nf)
    k_means = [KMeans(n_clusters=n) for n in n_clusters_range]
    scores = [k_means[i].fit(pixels).score(pixels) for i in range(len(k_means))]
    optimal_score_index = find_optimal_score_index(scores)
    return (k_means, optimal_score_index)


def calculate_dominant_colors3(pixels, k, layers=3, layer_step_size=None, n0=1, nf=10):
    k_means_list, optimal_score_index = get_optimal_k_means(pixels, n0, nf)
    begin = optimal_score_index
    end = optimal_score_index + layers * k
    if layer_step_size is None:
        layer_step_size = k
    k_means_range = range(begin, end, layer_step_size)
    results = []
    for idx in k_means_range:
        if idx < len(k_means_list):
            k_means = k_means_list[idx]
        else:
            n_clusters = n0 + idx
            k_means = KMeans(n_clusters=n_clusters)
            k_means.fit(pixels)
        labels = k_means.predict(pixels)
        colors = _calculate_dominant_colors(pixels, labels, k_means.n_clusters)
        results.extend(colors)
        results = collapse_closest_points(results, k)
    return results


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
            'hls': lambda y, i, q: colorsys.rgb_to_hls(*list(get_colorsys('yiq', 'rgb')(y, i, q))),
            'hsv': lambda y, i, q: colorsys.rgb_to_hsv(*list(get_colorsys('yiq', 'rgb')(y, i, q)))
        }
    }[input_system][output_system]
