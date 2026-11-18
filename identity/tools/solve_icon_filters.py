#!/usr/bin/env python3
"""Solve the CSS filter chains web_theme_slate applies to the 'symbol' icon files.

The files are drawn in the light theme's own colours (glyph = muted ink, tile = surface-high,
hairline ink at 32 %), so light mode at rest needs no filter. Hover (light) and rest / hover (dark)
are filter chains; this script searches the chain parameters so the three drawn colours land on
the theme's target colours. CSS shorthand filters are applied in sRGB, in the order written.
"""
import math, random, sys

def clamp(v): return min(1.0, max(0.0, v))
def hex2rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
def rgb2hex(c): return '#%02X%02X%02X' % tuple(round(clamp(v) * 255) for v in c)
def mat(c, m): r, g, b = c; return tuple(clamp(m[i][0]*r + m[i][1]*g + m[i][2]*b) for i in range(3))
def invert(c, a): return tuple(clamp(a*(1-v) + (1-a)*v) for v in c)
def sepia(c, a):
    return mat(c, [[0.393+0.607*(1-a), 0.769-0.769*(1-a), 0.189-0.189*(1-a)],
                   [0.349-0.349*(1-a), 0.686+0.314*(1-a), 0.168-0.168*(1-a)],
                   [0.272-0.272*(1-a), 0.534-0.534*(1-a), 0.131+0.869*(1-a)]])
def saturate(c, s):
    return mat(c, [[0.213+0.787*s, 0.715-0.715*s, 0.072-0.072*s],
                   [0.213-0.213*s, 0.715+0.285*s, 0.072-0.072*s],
                   [0.213-0.213*s, 0.715-0.715*s, 0.072+0.928*s]])
def hue_rotate(c, deg):
    a = math.radians(deg); cs, sn = math.cos(a), math.sin(a)
    return mat(c, [[0.213+cs*0.787-sn*0.213, 0.715-cs*0.715-sn*0.715, 0.072-cs*0.072+sn*0.928],
                   [0.213-cs*0.213+sn*0.143, 0.715+cs*0.285+sn*0.140, 0.072-cs*0.072-sn*0.283],
                   [0.213-cs*0.213-sn*0.787, 0.715-cs*0.715+sn*0.715, 0.072+cs*0.928+sn*0.072]])
def brightness(c, b): return tuple(clamp(v*b) for v in c)
def contrast(c, k): return tuple(clamp((v-0.5)*k + 0.5) for v in c)

def apply(chain, c):
    for name, val in chain:
        c = {'invert': invert, 'sepia': sepia, 'saturate': saturate, 'hue-rotate': hue_rotate,
             'brightness': brightness, 'contrast': contrast}[name](c, val)
    return c

def css(chain):
    out = []
    for name, val in chain:
        if name == 'hue-rotate': out.append(f'hue-rotate({val:.0f}deg)')
        elif name in ('invert', 'sepia') and val <= 0.005: continue
        else: out.append(f'{name}({val:.2f})')
    return ' '.join(out) or 'none'

def solve(colours, targets, weights, use_invert, seed=1):
    """colours/targets: dicts name -> hex. Random search + local refinement."""
    rnd = random.Random(seed)
    names = list(colours)
    src = {n: hex2rgb(colours[n]) for n in names}
    dst = {n: hex2rgb(targets[n]) for n in names}
    def err(p):
        chain = build(p)
        return sum(weights[n] * sum((a-b)**2 for a, b in zip(apply(chain, src[n]), dst[n])) for n in names)
    def build(p):
        inv, sep, sat, hue, bri, con = p
        return [('invert', inv if use_invert else 0.0), ('sepia', sep), ('saturate', sat), ('hue-rotate', hue), ('brightness', bri), ('contrast', con)]
    best, best_e = None, 1e9
    for _ in range(6000):
        p = [1.0 if use_invert else 0.0, rnd.random(), rnd.uniform(0.3, 12), rnd.uniform(0, 360), rnd.uniform(0.4, 2.0), rnd.uniform(0.4, 2.0)]
        e = err(p)
        if e < best_e: best, best_e = p, e
    step = [0.0, 0.1, 1.0, 20.0, 0.1, 0.1]
    for it in range(4000):
        q = list(best); i = rnd.randrange(1, 6); q[i] += rnd.gauss(0, step[i])
        q[1] = clamp(q[1]); q[2] = max(0, q[2]); q[3] %= 360; q[4] = max(0, q[4]); q[5] = max(0, q[5])
        e = err(q)
        if e < best_e: best, best_e = q, e
        if it % 800 == 799: step = [s*0.6 for s in step]
    chain = build(best)
    return chain, best_e, {n: rgb2hex(apply(chain, src[n])) for n in names}

if __name__ == '__main__':
    drawn = {'glyph': '#4B5563', 'tile': '#F4F6F9', 'hair': '#C0C6D0'}   # hair = hairline ink at .32 over the tile
    W = {'glyph': 3.0, 'tile': 1.5, 'hair': 0.5}
    cases = {
        'light hover': ({'glyph': '#3F54AD', 'tile': '#EBEEF7', 'hair': '#3F54AD'}, False),   # accent glyph, 8 % accent tint on the tile
        'dark rest':   ({'glyph': '#B4BCC8', 'tile': '#2E333B', 'hair': '#4A5160'}, True),
        'dark hover':  ({'glyph': '#6F84D9', 'tile': '#333A4E', 'hair': '#6F84D9'}, True),
    }
    for label, (targets, inv) in cases.items():
        chain, e, got = solve(drawn, targets, W, inv)
        print(f'{label:12s} {css(chain)}')
        for n in drawn: print(f'    {n:6s} {drawn[n]} -> {got[n]}  (target {targets[n]})')
