"""Visual style presets.

A style bundles the aesthetic choices that make the *same* tree read as an
artery, a river delta, or a circuit trace: colour map, background, how line
width scales with radius, and whether junctions are rounded (organic) or
squared (artificial). Colouring can key off radius, depth, flow, or velocity.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Style:
    """Rendering parameters for one visual language.

    Attributes:
        name: Human-readable identifier.
        cmap: Matplotlib colormap name used along the ``color_by`` axis.
        background: Figure/axes background colour.
        color_by: Which per-node quantity drives colour — one of
            ``"radius"``, ``"depth"``, ``"flow"``, ``"velocity"``.
        width_scale: Multiplier from radius to line width in points.
        width_gamma: Exponent applied to radius before scaling; < 1 fattens
            thin vessels, > 1 exaggerates the trunk.
        capstyle: ``"round"`` for organic tissue, ``"projecting"`` for circuits.
        glow: If set, draw a soft wider stroke underneath for a neon look.
    """

    name: str
    cmap: str
    background: str
    color_by: str = "radius"
    width_scale: float = 6.0
    width_gamma: float = 1.0
    capstyle: str = "round"
    glow: bool = False


ANATOMICAL = Style(
    name="anatomical",
    cmap="Reds",
    background="#f5efe6",
    color_by="velocity",
    width_scale=7.0,
    width_gamma=0.9,
    capstyle="round",
)

BOTANICAL = Style(
    name="botanical",
    cmap="YlGn",
    background="#1a1a12",
    color_by="depth",
    width_scale=6.0,
    width_gamma=1.1,
    capstyle="round",
)

RIVER = Style(
    name="river",
    cmap="Blues",
    background="#e8e0cf",
    color_by="flow",
    width_scale=5.0,
    width_gamma=0.8,
    capstyle="round",
)

CIRCUIT = Style(
    name="circuit",
    cmap="summer",
    background="#04120a",
    color_by="depth",
    width_scale=4.0,
    width_gamma=1.0,
    capstyle="projecting",
    glow=True,
)

NEURAL = Style(
    name="neural",
    cmap="magma",
    background="#000010",
    color_by="radius",
    width_scale=4.5,
    width_gamma=0.85,
    capstyle="round",
    glow=True,
)

STYLES: dict[str, Style] = {
    s.name: s for s in (ANATOMICAL, BOTANICAL, RIVER, CIRCUIT, NEURAL)
}


def get_style(name: str) -> Style:
    """Look up a style by name, with a helpful error listing the options."""
    try:
        return STYLES[name]
    except KeyError:
        raise KeyError(
            f"unknown style {name!r}; choose from {sorted(STYLES)}"
        ) from None
