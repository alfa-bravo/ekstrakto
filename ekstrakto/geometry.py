from functools import reduce
from operator import xor
from struct import pack, unpack

def dist2(a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return (dx**2 + dy**2)**0.5

def dist(a, b):
    '''

    :param a: vector list a
    :param b: vector list b
    :return: ||ab|| = sqrt((b - a)^2)
    '''
    ab = zip(a, b)
    return reduce(lambda sum, comp: sum + (comp[1] - comp[0])**2, ab, 0.0)**0.5

def triangulate(points):
    start_b = 1
    results = []
    for i_a, p_a in enumerate(points):
        points_b = list(enumerate(points[start_b:]))
        results.extend([((i_a, i_b + start_b), (p_a, p_b)) for i_b, p_b in points_b])
        start_b += 1
    return results

def get_point_pair_SLOW(points, criterion=min):
    '''
    Crummy, O(n^2) implementation
    :param points:
    :return: tuple of indices to the two points that are the closest
    '''
    compare = triangulate(points)
    return criterion(compare, key=(lambda index_and_pair: dist(*(index_and_pair[1]))))[0]

def line_point_distance(l0, l1, p):
    # http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    a = l1[0] - l0[0]
    b = l0[1] - p[1]
    c = l0[0] - p[0]
    d = l1[1] - l0[1]
    return abs(a * b - c * d) / (a**2 + d**2)**0.5

def collapse_closest_points(points, max_n_points):
    if len(points) < max_n_points:
        return points
    (idx_a, idx_b) = get_point_pair_SLOW(points, min)
    del(points[idx_b])
    if len(points) > max_n_points:
        collapse_closest_points(points, max_n_points)
    return points

def xorf(a, b):
    x = unpack('I', pack('f', a))[0]
    y = unpack('I', pack('f', b))[0]
    return xor(x, y)

def xorf2(a, b, resolution=4):
    a = round(a, resolution)
    b = round(b, resolution)
    return xorf(a, b)

def distinct(list_):
    results = list({ reduce(xorf2, list(e), 0): e for e in list_}.values())
    return results

def retain_farthest_colors(points, max_n_points):
    '''
    Currently not working...
    :param points:
    :param max_n_points:
    :return:
    '''
    if len(points) < max_n_points:
        return points
    results = []
    while len(results) < max_n_points:
        (idx_a, idx_b) = get_point_pair_SLOW(points, max)
        a = points[idx_a]
        b = points[idx_b]
        results.append(a)
        results.append(b)
        points = [p[1] for p in enumerate(points) if p[0] not in [idx_a, idx_b]]
    return results

'''
TODO:
Mashilamani Sambasivam
Time-Optimal Heuristic Algorithms
For Finding Closest-Pair of Points
in 2D And 3D
https://airccj.org/CSCP/vol5/csit54302.pdf
'''