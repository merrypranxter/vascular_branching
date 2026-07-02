"""Example 02 — Space colonization filling a leaf-shaped region.

Instead of dictating angles, we scatter attractor points in the shape we want
filled and let the network find its own way there. Here the attractors form a
leaf blade, so the result reads as leaf venation. Swap the attractor cloud for
an organ outline to get anatomical vasculature.

Run:  python examples/02_space_colonization.py
"""

import numpy as np

import vascular as vb


def leaf_attractors(n, rng):
    """Sample points inside a simple pointed-leaf silhouette."""
    pts = []
    while len(pts) < n:
        x = rng.uniform(-0.7, 0.7)
        y = rng.uniform(0.0, 2.2)
        # Leaf half-width tapers to a point at top and base.
        width = 0.7 * np.sin(np.pi * y / 2.2)
        if abs(x) <= width:
            pts.append((x, y))
    return np.array(pts)


rng = np.random.default_rng(7)
attractors = leaf_attractors(600, rng)

tree = vb.grow_space_colonization(
    attractors,
    root=(0.0, 0.0),
    step=0.03,
    influence_radius=0.35,
    kill_radius=0.06,
)
vb.apply_murray(tree, leaf_radius=0.35)
vb.compute_flow(tree)

print(tree)
print(f"attractors reached => {len(tree.leaves())} terminal veins")

vb.save(tree, "gallery/02_space_colonization_leaf.png", style="botanical")
print("wrote gallery/02_space_colonization_leaf.png")
