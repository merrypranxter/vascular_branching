"""Diffusion-limited aggregation (Witten & Sander 1981).

Particles released from far away random-walk until they touch the existing
cluster, then freeze in place. The result is a stochastic, fractal tree with a
dimension of about 1.71 in 2D. Because each particle sticks to a *specific*
existing particle, the aggregate is naturally a parent-linked tree — exactly
our :class:`Tree` structure — so DLA growth and vessel growth share code.
"""

from __future__ import annotations

import numpy as np

from .core import Tree

# The four von Neumann neighbours a walker can step to on the lattice.
_STEPS = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])


def grow_dla(
    n_particles: int = 800,
    grid_size: int = 201,
    stickiness: float = 1.0,
    max_walk: int = 100_000,
    seed_pos: tuple[int, int] | None = None,
    rng: np.random.Generator | None = None,
) -> Tree:
    """Grow a DLA cluster and return it as a tree.

    Args:
        n_particles: How many particles to aggregate.
        grid_size: Side length of the square lattice (odd is tidiest).
        stickiness: Probability a contacting particle actually sticks
            (< 1 produces denser, bushier clusters).
        max_walk: Steps before a wandering particle is abandoned.
        seed_pos: Lattice cell for the initial seed; defaults to the centre.
        rng: Optional NumPy generator for reproducibility.

    Returns:
        A :class:`Tree` in lattice coordinates. Positions are integer cell
        indices cast to float; scale them as you like before rendering.
    """
    rng = rng or np.random.default_rng()
    g = grid_size
    occupied = -np.ones((g, g), dtype=int)  # stores node index, -1 if empty

    tree = Tree(dim=2)
    seed = seed_pos or (g // 2, g // 2)
    seed_idx = tree.add_node(np.array(seed, dtype=float))
    occupied[seed] = seed_idx

    max_radius = 2.0  # spawn ring, grows with the cluster
    center = np.array(seed, dtype=float)

    for _ in range(n_particles):
        spawn_r = min(max_radius + 5, g / 2 - 1)
        angle = rng.random() * 2 * np.pi
        pos = np.round(center + spawn_r * np.array([np.cos(angle), np.sin(angle)]))
        pos = pos.astype(int)

        stuck_to = _walk_until_contact(pos, occupied, g, center, spawn_r,
                                       max_walk, stickiness, rng)
        if stuck_to is None:
            continue

        cell, parent_idx = stuck_to
        idx = tree.add_node(np.array(cell, dtype=float), parent=parent_idx)
        occupied[cell] = idx
        r = np.linalg.norm(np.array(cell) - center)
        max_radius = max(max_radius, r)

    return tree


def _walk_until_contact(pos, occupied, g, center, spawn_r, max_walk, stickiness, rng):
    """Random-walk one particle; return ``(cell, parent_idx)`` when it sticks."""
    kill_r = spawn_r * 2 + 5
    for _ in range(max_walk):
        neighbour = _adjacent_occupied(pos, occupied, g)
        if neighbour is not None and rng.random() <= stickiness:
            return tuple(pos), neighbour

        pos = pos + _STEPS[rng.integers(4)]

        # Abandon walkers that step off the lattice — the next particle spawns
        # fresh, so there's no need to reflect or wrap them.
        if not (0 <= pos[0] < g and 0 <= pos[1] < g):
            return None
        # Compare squared distance to avoid a sqrt in this hot inner loop.
        if (pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2 > kill_r ** 2:
            return None
    return None


def _adjacent_occupied(pos, occupied, g):
    """Index of an occupied von Neumann neighbour, or ``None``."""
    for step in _STEPS:
        nb = pos + step
        if 0 <= nb[0] < g and 0 <= nb[1] < g:
            occ = occupied[nb[0], nb[1]]
            if occ >= 0:
                return int(occ)
    return None
