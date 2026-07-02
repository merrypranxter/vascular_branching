"""Core data structures for branching transport networks.

Every generator in this package — DLA, space colonization, recursive CSG —
produces the same thing: a :class:`Tree`.  A tree is a set of :class:`Node`
objects, each of which knows its position, its radius, and the index of its
parent.  Segments (the drawable pipes) are implied by the parent links.

Keeping one shared representation means renderers, Murray's-law optimisation,
and flow analysis are written once and work for every generator.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Node:
    """A single junction in the network.

    Attributes:
        pos: Position, shape ``(2,)`` or ``(3,)``.
        parent: Index of the parent node in :attr:`Tree.nodes`, or ``-1`` for a root.
        radius: Vessel radius at this node. Set by :func:`vascular.murray.apply_murray`.
        depth: Topological distance from the root (root == 0).
        flow: Relative volumetric flow through the node. Set by the flow module.
    """

    pos: np.ndarray
    parent: int = -1
    radius: float = 1.0
    depth: int = 0
    flow: float = 0.0

    def __post_init__(self) -> None:
        self.pos = np.asarray(self.pos, dtype=float)


class Tree:
    """A branching network as a parent-linked list of nodes.

    The tree is a *directed* structure that flows from root(s) outward to the
    leaves. Add the root first, then attach children to existing nodes by index.
    """

    def __init__(self, dim: int = 2) -> None:
        self.dim = dim
        self.nodes: list[Node] = []
        self._children: dict[int, list[int]] = {}

    # -- construction ------------------------------------------------------
    def add_node(self, pos, parent: int = -1, radius: float = 1.0) -> int:
        """Append a node and return its index.

        The depth is derived from the parent automatically, so callers never
        have to bookkeep it.
        """
        pos = np.asarray(pos, dtype=float)
        if pos.shape != (self.dim,):
            raise ValueError(f"expected {self.dim}D position, got shape {pos.shape}")
        depth = 0 if parent < 0 else self.nodes[parent].depth + 1
        idx = len(self.nodes)
        self.nodes.append(Node(pos=pos, parent=parent, radius=radius, depth=depth))
        self._children.setdefault(idx, [])
        if parent >= 0:
            self._children.setdefault(parent, []).append(idx)
        return idx

    # -- topology ----------------------------------------------------------
    def children(self, idx: int) -> list[int]:
        """Indices of the direct children of node ``idx``."""
        return self._children.get(idx, [])

    def roots(self) -> list[int]:
        """Indices of every node without a parent."""
        return [i for i, n in enumerate(self.nodes) if n.parent < 0]

    def leaves(self) -> list[int]:
        """Indices of every node without children (the terminals)."""
        return [i for i in range(len(self.nodes)) if not self._children.get(i)]

    def segments(self):
        """Yield ``(parent_pos, child_pos, child_node)`` for every edge.

        This is what renderers iterate over: one drawable pipe per non-root
        node, sized by ``child_node.radius``.
        """
        for i, node in enumerate(self.nodes):
            if node.parent >= 0:
                yield self.nodes[node.parent].pos, node.pos, node

    # -- geometry ----------------------------------------------------------
    def positions(self) -> np.ndarray:
        """All node positions stacked into an ``(N, dim)`` array."""
        if not self.nodes:
            return np.empty((0, self.dim))
        return np.array([n.pos for n in self.nodes])

    def bounds(self):
        """Axis-aligned bounding box as ``(min_corner, max_corner)``.

        An empty tree has no extent, so we return a degenerate box at the
        origin rather than letting ``min``/``max`` raise on an empty array.
        """
        p = self.positions()
        if len(p) == 0:
            return np.zeros(self.dim), np.zeros(self.dim)
        return p.min(axis=0), p.max(axis=0)

    def total_length(self) -> float:
        """Sum of every segment length — a cheap proxy for 'how much pipe'."""
        return float(sum(np.linalg.norm(c - p) for p, c, _ in self.segments()))

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return (
            f"Tree(dim={self.dim}, nodes={len(self.nodes)}, "
            f"roots={len(self.roots())}, leaves={len(self.leaves())})"
        )
