from scipy.sparse.linalg import spsolve

from flatutils import graphic as gr
from flatutils.split_rectangle import TrianglulatedRect
from flatutils.elem_util import *
from flatutils.gl import show_results_nodal

w = 300
h = 100
N = 3000
v = 0.2
E = 1
t = 0.1

print('start')
rect = TrianglulatedRect(w, h, N)

elements, nodes = rect.elements, rect.nodes
x, y = zip(*nodes)
if N <= 2000:
    gr.show_mesh(x, y, elements)
K = compute_k_mat(elements, nodes, v, E, t)
print('matrix computed')

fv = np.zeros(len(nodes) * 2)
add_bc_force(nodes, rect.boundary('right'), fv, [1, 0], t)
add_bc_displacement(nodes, rect.boundary('left'), K, fv, [0, None])
add_bc_displacement(nodes, [rect.corner('left', 'bottom')], K, fv, [None, 0])
add_bc_displacement(nodes, [rect.corner('left', 'top')], K, fv, [None, 0])

print('Start Solving')
u = spsolve(K.tocsr(), fv)
if N <= 1000:
    gr.show_system(K, fv)


# Output results
print('solved!')
ux = np.array([u[i * 2] for i in range(0, len(nodes))])
uy = np.array([u[i * 2 + 1] for i in range(0, len(nodes))])
#utotal = np.array([(ux[i] ** 2 + uy[i] ** 2) ** 0.5 for i in range(0, len(nodes))])

# gr.show_results(x, y, elements, a=uy, ux=ux, uy=uy, multiplier=1, mesh=N <= 2000)
show_results_nodal(x, y, elements, a=uy, ux=ux, uy=uy, multiplier=1, mesh=N <= 2000)
