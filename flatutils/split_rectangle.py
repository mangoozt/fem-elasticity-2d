class TrianglulatedRect:

    def __init__(self, width, height, n):
        """
        :param width: float
        :param height: float
        :param n: int desired number of elements
        """

        n_squares = n / 4
        h = (width * height / n_squares) ** .5
        ny = int(round(height / h))
        h = height / ny
        nx = int(n_squares / ny)
        w = width / nx

        self.nodes = []
        self.elements = []
        for i in range(0, nx):
            for j in range(0, ny):
                self.nodes.append((i * w, j * h))
                self.nodes.append((i * w + w / 2, j * h + h / 2))
            self.nodes.append((i * w, ny * h))
        for j in range(0, ny + 1):
            self.nodes.append((nx * w, j * h))
        """
4*--9*--
 |\ /|\ /
 |3* |8*
 |/ \|/ \
2*--7*--c*--e*
 |\ /|\ /|\ /|\
 |1* |6* |b* |
 |/ \|/ \|/ \|/
0*--5*--a*--d*-

a=i * (ny * 2 + 1) + j * 2 + 0
b=i * (ny * 2 + 1) + j * 2 + 1
c=i * (ny * 2 + 1) + j * 2 + 2
d=(i + 1) * (ny * 2 + 1) + j * 2 + 0
e=(i + 1) * (ny * 2 + 1) + j * 2 + 2
        """
        for i in range(0, nx - 1):
            for j in range(0, ny):
                a = i * (ny * 2 + 1) + j * 2 + 0
                b = i * (ny * 2 + 1) + j * 2 + 1
                c = i * (ny * 2 + 1) + j * 2 + 2
                d = (i + 1) * (ny * 2 + 1) + j * 2 + 0
                e = (i + 1) * (ny * 2 + 1) + j * 2 + 2

                self.elements.append((a, d, b))
                self.elements.append((a, b, c))
                self.elements.append((c, b, e))
                self.elements.append((d, e, b))

        # Last column (different numbering for absence of middle points from next column)
        for j in range(0, ny):
            a = (nx - 1) * (ny * 2 + 1) + j * 2 + 0
            b = (nx - 1) * (ny * 2 + 1) + j * 2 + 1
            c = (nx - 1) * (ny * 2 + 1) + j * 2 + 2
            d = (nx) * (ny * 2 + 1) + j + 0
            e = (nx) * (ny * 2 + 1) + j + 1
            self.elements.append((a, d, b))
            self.elements.append((a, b, c))
            self.elements.append((c, b, e))
            self.elements.append((d, e, b))
        # Save some significant variables
        self._height = height
        self._width = width
        self._n = int(nx * ny)
        self._nx = nx
        self._ny = ny
        self._w = w
        self._h = h

    def boundary(self, side):
        if side == 'left':
            return range(0, self._ny * 2 + 1, 2)
        if side == 'right':
            return range(len(self.nodes) - self._ny - 1, len(self.nodes))
        if side == 'top':
            return [i for i in range(self._ny * 2, len(self.nodes) - 1, self._ny * 2 + 1)] + [len(self.nodes) - 1]
        if side == 'bottom':
            return range(0, len(self.nodes), self._ny * 2 + 1)

    def corner(self, lr, tb):
        res = 0
        if lr == 'right':
            res += len(self.nodes) - self._ny - 1
            if tb == 'top':
                res += self._ny
        else:
            if tb == 'top':
                res += self._ny * 2
        return res
