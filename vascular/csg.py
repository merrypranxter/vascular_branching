"""Recursive constructive branching (the "CSG tree" of the README).

Each branch splits into ``n`` children, each shorter and rotated relative to
the parent by ``branching_angle``. This is the deterministic, self-similar end
of the spectrum — the cleanest way to see how angle, length ratio, and depth
control the silhouette. Space colonization and DLA are its stochastic cousins.
"""

from __future__ import annotations

import numpy as np

from .core import Tree


def grow_csg(
    depth: int = 8,
    branching_angle: float = 30.0,
    length_ratio: float = 0.75,
    n_children: int = 2,
    initial_length: float = 1.0,
    root: tuple[float, float] = (0.0, 0.0),
    direction: float = 90.0,
    spread: float | None = None,
) -> Tree:
    """Grow a self-similar 2D branching tree.

    Args:
        depth: Number of recursive generations.
        branching_angle: Total angular spread between the outermost siblings,
            in degrees. Each child is fanned evenly within this cone.
        length_ratio: ``child_length / parent_length``. < 1 for a finite tree.
        n_children: Branches created at each split.
        initial_length: Length of the trunk segment.
        root: Position of the base of the trunk.
        direction: Heading of the trunk, in degrees (90 == straight up).
        spread: Optional override for the fan half-angle; defaults to
            ``branching_angle`` so the cone spans ``[-angle, +angle]``.

    Returns:
        A :class:`Tree` (radii unset — run :func:`vascular.murray.apply_murray`).
    """
    tree = Tree(dim=2)
    root_pos = np.asarray(root, dtype=float)
    trunk_dir = np.deg2rad(direction)
    root_idx = tree.add_node(root_pos)

    tip = root_pos + initial_length * np.array([np.cos(trunk_dir), np.sin(trunk_dir)])
    trunk_idx = tree.add_node(tip, parent=root_idx)

    half = np.deg2rad(branching_angle if spread is None else spread)
    _branch(tree, trunk_idx, trunk_dir, initial_length, depth,
            half, length_ratio, n_children)
    return tree


def _branch(tree, parent_idx, heading, length, depth, half, length_ratio, n_children):
    if depth <= 0:
        return
    new_len = length * length_ratio
    offsets = _fan_offsets(n_children, half)
    parent_pos = tree.nodes[parent_idx].pos
    for off in offsets:
        theta = heading + off
        tip = parent_pos + new_len * np.array([np.cos(theta), np.sin(theta)])
        child_idx = tree.add_node(tip, parent=parent_idx)
        _branch(tree, child_idx, theta, new_len, depth - 1,
                half, length_ratio, n_children)


def _fan_offsets(n_children: int, half: float) -> np.ndarray:
    """Angular offsets that spread ``n_children`` evenly across ``[-half, half]``."""
    if n_children == 1:
        return np.array([0.0])
    return np.linspace(-half, half, n_children)
