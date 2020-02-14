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


def line_point_distance(l0, l1, p):
    # http://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    a = l1[0] - l0[0]
    b = l0[1] - p[1]
    c = l0[0] - p[0]
    d = l1[1] - l0[1]
    return abs(a * b - c * d) / (a**2 + d**2)**0.5
