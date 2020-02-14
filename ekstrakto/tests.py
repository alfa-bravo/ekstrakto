import unittest
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from ekstrakto.helpers import *

np.random.seed(546)

cdict = {
    'red': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
    'green': [[0.0, 0.5, 0.5], [1.0, 0.5, 0.5]],
    'blue': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
    'alpha': [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
}

cmap = LinearSegmentedColormap('foo', segmentdata=cdict)


class TestNumericMethods(unittest.TestCase):
    def test_peak_find_3d(self):
        s1 = np.random.random((10, 3))
        s2 = np.random.random((1000, 3))
        stuff = np.vstack((s1, s1, s1, s1, s1, s1, s1, s1, s2))
        n_bins = 19
        top_cooords, top_values = peak_find_3d(stuff, n_bins)
        top_cooords = np.array(list(top_cooords))
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        top_values = top_values / np.max(top_values)
        print(list(top_values))
        ax.scatter(top_cooords[:, 0], top_cooords[:, 1], top_cooords[:, 2],
                   c=top_values, cmap=cmap, vmin=0, vmax=1)
        plt.show()


if __name__ == '__main__':
    unittest.main()
