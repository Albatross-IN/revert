# -*- coding: utf-8 -*-
"""
Identity icon catalog — "Soft" (neumorphic) edition.

Every Odoo 20 application icon (Community + Enterprise) redrawn as a filled,
multi-tone object extruded from a pastel tile: soft light shadow top-left,
soft dark shadow bottom-right, one hue per application.

Glyphs are authored in a 100x100 box.  Fills and strokes use tone tokens that
the builder resolves per icon:

    T:base   main gradient of the app hue      T:dark   darker shade
    T:light  lighter tint                       T:white  near-white
    T:#RRGGBB literal accent colour

Run ``python3 tools/build_icons.py`` from the module root to regenerate the
SVG files, the brand mark and the design page.
"""
import math

# ---------------------------------------------------------------------------
# Category → label (used for grouping on the design sheet)
# ---------------------------------------------------------------------------
CATEGORIES = {
    'sales':        'Sales',
    'finance':      'Finance',
    'supply':       'Supply Chain',
    'hr':           'Human Resources',
    'services':     'Services',
    'productivity': 'Productivity',
    'marketing':    'Marketing',
    'website':      'Website',
    'admin':        'Administration',
    'connectors':   'Connectors',
}

# Fixed accents shared across the set
GOLD = 'T:#FFC857'
GOLD_L = 'T:#FFE39A'
GREEN = 'T:#3ECF8E'
RED = 'T:#FF5A6E'


# ---------------------------------------------------------------------------
# Shape helpers
# ---------------------------------------------------------------------------
def _a(attrs):
    out = ''
    for k, v in attrs.items():
        if v is None:
            continue
        out += f' {k.replace("_", "-")}="{v}"'
    return out

def R(x, y, w, h, rx=0, fill='T:base', **kw):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{_a(kw)}/>'

def C(cx, cy, r, fill='T:base', **kw):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{_a(kw)}/>'

def E(cx, cy, rx, ry, fill='T:base', **kw):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"{_a(kw)}/>'

def P(d, fill='T:base', **kw):
    return f'<path d="{d}" fill="{fill}"{_a(kw)}/>'

def S(d, stroke='T:white', w=5, **kw):
    """stroked open path (round caps)"""
    kw.setdefault('stroke_linecap', 'round')
    kw.setdefault('stroke_linejoin', 'round')
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}"{_a(kw)}/>'

def Poly(points, fill='T:base', **kw):
    pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}"{_a(kw)}/>'

def star(cx, cy, r_out, r_in, points=5, rotate=-90, fill='T:white', **kw):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rotate + i * 180 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return Poly(pts, fill=fill, **kw)

def sparkle(cx, cy, r_out, r_in, fill='T:white', **kw):
    return star(cx, cy, r_out, r_in, points=4, fill=fill, **kw)

def gear(cx, cy, r_out, r_in, teeth=8, fill='T:base', **kw):
    pts = []
    step = math.pi / teeth
    for i in range(teeth * 2):
        a0 = i * step
        a1 = a0 + step * 0.55
        r = r_out if i % 2 == 0 else r_in
        for a in (a0, a1):
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return Poly(pts, fill=fill, **kw)

def check(x, y, s=1.0, stroke='T:white', w=7):
    return S(f'M{x} {y} l{9*s} {9*s} l{18*s} -{18*s}', stroke=stroke, w=w)

def dots(coords, r=4, fill='T:white'):
    return ''.join(C(x, y, r, fill=fill) for x, y in coords)

def person(cx, cy, r=12, w=44, fill='T:base'):
    return (C(cx, cy, r, fill=fill) +
            P(f'M{cx - w/2} {cy + r + 30} C{cx - w/2} {cy + r + 4} {cx + w/2} {cy + r + 4} {cx + w/2} {cy + r + 30} Z', fill=fill))

def calendar_frame(header='T:base', body='T:white'):
    return (R(16, 22, 68, 64, 9, fill=body) +
            P('M16 31 Q16 22 25 22 H75 Q84 22 84 31 V40 H16 Z', fill=header) +
            R(29, 13, 7, 16, 3.5, fill='T:dark') + R(64, 13, 7, 16, 3.5, fill='T:dark'))

def bubble(x, y, w, h, tail='left', fill='T:base', r=9):
    if tail == 'left':
        return P(f'M{x} {y+r} Q{x} {y} {x+r} {y} H{x+w-r} Q{x+w} {y} {x+w} {y+r} V{y+h-r} Q{x+w} {y+h} {x+w-r} {y+h} '
                 f'H{x+20} L{x+9} {y+h+11} V{y+h} H{x+r} Q{x} {y+h} {x} {y+h-r} Z', fill=fill)
    return P(f'M{x} {y+r} Q{x} {y} {x+r} {y} H{x+w-r} Q{x+w} {y} {x+w} {y+r} V{y+h-r} Q{x+w} {y+h} {x+w-r} {y+h} '
             f'V{y+h+11} L{x+w-20} {y+h} H{x+r} Q{x} {y+h} {x} {y+h-r} Z', fill=fill)

def ticket(fill='T:base'):
    return P('M12 30 Q12 24 18 24 H82 Q88 24 88 30 V40 A10 10 0 0 0 88 60 V70 Q88 76 82 76 H18 Q12 76 12 70 '
             'V60 A10 10 0 0 0 12 40 Z', fill=fill)


