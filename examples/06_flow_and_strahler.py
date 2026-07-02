"""Example 06 — Reading the network: flow, velocity, and Strahler order.

A sized tree is more than a picture — it's a transport model. This example
colours the same tree three ways:

    * flow      — total volume carried (biggest at the trunk)
    * velocity  — flow / area (fastest in the trunk, slowest in capillaries)
    * Strahler  — the discrete "generation" of each vessel

and prints a small table of how vessel count and mean velocity change with
Strahler order — the kind of summary you'd compare against real morphometry.

Run:  python examples/06_flow_and_strahler.py
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

import vascular as vb

tree = vb.grow_csg(depth=9, branching_angle=28, length_ratio=0.76)
vb.apply_murray(tree, leaf_radius=0.5)
vb.compute_flow(tree)

vel = vb.velocities(tree)
order = vb.strahler_order(tree)

print(f"{'order':>5} {'vessels':>8} {'mean vel':>10}")
for o in range(1, order.max() + 1):
    mask = order == o
    if mask.any():
        print(f"{o:>5} {int(mask.sum()):>8} {vel[mask].mean():>10.2f}")


def color_plot(ax, values, title, cmap):
    segs = list(tree.segments())
    lines = np.array([[p, c] for p, c, _ in segs])
    child_idx = [i for i, n in enumerate(tree.nodes) if n.parent >= 0]
    widths = np.array([n.radius for _, _, n in segs]) * 5
    lc = LineCollection(lines, linewidths=widths, cmap=cmap, capstyle="round")
    lc.set_array(values[child_idx])
    ax.add_collection(lc)
    lo, hi = tree.bounds()
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1])
    ax.set_aspect("equal"); ax.set_axis_off()
    ax.set_title(title, color="#333")


flow = np.array([n.flow for n in tree.nodes])
fig, axes = plt.subplots(1, 3, figsize=(16, 6))
color_plot(axes[0], flow, "flow (volume carried)", "viridis")
color_plot(axes[1], vel, "velocity (flow / area)", "inferno")
color_plot(axes[2], order.astype(float), "Strahler order", "cividis")

fig.tight_layout()
fig.savefig("gallery/06_flow_analysis.png", dpi=120, bbox_inches="tight")
print("wrote gallery/06_flow_analysis.png")
