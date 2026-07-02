"""vascular — generate and visualise fractal branching transport networks.

The package is organised around one shared data structure, :class:`Tree`, that
every generator produces and every analysis/renderer consumes:

    generators        analysis            output
    ---------         --------            ------
    grow_csg          apply_murray        render / save
    grow_dla          compute_flow        Style presets
    grow_space_...    velocities
                      strahler_order

Typical use::

    import vascular as vb

    tree = vb.grow_csg(depth=9, branching_angle=28, length_ratio=0.76)
    vb.apply_murray(tree, leaf_radius=0.6)
    vb.compute_flow(tree)
    vb.save(tree, "tree.png", style="botanical")
"""

from __future__ import annotations

from .core import Node, Tree
from .csg import grow_csg
from .dla import grow_dla
from .flow import compute_flow, strahler_order, velocities
from .murray import apply_murray, murray_residual
from .render import render, save
from .space_colonization import disc_attractors, grow_space_colonization
from .styles import (
    ANATOMICAL,
    BOTANICAL,
    CIRCUIT,
    NEURAL,
    RIVER,
    STYLES,
    Style,
    get_style,
)

__version__ = "0.1.0"

__all__ = [
    "Node",
    "Tree",
    "grow_csg",
    "grow_dla",
    "grow_space_colonization",
    "disc_attractors",
    "apply_murray",
    "murray_residual",
    "compute_flow",
    "velocities",
    "strahler_order",
    "render",
    "save",
    "Style",
    "STYLES",
    "get_style",
    "ANATOMICAL",
    "BOTANICAL",
    "RIVER",
    "CIRCUIT",
    "NEURAL",
    "__version__",
]