# ---------------------------------------------------------------------------
# Glyphs (filled, layered back → front)
# ---------------------------------------------------------------------------
GLYPHS = {
    # --- Administration ----------------------------------------------------
    'base__settings': gear(50, 50, 36, 27, 8) + C(50, 50, 14, 'T:white') + C(50, 50, 7, 'T:light'),
    'base__modules': (R(14, 14, 32, 32, 9) + R(54, 14, 32, 32, 9, 'T:light') +
                      R(14, 54, 32, 32, 9, 'T:light') + R(54, 54, 32, 32, 9)),
    'base__exception': (P('M40 12 H60 V38 L82 74 Q86 86 74 86 H26 Q14 86 18 74 L40 38 Z', 'T:white') +
                        P('M30 66 L40 50 H60 L70 66 Q76 76 68 80 H32 Q24 76 30 66 Z') +
                        R(36, 8, 28, 8, 4, 'T:dark') + dots([(46, 66), (58, 72)], 3, 'T:light')),
    'databases': (R(16, 12, 68, 21, 7) + R(16, 39, 68, 21, 7, 'T:light') + R(16, 66, 68, 21, 7) +
                  dots([(27, 22.5), (27, 76.5)], 3.5) + dots([(27, 49.5)], 3.5, 'T:dark') +
                  R(40, 20, 34, 5, 2.5, 'T:light') + R(40, 47, 34, 5, 2.5, 'T:white') + R(40, 74, 34, 5, 2.5, 'T:light')),
    'iot': (''.join(R(x, 14, 6, 12, 2, 'T:dark') for x in (32, 47, 62)) +
            ''.join(R(x, 74, 6, 12, 2, 'T:dark') for x in (32, 47, 62)) +
            ''.join(R(14, y, 12, 6, 2, 'T:dark') for y in (32, 47, 62)) +
            ''.join(R(74, y, 12, 6, 2, 'T:dark') for y in (32, 47, 62)) +
            R(24, 24, 52, 52, 10) + R(34, 34, 32, 32, 6, 'T:white') +
            S('M40 40 A14 14 0 0 1 60 40', 'T:light', 4) + S('M45 47 A7 7 0 0 1 55 47', 'T:base', 4) + C(50, 54, 3, 'T:base')),
    'obox': (R(66, 12, 8, 26, 4, 'T:dark') + C(70, 13, 7, 'T:dark') +
             R(10, 34, 80, 46, 11) +
             C(27, 57, 7, 'T:white') + R(42, 51, 15, 12, 3, 'T:white') + R(63, 51, 15, 12, 3, 'T:white')),
    'web_studio': (Poly([(20, 80), (28, 88), (66, 50), (58, 42)], 'T:dark') +
                   Poly([(58, 42), (66, 50), (72, 44), (64, 36)], 'T:light') +
                   star(74, 26, 15, 6, 4, fill=GOLD) + sparkle(84, 50, 7, 2.5) + sparkle(52, 16, 7, 2.5)),
    'esg': (C(50, 50, 36, 'T:light') +
            P('M28 74 C28 44 50 26 80 24 C82 54 62 76 28 74 Z') +
            S('M30 72 C42 60 54 50 68 34', 'T:white', 3.5)),
    'ai_app': (sparkle(46, 52, 34, 11, 'T:base') + sparkle(78, 24, 13, 4.5, 'T:light') +
               sparkle(78, 78, 9, 3, 'T:dark') + C(46, 52, 6, 'T:white')),
    # --- Finance -----------------------------------------------------------
    'account': (P('M26 12 H62 L76 26 V88 H26 Z', 'T:white') + P('M62 12 V26 H76 Z', 'T:light') +
                R(34, 36, 30, 5, 2.5, 'T:light') + R(34, 46, 30, 5, 2.5, 'T:light') + R(34, 56, 18, 5, 2.5, 'T:light') +
                R(34, 70, 22, 6, 3) + C(70, 72, 14, GOLD) + C(70, 72, 9, GOLD_L) + R(68, 66, 4, 12, 2, GOLD)),
    'accountant': (R(24, 10, 52, 80, 9) + R(31, 17, 38, 17, 4, 'T:white') + R(36, 24, 28, 4, 2, 'T:light') +
                   ''.join(R(x, y, 9, 9, 2.5, 'T:white') for y in (41, 54, 67) for x in (32, 45.5)) +
                   ''.join(R(59, y, 9, 9, 2.5, GOLD) for y in (41, 54)) + R(59, 67, 9, 9, 2.5, 'T:light')),
    'equity': (C(50, 50, 34, 'T:light') +
               P('M50 50 L50 16 A34 34 0 0 1 79.4 67 Z') +
               P('M50 50 L79.4 67 A34 34 0 0 1 20.6 67 Z', 'T:dark') +
               C(50, 50, 11, 'T:white')),
    'hr_payroll': (R(22, 26, 64, 36, 6, 'T:dark') + R(14, 36, 64, 36, 6) + C(46, 54, 11, 'T:white') +
                   dots([(22, 54), (70, 54)], 3, 'T:light') + C(78, 74, 12, GOLD) + C(78, 74, 7, GOLD_L)),
    'hr_expense': (P('M26 10 H74 V84 L66 78 L58 84 L50 78 L42 84 L34 78 L26 84 Z', 'T:white') +
                   R(34, 20, 32, 6, 3) + R(34, 32, 32, 4, 2, 'T:light') + R(34, 40, 24, 4, 2, 'T:light') +
                   R(34, 48, 32, 4, 2, 'T:light') + R(34, 60, 32, 5, 2.5, 'T:dark') +
                   C(70, 72, 12, GOLD) + C(70, 72, 7, GOLD_L)),
    # --- Sales -------------------------------------------------------------
    'sale_management': (P('M14 46 V19 Q14 14 19 14 H46 L86 54 L54 86 Z') + C(30, 30, 7, 'T:white') +
                        S('M44 44 L66 66', 'T:white', 6, stroke_opacity='.55') + S('M40 56 L52 68', 'T:white', 6, stroke_opacity='.55')),
    'crm': (P('M10 14 H90 L74 36 H26 Z') + P('M28 40 H72 L62 60 H38 Z', 'T:light') + R(40, 64, 20, 24, 5, 'T:dark') +
            C(72, 22, 9, GOLD) + C(72, 22, 5, GOLD_L)),
    'contacts': (R(24, 10, 56, 80, 9) + R(32, 18, 40, 64, 5, 'T:white') +
                 ''.join(R(17, y, 10, 10, 3, 'T:dark') for y in (22, 45, 68)) +
                 C(52, 40, 10) + P('M36 70 C36 54 68 54 68 70 Z')),
    'point_of_sale': (R(18, 10, 64, 46, 9) + R(25, 17, 50, 30, 4, 'T:white') + R(31, 23, 24, 5, 2.5, 'T:light') +
                      R(31, 32, 34, 5, 2.5, 'T:light') + R(12, 62, 76, 26, 8, 'T:dark') +
                      ''.join(R(x, 69, 10, 10, 3, 'T:light') for x in (20, 34, 48)) + C(74, 74, 6, GREEN)),
    'pos_restaurant': (C(50, 50, 26, 'T:white') + C(50, 50, 18, 'T:light') + C(50, 50, 10) +
                       R(11, 14, 6, 72, 3, 'T:dark') + R(7, 14, 4, 16, 2, 'T:dark') + R(17, 14, 4, 16, 2, 'T:dark') +
                       P('M82 14 C76 26 76 44 84 52 V86 H90 V14 Z', 'T:dark')),
    'pos_enterprise': (P('M18 66 A32 32 0 0 1 82 66 Z') + R(10, 66, 80, 9, 4.5, 'T:dark') +
                       C(50, 30, 7, 'T:light') + R(46, 34, 8, 6, 2, 'T:light') + S('M34 50 A18 18 0 0 1 50 40', 'T:white', 4, stroke_opacity='.7')),
    'sale_subscription': (calendar_frame() +
                          S('M62 62 A13 13 0 1 0 60 72', 'T:base', 6) + Poly([(66, 56), (68, 70), (56, 66)], 'T:base')),
    'sale_renting': (C(34, 38, 20) + C(34, 38, 8, 'T:white') +
                     Poly([(46, 46), (54, 38), (90, 74), (86, 84), (78, 84), (74, 78), (68, 82), (62, 76)], 'T:dark')),
    'sign': (R(18, 10, 64, 80, 7, 'T:white') + R(26, 20, 40, 5, 2.5, 'T:light') + R(26, 30, 48, 4, 2, 'T:light') +
             S('M28 68 C34 58 38 76 44 66 C48 58 54 74 60 64 C64 58 68 66 72 64', 'T:base', 4) +
             Poly([(52, 44), (72, 24), (82, 34), (62, 54), (48, 58)], 'T:dark') +
             Poly([(72, 24), (82, 34), (86, 30), (76, 20)], GOLD)),
    'marketplace': (R(18, 40, 64, 46, 4, 'T:white') + P('M12 40 L22 16 H78 L88 40 Z') +
                    P('M28 16 H46 L44 40 H24 Z', 'T:light') + P('M60 16 H78 L82 40 H62 Z', 'T:light') +
                    R(42, 58, 16, 28, 3, 'T:dark') + R(24, 50, 12, 12, 2, 'T:light') + R(64, 50, 12, 12, 2, 'T:light')),
    # --- Supply chain ------------------------------------------------------
    'stock': (P('M50 12 L86 30 L50 48 L14 30 Z', 'T:light') + P('M14 30 L50 48 V88 L14 70 Z') +
              P('M86 30 L50 48 V88 L86 70 Z', 'T:dark') + P('M40 17 L76 35 V45 L40 27 Z', 'T:white', fill_opacity='.85')),
    'purchase': (P('M22 36 H78 L74 88 H26 Z') + S('M36 36 V30 A14 14 0 0 1 64 30 V36', 'T:dark', 6) +
                 R(22, 36, 56, 10, 0, 'T:dark') + check(38, 62, 0.9)),
    'mrp': (P('M12 88 V50 L34 40 V50 L56 40 V50 L78 40 V88 Z') + R(18, 22, 12, 30, 2, 'T:dark') +
            R(16, 18, 16, 6, 2, 'T:dark') + ''.join(R(x, 60, 9, 9, 2, 'T:white') for x in (22, 37, 52, 67)) +
            R(43, 74, 14, 14, 2, 'T:dark') + S('M28 32 A4 4 0 0 1 36 28', 'T:light', 3, stroke_opacity='.8')),
    'mrp_plm': (S('M74 30 A32 32 0 0 0 20 42', 'T:base', 7) + Poly([(14, 30), (30, 34), (18, 48)], 'T:base') +
                S('M26 70 A32 32 0 0 0 80 58', 'T:dark', 7) + Poly([(86, 70), (70, 66), (82, 52)], 'T:dark') +
                P('M50 34 L64 41 L50 48 L36 41 Z', 'T:light') + P('M36 41 L50 48 V64 L36 57 Z') + P('M64 41 L50 48 V64 L64 57 Z', 'T:dark')),
    'mrp_workorder': (R(12, 14, 76, 52, 8) + R(18, 20, 64, 40, 4, 'T:white') +
                      R(24, 28, 52, 7, 3.5, 'T:light') + R(24, 28, 36, 7, 3.5, GREEN) +
                      R(24, 41, 52, 7, 3.5, 'T:light') + R(24, 41, 18, 7, 3.5) +
                      R(46, 66, 8, 10, 0, 'T:dark') + R(32, 76, 36, 7, 3.5, 'T:dark')),
    'quality_control': (Poly([(36, 60), (30, 92), (44, 84), (50, 94), (56, 84), (70, 92), (64, 60)], 'T:dark') +
                        C(50, 42, 28) + C(50, 42, 20, 'T:light') + check(39, 42, 0.75)),
    'maintenance': (gear(28, 30, 18, 13, 8, 'T:light') + C(28, 30, 6, 'T:white') +
                    Poly([(52, 42), (60, 50), (24, 90), (12, 78)], 'T:dark') +
                    P('M81.7 32.9 A18 18 0 1 1 67.1 18.3 L65.4 28.1 A8 8 0 1 0 71.9 34.6 Z')),
    'repair': (Poly([(18, 22), (30, 12), (44, 26), (34, 36)], GOLD) + Poly([(38, 32), (44, 26), (84, 66), (78, 72)], 'T:light') +
               Poly([(50, 18), (70, 18), (80, 28), (80, 42), (60, 42), (50, 32)], 'T:dark') +
               Poly([(58, 42), (66, 46), (30, 88), (22, 80)])),
    'stock_barcode': (R(14, 24, 72, 52, 8, 'T:white') +
                      ''.join(R(x, 32, w, 36, 1, 'T:dark') for x, w in ((22, 4), (30, 2), (36, 5), (45, 2), (51, 4), (59, 2), (65, 5), (74, 3))) +
                      R(10, 48, 80, 4, 2, RED)),
    'fleet': (P('M18 60 L26 40 Q28 34 34 34 H66 Q72 34 74 40 L82 60 V78 Q82 82 78 82 H22 Q18 82 18 78 Z') +
              P('M30 56 L34 42 H66 L70 56 Z', 'T:white') + C(28, 66, 5, GOLD) + C(72, 66, 5, GOLD) +
              R(40, 66, 20, 6, 3, 'T:dark') + R(22, 80, 14, 8, 3, 'T:dark') + R(64, 80, 14, 8, 3, 'T:dark')),
    # --- Human resources ---------------------------------------------------
    'hr': (R(22, 20, 56, 68, 8, 'T:white') + R(42, 10, 16, 16, 4, 'T:dark') + R(46, 14, 8, 4, 2, 'T:light') +
           C(50, 46, 11) + P('M32 72 C32 58 68 58 68 72 Z') + R(30, 76, 40, 5, 2.5, 'T:light')),
    'hr_attendance': (C(50, 50, 34) + C(50, 50, 27, 'T:white') + R(48, 30, 4, 22, 2, 'T:dark') +
                      S('M50 50 L62 58', 'T:dark', 4) + C(50, 50, 3.5, 'T:dark') +
                      C(78, 78, 13, GREEN) + check(70, 78, 0.55)),
    'hr_holidays': (C(28, 30, 14, GOLD) + P('M40 60 A24 24 0 0 1 88 60 Z') + P('M52 60 A12 24 0 0 1 76 60 Z', 'T:light') +
                    R(62, 60, 4, 26, 2, 'T:dark') + P('M8 88 Q50 72 92 88 Z', 'T:light')),
    'hr_recruitment': (C(44, 44, 28) + C(44, 44, 21, 'T:white') + C(44, 37, 7) + P('M32 56 C32 46 56 46 56 56 Z') +
                       Poly([(60, 68), (68, 60), (90, 82), (82, 90)], 'T:dark')),
    'hr_skills': (Poly([(34, 8), (48, 8), (44, 42), (30, 42)]) + Poly([(52, 8), (66, 8), (70, 42), (56, 42)], 'T:dark') +
                  C(50, 62, 24, GOLD) + C(50, 62, 18, GOLD_L) + star(50, 62, 11, 4.5, 5, fill='T:base')),
    'hr_referral': (person(36, 36, 12, 42) + person(66, 42, 9, 34, 'T:light') +
                    C(80, 22, 12, GREEN) + R(78, 15, 4, 14, 2, 'T:white') + R(73, 20, 14, 4, 2, 'T:white')),
    'hr_appraisal': (person(40, 40, 13, 48) + star(76, 28, 14, 6, 5, fill=GOLD) +
                     R(62, 60, 6, 24, 3, 'T:light') + R(72, 50, 6, 34, 3, 'T:light') + R(82, 68, 6, 16, 3, 'T:light')),
    'hr_timesheet': (R(44, 12, 12, 8, 2, 'T:dark') + R(46, 20, 8, 6, 1, 'T:dark') + C(50, 56, 30) + C(50, 56, 23, 'T:white') +
                     S('M50 56 V38', 'T:dark', 4) + S('M50 56 L60 62', 'T:dark', 4) + C(50, 56, 3, 'T:dark')),
    'lunch': (P('M12 46 H88 A38 38 0 0 1 12 46 Z') + R(9, 43, 82, 7, 3.5, 'T:light') +
              S('M38 34 C34 28 44 24 38 16', 'T:dark', 4) + S('M62 34 C58 28 68 24 62 16', 'T:dark', 4) +
              S('M50 32 C46 26 56 22 50 14', 'T:dark', 4)),
    'approvals': (P('M24 10 H62 L76 24 V90 H24 Z', 'T:white') + R(32, 32, 30, 5, 2.5, 'T:light') +
                  R(32, 42, 30, 5, 2.5, 'T:light') + R(32, 52, 18, 5, 2.5, 'T:light') +
                  C(64, 68, 18, GREEN) + check(52, 68, 0.8)),
    'frontdesk': (P('M20 64 A30 30 0 0 1 80 64 Z') + R(12, 64, 76, 10, 5, 'T:dark') + C(50, 28, 7, 'T:light') +
                  R(47, 16, 6, 8, 2, 'T:light') + S('M34 50 A16 16 0 0 1 48 40', 'T:white', 4, stroke_opacity='.7')),
    'planning': (R(12, 12, 76, 76, 9, 'T:white') + R(18, 18, 8, 64, 2, 'T:light') +
                 R(22, 26, 36, 11, 5.5) + R(34, 44, 46, 11, 5.5, 'T:light') + R(22, 62, 28, 11, 5.5, 'T:dark')),
    # --- Services ----------------------------------------------------------
    'project': (R(12, 12, 76, 76, 9, 'T:white') +
                R(18, 20, 20, 15, 3.5) + R(18, 39, 20, 15, 3.5) + R(18, 58, 20, 15, 3.5, 'T:light') +
                R(40, 20, 20, 15, 3.5, 'T:light') + R(40, 39, 20, 15, 3.5) +
                R(62, 20, 20, 15, 3.5, 'T:dark')),
    'project_todo': (R(14, 12, 72, 76, 9, 'T:white') +
                     C(28, 30, 8, GREEN) + check(22.5, 30, 0.42) + R(42, 27, 32, 6, 3, 'T:light') +
                     C(28, 50, 8, GREEN) + check(22.5, 50, 0.42) + R(42, 47, 26, 6, 3, 'T:light') +
                     C(28, 70, 8, 'T:light') + R(42, 67, 32, 6, 3, 'T:light')),
    'helpdesk': (S('M22 58 V50 A28 28 0 0 1 78 50 V58', 'T:base', 9) +
                 R(14, 52, 14, 24, 6, 'T:dark') + R(72, 52, 14, 24, 6, 'T:dark') +
                 S('M78 76 Q78 88 60 88', 'T:base', 6) + C(58, 88, 5, 'T:dark')),
    'industry_fsm': (P('M50 92 C50 92 20 60 20 42 A30 30 0 0 1 80 42 C80 60 50 92 50 92 Z') + C(50, 42, 15, 'T:white') +
                     Poly([(40, 50), (44, 54), (58, 40), (54, 36)], 'T:dark') + C(57, 37, 6, 'T:dark') + C(59, 35, 2.5, 'T:white')),
    'appointment': (calendar_frame() + C(50, 63, 15) + S('M50 63 V54', 'T:white', 4) + S('M50 63 L56 67', 'T:white', 4)),
    'room': (R(22, 8, 56, 84, 8, 'T:dark') + R(29, 15, 42, 77, 4) + C(63, 54, 4, GOLD) +
             R(36, 24, 28, 18, 3, 'T:light')),
    # --- Productivity ------------------------------------------------------
    'mail': (bubble(10, 12, 64, 44, 'left') + bubble(40, 44, 50, 36, 'right', 'T:light') +
             dots([(28, 34), (42, 34), (56, 34)], 4.5)),
    'calendar': (calendar_frame() +
                 dots([(30, 52), (44, 52), (58, 52), (72, 52), (30, 66), (44, 66), (72, 66)], 4, 'T:light') +
                 C(58, 66, 5, RED)),
    'documents': (P('M14 28 Q14 20 22 20 H38 L46 28 H78 Q86 28 86 36 V78 Q86 86 78 86 H22 Q14 86 14 78 Z', 'T:dark') +
                  R(24, 34, 52, 40, 4, 'T:white') + R(32, 42, 30, 4, 2, 'T:light') + R(32, 50, 22, 4, 2, 'T:light') +
                  P('M14 48 H86 V78 Q86 86 78 86 H22 Q14 86 14 78 Z')),
    'knowledge': (P('M50 26 C40 18 26 18 12 22 V80 C26 76 40 76 50 84 Z') +
                  P('M50 26 C60 18 74 18 88 22 V80 C74 76 60 76 50 84 Z', 'T:light') +
                  R(48, 26, 4, 58, 2, 'T:dark') +
                  S('M22 36 C30 34 38 34 42 36 M22 48 C30 46 38 46 42 48 M22 60 C30 58 38 58 42 60', 'T:white', 3.5, stroke_opacity='.85') +
                  S('M58 36 C62 34 70 34 78 36 M58 48 C62 46 70 46 78 48', 'T:dark', 3.5, stroke_opacity='.5')),
    'spreadsheet_dashboard': (R(12, 12, 76, 76, 9, 'T:white') + R(22, 52, 11, 26, 3) + R(38, 40, 11, 38, 3, 'T:light') +
                              R(54, 28, 11, 50, 3) + R(70, 46, 11, 32, 3, 'T:dark') + R(18, 80, 64, 3, 1.5, 'T:light')),
    'voip': (P('M22 10 H36 L44 32 L34 40 C40 52 48 60 60 66 L68 56 L88 64 V78 Q88 90 78 90 C46 90 10 54 10 22 Q10 10 22 10 Z') +
             S('M60 26 A16 16 0 0 1 76 42', 'T:light', 5) + S('M62 14 A28 28 0 0 1 88 40', 'T:light', 5, stroke_opacity='.7')),
    'whatsapp': (P('M50 10 A37 37 0 1 1 19 68 L12 90 L34 84 A37 37 0 0 1 50 10 Z') +
                 P('M38 32 H45 L48 42 L43 46 C46 53 51 58 58 61 L62 56 L70 60 V67 Q70 70 66 70 C50 70 32 52 32 36 Q32 32 38 32 Z', 'T:white')),
    'data_recycle': (E(50, 26, 30, 10, 'T:light') + R(20, 26, 60, 44) + E(50, 70, 30, 10) +
                     E(50, 26, 30, 10, 'T:light') + sparkle(80, 74, 14, 5, GOLD) + sparkle(66, 88, 7, 2.5, 'T:white')),
    'utm': (C(36, 50, 18, 'none', stroke='T:base', stroke_width='10') +
            C(64, 50, 18, 'none', stroke='T:dark', stroke_width='10')),
    'marketing_card': (R(12, 16, 76, 68, 9, 'T:white') + R(18, 22, 64, 38, 4, 'T:light') +
                       P('M18 60 L38 40 L50 52 L60 44 L82 60 Z') + C(70, 33, 6, GOLD) +
                       R(18, 66, 40, 5, 2.5, 'T:light') + R(18, 74, 26, 5, 2.5, 'T:light')),
    # --- Marketing ---------------------------------------------------------
    'mass_mailing': (R(12, 24, 76, 54, 8) + P('M12 30 L50 60 L88 30 Z', 'T:light') +
                     P('M12 78 L44 52 L50 57 L56 52 L88 78 Z', 'T:dark') + Poly([(66, 8), (92, 18), (74, 30)], GOLD)),
    'mass_mailing_sms': (R(28, 8, 44, 84, 10) + R(34, 18, 32, 58, 4, 'T:white') + R(44, 12, 12, 3, 1.5, 'T:light') +
                         bubble(38, 30, 24, 16, 'left') + dots([(45, 38), (50, 38), (55, 38)], 2) +
                         C(50, 84, 3.5, 'T:light')),
    'social': (S('M34 45 L64 27', 'T:light', 7) + S('M34 55 L64 73', 'T:light', 7) +
               C(74, 22, 12) + C(24, 50, 12, 'T:dark') + C(74, 78, 12)),
    'marketing_automation': (S('M36 50 H50 V22 H64', 'T:light', 6) + S('M50 50 V78 H64', 'T:light', 6) +
                             R(10, 36, 26, 28, 7) + Poly([(19, 43), (19, 57), (29, 50)], 'T:white') +
                             R(64, 8, 26, 28, 7, 'T:light') + R(64, 64, 26, 28, 7, 'T:dark') +
                             check(70, 78, 0.5) + R(72, 18, 10, 3, 1.5, 'T:white') + R(72, 24, 10, 3, 1.5, 'T:white')),
    'event': (ticket() + S('M62 30 V70', 'T:white', 3, stroke_dasharray='4 6', stroke_opacity='.8') +
              star(38, 50, 12, 5, 5, fill='T:white')),
    'survey': (R(20, 14, 60, 76, 8) + R(28, 26, 44, 56, 4, 'T:white') + R(38, 8, 24, 12, 4, 'T:dark') +
               R(34, 34, 9, 9, 2.5, GREEN) + R(48, 36.5, 20, 4, 2, 'T:light') +
               R(34, 49, 9, 9, 2.5, GREEN) + R(48, 51.5, 20, 4, 2, 'T:light') +
               R(34, 64, 9, 9, 2.5, 'T:light') + R(48, 66.5, 20, 4, 2, 'T:light')),
    # --- Website -----------------------------------------------------------
    'website': (C(50, 50, 35) + E(50, 50, 15, 35, 'none', stroke='T:white', stroke_width='4') +
                S('M15 50 H85', 'T:white', 4) + S('M22 33 H78 M22 67 H78', 'T:white', 3, stroke_opacity='.75')),
    'website_sale': (P('M26 32 H86 L76 62 H34 Z') + S('M8 20 H22 L34 64 H76', 'T:dark', 6) +
                     C(40, 76, 7, 'T:dark') + C(70, 76, 7, 'T:dark') + R(44, 40, 24, 4, 2, 'T:white') + R(46, 48, 20, 4, 2, 'T:white')),
    'website_slides': (P('M50 16 L92 38 L50 60 L8 38 Z') + P('M28 46 V64 C28 78 72 78 72 64 V46 L50 58 Z', 'T:dark') +
                       S('M88 40 V60', GOLD, 4) + C(88, 63, 4, GOLD)),
    'im_livechat': (bubble(10, 12, 58, 40, 'left', 'T:dark') + bubble(36, 44, 54, 36, 'right', 'T:light') +
                    dots([(26, 32), (39, 32), (52, 32)], 4, 'T:light') + dots([(52, 62), (63, 62), (74, 62)], 4, 'T:dark')),
    'website_hr_recruitment': (R(38, 10, 24, 14, 5, 'T:dark') + R(43, 15, 14, 4, 2, 'T:light') +
                               R(12, 26, 76, 58, 9) + R(12, 46, 76, 8, 0, 'T:dark') + R(43, 42, 14, 14, 3, GOLD)),
    # --- Connectors --------------------------------------------------------
    'delivery': (R(10, 26, 50, 40, 6) + P('M60 38 H76 L90 54 V66 H60 Z', 'T:dark') + R(64, 43, 12, 10, 2, 'T:white') +
                 C(26, 72, 8, 'T:dark') + C(26, 72, 3, 'T:white') + C(74, 72, 8, 'T:dark') + C(74, 72, 3, 'T:white') +
                 R(20, 34, 30, 5, 2.5, 'T:light')),
}
GLYPHS['timesheet_grid'] = GLYPHS['hr_timesheet']
GLYPHS['website_event'] = GLYPHS['event']


