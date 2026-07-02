import numpy as np
import pytest

from vascular.core import Tree


def test_add_node_sets_depth_from_parent():
    t = Tree()
    r = t.add_node((0, 0))
    a = t.add_node((0, 1), parent=r)
    b = t.add_node((0, 2), parent=a)
    assert t.nodes[r].depth == 0
    assert t.nodes[a].depth == 1
    assert t.nodes[b].depth == 2


def test_roots_and_leaves():
    t = Tree()
    r = t.add_node((0, 0))
    a = t.add_node((1, 0), parent=r)
    t.add_node((2, 0), parent=r)
    t.add_node((1, 1), parent=a)
    assert t.roots() == [r]
    # leaves are the two terminals, not the branching node a
    assert set(t.leaves()) == {2, 3}


def test_children_tracks_links():
    t = Tree()
    r = t.add_node((0, 0))
    c1 = t.add_node((1, 0), parent=r)
    c2 = t.add_node((0, 1), parent=r)
    assert set(t.children(r)) == {c1, c2}
    assert t.children(c1) == []


def test_segments_count_equals_non_root_nodes():
    t = Tree()
    r = t.add_node((0, 0))
    t.add_node((1, 0), parent=r)
    t.add_node((0, 1), parent=r)
    assert len(list(t.segments())) == 2


def test_total_length_matches_geometry():
    t = Tree()
    r = t.add_node((0, 0))
    t.add_node((3, 4), parent=r)  # length 5
    assert t.total_length() == pytest.approx(5.0)


def test_wrong_dimension_rejected():
    t = Tree(dim=2)
    with pytest.raises(ValueError):
        t.add_node((0, 0, 0))


def test_bounds():
    t = Tree()
    t.add_node((-1, 2))
    t.add_node((3, -4))
    lo, hi = t.bounds()
    assert np.allclose(lo, [-1, -4])
    assert np.allclose(hi, [3, 2])
