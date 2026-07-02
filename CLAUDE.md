# CLAUDE.md

Guidance for AI assistants (and humans) working in this repo.

## What this is

A Python library that generates and visualises fractal branching transport
networks (vessels, rivers, trees). See `README.md` for the tour and
`docs/THEORY.md` for the maths.

## The one idea to hold onto

**Everything is a `Tree`.** Every generator (`grow_csg`, `grow_dla`,
`grow_space_colonization`) returns the same `vascular.core.Tree`, and every
consumer (`apply_murray`, `compute_flow`, `render`, styles) operates on it. When
adding a generator, emit a `Tree`; when adding analysis or output, take one.
That is what keeps the modules composable — don't invent a parallel structure.

## Pipeline order

`grow_* → apply_murray → compute_flow → render/save`. Radii must be set before
velocity/flow styles render meaningfully; flow must be computed before
`velocities`.

## Conventions

- Stochastic generators (`grow_dla`, `grow_space_colonization`) accept an
  `rng: np.random.Generator` for reproducibility — thread it through, don't call
  the global `np.random`.
- Radii come only from `apply_murray`; don't hardcode widths elsewhere.
- `render` never opens a window (uses the Agg backend) and returns `(fig, ax)`.
- Keep new visual looks as `Style` instances registered in `styles.STYLES`.

## Working on it

```bash
pip install -e ".[dev]"
pytest                       # full suite, ~3s
python examples/05_styles_gallery.py   # regenerate a gallery image
```

When you change `render.py` or `styles.py`, re-run the affected `examples/*.py`
so the committed `gallery/` images stay in sync.
