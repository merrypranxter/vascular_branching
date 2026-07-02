"""Space colonization (Runions et al. 2007).

Scatter *attractor* points through the region you want filled — an organ, a
leaf blade, a watershed. The network grows one segment at a time: every
attractor pulls on its nearest node, the pulls are averaged into a growth
direction, and a new node is placed a fixed step in that direction. Attractors
that get close enough to the network are consumed. The result naturally
fills space and never overshoots, which is why it looks so much like real
venation and neuron arbors.
"""

from __future__ import annotations

import numpy as np

from .core import Tree


def grow_space_colonization(
    attractors: np.ndarray,
    root: tuple[float, float] = (0.0, 0.0),
    step: float = 0.05,
    influence_radius: float = 0.5,
    kill_radius: float = 0.1,
    max_iterations: int = 2000,
    rng: np.random.Generator | None = None,
) -> Tree:
    """Grow a network that colonises a cloud of attractor points.

    Args:
        attractors: ``(M, 2)`` array of target points to fill.
        root: Seed position for the network.
        step: Distance a node grows per iteration. Smaller == smoother, slower.
        influence_radius: An attractor only pulls on nodes within this range.
        kill_radius: An attractor is consumed once a node comes this close.
        max_iterations: Safety cap on growth steps.
        rng: Optional NumPy generator (unused by the deterministic core, kept
            for API symmetry with the stochastic generators).

    Returns:
        A :class:`Tree` filling the attractor cloud.
    """
    attractors = np.asarray(attractors, dtype=float)
    if attractors.ndim != 2 or attractors.shape[1] != 2:
        raise ValueError("attractors must be an (M, 2) array")

    tree = Tree(dim=2)
    tree.add_node(np.asarray(root, dtype=float))
    alive = np.ones(len(attractors), dtype=bool)

    for _ in range(max_iterations):
        if not alive.any():
            break
        node_pos = tree.positions()

        # For each live attractor, find its nearest node.
        live_idx = np.where(alive)[0]
        deltas = attractors[live_idx, None, :] - node_pos[None, :, :]
        dists = np.linalg.norm(deltas, axis=2)
        nearest = dists.argmin(axis=1)
        nearest_dist = dists[np.arange(len(live_idx)), nearest]

        # Consume attractors the network has already reached.
        reached = nearest_dist < kill_radius
        alive[live_idx[reached]] = False

        # Accumulate normalised pulls onto each node within influence range.
        influenced = (~reached) & (nearest_dist < influence_radius)
        pulls: dict[int, np.ndarray] = {}
        for k in np.where(influenced)[0]:
            n = int(nearest[k])
            d = deltas[k, n]
            norm = nearest_dist[k]  # already the norm of d, computed above
            if norm == 0:
                continue
            pulls.setdefault(n, np.zeros(2))
            pulls[n] += d / norm

        if not pulls:
            # Nothing in range: nudge the single closest node toward its
            # attractor so growth can resume instead of stalling.
            k = int(nearest_dist.argmin())
            n = int(nearest[k])
            d = deltas[k, n]
            norm = nearest_dist[k]  # already the norm of d, computed above
            if norm == 0:
                break
            pulls[n] = d / norm

        for n, direction in pulls.items():
            norm = np.linalg.norm(direction)
            if norm == 0:
                continue
            new_pos = tree.nodes[n].pos + step * direction / norm
            tree.add_node(new_pos, parent=n)

    return tree


def disc_attractors(
    n: int,
    center: tuple[float, float] = (0.0, 1.0),
    radius: float = 1.0,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Uniformly sample ``n`` attractor points inside a disc — a quick canopy."""
    rng = rng or np.random.default_rng()
    r = radius * np.sqrt(rng.random(n))
    theta = rng.random(n) * 2 * np.pi
    pts = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
    return pts + np.asarray(center)
