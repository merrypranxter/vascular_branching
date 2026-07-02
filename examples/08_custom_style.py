"""Example 08 — Define your own style.

A :class:`~vascular.styles.Style` is a plain frozen dataclass, so making a new
look is a one-liner. Here we build a "gold circuitry" style — squared caps, a
glow, and a warm colormap keyed to depth — and register it so it works exactly
like the built-ins.

Run:  python examples/08_custom_style.py
"""

import vascular as vb
from vascular.styles import STYLES, Style

GOLD_CIRCUIT = Style(
    name="gold_circuit",
    cmap="autumn",
    background="#0a0600",
    color_by="depth",
    width_scale=4.0,
    width_gamma=1.0,
    capstyle="projecting",  # squared ends read as artificial / etched
    glow=True,
)

# Register it so vb.save(..., style="gold_circuit") resolves by name too.
STYLES[GOLD_CIRCUIT.name] = GOLD_CIRCUIT

tree = vb.grow_csg(depth=9, branching_angle=22, length_ratio=0.72, n_children=3)
vb.apply_murray(tree, leaf_radius=0.5)
vb.compute_flow(tree)

# You can pass the Style object directly, or now by its registered name.
vb.save(tree, "gallery/08_gold_circuit.png", style=GOLD_CIRCUIT)
print("wrote gallery/08_gold_circuit.png")