# ---------------------------------------------------------------------------
# Catalog: (key, glyph, title, category, edition, hue, note)
# key = SVG file name and lookup key (see identity/models/identity_brand.py)
# ---------------------------------------------------------------------------
ICONS = [
    # Administration ------------------------------------------------------
    ('base__settings',  'base__settings',  'Settings',           'admin', 'both', '#6F7C93', 'base/static/description/settings.png'),
    ('base__modules',   'base__modules',   'Apps',               'admin', 'both', '#5F6E86', 'base/static/description/modules.png'),
    ('base__exception', 'base__exception', 'Tests (debug menu)', 'admin', 'both', '#7A879C', 'base/static/description/exception.png'),
    ('databases',       'databases',       'Databases',          'admin', 'enterprise', '#5B7290', ''),
    ('iot',             'iot',             'Internet of Things', 'admin', 'enterprise', '#5E8BA8', ''),
    ('web_studio',      'web_studio',      'Studio',             'admin', 'enterprise', '#7E63E6', ''),
    ('esg',             'esg',             'ESG',                'admin', 'enterprise', '#3DAA6E', ''),
    ('ai',             'ai_app',          'AI (core)',          'productivity', 'enterprise', '#8E5A8C', 'ai/static/description/icon.png: systray, composer, agent avatars'),
    ('ai_agentic',      'ai_app',          'AI',                 'admin', 'enterprise', '#6E5CE6', ''),
    ('obox',            'obox',            'IoT Boxes',          'admin', 'enterprise', '#4F86C6', ''),
    # Finance -------------------------------------------------------------
    ('account',         'account',         'Invoicing',          'finance', 'both', '#2EAF7A', ''),
    ('accountant',      'accountant',      'Accounting',         'finance', 'enterprise', '#1E9E74', ''),
    ('equity',          'equity',          'Equity',             'finance', 'enterprise', '#22A38E', ''),
    ('hr_payroll',      'hr_payroll',      'Payroll',            'finance', 'enterprise', '#39AC6A', 'menu defined by hr_work_entry_enterprise'),
    ('hr_expense',      'hr_expense',      'Expenses',           'finance', 'both', '#31AD86', ''),
    # Sales ---------------------------------------------------------------
    ('sale_management', 'sale_management', 'Sales',              'sales', 'both', '#EF6A4B', 'menu defined by sale'),
    ('crm',             'crm',             'CRM',                'sales', 'both', '#E5533F', ''),
    ('contacts',        'contacts',        'Contacts',           'sales', 'both', '#EE8A3E', ''),
    ('point_of_sale',   'point_of_sale',   'Point of Sale',      'sales', 'both', '#E25C78', ''),
    ('pos_restaurant',  'pos_restaurant',  'Restaurant',         'sales', 'both', '#EA6B57', ''),
    ('pos_enterprise',  'pos_enterprise',  'Kitchen Display',    'sales', 'enterprise', '#E0573F', ''),
    ('sale_subscription', 'sale_subscription', 'Subscriptions',  'sales', 'enterprise', '#EC7A4E', ''),
    ('sale_renting',    'sale_renting',    'Rental',             'sales', 'enterprise', '#E3605C', ''),
    ('sign',            'sign',            'Sign',               'sales', 'enterprise', '#D7524F', ''),
    ('sale_amazon',     'marketplace',     'Amazon Connector',   'sales', 'enterprise', '#EF8C4A', ''),
    ('sale_lazada',     'marketplace',     'Lazada Connector',   'sales', 'enterprise', '#E86A8A', ''),
    ('sale_shopee',     'marketplace',     'Shopee Connector',   'sales', 'enterprise', '#EE6B3B', ''),
    ('sale_tiktok',     'marketplace',     'TikTok Shop Connector', 'sales', 'enterprise', '#D9536F', ''),
    # Supply chain --------------------------------------------------------
    ('stock',           'stock',           'Inventory',          'supply', 'both', '#5B6EF0', ''),
    ('purchase',        'purchase',        'Purchase',           'supply', 'both', '#4A7DEC', ''),
    ('mrp',             'mrp',             'Manufacturing',      'supply', 'both', '#6A62EE', ''),
    ('mrp_plm',         'mrp_plm',         'PLM',                'supply', 'enterprise', '#5877E3', ''),
    ('mrp_workorder',   'mrp_workorder',   'Shop Floor',         'supply', 'enterprise', '#4C6ADB', 'mrp_workorder/static/description/mrp_display_icon.png'),
    ('quality_control', 'quality_control', 'Quality',            'supply', 'enterprise', '#5A86EA', ''),
    ('maintenance',     'maintenance',     'Maintenance',        'supply', 'both', '#546FE0', ''),
    ('repair',          'repair',          'Repairs',            'supply', 'both', '#6478EA', ''),
    ('stock_barcode',   'stock_barcode',   'Barcode',            'supply', 'enterprise', '#4865D4', ''),
    ('fleet',           'fleet',           'Fleet',              'supply', 'both', '#4B79E4', ''),
    # Human resources -----------------------------------------------------
    ('hr',              'hr',              'Employees',          'hr', 'both', '#F0A126', ''),
    ('hr_attendance',   'hr_attendance',   'Attendances',        'hr', 'both', '#EFAE2F', ''),
    ('hr_holidays',     'hr_holidays',     'Time Off',           'hr', 'both', '#2FB0D6', ''),
    ('hr_recruitment',  'hr_recruitment',  'Recruitment',        'hr', 'both', '#EC9629', ''),
    ('hr_skills',       'hr_skills',       'Skills Management',  'hr', 'both', '#E58A2A', ''),
    ('hr_referral',     'hr_referral',     'Referrals',          'hr', 'enterprise', '#F0A538', ''),
    ('hr_appraisal',    'hr_appraisal',    'Appraisals',         'hr', 'enterprise', '#F2AD31', ''),
    ('hr_timesheet',    'hr_timesheet',    'Timesheets',         'hr', 'both', '#EC9C2E', 'hr_timesheet/static/description/icon_timesheet.png'),
    ('timesheet_grid',  'timesheet_grid',  'Timesheets (Enterprise app)', 'hr', 'enterprise', '#EC9C2E', ''),
    ('lunch',           'lunch',           'Lunch',              'hr', 'both', '#F1A24A', ''),
    ('approvals',       'approvals',       'Approvals',          'hr', 'enterprise', '#EB9D2D', ''),
    ('frontdesk',       'frontdesk',       'Frontdesk',          'hr', 'enterprise', '#EEA93B', ''),
    ('planning',        'planning',        'Planning',           'hr', 'enterprise', '#E9962A', ''),
    # Services ------------------------------------------------------------
    ('project',         'project',         'Project',            'services', 'both', '#21B3CA', ''),
    ('project_todo',    'project_todo',    'To-do',              'services', 'both', '#28AEBF', ''),
    ('helpdesk',        'helpdesk',        'Helpdesk',           'services', 'enterprise', '#1DAABB', ''),
    ('planning_field_service', 'industry_fsm', 'Field Service', 'services', 'enterprise', '#22ABB8', ''),
    ('appointment',     'appointment',     'Appointments',       'services', 'enterprise', '#2CB2C4', ''),
    ('room',            'room',            'Meeting Rooms',      'services', 'enterprise', '#27A9C1', ''),
    # Productivity --------------------------------------------------------
    ('mail',            'mail',            'Discuss',            'productivity', 'both', '#8A69F0', ''),
    ('calendar',        'calendar',        'Calendar',           'productivity', 'both', '#9A78F4', ''),
    ('documents',       'documents',       'Documents',          'productivity', 'enterprise', '#886FEA', ''),
    ('knowledge',       'knowledge',       'Knowledge',          'productivity', 'enterprise', '#916BEE', ''),
    ('spreadsheet_dashboard', 'spreadsheet_dashboard', 'Dashboards', 'productivity', 'both', '#8C75EC', ''),
    ('voip',            'voip',            'Phone',              'productivity', 'enterprise', '#906DF1', ''),
    ('whatsapp',        'whatsapp',        'WhatsApp',           'productivity', 'enterprise', '#27B36A', ''),
    ('data_recycle',    'data_recycle',    'Data Cleaning',      'productivity', 'both', '#9679EE', ''),
    # Marketing -----------------------------------------------------------
    ('mass_mailing',    'mass_mailing',    'Email Marketing',    'marketing', 'both', '#E65CA3', ''),
    ('mass_mailing_sms', 'mass_mailing_sms', 'SMS Marketing',    'marketing', 'both', '#E467A5', ''),
    ('social',          'social',          'Social Marketing',   'marketing', 'enterprise', '#E45A9B', ''),
    ('marketing_automation', 'marketing_automation', 'Marketing Automation', 'marketing', 'enterprise', '#E86CAC', ''),
    ('marketing_card',  'marketing_card',  'Marketing Card',     'marketing', 'both', '#E268AD', ''),
    ('event',           'event',           'Events',             'marketing', 'both', '#E75999', ''),
    ('website_event',   'website_event',   'Events (website app)', 'marketing', 'both', '#E75999', ''),
    ('survey',          'survey',          'Surveys',            'marketing', 'both', '#E564A1', ''),
    ('utm',             'utm',             'Link Tracker',       'marketing', 'both', '#E46DA7', ''),
    # Website -------------------------------------------------------------
    ('website',         'website',         'Website',            'website', 'both', '#3CA5F2', ''),
    ('website_sale',    'website_sale',    'eCommerce',          'website', 'both', '#3A9AEC', ''),
    ('website_slides',  'website_slides',  'eLearning',          'website', 'both', '#46A4EF', ''),
    ('im_livechat',     'im_livechat',     'Live Chat',          'website', 'both', '#3E9FED', ''),
    ('website_hr_recruitment', 'website_hr_recruitment', 'Online Jobs', 'website', 'both', '#3897E6', ''),
    # Shipping connectors -------------------------------------------------
    ('delivery_bpost',      'delivery', 'bpost Shipping',       'connectors', 'enterprise', '#4CAABD', ''),
    ('delivery_dhl_rest',   'delivery', 'DHL Express Shipping', 'connectors', 'enterprise', '#E3A11F', ''),
    ('delivery_easypost',   'delivery', 'Easypost Shipping',    'connectors', 'enterprise', '#4CAABD', ''),
    ('delivery_envia',      'delivery', 'Envia Shipping',       'connectors', 'enterprise', '#4CAABD', ''),
    ('delivery_fedex_rest', 'delivery', 'Fedex Shipping',       'connectors', 'enterprise', '#6B5BD6', ''),
    ('delivery_sendcloud',  'delivery', 'Sendcloud Shipping',   'connectors', 'enterprise', '#4CAABD', ''),
    ('delivery_shiprocket', 'delivery', 'Shiprocket Shipping',  'connectors', 'enterprise', '#4CAABD', ''),
    ('delivery_shipstation', 'delivery', 'ShipStation Shipping', 'connectors', 'enterprise', '#4CAABD', ''),
    ('delivery_starshipit', 'delivery', 'Starshipit Shipping',  'connectors', 'enterprise', '#4CAABD', ''),
    ('delivery_ups_rest',   'delivery', 'UPS Shipping',         'connectors', 'enterprise', '#8A6A3B', ''),
    ('delivery_usps_rest',  'delivery', 'USPS Shipping',        'connectors', 'enterprise', '#3E6FC2', ''),
    # marut ---------------------------------------------------------------
    ('queue_job',       'base__settings',  'Job Queue',          'admin',    'both', '#5B7290', 'marut'),
    ('gate_management', 'frontdesk',       'Gate Management',    'services', 'both', '#5E8BA8', 'marut'),
    ('field_sales',     'crm',             'Field Sales',        'sales',    'both', '#EF6A4B', 'marut'),
]

