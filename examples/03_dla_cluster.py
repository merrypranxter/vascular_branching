"""Example 03 — Diffusion-limited aggregation, the stochastic fractal.

Particles random-walk in from a spawn ring and freeze where they touch the
cluster. No angles, no attractors — the branching emerges from the physics of
diffusion. The neural style suits its wiry, dendritic look.

DLA is genuinely random: pass a seeded generator for reproducible clusters.

Run:  python examples/03_dla_cluster.py
"""

import numpy as np

import vascular as vb

tree = vb.grow_dla(
    n_particles=1500,
    grid_size=241,
    stickiness=0.9,
    rng=np.random.default_rng(42),
)
vb.apply_murray(tree, leaf_radius=0.5)
vb.compute_flow(tree)

lo, hi = tree.bounds()
extent = hi - lo
print(tree)
print(f"cluster extent: {extent[0]:.0f} x {extent[1]:.0f} cells")

vb.save(tree, "gallery/03_dla_neural.png", style="neural")
print("wrote gallery/03_dla_neural.png")
