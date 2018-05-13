import scipy.sparse as sp


def connections_matrix(elements, nodes):
    mat = sp.lil_matrix((len(nodes), len(nodes)))
    for element in elements:
        for k in element:
            for m in element:
                mat[k, m] = 1
    return mat
