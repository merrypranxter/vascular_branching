"""Render a :class:`Tree` to a matplotlib figure.

The renderer is style-driven: hand it a tree and a :class:`~vascular.styles.Style`
and it picks line widths from the Murray radii and colours from whichever
quantity the style selects. It never opens a window itself — it returns the
figure/axes so callers decide whether to ``savefig`` or ``show``.
"""

from __future__ import annotations

import matplotlib

# Headless-safe default, but don't wrestle a backend away from a caller who has
# already set one (e.g. an interactive notebook) — force=False leaves theirs be.
matplotlib.use("Agg", force=False)

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

from .core import Tree
from .flow import velocities
from .styles import Style, get_style


def _node_values(tree: Tree, color_by: str) -> np.ndarray:
    if color_by == "radius":
        return np.array([n.radius for n in tree.nodes])
    if color_by == "depth":
        return np.array([n.depth for n in tree.nodes], dtype=float)
    if color_by == "flow":
        return np.array([n.flow for n in tree.nodes])
    if color_by == "velocity":
        return velocities(tree)
    raise ValueError(f"unknown color_by {color_by!r}")


def render(
    tree: Tree,
    style: Style | str = "anatomical",
    ax=None,
    figsize: tuple[float, float] = (8, 8),
    dpi: int = 120,
):
    """Draw ``tree`` and return ``(fig, ax)``.

    Args:
        tree: A network. Radii should be set (Murray) for sensible line widths;
            flow/velocity styles also need :func:`vascular.flow.compute_flow`.
        style: A :class:`Style` or the name of a built-in one.
        ax: Draw onto an existing axes instead of creating a figure.
        figsize: Figure size in inches (ignored when ``ax`` is given).
        dpi: Figure resolution (ignored when ``ax`` is given).

    Returns:
        ``(fig, ax)`` for further tweaking, saving, or showing.
    """
    if isinstance(style, str):
        style = get_style(style)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else:
        fig = ax.figure

    fig.patch.set_facecolor(style.background)
    ax.set_facecolor(style.background)

    _strip_axes(ax)

    segs = list(tree.segments())
    if not segs:
        return fig, ax

    lines = np.array([[p, c] for p, c, _ in segs])
    node_vals = _node_values(tree, style.color_by)
    # Colour each segment by the value at its distal (child) node.
    child_idx = [i for i, n in enumerate(tree.nodes) if n.parent >= 0]
    seg_vals = node_vals[child_idx]
    widths = np.array([n.radius for _, _, n in segs])
    widths = style.width_scale * np.power(np.clip(widths, 1e-6, None), style.width_gamma)

    vmin, vmax = float(seg_vals.min()), float(seg_vals.max())
    if vmax <= vmin:
        vmax = vmin + 1e-9

    if style.glow:
        glow = LineCollection(
            lines, linewidths=widths * 3.0, colors="white",
            alpha=0.08, capstyle=style.capstyle,
        )
        ax.add_collection(glow)

    lc = LineCollection(
        lines,
        linewidths=widths,
        cmap=style.cmap,
        capstyle=style.capstyle,
        joinstyle="round",
    )
    lc.set_array(seg_vals)
    lc.set_clim(vmin, vmax)
    ax.add_collection(lc)

    _autoscale(ax, tree)
    ax.set_aspect("equal")
    return fig, ax


def _strip_axes(ax) -> None:
    """Hide ticks and spines but keep the axes background colour visible.

    ``ax.set_axis_off()`` would also hide the patch, which erases the per-panel
    background in multi-style contact sheets — so we remove the furniture by
    hand instead.
    """
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _autoscale(ax, tree: Tree, pad: float = 0.05) -> None:
    lo, hi = tree.bounds()
    span = np.maximum(hi - lo, 1e-9)
    ax.set_xlim(lo[0] - pad * span[0], hi[0] + pad * span[0])
    ax.set_ylim(lo[1] - pad * span[1], hi[1] + pad * span[1])


def save(tree: Tree, path: str, style: Style | str = "anatomical", **kwargs) -> str:
    """Render ``tree`` and write it to ``path``; returns the path.

    Convenience wrapper so one-liners in examples stay short.
    """
    fig, _ = render(tree, style=style, **kwargs)
    fig.savefig(path, facecolor=fig.get_facecolor(), bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return path
