"""Example 05 — One tree, every visual style.

The point of the style system: geometry and aesthetics are separate. A single
network renders as an artery, a leaf, a river delta, a circuit trace, or a
neuron depending only on the :class:`~vascular.styles.Style` you pass. This
builds a 2x3 contact sheet of all five presets.

Run:  python examples/05_styles_gallery.py
"""

import matplotlib.pyplot as plt

import vascular as vb
from vascular.styles import STYLES

tree = vb.grow_csg(depth=9, branching_angle=27, length_ratio=0.76)
vb.apply_murray(tree, leaf_radius=0.6)
vb.compute_flow(tree)

names = list(STYLES)
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.ravel()

for ax, name in zip(axes, names):
    vb.render(tree, style=name, ax=ax)
    ax.set_title(name, color="#888", fontsize=12)

for ax in axes[len(names):]:
    ax.set_axis_off()

fig.tight_layout()
fig.savefig("gallery/05_styles_gallery.png", dpi=110, bbox_inches="tight")
print("wrote gallery/05_styles_gallery.png")
