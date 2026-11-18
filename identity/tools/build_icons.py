#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for the Identity "Soft" icon set.

Generates:
  static/src/img/apps/<key>.svg          one neumorphic tile per Odoo application
  static/src/img/apps/png/<key>.png      192 px rasters (Safari PWA icon route)
  static/src/img/brand/{icon,logo}.svg    default brand mark + wordmark
  static/src/img/brand/icon-*.png         PWA / apple-touch / favicon rasters
  static/description/icon.png             module icon
  static/description/icons.html           the design sheet

PNG rasterisation uses headless Chrome (google-chrome / chromium on PATH) and
Pillow; when unavailable the PNGs are left untouched.
"""
import base64
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from icon_catalog import BRAND_SYMBOL, CATEGORIES, GLYPHS, ICONS, SYMBOLS  # noqa: E402

APPS_DIR = os.path.join(MODULE, 'static', 'src', 'img', 'apps')
SYMBOLS_DIR = os.path.join(HERE, 'symbols')
GLYPH_DIR = os.path.join(APPS_DIR, 'glyph')       # glyph-only files: the theme paints them through a CSS mask     # Material Symbols Outlined sources (24 px, viewBox 0 -960 960 960)
BRAND_DIR = os.path.join(MODULE, 'static', 'src', 'img', 'brand')
DESC_DIR = os.path.join(MODULE, 'static', 'description')

TILE = 512
RADIUS = 116          # 22.6 % — same corner ratio Odoo uses for its app tiles
GLYPH_SCALE = 3.9     # 100 → 390 px object box, 61 px margin


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _hex(rgb):
    return '#%02X%02X%02X' % tuple(max(0, min(255, round(c))) for c in rgb)

def mix(a, b, t):
    """t = 0 → a, t = 1 → b"""
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))

def lighten(c, t):
    return mix(c, '#FFFFFF', t)

def darken(c, t):
    return mix(c, '#000000', t)


def tones(hue):
    """All colours derived from one application hue."""
    return {
        'tile_a': lighten(hue, 0.84),      # pastel ground, top-left
        'tile_b': lighten(hue, 0.70),      # pastel ground, bottom-right
        'rim': lighten(hue, 0.6),
        'base_a': lighten(hue, 0.22),      # main object gradient
        'base_b': darken(hue, 0.08),
        'dark_a': darken(hue, 0.18),
        'dark_b': darken(hue, 0.42),
        'light_a': lighten(hue, 0.62),
        'light_b': lighten(hue, 0.40),
        'shadow': darken(hue, 0.55),
        'white': '#FFFFFF',
    }


DEFAULT_STYLE = 'symbol'

STYLES = {
    'soft':   'Soft (multi-tone, raised)',
    'mono':   'Option A · Mono Raised',
    'carved': 'Option B · Carved Grey',
    'pill':   'Option C · Pill',
    'symbol': 'Option E · Material Symbols on a clay tile',
}


def resolve(glyph, uid, style='soft', white='#FFFFFF'):
    """Turn tone tokens into gradient / colour references.

    ``soft``: base / dark / light gradients + accents.
    minimal styles: every tone and accent collapses to the base gradient,
    white stays as a cut-out colour."""
    def rep(m):
        tok = m.group(1)
        if tok == 'white':
            return f'"{white}"'
        if style != 'soft':
            return f'"url(#b-{uid})"'
        if tok.startswith('#'):
            return f'"{tok}"'
        return f'"url(#{tok[0]}-{uid})"'
    return re.sub(r'"T:([^"]+)"', rep, glyph)


def tile_svg(uid, glyph, hue, title='', style='soft'):
    """Compose one 512x512 neumorphic tile in the given style."""
    if style != 'soft':
        return tile_svg_minimal(uid, glyph, hue, title, style)
    t = tones(hue)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE} {TILE}" width="{TILE}" height="{TILE}" role="img" aria-label="{html.escape(title)}">'
        f'<defs>'
        f'<linearGradient id="t-{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["tile_a"]}"/><stop offset="1" stop-color="{t["tile_b"]}"/></linearGradient>'
        f'<linearGradient id="b-{uid}" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="{t["base_a"]}"/><stop offset="1" stop-color="{t["base_b"]}"/></linearGradient>'
        f'<linearGradient id="d-{uid}" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="{t["dark_a"]}"/><stop offset="1" stop-color="{t["dark_b"]}"/></linearGradient>'
        f'<linearGradient id="l-{uid}" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="{t["light_a"]}"/><stop offset="1" stop-color="{t["light_b"]}"/></linearGradient>'
        f'<filter id="e-{uid}" x="-35%" y="-35%" width="170%" height="170%" color-interpolation-filters="sRGB">'
        f'<feDropShadow dx="-6" dy="-6" stdDeviation="6" flood-color="#FFFFFF" flood-opacity="0.85"/>'
        f'<feDropShadow dx="8" dy="10" stdDeviation="8" flood-color="{t["shadow"]}" flood-opacity="0.30"/>'
        f'</filter>'
        f'<filter id="i-{uid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="10"/></filter>'
        f'</defs>'
        # pastel ground
        f'<rect width="{TILE}" height="{TILE}" rx="{RADIUS}" fill="url(#t-{uid})"/>'
        # soft inner shading: light top-left, darker bottom-right
        f'<rect x="12" y="12" width="{TILE - 24}" height="{TILE - 24}" rx="{RADIUS - 10}" fill="none" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="6" filter="url(#i-{uid})"/>'
        f'<rect x="10" y="10" width="{TILE - 20}" height="{TILE - 20}" rx="{RADIUS - 8}" fill="none" stroke="{t["shadow"]}" stroke-opacity="0.10" stroke-width="18" filter="url(#i-{uid})" transform="translate(14 16)"/>'
        f'<rect width="{TILE}" height="{TILE}" rx="{RADIUS}" fill="none" stroke="{t["rim"]}" stroke-opacity="0.9" stroke-width="3"/>'
        # the object
        f'<g transform="translate(61 61) scale({GLYPH_SCALE})" filter="url(#e-{uid})">{resolve(glyph, uid)}</g>'
        f'</svg>'
    )


def tile_svg_minimal(uid, glyph, hue, title, style):
    """Minimal neumorphic variants (see STYLES)."""
    t = tones(hue)
    neutral_a, neutral_b, neutral_rim = '#F1F3F8', '#DCE0E9', '#FFFFFF'
    if style == 'carved':
        tile_a, tile_b, rim = neutral_a, neutral_b, neutral_rim
        base_a, base_b = lighten(hue, 0.05), darken(hue, 0.12)
        white = '#EEF0F5'
    elif style == 'pill':
        tile_a, tile_b, rim = t['tile_a'], t['tile_b'], t['rim']
        base_a, base_b = lighten(hue, 0.05), darken(hue, 0.15)
        white = lighten(hue, 0.9)
    else:  # mono
        tile_a, tile_b, rim = t['tile_a'], t['tile_b'], t['rim']
        base_a, base_b = lighten(hue, 0.12), darken(hue, 0.14)
        white = '#FFFFFF'
    defs = (
        f'<linearGradient id="t-{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{tile_a}"/><stop offset="1" stop-color="{tile_b}"/></linearGradient>'
        f'<linearGradient id="b-{uid}" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="{base_a}"/><stop offset="1" stop-color="{base_b}"/></linearGradient>'
        f'<linearGradient id="p-{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{lighten(tile_a, 0.5)}"/><stop offset="1" stop-color="{tile_b}"/></linearGradient>'
        f'<filter id="e-{uid}" x="-35%" y="-35%" width="170%" height="170%" color-interpolation-filters="sRGB">'
        f'<feDropShadow dx="-7" dy="-7" stdDeviation="7" flood-color="#FFFFFF" flood-opacity="0.9"/>'
        f'<feDropShadow dx="9" dy="11" stdDeviation="9" flood-color="{t["shadow"]}" flood-opacity="0.28"/>'
        f'</filter>'
        # inner shadow (pressed into the surface)
        f'<filter id="n-{uid}" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
        f'<feComponentTransfer in="SourceAlpha" result="inv"><feFuncA type="table" tableValues="1 0"/></feComponentTransfer>'
        f'<feGaussianBlur in="inv" stdDeviation="6" result="blur"/>'
        f'<feOffset in="blur" dx="7" dy="8" result="off1"/>'
        f'<feFlood flood-color="{t["shadow"]}" flood-opacity="0.45" result="c1"/><feComposite in="c1" in2="off1" operator="in" result="s1"/>'
        f'<feOffset in="blur" dx="-6" dy="-6" result="off2"/>'
        f'<feFlood flood-color="#FFFFFF" flood-opacity="0.9" result="c2"/><feComposite in="c2" in2="off2" operator="in" result="s2"/>'
        f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="s1"/><feMergeNode in="s2"/></feMerge>'
        f'<feComposite in2="SourceAlpha" operator="in"/>'
        f'</filter>'
        f'<filter id="i-{uid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="10"/></filter>'
    )
    ground = (
        f'<rect width="{TILE}" height="{TILE}" rx="{RADIUS}" fill="url(#t-{uid})"/>'
        f'<rect x="12" y="12" width="{TILE - 24}" height="{TILE - 24}" rx="{RADIUS - 10}" fill="none" stroke="#FFFFFF" stroke-opacity="0.75" stroke-width="6" filter="url(#i-{uid})"/>'
        f'<rect x="10" y="10" width="{TILE - 20}" height="{TILE - 20}" rx="{RADIUS - 8}" fill="none" stroke="{t["shadow"]}" stroke-opacity="0.10" stroke-width="18" filter="url(#i-{uid})" transform="translate(14 16)"/>'
        f'<rect width="{TILE}" height="{TILE}" rx="{RADIUS}" fill="none" stroke="{rim}" stroke-opacity="0.9" stroke-width="3"/>'
    )
    body = resolve(glyph, uid, style, white)
    if style == 'carved':
        obj = f'<g transform="translate(76 76) scale(3.6)" filter="url(#n-{uid})">{body}</g>'
    elif style == 'pill':
        obj = (f'<circle cx="256" cy="256" r="176" fill="url(#p-{uid})" filter="url(#e-{uid})"/>'
               f'<circle cx="256" cy="256" r="176" fill="none" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="3"/>'
               f'<g transform="translate(131 131) scale(2.5)">{body}</g>')
    else:
        obj = f'<g transform="translate(71 71) scale(3.7)" filter="url(#e-{uid})">{body}</g>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE} {TILE}" width="{TILE}" height="{TILE}" role="img" aria-label="{html.escape(title)}">'
        f'<defs>{defs}</defs>{ground}{obj}</svg>'
    )


# ---------------------------------------------------------------------------
# 'symbol' style (2026-09-27, the shipped set): a Material Symbols Outlined
# glyph on a flat, lighter clay tile with a hairline.  One ink only.  The file
# is drawn in the theme's accent indigo; the Slate theme greys it out at rest
# with a CSS filter and lets the colour through on hover / for the active app
# (tokens --nm-icon-rest / --nm-icon-hover), so one file serves both states
# and both colour schemes.  Symbols: Apache-2.0, Google (tools/symbols/).
# ---------------------------------------------------------------------------
# Colours = the Slate theme's light tokens, so the file IS the design at rest (no filter in light
# mode): muted ink for the glyph, surface-high for the tile, the hairline ink at 32 %. Hover and
# dark mode are CSS filters solved by tools/solve_icon_filters.py against the mock-up's targets.
SYM_INK = '#4B5563'                       # web_theme_slate --nm-text-muted (light)
SYM_TILE = '#F4F6F9'                      # web_theme_slate --nm-surface-high (light)
SYM_HAIR = '#8B96A6'                      # web_theme_slate hairline ink, drawn at .32
SYM_HAIR_OPACITY = 0.32
SYM_TILE_SIZE = 400                       # of 512 → the theme's clay key shows as a 56 px margin all round
SYM_TILE_RX = 104                         # 26 % of the tile
SYM_HAIRLINE = 8                          # 1 px at the 64 px key
SYM_GLYPH = 224                           # 56 % of the tile (28 px of the mock-up's 50 px tile)


def symbol_path(name):
    with open(os.path.join(SYMBOLS_DIR, name + '.svg'), encoding='utf-8') as f:
        svg = f.read()
    return ''.join(re.findall(r'<path d="([^"]+)"', svg))


def tile_svg_symbol(uid, symbol, title=''):
    d = symbol_path(symbol)
    m = (TILE - SYM_TILE_SIZE) / 2
    h = SYM_HAIRLINE / 2
    sc = SYM_GLYPH / 960
    off = (TILE - SYM_GLYPH) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE} {TILE}" width="{TILE}" height="{TILE}" role="img" aria-label="{html.escape(title)}">'
        f'<rect x="{m:g}" y="{m:g}" width="{SYM_TILE_SIZE}" height="{SYM_TILE_SIZE}" rx="{SYM_TILE_RX}" fill="{SYM_TILE}"/>'
        f'<rect x="{m + h:g}" y="{m + h:g}" width="{SYM_TILE_SIZE - SYM_HAIRLINE}" height="{SYM_TILE_SIZE - SYM_HAIRLINE}" rx="{SYM_TILE_RX - h:g}" fill="none" stroke="{SYM_HAIR}" stroke-opacity="{SYM_HAIR_OPACITY}" stroke-width="{SYM_HAIRLINE}"/>'
        f'<path transform="translate({off:g} {off + SYM_GLYPH:g}) scale({sc:g})" d="{d}" fill="{SYM_INK}"/>'
        f'</svg>'
    )


def glyph_svg_symbol(symbol, title=''):
    """The glyph alone, black on transparent, in the tile file's coordinates: used as a CSS mask so
    the theme can paint it in any colour (rest / hover / active, light / dark) without filters."""
    d = symbol_path(symbol)
    sc = SYM_GLYPH / 960
    off = (TILE - SYM_GLYPH) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE} {TILE}" width="{TILE}" height="{TILE}" role="img" aria-label="{html.escape(title)}">'
            f'<path transform="translate({off:g} {off + SYM_GLYPH:g}) scale({sc:g})" d="{d}" fill="#000"/></svg>')


def render(key, uid=None, style=None):
    style = style or DEFAULT_STYLE
    entry = next(i for i in ICONS if i[0] == key)
    _, glyph_key, title, _cat, _ed, hue, _note = entry
    if style == 'symbol':
        return tile_svg_symbol(uid or key, SYMBOLS[key], title)
    return tile_svg(uid or key, GLYPHS[glyph_key], hue, title, style)


def build_app_icons(style=None):
    style = style or DEFAULT_STYLE
    os.makedirs(APPS_DIR, exist_ok=True)
    out = {}
    for key, glyph_key, title, cat, edition, hue, note in ICONS:
        svg = render(key, style=style)
        with open(os.path.join(APPS_DIR, key + '.svg'), 'w', encoding='utf-8') as f:
            f.write(svg)
        out[key] = svg
        if style == 'symbol':
            os.makedirs(GLYPH_DIR, exist_ok=True)
            with open(os.path.join(GLYPH_DIR, key + '.svg'), 'w', encoding='utf-8') as f:
                f.write(glyph_svg_symbol(SYMBOLS[key], title))
    return out


# ---------------------------------------------------------------------------
# Brand mark: a ring with a core — "one identity, many facets".
# ---------------------------------------------------------------------------
BRAND_HUE = '#3E4C7A'


def brand_mark_glyph():
    return ('<circle cx="50" cy="50" r="34" fill="T:base"/>'
            '<circle cx="50" cy="50" r="24" fill="T:white"/>'
            '<circle cx="50" cy="50" r="12" fill="T:dark"/>'
            '<circle cx="42" cy="42" r="4" fill="T:white" fill-opacity=".9"/>')


def brand_icon_svg(uid='brand'):
    if DEFAULT_STYLE == 'symbol':
        return tile_svg_symbol(uid, BRAND_SYMBOL, 'Identity')
    return tile_svg(uid, brand_mark_glyph(), BRAND_HUE, 'Identity', DEFAULT_STYLE)


def brand_logo_svg():
    """Horizontal wordmark: mark + 'Identity'."""
    if DEFAULT_STYLE == 'symbol':
        d = symbol_path(BRAND_SYMBOL)
        sc = 58 / 960
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 120" width="420" height="120" role="img" aria-label="Identity">'
            f'<rect x="10" y="10" width="100" height="100" rx="26" fill="{SYM_TILE}"/>'
            f'<rect x="10.75" y="10.75" width="98.5" height="98.5" rx="25.25" fill="none" stroke="{SYM_HAIR}" stroke-opacity="{SYM_HAIR_OPACITY}" stroke-width="1.5"/>'
            f'<path transform="translate(31 89) scale({sc:g})" d="{d}" fill="{SYM_INK}"/>'
            '<text x="134" y="78" font-family="Inter, Segoe UI, Helvetica Neue, Arial, sans-serif" font-size="56" font-weight="600" letter-spacing="-1.5" fill="#1F2937">Identity</text>'
            '</svg>'
        )
    t = tones(BRAND_HUE)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 120" width="420" height="120" role="img" aria-label="Identity">'
        '<defs>'
        f'<linearGradient id="lg-t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["tile_a"]}"/><stop offset="1" stop-color="{t["tile_b"]}"/></linearGradient>'
        f'<linearGradient id="lg-b" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="{t["base_a"]}"/><stop offset="1" stop-color="{t["base_b"]}"/></linearGradient>'
        f'<linearGradient id="lg-d" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="{t["dark_a"]}"/><stop offset="1" stop-color="{t["dark_b"]}"/></linearGradient>'
        f'<filter id="lg-e" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="-2" dy="-2" stdDeviation="2" flood-color="#fff" flood-opacity=".9"/>'
        f'<feDropShadow dx="3" dy="4" stdDeviation="3" flood-color="{t["shadow"]}" flood-opacity=".3"/></filter>'
        '</defs>'
        '<rect x="10" y="10" width="100" height="100" rx="23" fill="url(#lg-t)"/>'
        f'<rect x="10" y="10" width="100" height="100" rx="23" fill="none" stroke="{t["rim"]}" stroke-width="1.5"/>'
        '<g transform="translate(26 26) scale(0.68)" filter="url(#lg-e)">'
        '<circle cx="50" cy="50" r="34" fill="url(#lg-b)"/><circle cx="50" cy="50" r="24" fill="#fff"/>'
        '<circle cx="50" cy="50" r="12" fill="url(#lg-d)"/><circle cx="42" cy="42" r="4" fill="#fff" fill-opacity=".9"/>'
        '</g>'
        '<text x="134" y="78" font-family="Sora, Segoe UI, Helvetica Neue, Arial, sans-serif" font-size="56" font-weight="600" letter-spacing="-1.5" fill="#1B2030">Identity</text>'
        '</svg>'
    )


def ai_avatar_svg():
    """Agent avatar: the AI tile filling the box (no margin) so it reads at 16 px in a chat header."""
    d = symbol_path(SYMBOLS['ai'])
    g = int(TILE * 0.58)
    sc = g / 960
    off = (TILE - g) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TILE} {TILE}" width="{TILE}" height="{TILE}" role="img" aria-label="AI">'
            f'<rect width="{TILE}" height="{TILE}" rx="{RADIUS}" fill="{SYM_TILE}"/>'
            f'<rect x="4" y="4" width="{TILE - 8}" height="{TILE - 8}" rx="{RADIUS - 4}" fill="none" stroke="{SYM_HAIR}" stroke-opacity="{SYM_HAIR_OPACITY}" stroke-width="8"/>'
            f'<path transform="translate({off:g} {off + g:g}) scale({sc:g})" d="{d}" fill="{SYM_INK}"/></svg>')


def ai_glyph_svg():
    """The AI glyph alone in the muted ink: buttons and systray (16–22 px), where a tile is too small."""
    d = symbol_path(SYMBOLS['ai'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" width="24" height="24" role="img" aria-label="AI">'
            f'<path d="{d}" fill="{SYM_INK}"/></svg>')


def build_ai_assets():
    os.makedirs(BRAND_DIR, exist_ok=True)
    svg = os.path.join(BRAND_DIR, 'ai_avatar.svg')
    with open(svg, 'w', encoding='utf-8') as f:
        f.write(ai_avatar_svg())
    with open(os.path.join(BRAND_DIR, 'ai_glyph.svg'), 'w', encoding='utf-8') as f:
        f.write(ai_glyph_svg())
    ok = rasterize(svg, os.path.join(BRAND_DIR, 'ai_avatar.png'), 256)
    print(f'  {"ok" if ok else "skip"}  static/src/img/brand/ai_avatar.png (+ ai_avatar.svg, ai_glyph.svg)')


def build_brand():
    os.makedirs(BRAND_DIR, exist_ok=True)
    with open(os.path.join(BRAND_DIR, 'icon.svg'), 'w', encoding='utf-8') as f:
        f.write(brand_icon_svg())
    with open(os.path.join(BRAND_DIR, 'logo.svg'), 'w', encoding='utf-8') as f:
        f.write(brand_logo_svg())


# ---------------------------------------------------------------------------
# Rasters
# ---------------------------------------------------------------------------
def find_chrome():
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        p = shutil.which(name)
        if p:
            return p
    return None


def rasterize(svg_path, png_path, size):
    chrome = find_chrome()
    if not chrome:
        print('  ! no chrome/chromium on PATH, skipping', png_path)
        return False
    with open(svg_path, encoding='utf-8') as f:
        svg = f.read()
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, 'page.html')
        with open(page, 'w', encoding='utf-8') as f:
            f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;background:transparent}}'
                    f'svg{{display:block;width:{size}px;height:{size}px}}</style></head><body>{svg}</body></html>')
        cmd = [chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
               '--default-background-color=00000000',
               f'--window-size={size},{size}', f'--screenshot={png_path}', 'file://' + page]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and os.path.exists(png_path)


def build_app_rasters(svgs, size=192, cols=2):
    """All tiles on one page, one screenshot, then cropped with Pillow."""
    chrome = find_chrome()
    try:
        from PIL import Image
    except ImportError:
        Image = None
    if not chrome or Image is None:
        print('  ! chrome or Pillow missing, skipping app PNGs')
        return
    png_dir = os.path.join(APPS_DIR, 'png')
    os.makedirs(png_dir, exist_ok=True)
    keys = list(svgs)
    rows = (len(keys) + cols - 1) // cols
    cells = ''.join(f'<div>{svgs[k]}</div>' for k in keys)
    with tempfile.TemporaryDirectory() as tmp:
        page = os.path.join(tmp, 'grid.html')
        shot = os.path.join(tmp, 'grid.png')
        with open(page, 'w', encoding='utf-8') as f:
            f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;background:transparent}}'
                    f'body{{display:grid;grid-template-columns:repeat({cols},{size}px)}}div{{width:{size}px;height:{size}px}}'
                    f'svg{{display:block;width:{size}px;height:{size}px}}</style></head><body>{cells}</body></html>')
        cmd = [chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
               '--default-background-color=00000000', f'--window-size={cols * size},{rows * size}',
               f'--screenshot={shot}', 'file://' + page]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(shot):
            print('  ! chrome failed, skipping app PNGs')
            return
        sheet = Image.open(shot)
        for i, key in enumerate(keys):
            x, y = (i % cols) * size, (i // cols) * size
            sheet.crop((x, y, x + size, y + size)).save(os.path.join(png_dir, key + '.png'), optimize=True)
    print(f'  {len(keys)} PNGs -> {os.path.relpath(png_dir, MODULE)}')


def build_rasters():
    icon = os.path.join(BRAND_DIR, 'icon.svg')
    targets = [
        (os.path.join(BRAND_DIR, 'icon-512.png'), 512),
        (os.path.join(BRAND_DIR, 'icon-192.png'), 192),
        (os.path.join(BRAND_DIR, 'icon-180.png'), 180),   # apple-touch-icon
        (os.path.join(BRAND_DIR, 'favicon.png'), 64),
        (os.path.join(DESC_DIR, 'icon.png'), 140),        # module icon (Apps list)
    ]
    for png, size in targets:
        ok = rasterize(icon, png, size)
        print(f'  {"ok" if ok else "skip"}  {os.path.relpath(png, MODULE)}')


# ---------------------------------------------------------------------------
# Design sheet
# ---------------------------------------------------------------------------
SCREENS = [
    ('home_menu.png', 'Home menu (Enterprise)', 'Every app tile replaced; the tab title carries the brand.'),
    ('navbar_crm.png', 'Navbar', 'The current app icon at 24 px.'),
    ('apps_list.png', 'Apps', 'Module kanban icons, vendor "Learn More" links removed, summaries debranded.'),
    ('settings_identity.png', 'Settings → Identity', 'Brand, logo/icon, links and behaviour switches.'),
    ('settings_about.png', 'Settings → About + user menu', 'Edition block shows the brand and version; user menu without vendor entries.'),
    ('discuss_bot.png', 'Discuss', 'The bot renamed and re-avatared.'),
    ('login.png', 'Login (Community, no website)', 'Brand logo, favicon, "Powered by" line.'),
    ('database_manager.png', 'Database manager', 'Branded without any database (config-file / built-in defaults).'),
]


def build_design_page(svgs):
    by_cat = {}
    for key, glyph_key, title, cat, edition, hue, note in ICONS:
        by_cat.setdefault(cat, []).append((key, title, edition, hue, note))
    hues = {k: h for k, _, _, _, _, h, _ in ICONS}
    titles = {k: t for k, _, t, _, _, _, _ in ICONS}

    n_total = len(ICONS)
    n_ent = sum(1 for i in ICONS if i[4] == 'enterprise')
    n_both = n_total - n_ent

    def edition_pill(ed):
        return {'both': '<span class="pill pill-c">Community + Enterprise</span>',
                'enterprise': '<span class="pill pill-e">Enterprise</span>'}[ed]

    # --- tone strip for one hue (how the five tones are derived)
    t = tones(hues['crm'])
    tone_strip = ''.join(
        f'<div class="tone"><div class="tone-chip" style="background:{c}"></div><span>{label}</span></div>'
        for label, c in (('tile', t['tile_a']), ('light', t['light_a']), ('base', t['base_b']),
                         ('dark', t['dark_b']), ('shadow', t['shadow'])))

    # --- home menu mock (a representative set, at Odoo's real 70px tile size)
    mock_keys = ['mail', 'calendar', 'contacts', 'crm', 'sale_management', 'account', 'stock', 'purchase',
                 'mrp', 'project', 'hr', 'hr_holidays', 'website', 'point_of_sale', 'mass_mailing',
                 'helpdesk', 'documents', 'knowledge', 'base__settings', 'base__modules']
    mock = ''.join(
        f'<div class="mock-app"><div class="mock-tile">{render(k, "m-" + k)}</div>'
        f'<div class="mock-label">{html.escape(titles[k])}</div></div>'
        for k in mock_keys)

    navbar_svg = render('crm', 'nav-crm')
    sizes_svg = ''.join(
        f'<div class="size"><div style="width:{s}px;height:{s}px">{render("accountant", f"s{s}")}</div><code>{s} px</code></div>'
        for s in (140, 70, 40, 24, 16))

    # --- catalog
    catalog = ''
    for cat, label in CATEGORIES.items():
        items = by_cat.get(cat, [])
        if not items:
            continue
        cards = ''.join(
            f'<div class="card"><div class="tile">{svgs[k]}</div>'
            f'<div class="card-body"><div class="card-title">{html.escape(ttl)}</div>'
            f'<code class="key">{k}.svg · {hue}</code>{edition_pill(ed)}</div></div>'
            for k, ttl, ed, hue, note in items)
        catalog += (f'<section class="cat" id="cat-{cat}"><header class="cat-head">'
                    f'<span class="cat-dot" style="background:{items[0][3]}"></span>'
                    f'<h3>{label}</h3><span class="cat-count">{len(items)}</span></header>'
                    f'<div class="grid">{cards}</div></section>')

    # --- coverage table
    rows = ''.join(
        f'<tr><td>{html.escape(ttl)}</td><td><code>{html.escape(k.split("__")[0])}</code></td>'
        f'<td>{ {"both": "Community + Enterprise", "enterprise": "Enterprise"}[ed] }</td>'
        f'<td><code>{k}.svg</code></td><td class="muted">{html.escape(note or "static/description/icon.png")}</td></tr>'
        for k, _, ttl, cat, ed, hue, note in ICONS)

    # --- debranded views (real screenshots, embedded when present)
    screens_dir = os.path.join(DESC_DIR, 'screens')
    shots = ''
    for fname, title, caption in SCREENS:
        fpath = os.path.join(screens_dir, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, 'rb') as f:
            uri = 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
        shots += (f'<figure class="shot"><img src="{uri}" alt="{html.escape(title)}" loading="lazy">'
                  f'<figcaption><b>{html.escape(title)}</b> {html.escape(caption)}</figcaption></figure>')
    screens_section = f'''
<section class="block" id="views">
  <div class="eyebrow">Debranded views</div>
  <h2>What the module changes, as rendered by Odoo 20</h2>
  <p>Captured from a test database with the brand set to "Acme". Everything you see is produced by the <code>identity</code> module: no template was edited by hand.</p>
  <div class="shots">{shots}</div>
</section>''' if shots else ''

    page = f'''<title>Identity Pill Icons</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
:root {{
  --bg:#F3F4F9; --surface:#FFFFFF; --ink:#1B2030; --ink-2:#4A5268; --muted:#7A8297;
  --rule:#E0E4EE; --accent:#3A46C4; --accent-ink:#2B35A0; --mock:#F2F0F8; --mock-ink:#2B2340;
  --pill-c:#E4F5EC; --pill-c-ink:#166B45; --pill-e:#ECEAFE; --pill-e-ink:#4634B2;
  --display:'Sora', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  --body:'Source Sans 3', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  --mono:'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#12151E; --surface:#1A1E2A; --ink:#EAEDF4; --ink-2:#B6BCCB; --muted:#8B93A7;
  --rule:#2A3040; --accent:#8C96F0; --accent-ink:#B4BBF6; --mock:#20242F; --mock-ink:#EEF0F6;
  --pill-c:#173A2A; --pill-c-ink:#8FE0B4; --pill-e:#282555; --pill-e-ink:#C3BCFF;
}} }}
:root[data-theme="dark"] {{
  --bg:#12151E; --surface:#1A1E2A; --ink:#EAEDF4; --ink-2:#B6BCCB; --muted:#8B93A7;
  --rule:#2A3040; --accent:#8C96F0; --accent-ink:#B4BBF6; --mock:#20242F; --mock-ink:#EEF0F6;
  --pill-c:#173A2A; --pill-c-ink:#8FE0B4; --pill-e:#282555; --pill-e-ink:#C3BCFF;
}}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:var(--body); font-size:16px; line-height:1.5; }}
.wrap {{ max-width:1180px; margin:0 auto; padding-inline:24px; padding-block:0 64px; }}
h1,h2,h3 {{ font-family:var(--display); text-wrap:balance; margin:0; }}
h1 {{ font-size:clamp(28px,4vw,44px); font-weight:700; letter-spacing:-.02em; line-height:1.1; }}
h2 {{ font-size:22px; font-weight:600; letter-spacing:-.01em; }}
h3 {{ font-size:17px; font-weight:600; }}
p {{ max-width:64ch; color:var(--ink-2); margin:0; }}
code {{ font-family:var(--mono); font-size:.8em; }}
.eyebrow {{ font-family:var(--display); font-size:12px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; color:var(--accent); }}
.topbar {{ position:sticky; top:env(safe-area-inset-top,0px); z-index:5; background:color-mix(in srgb, var(--bg) 88%, transparent); backdrop-filter:blur(8px); border-bottom:1px solid var(--rule); }}
.topbar-in {{ max-width:1180px; margin:0 auto; padding:12px 24px; display:flex; align-items:center; gap:16px; flex-wrap:wrap; }}
.topbar-in .brand {{ display:flex; align-items:center; gap:10px; font-family:var(--display); font-weight:600; }}
.topbar-in .brand svg {{ width:28px; height:28px; }}
.topbar nav {{ display:flex; gap:4px 16px; flex-wrap:wrap; margin-left:auto; font-size:14px; }}
.topbar nav a {{ color:var(--ink-2); text-decoration:none; }}
.topbar nav a:hover, .topbar nav a:focus-visible {{ color:var(--accent-ink); outline:none; text-decoration:underline; }}
.hero {{ padding-block:48px 32px; display:grid; gap:20px; }}
.hero .stats {{ display:flex; gap:28px; flex-wrap:wrap; font-family:var(--display); }}
.stat b {{ display:block; font-size:28px; font-weight:700; font-variant-numeric:tabular-nums; }}
.stat span {{ font-size:13px; color:var(--muted); font-family:var(--body); }}
section.block {{ padding-block:36px; border-top:1px solid var(--rule); display:grid; gap:20px; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
@media (max-width:760px) {{ .two {{ grid-template-columns:1fr }} }}
.panel {{ background:var(--surface); border:1px solid var(--rule); border-radius:14px; padding:20px; }}
.anatomy {{ display:grid; grid-template-columns:auto 1fr; gap:20px; align-items:center; }}
.anatomy svg {{ width:180px; height:180px; }}
.anatomy ul {{ margin:0; padding-left:18px; color:var(--ink-2); font-size:15px; display:grid; gap:6px; }}
.tones {{ display:flex; gap:14px; flex-wrap:wrap; }}
.tone {{ display:flex; flex-direction:column; align-items:center; gap:6px; font-size:12px; color:var(--muted); }}
.tone-chip {{ width:52px; height:52px; border-radius:14px; border:1px solid var(--rule); }}
.mock {{ background:var(--mock); color:var(--mock-ink); border-radius:14px; padding:0 0 28px; overflow:hidden; border:1px solid var(--rule); }}
.mock-nav {{ display:flex; align-items:center; gap:12px; padding:10px 16px; background:rgba(0,0,0,.04); border-bottom:1px solid var(--rule); font-size:14px; }}
.mock-nav svg {{ width:22px; height:22px; }}
.mock-nav .crumb {{ font-weight:600; }}
.mock-nav .right {{ margin-left:auto; display:flex; gap:12px; opacity:.7; font-size:12px; }}
.mock-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(112px,1fr)); gap:22px 8px; padding:32px 24px 8px; max-width:760px; margin:0 auto; }}
.mock-app {{ display:flex; flex-direction:column; align-items:center; gap:8px; }}
.mock-tile {{ width:70px; height:70px; }}
.mock-tile svg {{ width:70px; height:70px; display:block; box-shadow:0 8px 18px rgba(30,20,60,.18); border-radius:16px; }}
.mock-label {{ font-size:13px; }}
.sizes {{ display:flex; gap:28px; align-items:flex-end; flex-wrap:wrap; }}
.size {{ display:flex; flex-direction:column; align-items:center; gap:8px; }}
.size svg {{ width:100%; height:100%; display:block; }}
.size code {{ color:var(--muted); }}
.cat {{ display:grid; gap:14px; padding-block:18px; }}
.cat-head {{ display:flex; align-items:center; gap:10px; }}
.cat-dot {{ width:14px; height:14px; border-radius:4px; }}
.cat-count {{ color:var(--muted); font-family:var(--mono); font-size:13px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(232px,1fr)); gap:12px; }}
.card {{ background:var(--surface); border:1px solid var(--rule); border-radius:12px; padding:14px; display:flex; gap:14px; align-items:center; }}
.tile {{ width:72px; height:72px; flex:none; }}
.tile svg {{ width:72px; height:72px; display:block; }}
.card-body {{ display:grid; gap:4px; min-width:0; }}
.card-title {{ font-weight:600; font-size:15px; }}
.key {{ color:var(--muted); font-size:11px; overflow-wrap:anywhere; }}
.pill {{ display:inline-block; font-size:11px; font-weight:600; padding:2px 8px; border-radius:999px; width:max-content; }}
.pill-c {{ background:var(--pill-c); color:var(--pill-c-ink); }}
.pill-e {{ background:var(--pill-e); color:var(--pill-e-ink); }}
.tablewrap {{ overflow-x:auto; border:1px solid var(--rule); border-radius:12px; background:var(--surface); }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
th,td {{ text-align:left; padding:8px 12px; border-bottom:1px solid var(--rule); vertical-align:top; white-space:nowrap; }}
th {{ font-family:var(--display); font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); font-weight:600; }}
tr:last-child td {{ border-bottom:none; }}
.muted {{ color:var(--muted); }}
.note {{ font-size:14px; color:var(--muted); }}
.shots {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr)); gap:20px; }}
.shot {{ margin:0; background:var(--surface); border:1px solid var(--rule); border-radius:12px; overflow:hidden; }}
.shot img {{ display:block; width:100%; height:auto; border-bottom:1px solid var(--rule); }}
.shot figcaption {{ padding:10px 14px; font-size:14px; color:var(--ink-2); }}
.shot figcaption b {{ color:var(--ink); margin-right:6px; }}
@media (prefers-reduced-motion: no-preference) {{ .card:hover .tile svg {{ transform:translateY(-2px); transition:transform .15s ease; }} }}
</style>

<div class="topbar"><div class="topbar-in">
  <div class="brand">{brand_icon_svg('top')} Identity</div>
  <nav><a href="#system">System</a><a href="#preview">In context</a>{'<a href="#views">Debranded views</a>' if shots else ''}<a href="#catalog">Catalog</a><a href="#coverage">Coverage</a></nav>
</div></div>

<div class="wrap">
<header class="hero">
  <div class="eyebrow">Odoo 20 · app icon redesign · minimal neumorphism · option C</div>
  <h1>Pill: a raised button, a quiet mark, one hue per app</h1>
  <p>Every application icon in Odoo 20 Community and Enterprise as a pastel tile of the app's own hue carrying a raised circular button; inside it a small one-colour glyph with a familiar, literal metaphor (calculator, factory, headset, ID badge, cart…). The set ships inside the <code>identity</code> debranding module, which swaps the icons in the home menu, the navbar, the Apps list, the Settings sidebar and the PWA shortcuts.</p>
  <div class="stats">
    <div class="stat"><b>{n_total}</b><span>icons</span></div>
    <div class="stat"><b>{n_both}</b><span>in Community &amp; Enterprise</span></div>
    <div class="stat"><b>{n_ent}</b><span>Enterprise only</span></div>
    <div class="stat"><b>{len({h for h in hues.values()})}</b><span>distinct hues</span></div>
  </div>
</header>

<section class="block" id="system">
  <div class="eyebrow">System</div>
  <h2>Tile anatomy</h2>
  <div class="two">
    <div class="panel anatomy">
      {render('accountant', 'anat')}
      <ul>
        <li><b>Ground</b> 512 × 512, radius 116 (22.6 %, Odoo's own tile ratio). A pastel gradient of the app hue with a blurred light rim top-left and a soft dark rim bottom-right.</li>
        <li><b>Pill</b> a 352 px circle raised from the ground by two soft shadows — white (−7, −7) and hue-dark (+9, +11, 28 %) — the one neumorphic element on the tile.</li>
        <li><b>Glyph</b> one colour (the app hue, light-to-dark gradient) with cut-outs in the pill tint; no accents, no second tone, so the mark stays quiet and reads at 24 px.</li>
        <li><b>Metaphors</b> literal and conventional: Accounting is a calculator, Manufacturing a factory, Helpdesk a headset, Employees an ID badge, eCommerce a cart, Inventory a box.</li>
        <li><b>Format</b> SVG (filters render natively in every browser); 192 px PNG rasters back Safari's home-screen icons.</li>
      </ul>
    </div>
    <div class="panel">
      <h3 style="margin-bottom:12px">Tones from one hue</h3>
      <div class="tones">{tone_strip}</div>
      <p class="note" style="margin-top:14px">Shown for CRM (<code>{hues['crm']}</code>). Hues stay in the family of the Odoo category (Sales warm, Finance green, Supply Chain indigo, HR amber, Services teal, Productivity violet, Marketing pink, Website blue, Administration slate) but every app gets its own, so neighbours never look alike.</p>
    </div>
  </div>
</section>

<section class="block" id="preview">
  <div class="eyebrow">In context</div>
  <h2>Home menu and navbar, at Odoo's real sizes</h2>
  <div class="mock">
    <div class="mock-nav">{navbar_svg}<span class="crumb">CRM</span><span>Sales</span><span>Reporting</span><span>Configuration</span><span class="right"><span>Discuss</span><span>Activities</span><span>Mitchell Admin</span></span></div>
    <div class="mock-grid">{mock}</div>
  </div>
  <div class="panel">
    <h3 style="margin-bottom:12px">Scale check</h3>
    <div class="sizes">{sizes_svg}</div>
    <p class="note" style="margin-top:12px">140 px Apps kanban · 70 px home menu · 40 px settings sidebar · 24 px navbar · 16 px favicon-class contexts.</p>
  </div>
</section>
{screens_section}

<section class="block" id="catalog">
  <div class="eyebrow">Catalog</div>
  <h2>All {n_total} icons by category</h2>
  {catalog}
</section>

<section class="block" id="coverage">
  <div class="eyebrow">Coverage</div>
  <h2>What each file replaces</h2>
  <p>Keys map to Odoo's <code>web_icon</code> value: <code>&lt;module&gt;.svg</code> replaces whichever icon file the module uses; the double-underscore form is for modules shipping several icons (base: Settings, Apps, Tests).</p>
  <div class="tablewrap"><table>
    <thead><tr><th>Application</th><th>Module</th><th>Edition</th><th>File</th><th>Replaces</th></tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</section>
</div>
'''
    os.makedirs(DESC_DIR, exist_ok=True)
    with open(os.path.join(DESC_DIR, 'icons.html'), 'w', encoding='utf-8') as f:
        f.write(page)


PREVIEW_CSS = """
:root { --bg:#F3F4F9; --surface:#FFFFFF; --ink:#1B2030; --ink-2:#4A5268; --muted:#7A8297; --rule:#E0E4EE; --accent:#3A46C4;
  --mock:#F2F0F8; --mock-ink:#2B2340; --display:'Sora','Segoe UI','Helvetica Neue',Arial,sans-serif; --body:'Source Sans 3','Segoe UI',Arial,sans-serif; --mono:'JetBrains Mono',ui-monospace,Menlo,monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#12151E; --surface:#1A1E2A; --ink:#EAEDF4; --ink-2:#B6BCCB; --muted:#8B93A7; --rule:#2A3040; --accent:#8C96F0; --mock:#20242F; --mock-ink:#EEF0F6; } }
:root[data-theme="dark"] { --bg:#12151E; --surface:#1A1E2A; --ink:#EAEDF4; --ink-2:#B6BCCB; --muted:#8B93A7; --rule:#2A3040; --accent:#8C96F0; --mock:#20242F; --mock-ink:#EEF0F6; }
* { box-sizing:border-box } body { margin:0; background:var(--bg); color:var(--ink); font-family:var(--body); font-size:16px; line-height:1.5; }
.wrap { max-width:1180px; margin:0 auto; padding-inline:24px; padding-block:40px 64px; display:grid; gap:36px; }
h1,h2,h3 { font-family:var(--display); text-wrap:balance; margin:0; } h1 { font-size:clamp(28px,4vw,42px); letter-spacing:-.02em; line-height:1.1; } h2 { font-size:22px; } h3 { font-size:16px; }
p { max-width:64ch; color:var(--ink-2); margin:0; } code { font-family:var(--mono); font-size:.8em; }
.eyebrow { font-family:var(--display); font-size:12px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; color:var(--accent); }
.hero { display:grid; gap:14px; } .options { display:flex; gap:10px; flex-wrap:wrap; font-size:14px; }
.options a { padding:6px 12px; border:1px solid var(--rule); border-radius:999px; color:var(--ink-2); text-decoration:none; background:var(--surface); }
.options a.cur { border-color:var(--accent); color:var(--accent); font-weight:600; }
.mock { background:var(--mock); color:var(--mock-ink); border-radius:14px; padding:0 0 28px; overflow:hidden; border:1px solid var(--rule); }
.mock-nav { display:flex; align-items:center; gap:12px; padding:10px 16px; background:rgba(0,0,0,.04); border-bottom:1px solid var(--rule); font-size:14px; }
.mock-nav svg { width:22px; height:22px; } .mock-nav .crumb { font-weight:600; } .mock-nav .right { margin-left:auto; display:flex; gap:12px; opacity:.7; font-size:12px; }
.mock-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(112px,1fr)); gap:22px 8px; padding:32px 24px 8px; max-width:760px; margin:0 auto; }
.mock-app { display:flex; flex-direction:column; align-items:center; gap:8px; } .mock-tile svg { width:70px; height:70px; display:block; box-shadow:0 8px 18px rgba(30,20,60,.18); border-radius:16px; } .mock-label { font-size:13px; }
.panel { background:var(--surface); border:1px solid var(--rule); border-radius:14px; padding:20px; display:grid; gap:12px; }
.sizes { display:flex; gap:28px; align-items:flex-end; flex-wrap:wrap; } .size { display:flex; flex-direction:column; align-items:center; gap:8px; } .size svg { width:100%; height:100%; display:block; } .size code { color:var(--muted); }
.cat { display:grid; gap:12px; } .cat-head { display:flex; align-items:center; gap:10px; } .cat-dot { width:14px; height:14px; border-radius:4px; } .cat-count { color:var(--muted); font-family:var(--mono); font-size:13px; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; }
.card { background:var(--surface); border:1px solid var(--rule); border-radius:12px; padding:14px 10px; display:flex; flex-direction:column; align-items:center; gap:8px; text-align:center; }
.card svg { width:72px; height:72px; display:block; } .card-title { font-weight:600; font-size:13px; } .key { color:var(--muted); font-size:10px; overflow-wrap:anywhere; }
.note { font-size:14px; color:var(--muted); }
"""

PREVIEW_COPY = {
    'symbol': ('Material Symbols on a clay tile',
               'One ink. A Material Symbols Outlined glyph on a flat, lighter clay tile with a hairline; the theme greys the file at rest and lets the accent through on hover and for the active app.'),
    'mono': ('Mono Raised',
             'The quietest raised tile: one silhouette in the app hue, white cut-outs for the details, the same pastel ground and dual soft shadow as the full set. No accents, no second tone.'),
    'carved': ('Carved Grey',
               'Classic neumorphism: every app sits on the same neutral soft-grey surface and the glyph is pressed into it. Colour lives only in the glyph, so the home screen reads as one calm surface with coloured marks.'),
    'pill': ('Pill',
             'A raised circular button on a pastel tile, holding a small mono glyph. The most minimal of the three: the pill carries the neumorphic depth, the glyph stays flat and small.'),
    'soft': ('Soft', 'Full multi-tone set with accents (the current module default).'),
}


def build_preview_page(style):
    """Stand-alone preview of one style: hero, home-menu mock, scale check, catalog."""
    name, blurb = PREVIEW_COPY[style]
    titles = {k: t for k, _, t, _, _, _, _ in ICONS}
    by_cat = {}
    for key, glyph_key, title, cat, edition, hue, note in ICONS:
        by_cat.setdefault(cat, []).append((key, title, hue))
    mock_keys = ['mail', 'calendar', 'contacts', 'crm', 'sale_management', 'account', 'stock', 'purchase',
                 'mrp', 'project', 'hr', 'hr_holidays', 'website', 'point_of_sale', 'mass_mailing',
                 'helpdesk', 'documents', 'knowledge', 'base__settings', 'base__modules']
    mock = ''.join(f'<div class="mock-app"><div class="mock-tile">{render(k, "m-" + k, style)}</div><div class="mock-label">{html.escape(titles[k])}</div></div>' for k in mock_keys)
    sizes = ''.join(f'<div class="size"><div style="width:{sz}px;height:{sz}px">{render("accountant", f"s{sz}", style)}</div><code>{sz} px</code></div>' for sz in (140, 70, 40, 24, 16))
    catalog = ''
    for cat, label in CATEGORIES.items():
        items = by_cat.get(cat, [])
        cards = ''.join(f'<div class="card">{render(k, k, style)}<div class="card-title">{html.escape(t)}</div><code class="key">{k}.svg</code></div>' for k, t, hue in items)
        catalog += (f'<section class="cat"><header class="cat-head"><span class="cat-dot" style="background:{items[0][2]}"></span>'
                    f'<h3>{label}</h3><span class="cat-count">{len(items)}</span></header><div class="grid">{cards}</div></section>')
    options = ''.join(f'<a href="preview_{k}.html" class="{"cur" if k == style else ""}">{html.escape(v)}</a>' for k, v in STYLES.items() if k != 'soft')
    page = f'''<title>Identity Icons · {html.escape(name)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400&display=swap">
<style>{PREVIEW_CSS}</style>
<div class="wrap">
<header class="hero">
  <div class="eyebrow">Odoo 20 · minimal neumorphic icons · {html.escape(STYLES[style])}</div>
  <h1>{html.escape(name)}</h1>
  <p>{html.escape(blurb)} All {len(ICONS)} icons (Community + Enterprise) use the same glyph set, so any option can be switched on in the module without redrawing.</p>
  <div class="options">{options}</div>
</header>
<section class="mock">
  <div class="mock-nav">{render("crm", "nav", style)}<span class="crumb">CRM</span><span>Sales</span><span>Reporting</span><span>Configuration</span><span class="right"><span>Discuss</span><span>Activities</span><span>Mitchell Admin</span></span></div>
  <div class="mock-grid">{mock}</div>
</section>
<section class="panel"><h3>Scale check</h3><div class="sizes">{sizes}</div><p class="note">140 px Apps kanban · 70 px home menu · 40 px settings sidebar · 24 px navbar · 16 px.</p></section>
<section style="display:grid;gap:28px"><h2>All {len(ICONS)} icons</h2>{catalog}</section>
</div>
'''
    out = os.path.join(DESC_DIR, f'preview_{style}.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(page)
    return out


if __name__ == '__main__':
    if '--previews' in sys.argv:
        for st in ('mono', 'carved', 'pill', 'symbol'):
            print('  ->', os.path.relpath(build_preview_page(st), MODULE))
        sys.exit(0)
    style = DEFAULT_STYLE
    for arg in sys.argv[1:]:
        if arg.startswith('--style='):
            style = arg.split('=', 1)[1]
            assert style in STYLES, f'unknown style {style}, choose from {list(STYLES)}'
    print('app icons', f'({style})')
    svgs = build_app_icons(style)
    print(f'  {len(svgs)} files -> {os.path.relpath(APPS_DIR, MODULE)}')
    print('brand')
    build_brand()
    if style == 'symbol':
        build_ai_assets()
    if '--no-png' not in sys.argv:
        build_rasters()
        build_app_rasters(svgs)
    print('design sheet')
    build_design_page(svgs)
    print('  ->', os.path.relpath(os.path.join(DESC_DIR, 'icons.html'), MODULE))
