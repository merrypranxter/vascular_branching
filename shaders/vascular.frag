// vascular.frag — procedural branching veins, Shadertoy-compatible.
//
// A real-time cousin of the Python generators. Instead of growing an explicit
// tree, it carves vessels directly out of a domain-warped noise field: fractal
// Brownian motion warps space, and thin bright ridges through that field read
// as branching vasculature. Pumping is faked by animating flow along the veins.
//
// Paste into https://www.shadertoy.com/new, or drive it with any GLSL host that
// provides iResolution / iTime / iMouse uniforms.
//
// Uniforms (Shadertoy convention):
//   iResolution : viewport size in pixels
//   iTime       : seconds since start (drives the pulse)
//   iMouse      : xy = cursor in pixels (repositions the source)

#define OCTAVES 6

// -- style knobs --------------------------------------------------------------
const vec3  ARTERY = vec3(0.80, 0.10, 0.12);   // oxygenated red
const vec3  VEIN   = vec3(0.18, 0.28, 0.55);   // deoxygenated blue
const vec3  TISSUE = vec3(0.96, 0.90, 0.84);   // substrate the vessels sit in
const float VESSEL_SHARP = 42.0;               // higher = thinner vessels
const float WARP     = 0.65;                    // domain-warp strength
const float PULSE_HZ = 1.1;                     // heartbeats per second

// Hash / value noise ----------------------------------------------------------
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 345.45));
    p += dot(p, p + 34.345);
    return fract(p.x * p.y);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);           // smoothstep interpolation
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Fractal Brownian motion -----------------------------------------------------
float fbm(vec2 p) {
    float sum = 0.0, amp = 0.5, freq = 1.0;
    for (int i = 0; i < OCTAVES; i++) {
        sum += amp * noise(p * freq);
        freq *= 2.0;
        amp *= 0.5;
    }
    return sum;
}

// Ridged field: 1.0 on the crest lines, falling off to the sides. Those crests
// are the vessels. Domain-warping fbm with itself makes them branch and curl.
float vesselField(vec2 uv, out float along) {
    vec2 warp = vec2(fbm(uv + vec2(0.0, 1.7)),
                     fbm(uv + vec2(4.2, 9.3)));
    vec2 wp = uv + WARP * warp;
    float n = fbm(wp * 1.5);
    along = wp.x + wp.y;                    // coordinate used to animate flow
    float ridge = 1.0 - abs(2.0 * n - 1.0); // fold [0,1] into a crest at 0.5
    return pow(ridge, VESSEL_SHARP * 0.05);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (fragCoord - 0.5 * iResolution.xy) / iResolution.y;
    uv *= 3.0;

    // Vessels radiate from a source you can drag with the mouse.
    vec2 src = (iMouse.xy - 0.5 * iResolution.xy) / iResolution.y * 3.0;
    if (iMouse.xy == vec2(0.0)) src = vec2(0.0, -1.2);
    float r = length(uv - src);

    float along;
    float vessel = vesselField(uv, along);

    // Murray-ish taper: vessels thin with distance from the source.
    vessel *= smoothstep(3.0, 0.0, r);

    // Pulse: a bright wave of "flow" travelling outward along the vessels.
    float pulse = 0.5 + 0.5 * sin(along * 6.0 - iTime * PULSE_HZ * 6.2831);
    vessel *= 0.6 + 0.4 * pulse;

    // Artery near the source, cooling to venous blue at the periphery.
    vec3 blood = mix(ARTERY, VEIN, smoothstep(0.0, 2.5, r));
    vec3 col = mix(TISSUE, blood, clamp(vessel, 0.0, 1.0));

    // Subtle tissue shading so the substrate isn't flat.
    col *= 0.9 + 0.1 * fbm(uv * 2.0);

    fragColor = vec4(col, 1.0);
}
