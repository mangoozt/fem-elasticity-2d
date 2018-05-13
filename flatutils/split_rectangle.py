def split_rectangle_t(width, height, n):
    n_squares = n / 2
    h = (width * height / n_squares) ** .5
    ny = (height / h)

    ny = int(round(ny))
    h = height / ny
    nx = int(n_squares / ny)
    w = width / nx
    nodes = []
    elements = []
    for i in range(0, nx + 1):
        for j in range(0, ny + 1):
            nodes.append((i * w, j * h))
    for i in range(0, nx):
        for j in range(0, ny):
            elements.append((i * (ny + 1) + j, (i + 1) * (ny + 1) + j, i * (ny + 1) + j + 1))
            elements.append((i * (ny + 1) + j + 1, (i + 1) * (ny + 1) + j, (i + 1) * (ny + 1) + j + 1))

    return elements, nodes
