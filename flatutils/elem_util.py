import scipy.sparse as sp
import numpy as np


def area(ni, nj, nm):
    # xj*ym+xi*yj+xm*yi-xi*ym-xj*yi-xm*yj
    return (nj[0] * nm[1] + ni[0] * nj[1] + nm[0] * ni[1] - ni[0] * nm[1] - nj[0] * ni[1] - nm[0] * nj[1]) / 2


def comp_bc(ni, nj, nm):
    # bi=yj-ym , ci=xm-xj
    return nj[1] - nm[1], nm[0] - nj[0]


def comp_d_mat(E,v):
    return np.matrix([[1 - v, v, 0], [v, 1 - v, 0], [0, 0, (1 - 2 * v) / 2]]) * (E / ((1 + v) * (1 - 2 * v)))


def compute_k_mat(elements, nodes, v, E, t):
    D = comp_d_mat(E,v)
    K = sp.lil_matrix((len(nodes) * 2, len(nodes) * 2))
    for elem in elements:
        B = []
        area_rev = 1 / area(*map(lambda i: nodes[i], elem))
        for i in range(0, 3):
            b, c = comp_bc(nodes[elem[i]], nodes[elem[(i + 1) % 3]], nodes[elem[(i + 2) % 3]])
            B.append(np.matrix([[b, 0], [0, c], [c, b]]) * 0.5)

        for i in range(0, 3):
            for j in range(0, 3):
                Ke = B[i].transpose() * D * B[j] * t * area_rev
                K[elem[i] * 2, elem[j] * 2] += Ke[0, 0]
                K[elem[i] * 2, elem[j] * 2 + 1] += Ke[0, 1]
                K[elem[i] * 2 + 1, elem[j] * 2] += Ke[1, 0]
                K[elem[i] * 2 + 1, elem[j] * 2 + 1] += Ke[1, 1]
    return K


def add_bc_force(nodes, boundary_nodes, fv, f, t):
    pk = boundary_nodes[0]
    for nk in boundary_nodes[1:]:
        l = ((nodes[pk][0] - nodes[nk][0]) ** 2 + (nodes[pk][1] - nodes[nk][1]) ** 2) ** 0.5
        # prev node
        fv[2 * pk] = fv[2 * pk] + t * f[0] * 0.5 * l
        fv[2 * pk + 1] = fv[2 * pk + 1] + t * f[1] * 0.5 * l
        # this node
        fv[2 * nk] = fv[2 * nk] + t * f[0] * 0.5 * l
        fv[2 * nk + 1] = fv[2 * nk + 1] + t * f[1] * 0.5 * l
        pk = nk


def add_bc_displacement(node, boundary_nodes, k_mat, fv, u):
    for i in range(0, len(u)):
        if not (u[i] is None):
            for nk in boundary_nodes:
                fv[2 * nk + i] = u[i]
                k_mat[2 * nk + i, :] = 0
                k_mat[2 * nk + i, 2 * nk + i] = 1
