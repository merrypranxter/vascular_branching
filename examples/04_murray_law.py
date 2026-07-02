"""Example 04 — What Murray's exponent actually does.

Same tree topology, three different Murray exponents. The exponent controls how
aggressively the trunk thickens relative to the twigs:

    k = 2.0   area-preserving (Leonardo's rule) — trunk stays modest
    k = 3.0   classic cube law for laminar blood flow
    k = 4.0   turbulent-ish — trunk balloons

We print the resulting root radius for each so you can see the law numerically,
then render a side-by-side comparison.

Run:  python examples/04_murray_law.py
"""

import matplotlib.pyplot as plt

import vascular as vb

exponents = [2.0, 3.0, 4.0]
fig, axes = plt.subplots(1, len(exponents), figsize=(15, 5))

for ax, k in zip(axes, exponents):
    tree = vb.grow_csg(depth=8, branching_angle=30, length_ratio=0.75)
    vb.apply_murray(tree, leaf_radius=0.5, exponent=k)
    vb.compute_flow(tree)
    root = tree.roots()[0]
    print(f"k={k}:  root radius = {tree.nodes[root].radius:6.2f}  "
          f"residual = {vb.murray_residual(tree, exponent=k):.1e}")
    vb.render(tree, style="anatomical", ax=ax)
    ax.set_title(f"Murray exponent k = {k}", color="#333")

fig.tight_layout()
fig.savefig("gallery/04_murray_exponents.png", dpi=120, bbox_inches="tight")
print("wrote gallery/04_murray_exponents.png")
