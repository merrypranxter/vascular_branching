# The geometry of branching transport

Blood vessels, tree branches, river deltas, lungs, lightning, and neurons all
converge on the same shape. This is not a coincidence of appearance — it falls
out of a shared problem: **move stuff through space efficiently**. This document
collects the mathematics the code implements.

## 1. Why branching at all?

A single pipe can only serve the points along its length. To service a *volume*
(an organ, a canopy, a watershed) with bounded transport distance, you must
sub-divide repeatedly. Recursive bifurcation is the cheapest way to make a
network whose reach grows to fill space while total path length stays finite —
a space-filling curve made of pipes.

## 2. Murray's law

Cecil Murray (1926) minimised the total power cost of a vessel:

- **pumping cost** ∝ 1 / r⁴ (Poiseuille resistance — thin pipes are expensive to push through)
- **maintenance cost** ∝ r² (blood/tissue volume is metabolically expensive to keep alive)

Summing and minimising over radius at a bifurcation gives the cube law:

```
r_parent³ = r_child₁³ + r_child₂³
```

Generalised to a junction with any number of children and an exponent `k`:

```
r_parent^k = Σ r_childᵢ^k
```

`k = 3` is the classic laminar-flow result. Real systems vary:

| System                     | Observed exponent |
|----------------------------|-------------------|
| Large arteries (laminar)   | ≈ 3.0             |
| Plant xylem                | ≈ 2.3 – 2.5       |
| River networks (Hack-ish)  | ≈ 2.0 – 2.7       |
| Turbulent flow             | → 7/3 ≈ 2.33      |

Implemented in [`vascular/murray.py`](../vascular/murray.py). Because the law is
local (it only relates a node to its direct children), we can satisfy it exactly
by one leaves-to-root sweep — see `apply_murray`. `murray_residual` measures the
worst violation and should be ~1e-16 for trees we build this way.

## 3. Flow conservation and continuity

With radii set, flow follows. Assume each terminal (leaf) draws one unit of flow
and nothing is created or destroyed at junctions. Then each parent carries the
sum of its children — another single leaves-to-root sweep (`compute_flow`).

Velocity follows from continuity, `Q = v · A`:

```
v = Q / (π r²)
```

Because Murray sizing makes cross-sectional area *grow* toward the periphery
(the combined area of the children exceeds the parent for `k < ...`), velocity
drops in the fine vessels — exactly why blood crawls through capillaries and
races in the aorta. See [`vascular/flow.py`](../vascular/flow.py).

## 4. Horton–Strahler order

A topological ranking of "how major" a vessel is, borrowed from hydrology:

- every leaf has order 1;
- when two or more branches of equal, highest order `n` meet, the parent is `n+1`;
- otherwise the parent inherits the maximum child order.

It's the discrete analogue of vessel *generation* and is the standard axis for
comparing a synthetic tree against real morphometric data.

## 5. The three generators

| Generator            | Determinism | What controls the shape             | Best for                    |
|----------------------|-------------|-------------------------------------|-----------------------------|
| CSG (`grow_csg`)     | deterministic | angle, length ratio, depth        | clean self-similar trees    |
| Space colonization   | quasi-random  | attractor cloud, kill/influence radii | filling a given region  |
| DLA (`grow_dla`)     | stochastic    | particle count, stickiness        | wild, dendritic fractals    |

They all emit the same `Tree`, so Murray sizing, flow analysis, and rendering
are written once.

### Space colonization (Runions et al., 2007)

Scatter attractors in the target region. Each step: every attractor votes for
its nearest network node; votes within `influence_radius` are summed into a
normalised growth direction; a new node is added one `step` along it. Attractors
within `kill_radius` of the network are consumed. Growth halts when all
attractors are consumed. This "grow toward what isn't filled yet" rule is why
the output naturally tiles the region without overshoot.

### Diffusion-limited aggregation (Witten & Sander, 1981)

Release particles far away; let them random-walk until they touch the cluster,
then freeze. The probability of sticking is higher on exposed tips (they're
easier to reach by diffusion), which amplifies protrusions into branches. The
resulting fractal dimension in 2D is ≈ 1.71.

## Further reading

- C. D. Murray, "The Physiological Principle of Minimum Work" (1926).
- Witten & Sander, "Diffusion-Limited Aggregation, a Kinetic Critical Phenomenon" (1981).
- Runions, Lane & Prusinkiewicz, "Modeling Trees with a Space Colonization Algorithm" (2007).
- West, Brown & Enquist, "A General Model for the Origin of Allometric Scaling Laws in Biology" (1997).
