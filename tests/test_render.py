import matplotlib

matplotlib.use("Agg")

import pytest

import vascular as vb
from vascular.styles import STYLES


@pytest.mark.parametrize("name", list(STYLES))
def test_every_style_renders(name, tmp_path):
    tree = vb.grow_csg(depth=5, branching_angle=25, length_ratio=0.7)
    vb.apply_murray(tree, leaf_radius=0.5)
    vb.compute_flow(tree)
    out = tmp_path / f"{name}.png"
    path = vb.save(tree, str(out), style=name)
    assert out.exists() and out.stat().st_size > 0
    assert path == str(out)


def test_get_style_unknown_raises():
    with pytest.raises(KeyError):
        vb.get_style("does-not-exist")


def test_render_empty_tree_is_safe():
    from vascular.core import Tree
    fig, ax = vb.render(Tree())
    assert fig is not None
