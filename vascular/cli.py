"""Command-line front end: grow a network and save an image in one shot.

Installed as the ``vascular`` console script (see ``pyproject.toml``), or run
as ``python -m vascular``. Examples::

    vascular csg --depth 10 --angle 26 --style botanical -o tree.png
    vascular dla --particles 2000 --style neural -o dla.png
    vascular colonize --attractors 800 --style anatomical -o organ.png
"""

from __future__ import annotations

import argparse

import numpy as np

from . import (
    Tree,
    apply_murray,
    compute_flow,
    disc_attractors,
    grow_csg,
    grow_dla,
    grow_space_colonization,
    save,
)
from .styles import STYLES


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("-o", "--out", default="vascular.png", help="output image path")
    p.add_argument("--style", default="anatomical", choices=sorted(STYLES),
                   help="visual style preset")
    p.add_argument("--leaf-radius", type=float, default=0.5,
                   help="Murray leaf radius")
    p.add_argument("--exponent", type=float, default=3.0,
                   help="Murray's-law exponent (3.0 = cube law)")
    p.add_argument("--seed", type=int, default=None,
                   help="RNG seed for reproducible stochastic growth")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vascular",
        description="Generate and render fractal branching networks.",
    )
    sub = parser.add_subparsers(dest="model", required=True)

    csg = sub.add_parser("csg", help="recursive self-similar tree")
    csg.add_argument("--depth", type=int, default=9)
    csg.add_argument("--angle", type=float, default=27.0)
    csg.add_argument("--length-ratio", type=float, default=0.76)
    csg.add_argument("--children", type=int, default=2)
    _add_common(csg)

    dla = sub.add_parser("dla", help="diffusion-limited aggregation")
    dla.add_argument("--particles", type=int, default=1200)
    dla.add_argument("--grid", type=int, default=221)
    dla.add_argument("--stickiness", type=float, default=1.0)
    _add_common(dla)

    col = sub.add_parser("colonize", help="space colonization of a disc")
    col.add_argument("--attractors", type=int, default=600)
    col.add_argument("--step", type=float, default=0.04)
    _add_common(col)

    return parser


def _build_tree(args) -> Tree:
    rng = np.random.default_rng(args.seed)
    if args.model == "csg":
        return grow_csg(depth=args.depth, branching_angle=args.angle,
                        length_ratio=args.length_ratio, n_children=args.children)
    if args.model == "dla":
        return grow_dla(n_particles=args.particles, grid_size=args.grid,
                        stickiness=args.stickiness, rng=rng)
    if args.model == "colonize":
        pts = disc_attractors(args.attractors, center=(0, 1), radius=1.0, rng=rng)
        return grow_space_colonization(pts, root=(0, 0), step=args.step)
    raise ValueError(args.model)


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    tree = _build_tree(args)
    apply_murray(tree, leaf_radius=args.leaf_radius, exponent=args.exponent)
    compute_flow(tree)
    path = save(tree, args.out, style=args.style)
    print(f"{tree}  ->  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
