class TrianglulatedRect:

    def __init__(self, width, height, n):
        n_squares = n / 2
        h = (width * height / n_squares) ** .5
        ny = int(round(height / h))
        h = height / ny
        nx = int(n_squares / ny)
        w = width / nx
        self.nodes = []
        self.elements = []
        for i in range(0, nx + 1):
            for j in range(0, ny + 1):
                self.nodes.append((i * w, j * h))
        for i in range(0, nx):
            for j in range(0, ny):
                """
ny=2
j\i  0  1

   2*-5*-8*-
1   |  |  |
   1*-4*-7*-
0   |  |  |
   0*-3*-6*-

let i=1,j=1
(i * (ny + 1) + j)          :4*
(i + 1) * (ny + 1) + j      :7*
i * (ny + 1) + j + 1        :5*
(i + 1) * (ny + 1) + j + 1) :8*                
"""
                self.elements.append(
                    (i * (ny + 1) + j + 1, (i + 1) * (ny + 1) + j, (i + 1) * (ny + 1) + j + 1))
        self._height = height
        self._width = width
        self._n = int(nx * ny)
        self._nx = nx
        self._ny = ny
        self._w = w
        self._h = h

    def boundary(self, side):
        if side == 'left':
            return range(0, self._ny + 1)
        if side == 'right':
            return range(len(self.nodes) - self._ny - 1, len(self.nodes))
        if side == 'top':
            return range(self._ny, len(self.nodes), self._ny + 1)
        if side == 'bottom':
            return range(0, len(self.nodes), self._ny + 1)

    def corner(self, lr, tb):
        res = 0
        if lr == 'right':
            res += len(self.nodes) - self._ny - 1
        if tb == 'top':
            res += self._ny
        return res
