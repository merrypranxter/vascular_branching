"""Example 01 — Recursive CSG branching, the self-similar baseline.

Grows a deterministic binary tree, sizes it with Murray's law, and renders it
in the botanical style. Change ``branching_angle`` and ``length_ratio`` to feel
how the silhouette responds: wide angles + high ratio fill a hemisphere; narrow
angles + low ratio give a slender conifer.

Run:  python examples/01_csg_recursive.py
"""

import vascular as vb

tree = vb.grow_csg(
    depth=10,
    branching_angle=26,
    length_ratio=0.77,
    n_children=2,
)
vb.apply_murray(tree, leaf_radius=0.55, exponent=3.0)
vb.compute_flow(tree)

print(tree)
print(f"total pipe length: {tree.total_length():.1f}")
print(f"Murray residual:   {vb.murray_residual(tree):.2e}")

vb.save(tree, "gallery/01_csg_botanical.png", style="botanical")
print("wrote gallery/01_csg_botanical.png")
