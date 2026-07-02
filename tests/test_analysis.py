import numpy as np
import pytest

import vascular as vb
from vascular.core import Tree


def test_murray_law_holds_at_every_junction():
    tree = vb.grow_csg(depth=6, branching_angle=30, length_ratio=0.7)
    vb.apply_murray(tree, leaf_radius=1.0, exponent=3.0)
    assert vb.murray_residual(tree, exponent=3.0) < 1e-9


def test_murray_root_radius_by_hand():
    # A single symmetric bifurcation: two leaves of radius 1, cube law.
    t = Tree()
    r = t.add_node((0, 0))
    a = t.add_node((-1, 1), parent=r)
    b = t.add_node((1, 1), parent=r)
    vb.apply_murray(t, leaf_radius=1.0, exponent=3.0)
    # r_root**3 = 1 + 1 => r_root = 2**(1/3)
    assert t.nodes[r].radius == pytest.approx(2 ** (1 / 3))
    assert t.nodes[a].radius == 1.0


def test_flow_is_conserved():
    tree = vb.grow_csg(depth=5, branching_angle=25, length_ratio=0.7)
    vb.compute_flow(tree, leaf_flow=1.0)
    root = tree.roots()[0]
    # Root flow must equal the number of leaves (each contributes 1 unit).
    assert tree.nodes[root].flow == pytest.approx(len(tree.leaves()))


def test_velocity_zero_when_no_radius():
    t = Tree()
    r = t.add_node((0, 0))
    t.add_node((0, 1), parent=r, radius=0.0)
    vb.compute_flow(t)
    v = vb.velocities(t)
    assert v[1] == 0.0  # radius 0 => area 0 => guarded to 0, not inf


def test_strahler_orders():
    # Balanced binary tree of depth 2: leaves order 1, mid order 2, root order 3.
    tree = vb.grow_csg(depth=2, branching_angle=30, length_ratio=0.7)
    order = vb.strahler_order(tree)
    assert order.max() == 3
    for leaf in tree.leaves():
        assert order[leaf] == 1
