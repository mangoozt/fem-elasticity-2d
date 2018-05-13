import matplotlib.pyplot as plt
import matplotlib.patches as patches

from flatutils.split_rectangle import split_rectangle_t

w = 300
h = 100
N = 50

elements, nodes = split_rectangle_t(w, h, N)

fig1 = plt.figure()
ax2 = fig1.add_subplot(111, aspect='equal')
for elem in elements:
    ax2.add_patch(
        patches.Polygon([nodes[elem[0]], nodes[elem[1]], nodes[elem[2]]], ec=(1, 0, 0), lw=1)
    )

ax2.autoscale_view()
plt.show(fig1)
# fig1.savefig('rect9.png', dpi=90, bbox_inches='tight')
