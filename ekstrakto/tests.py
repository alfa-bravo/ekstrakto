import unittest
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from ekstrakto.geometry import *
from ekstrakto.helpers import *

from itertools import islice
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt

np.random.seed(546)

cdict = {
    'red': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
    'green': [[0.0, 0.5, 0.5], [1.0, 0.5, 0.5]],
    'blue': [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
    'alpha': [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]
}
cmap = LinearSegmentedColormap('foo',segmentdata=cdict)

class TestNumericMethods(unittest.TestCase):
    def test_peak_find_3d(self):
        s1 = np.random.random((10, 3))
        s2 = np.random.random((1000, 3))
        stuff = np.vstack((s1, s1, s1, s1, s1, s1, s1, s1, s2))
        n_bins = 19
        top_cooords, top_values = peak_find_3d(stuff, n_bins)
        top_cooords = np.array(list(top_cooords))
        #top_values = np.array(top_values)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        top_values = top_values / np.max(top_values)
        print(list(top_values))
        ax.scatter(top_cooords[:, 0], top_cooords[:, 1], top_cooords[:, 2],
                   c=top_values, cmap=cmap, vmin=0, vmax=1)
        plt.show()

    def test_gaussian_3d(self):
        return
        kernel_size = 49

        k0 = get_gaussian_kernel(kernel_size, 8192)
        k0 = k0 / np.sum(k0)
        k1 = get_gaussian_kernel(kernel_size, 1024)
        k1 = -k1 / np.sum(k1)
        k2 = get_gaussian_kernel(kernel_size, 64)
        k2 = -k2 / np.sum(k2)
        kernel = k0 + k1 * 2 + k2 * 50

        n_k2d = kernel.shape[0]
        w = int(n_k2d ** 0.5) + 1
        h = n_k2d // w + 1
        fig, ax = plt.subplots(w, h)
        ax_flat = ax.flatten()
        range_ = max(np.max(kernel), -np.min(kernel))
        for x in range(n_k2d):
            k2d = kernel[x]
            ax_flat[x].imshow(k2d, interpolation='nearest',
                              vmin=-range_, vmax=range_, cmap=plt.cm.gray)
        # Kernel filter leaves one out, exclusive range leaves one out
        plt.show()

    def test_marr_dog_3d(self):
        return
        kernel_size = 31
        step = (kernel_size + 1) // 16
        widths = list(range(kernel_size, kernel_size // 8, -step))
        print(widths)

        kernels = [marr_dog_func(w) for w in widths]
        fig, ax = plt.subplots(1, len(kernels))
        ax_flat = ax.flatten()
        for a, k in zip(ax_flat, kernels):
            print(k.shape)
            center_x = k.shape[0] // 2 + 1
            k2d = k[center_x]
            a.imshow(k2d, interpolation='nearest', cmap=plt.cm.gray,
                     vmin=-32, vmax=32)
        plt.show()


if __name__ == '__main__':
    unittest.main()