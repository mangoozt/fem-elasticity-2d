from scipy.sparse.linalg import spsolve

from flatutils import graphic as gr
from flatutils.split_rectangle import TrianglulatedRect
from flatutils.elem_util import *

w = 300e-2
h = 100e-2
N = 10000
v = 0.3
E = 200e9
t = 1e-2

rect = TrianglulatedRect(w, h, N)
K = compute_k_mat(rect.elements, rect.nodes, v, E, t)

elements, nodes = rect.elements, rect.nodes
fv = np.zeros(len(nodes) * 2)
add_bc_force(nodes, rect.boundary('right'), fv, [500, 0], t)
add_bc_displacement(nodes, rect.boundary('left'), K, fv, [0, None])
add_bc_displacement(nodes, [rect.corner('left', 'bottom')], K, fv, [None, 0])
add_bc_displacement(nodes, [rect.corner('left', 'top')], K, fv, [None, 0])

u = spsolve(K.tocsr(), fv)
if N <= 1000:
    gr.show_system(K, fv)

x, y = zip(*nodes)
if N <= 2000:
    gr.show_mesh(x, y, elements)

# Output results

ux = np.array([u[i * 2] for i in range(0, len(nodes))])
uy = np.array([u[i * 2 + 1] for i in range(0, len(nodes))])
#utotal = np.array([(ux[i] ** 2 + uy[i] ** 2) ** 0.5 for i in range(0, len(nodes))])

s = restore_stress(elements, nodes, u, v, E)
von_mises = [(s[0][i] ** 2 - s[0][i] * s[1][i] + s[1][i] ** 2 + 3 * s[2][i] ** 2) ** 0.5 for i in range(len(s[0]))]

# gr.show_results_nodal(x, y, elements, a=uy, ux=ux, uy=uy, multiplier=1, mesh=N <= 2000)
gr.show_results_elem(x, y, elements, a=von_mises, ux=ux, uy=uy, multiplier=1e8, mesh=N <= 2000)
