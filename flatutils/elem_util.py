import scipy.sparse as sp
import numpy as np


def area(ni, nj, nm):
    # xj*ym+xi*yj+xm*yi-xi*ym-xj*yi-xm*yj
    return (nj[0] * nm[1] + ni[0] * nj[1] + nm[0] * ni[1] - ni[0] * nm[1] - nj[0] * ni[1] - nm[0] * nj[1]) / 2


def comp_bc(ni, nj, nm):
    # bi=yj-ym , ci=xm-xj
    return nj[1] - nm[1], nm[0] - nj[0]


def comp_a(ni, nj, nm):
    # ai=xj*ym-xm*yj
    return nj[0] * nm[1] - nm[0] * nj[1]


def comp_d_mat(E, v):
    return np.matrix([[1 - v, v, 0], [v, 1 - v, 0], [0, 0, (1 - 2 * v) / 2]]) * (E / ((1 + v) * (1 - 2 * v)))


def compute_k_mat(elements, nodes, v, E, t):
    d = comp_d_mat(E, v)
    k = sp.lil_matrix((len(nodes) * 2, len(nodes) * 2))
    for elem in elements:
        one_o_2_area = 0.5 / area(*map(lambda i: nodes[i], elem))
        b = [0, 0, 0]
        c = [0, 0, 0]
        for i in range(0, 3):
            b[i], c[i] = comp_bc(nodes[elem[i]], nodes[elem[(i + 1) % 3]], nodes[elem[(i + 2) % 3]])
            b[i] *= one_o_2_area
            c[i] *= one_o_2_area

        for i in range(0, 3):
            # transpose(Bi) * D
            bid = [[b[i] * d[0, 0], b[i] * d[0, 1], c[i] * d[2, 2]],
                   [c[i] * d[1, 0], c[i] * d[1, 1], b[i] * d[2, 2]]]
            for j in range(i, 3):
                # transpose(Bi) * D * Bj
                Ke = [[bid[0][0] * b[j] + bid[0][2] * c[j], bid[0][1] * c[j] + bid[0][2] * b[j]],
                      [bid[1][0] * b[j] + bid[1][2] * c[j], bid[1][1] * c[j] + bid[1][2] * b[j]]]

                k[elem[i] * 2, elem[j] * 2] += Ke[0][0]
                k[elem[i] * 2, elem[j] * 2 + 1] += Ke[0][1]
                k[elem[i] * 2 + 1, elem[j] * 2] += Ke[1][0]
                k[elem[i] * 2 + 1, elem[j] * 2 + 1] += Ke[1][1]
                if i != j:
                    # transpose(transpose(Bi)*D*Bj) == transpose(Bj)*D*Bi
                    # as D == transpose(D)
                    k[elem[j] * 2, elem[i] * 2] += Ke[0][0]
                    k[elem[j] * 2, elem[i] * 2 + 1] += Ke[1][0]
                    k[elem[j] * 2 + 1, elem[i] * 2] += Ke[0][1]
                    k[elem[j] * 2 + 1, elem[i] * 2 + 1] += Ke[1][1]
    return k.tocsr()


def add_bc_force(nodes, boundary_nodes, fv, f, t):
    pk = boundary_nodes[0]
    for nk in boundary_nodes[1:]:
        # integrate Ni over boundary = 0.5*l
        t_times_n_integrated = t * 0.5 * (
                (nodes[pk][0] - nodes[nk][0]) ** 2 + (nodes[pk][1] - nodes[nk][1]) ** 2) ** 0.5
        # prev node
        fv[2 * pk] = fv[2 * pk] + f[0] * t_times_n_integrated
        fv[2 * pk + 1] = fv[2 * pk + 1] + f[1] * t_times_n_integrated
        # this node
        fv[2 * nk] = fv[2 * nk] + f[0] * t_times_n_integrated
        fv[2 * nk + 1] = fv[2 * nk + 1] + f[1] * t_times_n_integrated
        pk = nk


def setcsrrow2id(amat, rowind):
    indptr = amat.indptr
    values = amat.data
    indxs = amat.indices

    # get the range of the data that is changed
    rowpa = indptr[rowind]
    rowpb = indptr[rowind + 1]

    # new value and its new rowindex
    values[rowpa] = 1.0
    indxs[rowpa] = rowind

    # number of new zero values
    diffvals = rowpb - rowpa - 1

    # filter the data and indices and adjust the range
    values = np.r_[values[:rowpa + 1], values[rowpb:]]
    indxs = np.r_[indxs[:rowpa + 1], indxs[rowpb:]]
    indptr = np.r_[indptr[:rowind + 1], indptr[rowind + 1:] - diffvals]

    # hard set the new sparse data
    amat.indptr = indptr
    amat.data = values
    amat.indices = indxs


def add_bc_displacement(node, boundary_nodes, k_mat, fv, u):
    for i in range(0, len(u)):
        if not (u[i] is None):
            for nk in boundary_nodes:
                fv[2 * nk + i] = u[i]
                setcsrrow2id(k_mat, 2 * nk + i)


def restore_stress(elements, nodes, u, v, E):
    d = comp_d_mat(E, v)
    s = [[], [], []]
    one_third = 1 / 3
    for elem in elements:
        one_o_2_area = 0.5 / area(*map(lambda i: nodes[i], elem))

        sel = [0, 0, 0]
        for i in range(0, 3):
            b, c = comp_bc(nodes[elem[i]], nodes[elem[(i + 1) % 3]], nodes[elem[(i + 2) % 3]])
            b *= one_o_2_area
            c *= one_o_2_area
            # D*B*u
            sel[0] = sel[0] + (b * d[0, 0] * u[elem[i] * 2] + c * d[0, 1] * u[elem[i] * 2 + 1])
            sel[1] = sel[1] + (b * d[1, 0] * u[elem[i] * 2] + c * d[1, 1] * u[elem[i] * 2 + 1])
            sel[2] = sel[2] + (c * d[2, 2] * u[elem[i] * 2] + b * d[2, 2] * u[elem[i] * 2 + 1])
        # Ni(xc,yc) values in centriod equals exactly 1/3 Ni(xi,yi)
        # sum Ni(xc,yc)=1/3 sum Ni(xi,yi)
        s[0].append(sel[0] * one_third)
        s[1].append(sel[1] * one_third)
        s[2].append(sel[2] * one_third)
    return s
