# Shaders

Real-time procedural vasculature — the GPU counterpart to the Python
generators. Rather than growing an explicit `Tree`, these shaders carve vessels
straight out of a noise field, which is how you'd draw living, pulsing tissue in
a game, a music visualiser, or a demoscene intro.

## `vascular.frag`

Domain-warped fractal Brownian motion folded into ridge lines that read as
branching veins, with an animated flow pulse and arterial→venous colouring.

### Run it on Shadertoy

1. Open <https://www.shadertoy.com/new>.
2. Replace the default code with the contents of `vascular.frag`.
3. Press the ▶ button. Drag the mouse to move the blood source.

### Run it locally

Any GLSL host that supplies the Shadertoy uniforms works. A minimal option is
[`glslViewer`](https://github.com/patriciogonzalezvivo/glslViewer):

```bash
glslViewer shaders/vascular.frag
```

### How it maps to the Python models

| Python concept        | Shader analogue                                    |
|-----------------------|----------------------------------------------------|
| Space colonization    | domain warp pulling ridge lines toward structure   |
| Murray's-law taper    | `smoothstep(3.0, 0.0, r)` thinning with distance   |
| Flow visualisation    | travelling `pulse` term along the vessels          |
| `vein_vs_artery`      | `mix(ARTERY, VEIN, ...)` by radius from the source |

Tune `VESSEL_SHARP`, `WARP`, and `PULSE_HZ` at the top of the file to move
between capillary-fine and major-vessel looks.
