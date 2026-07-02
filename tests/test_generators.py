import numpy as np
import pytest

import vascular as vb


def test_csg_node_count_matches_geometry():
    # A binary tree of depth d adds a trunk plus 2 + 4 + ... + 2**d nodes.
    tree = vb.grow_csg(depth=3, n_children=2)
    # root + trunk tip + sum_{i=1..3} 2**i = 1 + 1 + (2+4+8) = 16
    assert len(tree) == 16
    assert len(tree.roots()) == 1


def test_csg_length_ratio_shrinks_children():
    tree = vb.grow_csg(depth=2, branching_angle=0, length_ratio=0.5,
                       n_children=1, initial_length=1.0)
    # With one child and zero angle it's a straight chain of shrinking segments.
    seg_lengths = [np.linalg.norm(c - p) for p, c, _ in tree.segments()]
    # trunk = 1.0, then 0.5, then 0.25
    assert seg_lengths[0] == pytest.approx(1.0)
    assert seg_lengths[1] == pytest.approx(0.5)
    assert seg_lengths[2] == pytest.approx(0.25)


def test_space_colonization_reaches_attractors():
    rng = np.random.default_rng(0)
    pts = vb.disc_attractors(200, center=(0, 1), radius=0.8, rng=rng)
    tree = vb.grow_space_colonization(pts, root=(0, 0), step=0.05)
    assert len(tree) > 1
    # The network should reach into the attractor cloud, not stall at the root.
    top = tree.positions()[:, 1].max()
    assert top > 0.5


def test_space_colonization_rejects_bad_shape():
    with pytest.raises(ValueError):
        vb.grow_space_colonization(np.zeros((5, 3)))


def test_dla_is_connected_tree():
    tree = vb.grow_dla(n_particles=200, grid_size=101,
                       rng=np.random.default_rng(1))
    # Exactly one root, and every other node has a valid parent index.
    assert len(tree.roots()) == 1
    for i, n in enumerate(tree.nodes):
        if n.parent >= 0:
            assert 0 <= n.parent < len(tree)
            assert n.parent != i


def test_dla_reproducible_with_seed():
    a = vb.grow_dla(n_particles=150, grid_size=81, rng=np.random.default_rng(5))
    b = vb.grow_dla(n_particles=150, grid_size=81, rng=np.random.default_rng(5))
    assert np.allclose(a.positions(), b.positions())
