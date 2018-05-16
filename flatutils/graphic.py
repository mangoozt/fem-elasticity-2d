import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.tri as mtri


class BinaryNorm(colors.Normalize):
    def __call__(self, value, clip=None):
        result = np.ma.array(value, copy=True)
        result[result > 1e-5] = 1
        result[result < -1e-5] = 1
        result[result != 1] = 0
        return result

    def inverse(self, value):
        return ValueError("ZeroNorm is not invertible")


def show_mesh(x, y, elements):
    fig1 = plt.figure()
    ax2 = fig1.add_subplot(111, aspect='equal')
    ax2.triplot(x, y, elements, lw=1, color=(0, 0, 0))
    ax2.autoscale_view()
    fig1.show()


def show_system(mat, b):
    fig2 = plt.figure()
    ax21 = plt.subplot2grid((1, 6), (0, 0), colspan=5)
    ax22 = plt.subplot2grid((1, 6), (0, 5))
    ax21.matshow(mat.toarray(), norm=BinaryNorm(), cmap=cm.get_cmap('binary'))

    ax22.matshow(np.matrix(b).transpose(), norm=BinaryNorm(), cmap=cm.get_cmap('binary'), aspect='equal')
    ax22.get_xaxis().set_ticks([])
    fig2.show()


def apply_displacement(x, y, ux, uy, multiplier):
    ux = np.array(ux)
    uy = np.array(uy)
    _x = np.array(x)
    _y = np.array(y)
    _x = _x + ux * multiplier
    _y = _y + uy * multiplier
    return _x, _y


def show_results(x, y, elements, a, ux=None, uy=None, multiplier=1, mesh=True):
    # add displacements to nodes' coordinates
    if not ((ux is None) & (uy is None)):
        _x, _y = x, y
        x, y = apply_displacement(x, y, ux, uy, multiplier)

    a = np.array(a)

    triang = mtri.Triangulation(x, y, elements)
    refiner = mtri.UniformTriRefiner(triang)
    tri_refi, z_test_refi = refiner.refine_field(a, subdiv=4)

    plt.figure(figsize=(10, 5))
    plt.gca().set_aspect('equal')
    levels = np.linspace(a.min(), a.max(), num=500)
    cmap = cm.get_cmap(name='jet')

    plt.tricontourf(tri_refi, z_test_refi, levels=levels, cmap=cmap, extend='both')
    if mesh:
        plt.triplot(x, y, elements, lw=1, color=(1, 1, 1))
    # plt.scatter(x, y, c=a, cmap=cmap, edgecolors='black')
    plt.colorbar()
    plt.show()
