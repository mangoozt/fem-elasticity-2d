import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
from scipy.sparse.linalg import spsolve

from flatutils.split_rectangle import TrianglulatedRect
from flatutils.elem_util import *

w = 300
h = 100
N = 50
v = 0.2
E = 1
t = 0.1

rect = TrianglulatedRect(w, h, N)
K = compute_k_mat(rect.elements, rect.nodes, v, E, t)

elements, nodes = rect.elements, rect.nodes
fv = np.zeros(len(nodes) * 2)
add_bc_force(nodes, rect.boundary('right'), fv, [0, 1], t)
add_bc_displacement(nodes, rect.boundary('left'), K, fv, [0, None])
add_bc_displacement(nodes, [rect.corner('left', 'bottom')], K, fv, [0, 0])

u = spsolve(K, fv)
print(u)


class BinaryNorm(colors.Normalize):
    def __call__(self, value, clip=None):
        result = np.ma.array(value, copy=True)
        result[result > 1e-5] = 1
        result[result < -1e-5] = 1
        result[result != 1] = 0
        return result

    def inverse(self, value):
        return ValueError("ZeroNorm is not invertible")


fig2 = plt.figure()
ax21 = plt.subplot2grid((1, 6), (0, 0), colspan=5)
ax22 = plt.subplot2grid((1, 6), (0, 5))
ax21.matshow(K.toarray(), norm=BinaryNorm(), cmap=cm.get_cmap('binary'))

ax22.matshow(np.matrix(fv).transpose(), norm=BinaryNorm(), cmap=cm.get_cmap('binary'), aspect='equal')
ax22.get_xaxis().set_ticks([])
fig2.show()

fig1 = plt.figure()
ax2 = fig1.add_subplot(111, aspect='equal')
x, y = zip(*nodes)
ax2.triplot(x, y, elements, lw=1, color=(0, 0, 0))

ax2.autoscale_view()
fig1.show()
# fig1.savefig('rect9.png', dpi=90, bbox_inches='tight')


# Output results

# add displacements to nodes coordinates

multiplier = 1e-3
ux = np.array([u[i * 2] for i in range(0, len(nodes))])
uy = np.array([u[i * 2 + 1] for i in range(0, len(nodes))])
x=np.array(x)
y=np.array(y)
x=x+ux*multiplier
y=y+uy*multiplier
#for i in range(0, len(nodes)):
#    x[i] = x[i] + ux[i] * multiplier
#    y[i] = y[i] + uy[i] * multiplier

import matplotlib.tri as mtri

utotal = np.array([(ux[i] ** 2 + uy[i] ** 2) ** 0.5 for i in range(0, len(nodes))])
ushow = uy

# triang = mtri.Triangulation(x, y)
triang = mtri.Triangulation(x, y, elements)
refiner = mtri.UniformTriRefiner(triang)
tri_refi, z_test_refi = refiner.refine_field(ushow, subdiv=4)

plt.figure(figsize=(10, 5))
plt.gca().set_aspect('equal')
levels = np.linspace(ushow.min(), ushow.max(), num=500)
cmap = cm.get_cmap(name='jet')

plt.tricontourf(tri_refi, z_test_refi, levels=levels, cmap=cmap, extend='both')
plt.triplot(x, y, elements, lw=1, color=(1, 1, 1))
plt.scatter(x, y, c=ushow, cmap=cmap, edgecolors='black')
plt.colorbar()
plt.show()
