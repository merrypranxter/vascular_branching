"""Example 07 — A river delta via space colonization.

A delta is a vascular network run in reverse: one channel enters and fans out
into a spreading wedge of distributaries before reaching the sea. We place the
root at the apex and scatter attractors across a fan-shaped coastal plain, then
render with the river style (flow-coloured, Blues).

Run:  python examples/07_river_delta.py
"""

import numpy as np

import vascular as vb


def fan_attractors(n, rng, apex=(0.0, 0.0), reach=2.0, half_angle_deg=55):
    """Scatter points across a fan opening upward from ``apex``."""
    half = np.deg2rad(half_angle_deg)
    r = reach * np.sqrt(rng.random(n))          # denser near the coastline
    a = rng.uniform(-half, half, n) + np.pi / 2  # centred on straight-up
    x = apex[0] + r * np.cos(a)
    y = apex[1] + r * np.sin(a)
    return np.column_stack([x, y])


rng = np.random.default_rng(3)
attractors = fan_attractors(700, rng, reach=2.2, half_angle_deg=58)

delta = vb.grow_space_colonization(
    attractors,
    root=(0.0, 0.0),
    step=0.035,
    influence_radius=0.4,
    kill_radius=0.07,
)
# Rivers gather flow downstream, so a shallower exponent reads better here.
vb.apply_murray(delta, leaf_radius=0.4, exponent=2.4)
vb.compute_flow(delta)

print(delta)
print(f"distributary mouths: {len(delta.leaves())}")

vb.save(delta, "gallery/07_river_delta.png", style="river")
print("wrote gallery/07_river_delta.png")
