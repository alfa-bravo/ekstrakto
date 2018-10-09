from ekstrakto.geometry import *
from ekstrakto.helpers import *

def _test_get_closest_pair_SLOW():
    some_points = [(1, 2), (7, 7), (3, 4), (90, 100), (12, 18), (7.1, 7.1), (8.5, 6.2)]
    closest = get_point_pair_SLOW(some_points, min)
    assert (closest == (1, 5))

    some_points = [(0.0, 1.0, 2.0), (1.0, 2.0, 3.0), (7.0, 2.0, 3.0),
                   (7.1, 2.1, 9.0), (0.0, -1.0, -99.0), (9.0, 17.0, 9.0), (7.2, 1.9, 2.9)]
    closest = get_point_pair_SLOW(some_points, min)
    assert (closest == (2, 6))

def _test_get_average():
    stuff = [(1, 2, 3), (1, 2, 3)]
    average = get_average(stuff)
    assert (average == [1, 2, 3])

    stuff = [[1,2,3], [3,4,5]]
    average = get_average(stuff)
    print(average)
    assert(average == [2,3,4])

def run_tests(args):
    _test_get_closest_pair_SLOW()
    _test_get_average()