# Material Symbols Outlined (Apache-2.0, Google) used by the 'symbol' style: catalogue key -> symbol name.
# Sources are cached in tools/symbols/<name>.svg by build_icons.py.
BRAND_SYMBOL = 'hub'
SYMBOLS = {
    'account': 'receipt_long',
    'accountant': 'account_balance',
    'ai': 'auto_awesome',
    'ai_agentic': 'auto_awesome',
    'appointment': 'event_available',
    'approvals': 'approval',
    'base__exception': 'bug_report',
    'base__modules': 'apps',
    'base__settings': 'settings',
    'calendar': 'calendar_month',
    'contacts': 'contacts',
    'crm': 'filter_alt',
    'data_recycle': 'cleaning_services',
    'databases': 'database',
    'delivery_bpost': 'local_shipping',
    'delivery_dhl_rest': 'local_shipping',
    'delivery_easypost': 'local_shipping',
    'delivery_envia': 'local_shipping',
    'delivery_fedex_rest': 'local_shipping',
    'delivery_sendcloud': 'local_shipping',
    'delivery_shiprocket': 'local_shipping',
    'delivery_shipstation': 'local_shipping',
    'delivery_starshipit': 'local_shipping',
    'delivery_ups_rest': 'local_shipping',
    'delivery_usps_rest': 'local_shipping',
    'documents': 'folder_open',
    'equity': 'pie_chart',
    'esg': 'eco',
    'event': 'confirmation_number',
    'fleet': 'directions_car',
    'frontdesk': 'desk',
    'helpdesk': 'support_agent',
    'hr': 'badge',
    'hr_appraisal': 'grade',
    'hr_attendance': 'schedule',
    'hr_expense': 'receipt',
    'hr_holidays': 'beach_access',
    'hr_payroll': 'payments',
    'hr_recruitment': 'person_search',
    'hr_referral': 'group_add',
    'hr_skills': 'psychology',
    'hr_timesheet': 'timer',
    'im_livechat': 'chat_bubble',
    'iot': 'devices',
    'knowledge': 'menu_book',
    'lunch': 'restaurant',
    'mail': 'forum',
    'maintenance': 'build',
    'marketing_automation': 'schema',
    'marketing_card': 'id_card',
    'mass_mailing': 'mail',
    'mass_mailing_sms': 'sms',
    'mrp': 'precision_manufacturing',
    'mrp_plm': 'design_services',
    'mrp_workorder': 'conveyor_belt',
    'obox': 'developer_board',
    'planning': 'calendar_view_week',
    'planning_field_service': 'engineering',
    'point_of_sale': 'point_of_sale',
    'pos_enterprise': 'restaurant_menu',
    'pos_restaurant': 'table_restaurant',
    'project': 'view_kanban',
    'project_todo': 'checklist',
    'purchase': 'shopping_bag',
    'quality_control': 'verified',
    'repair': 'handyman',
    'room': 'meeting_room',
    'sale_amazon': 'storefront',
    'sale_lazada': 'storefront',
    'sale_management': 'sell',
    'sale_renting': 'key',
    'sale_shopee': 'storefront',
    'sale_subscription': 'autorenew',
    'sale_tiktok': 'storefront',
    'sign': 'draw',
    'social': 'share',
    'spreadsheet_dashboard': 'dashboard',
    'stock': 'inventory_2',
    'stock_barcode': 'barcode_scanner',
    'survey': 'ballot',
    'timesheet_grid': 'timer',
    'utm': 'link',
    'voip': 'call',
    'web_studio': 'construction',
    'website': 'public',
    'website_event': 'confirmation_number',
    'website_hr_recruitment': 'work',
    'website_sale': 'shopping_cart',
    'website_slides': 'school',
    'whatsapp': 'chat',
    'queue_job': 'pending_actions',
    'gate_management': 'door_open',
    'field_sales': 'route',
}
