"""Murray's law: the diameter rule that real vascular systems obey.

Murray (1926) showed that the metabolic cost of pumping blood plus the cost of
maintaining blood volume is minimised when, at every bifurcation,

    r_parent**3 == r_child1**3 + r_child2**3

More generally, for a junction with any number of children and an exponent
``k`` (3 for laminar blood flow, ~2.3–2.7 observed in some plants and rivers):

    r_parent**k == sum(r_child**k)

We assign radii by walking the tree from the leaves inward, cubing and summing.
"""

from __future__ import annotations

from .core import Tree


def apply_murray(tree: Tree, leaf_radius: float = 1.0, exponent: float = 3.0) -> Tree:
    """Assign a radius to every node so the tree obeys Murray's law.

    Args:
        tree: The network to size. Modified in place *and* returned.
        leaf_radius: Radius given to every terminal vessel.
        exponent: The Murray exponent ``k``. 3.0 is the classic cube law.

    Returns:
        The same tree, with ``node.radius`` set everywhere.
    """
    order = _leaves_first(tree)
    for idx in order:
        kids = tree.children(idx)
        if not kids:
            tree.nodes[idx].radius = leaf_radius
        else:
            total = sum(tree.nodes[c].radius ** exponent for c in kids)
            tree.nodes[idx].radius = total ** (1.0 / exponent)
    return tree


def murray_residual(tree: Tree, exponent: float = 3.0) -> float:
    """Largest relative violation of Murray's law across all junctions.

    Returns 0.0 for a perfectly obedient tree. Useful as a test assertion and
    for checking hand-built or noisy networks.
    """
    worst = 0.0
    for idx in range(len(tree)):
        kids = tree.children(idx)
        if not kids:  # leaves have no junction to check
            continue
        lhs = tree.nodes[idx].radius ** exponent
        rhs = sum(tree.nodes[c].radius ** exponent for c in kids)
        if lhs > 0:
            worst = max(worst, abs(lhs - rhs) / lhs)
    return worst


def _leaves_first(tree: Tree) -> list[int]:
    """Return node indices ordered so children always precede their parents.

    Sorting by descending depth is enough: a child's depth is always strictly
    greater than its parent's, so processing deep nodes first guarantees a
    child is sized before we reach its parent.
    """
    return sorted(range(len(tree)), key=lambda i: tree.nodes[i].depth, reverse=True)
