"""Flow analysis over a network.

Once a tree has radii, we can reason about what moves through it. We use the
simplest conservative model: each leaf draws one unit of flow, and flow is
conserved at every junction, so a parent carries the sum of its children.
Velocity then follows from continuity — ``v = Q / area`` — which is why the
fine capillaries run slow and the trunk runs fast.
"""

from __future__ import annotations

import numpy as np

from .core import Tree
from .murray import _leaves_first


def compute_flow(tree: Tree, leaf_flow: float = 1.0) -> Tree:
    """Assign a conserved volumetric flow to every node (leaves inward).

    Args:
        tree: A network. ``node.flow`` is filled in place and the tree returned.
        leaf_flow: Flow drawn by each terminal node.

    Returns:
        The same tree with ``node.flow`` populated.
    """
    for idx in _leaves_first(tree):
        kids = tree.children(idx)
        if not kids:
            tree.nodes[idx].flow = leaf_flow
        else:
            tree.nodes[idx].flow = sum(tree.nodes[c].flow for c in kids)
    return tree


def velocities(tree: Tree) -> np.ndarray:
    """Per-node flow velocity from continuity, ``v = Q / (pi r^2)``.

    Nodes with zero radius report zero velocity rather than dividing by zero.
    Run :func:`compute_flow` and Murray sizing first.
    """
    v = np.zeros(len(tree))
    for i, node in enumerate(tree.nodes):
        area = np.pi * node.radius ** 2
        v[i] = node.flow / area if area > 0 else 0.0
    return v


def strahler_order(tree: Tree) -> np.ndarray:
    """Horton–Strahler stream order for every node.

    A leaf has order 1. When two or more children of the highest order meet,
    the parent's order increments; otherwise it inherits the max child order.
    This is the standard way hydrologists rank river tributaries, and it maps
    cleanly onto vessel generations.
    """
    order = np.zeros(len(tree), dtype=int)
    for idx in _leaves_first(tree):
        kids = tree.children(idx)
        if not kids:
            order[idx] = 1
            continue
        child_orders = [order[c] for c in kids]
        top = max(child_orders)
        order[idx] = top + 1 if child_orders.count(top) > 1 else top
    return order
