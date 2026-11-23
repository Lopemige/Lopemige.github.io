#!/usr/bin/env python3
"""
The picture cards: one for each job on the Experience page and one for each service.

They are drawn by art.py (python3 tools/art.py), which imports CARDS from here and writes
assets/cards/<name>.svg. Every card is 800 x 600. Nothing in a picture is text, so the same card
works in English and in Spanish.

To change one, edit its function below, run tools/art.py, and look at the result.
"""
import math
import random

from art import INK, INK2, ACCENT, fmt, hills, pumpjack, palm, cloud, tank, ICON_PATHS, ICONS

W, H = 800, 600
STEEL = "#c9ced6"
STEEL2 = "#9aa3b2"
HOLE = "#3d4654"


# ---------------------------------------------------------------------------
# Small drawing helpers
# ---------------------------------------------------------------------------

def svg(inner, defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
            'preserveAspectRatio="xMidYMid slice"><defs>%s</defs>%s</svg>') % (W, H, W, H, defs, inner)


def grad(i, stops, x1=0, y1=0, x2=0, y2=1):
    return '<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (
        i, x1, y1, x2, y2, "".join('<stop offset="%s" stop-color="%s"/>' % s for s in stops))


def rect(x, y, w, h, fill, extra=""):
    return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"%s/>' % (fmt(x), fmt(y), fmt(w), fmt(h), fill, extra)


def circ(x, y, r, fill, extra=""):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (fmt(x), fmt(y), fmt(r), fill, extra)


def ell(x, y, rx, ry, fill, extra=""):
    return '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"%s/>' % (fmt(x), fmt(y), fmt(rx), fmt(ry), fill, extra)


def line(x1, y1, x2, y2, stroke, w, extra=""):
    return '<path d="M%s %sL%s %s" stroke="%s" stroke-width="%s" stroke-linecap="round"%s/>' % (
        fmt(x1), fmt(y1), fmt(x2), fmt(y2), stroke, fmt(w), extra)


def path(d, fill="none", stroke=None, w=0, extra=""):
    s = ' stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"' % (stroke, fmt(w)) if stroke else ""
    return '<path d="%s" fill="%s"%s%s/>' % (d, fill, s, extra)


def poly(pts, fill, extra=""):
    return '<path d="M%sZ" fill="%s"%s/>' % ("L".join("%s %s" % (fmt(a), fmt(b)) for a, b in pts), fill, extra)


def truss(x, yb, h, wb, wt, n, sw, col=INK):
    """A lattice tower on the ground line yb: bottom width wb, top width wt, n panels."""
    lv = [(yb - h * i / n, (wb - (wb - wt) * i / n) / 2) for i in range(n + 1)]
    d = ["M%s %sL%s %sM%s %sL%s %s" % (fmt(x - lv[0][1]), fmt(yb), fmt(x - lv[-1][1]), fmt(lv[-1][0]),
                                      fmt(x + lv[0][1]), fmt(yb), fmt(x + lv[-1][1]), fmt(lv[-1][0]))]
    for ly, half in lv:
        d.append("M%s %sL%s %s" % (fmt(x - half), fmt(ly), fmt(x + half), fmt(ly)))
    for i in range(n):
        (y0, h0), (y1, h1) = lv[i], lv[i + 1]
        if i % 2 == 0:
            d.append("M%s %sL%s %s" % (fmt(x - h0), fmt(y0), fmt(x + h1), fmt(y1)))
        else:
            d.append("M%s %sL%s %s" % (fmt(x + h0), fmt(y0), fmt(x - h1), fmt(y1)))
    return path("".join(d), "none", col, sw)


def minirig(x, y, s=1.0):
    """A small drilling rig, for pictures where the rig is only a part of the story."""
    g = [truss(x, y - 14 * s, 84 * s, 38 * s, 12 * s, 5, max(1.5, 2.2 * s)),
         rect(x - 9 * s, y - 106 * s, 18 * s, 8 * s, ACCENT),
         rect(x - 32 * s, y - 14 * s, 64 * s, 14 * s, INK2),
         line(x - 3 * s, y - 98 * s, x - 3 * s, y - 40 * s, INK, max(1, 1.2 * s)),
         line(x + 3 * s, y - 98 * s, x + 3 * s, y - 40 * s, INK, max(1, 1.2 * s)),
         rect(x - 6 * s, y - 52 * s, 12 * s, 10 * s, ACCENT),
         rect(x + 36 * s, y - 16 * s, 34 * s, 16 * s, "#6b7280"),
         rect(x + 40 * s, y - 12 * s, 8 * s, 5 * s, "#e7eef5")]
    return "".join(g)


def wavy(y0, amp, seed, step=20):
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    pts = []
    x = -step
    while x <= W + step:
        y = y0 + amp * (0.6 * math.sin(x * 0.013 + ph[0]) + 0.3 * math.sin(x * 0.031 + ph[1]) + 0.2 * math.sin(x * 0.07 + ph[2]))
        pts.append("%s %s" % (fmt(x), fmt(y)))
        x += step
    return pts


def strata(layers, seed=3, bottom=H, grains=True):
    """Layers of rock, from the top down. layers = [(y, amplitude, colour, grain colour)]."""
    out = []
    rnd = random.Random(seed)
    for i, (y0, amp, col, gcol) in enumerate(layers):
        pts = wavy(y0, amp, seed + i)
        out.append('<path fill="%s" d="M%s L%d %d L%d %dZ"/>' % (col, " L".join(pts), W + 20, bottom, -20, bottom))
        if grains:
            y1 = layers[i + 1][0] if i + 1 < len(layers) else bottom
            for _ in range(26):
                gx = rnd.uniform(10, W - 10)
                gy = rnd.uniform(y0 + amp + 8, max(y0 + amp + 9, y1 - 10))
                out.append(ell(gx, gy, rnd.uniform(2, 5), rnd.uniform(1.4, 2.6), gcol, ' opacity=".5"'))
    return "".join(out)


def person(x, y, s, skin, vest, hat="#f5c518", shirt="#e8edf3", pants="#3b4a66", face_right=True):
    """A worker standing on y, about 110 units tall at s = 1."""
    g = []
    g.append(rect(x - 11 * s, y - 42 * s, 10 * s, 42 * s, pants, ' rx="3"'))
    g.append(rect(x + 1 * s, y - 42 * s, 10 * s, 42 * s, pants, ' rx="3"'))
    g.append(rect(x - 12 * s, y - 4 * s, 12 * s, 5 * s, INK, ' rx="2"'))
    g.append(rect(x + 0 * s, y - 4 * s, 12 * s, 5 * s, INK, ' rx="2"'))
    g.append(rect(x - 17 * s, y - 84 * s, 34 * s, 46 * s, shirt, ' rx="8"'))
    g.append(rect(x - 17 * s, y - 84 * s, 34 * s, 46 * s, vest, ' rx="8" opacity=".95"'))
    g.append(rect(x - 17 * s, y - 62 * s, 34 * s, 5 * s, "#f3f4f6", ""))
    g.append(rect(x - 24 * s, y - 80 * s, 9 * s, 34 * s, shirt, ' rx="4"'))
    g.append(rect(x + 15 * s, y - 80 * s, 9 * s, 34 * s, shirt, ' rx="4"'))
    g.append(circ(x - 19.5 * s, y - 44 * s, 5 * s, skin))
    g.append(circ(x + 19.5 * s, y - 44 * s, 5 * s, skin))
    g.append(rect(x - 4 * s, y - 92 * s, 8 * s, 9 * s, skin))
    g.append(circ(x, y - 100 * s, 12 * s, skin))
    g.append('<path d="M%s %sA%s %s 0 0 1 %s %sZ" fill="%s"/>' % (fmt(x - 14 * s), fmt(y - 102 * s), fmt(14 * s), fmt(14 * s), fmt(x + 14 * s), fmt(y - 102 * s), hat))
    g.append(rect(x - 17 * s, y - 103 * s, 34 * s, 4 * s, hat, ' rx="2"'))
    g.append(rect(x - 2 * s, y - 116 * s, 4 * s, 12 * s, hat, ' opacity=".9"'))
    return "".join(g)


def sky_defs(stops, id_="sky"):
    return grad(id_, stops) + ('<radialGradient id="sun"><stop offset="0" stop-color="#fff3cf" stop-opacity=".95"/>'
                               '<stop offset=".4" stop-color="#fff3cf" stop-opacity=".5"/><stop offset="1" stop-color="#fff3cf" stop-opacity="0"/></radialGradient>')


def ground_scene(sky, far, mid, ground, front, gy=470, sun=None, clouds=((130, 90, 1.1), (560, 60, 0.9), (700, 150, 0.8))):
    """Sky, sun, clouds, two ranges of hills and the ground. Returns (defs, markup)."""
    defs = sky_defs(sky)
    out = ['<rect width="%d" height="%d" fill="url(#sky)"/>' % (W, H)]
    if sun:
        out.append(circ(sun[0], sun[1], 150, "url(#sun)"))
        out.append(circ(sun[0], sun[1], 30, "#fff3cf"))
    for cx, cy, cs in clouds:
        out.append(cloud(cx, cy, cs))
    out.append(hills(W, H, gy - 78, 24, far, 1.3))
    out.append(hills(W, H, gy - 34, 22, mid, 4.1))
    out.append(rect(0, gy - 6, W, H - gy + 6, ground))
    out.append(hills(W, H, gy + 2, 5, ground, 7.7))
    out.append(rect(0, gy + 78, W, H - gy - 78, front))
    return defs, "".join(out)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

def fishing():
    """Roku Tech: fishing and remedial work. A well in section, and a close-up of the tool catching the lost pipe."""
    defs = grad("sky", [(0, "#a9d3ee"), (1, "#e9f4fa")]) + '<clipPath id="lens"><circle cx="590" cy="372" r="176"/></clipPath>'
    strata_layers = [(190, 6, "#dcbf91", "#b99668"), (270, 7, "#c79d6d", "#9d764d"), (350, 8, "#ad8359", "#82603f"),
                     (430, 8, "#92704f", "#6b4f37"), (510, 7, "#775a42", "#563f2c")]
    o = ['<rect width="800" height="190" fill="url(#sky)"/>', cloud(150, 60, 0.9), cloud(520, 40, 0.7)]
    o.append(hills(W, H, 170, 12, "#bfd8b0", 2.2))
    o.append(rect(0, 172, W, 30, "#86a46b"))
    o.append(strata(strata_layers, seed=5))
    o.append(rect(0, 168, W, 8, "#6f9157"))
    # surface equipment and the well
    o.append(minirig(220, 176, 1.15))
    o.append(rect(96, 164, 70, 12, "#6b7280", ' rx="2"'))
    o.append(rect(100, 150, 22, 14, "#ece8df"))
    o.append(rect(128, 150, 22, 14, "#ece8df"))
    wx = 220
    # cement and casing, then the open hole below the shoe
    o.append(rect(wx - 20, 176, 40, 262, "#d8d5cc"))
    o.append(rect(wx - 13, 176, 26, 262, STEEL2))
    o.append(rect(wx - 8, 176, 16, 262, HOLE))
    o.append(rect(wx - 8, 438, 16, 150, HOLE))
    o.append(path("M%d 438l-10 8h36l-10 -8z" % (wx - 8), "#d8d5cc"))
    # the string with the overshot on its end, and the lost pipe in the hole
    o.append(rect(wx - 3, 176, 6, 250, STEEL))
    o.append(rect(wx - 6, 426, 12, 26, "#e9eef4", ' stroke="%s" stroke-width="1.5"' % INK))
    o.append(rect(wx - 6, 436, 12, 4, ACCENT))
    o.append(rect(wx - 5, 462, 10, 120, STEEL2))
    o.append(rect(wx - 6, 462, 12, 8, "#b4bcc8"))
    # the ring that marks the close-up and the two lines that lead to it
    o.append('<path d="M%s 428L%s 214M%s 482L%s 530" stroke="#fff" stroke-width="3" stroke-dasharray="2 7" stroke-linecap="round" opacity=".95"/>' % (wx + 14, 432, wx + 14, 468))
    o.append('<circle cx="%d" cy="452" r="26" fill="none" stroke="#fff" stroke-width="4"/>' % wx)
    # the close-up
    o.append(circ(590, 372, 184, "#fff", ' opacity=".9"'))
    o.append('<g clip-path="url(#lens)">')
    o.append(rect(400, 180, 400, 400, "#8d6a4c"))
    o.append(strata([(180, 6, "#a9805a", "#82603f"), (330, 6, "#92704f", "#6b4f37"), (470, 6, "#775a42", "#563f2c")], seed=9, grains=False))
    # casing at the top, open hole below
    o.append(rect(498, 196, 184, 116, "#d8d5cc"))
    o.append(rect(508, 196, 164, 116, STEEL2))
    o.append(rect(520, 196, 140, 116, HOLE))
    o.append(rect(520, 312, 140, 280, HOLE))
    o.append(path("M498 312L520 312L520 322L498 322Z M682 312L660 312L660 322L682 322Z", "#d8d5cc"))
    # string, overshot and its guide
    o.append(rect(574, 190, 32, 140, "#e9eef4", ' stroke="%s" stroke-width="3"' % INK))
    for yy in (230, 290):
        o.append(rect(570, yy, 40, 8, STEEL2, ' stroke="%s" stroke-width="2"' % INK))
    o.append(rect(556, 326, 68, 72, "#e9eef4", ' stroke="%s" stroke-width="3.5" rx="3"' % INK))
    o.append(rect(556, 342, 68, 12, ACCENT))
    o.append(poly([(556, 398), (624, 398), (644, 424), (536, 424)], "#d6dbe3", ' stroke="%s" stroke-width="3.5" stroke-linejoin="round"' % INK))
    # the lost pipe with its neck, inside the guide
    o.append(rect(574, 408, 32, 30, STEEL2, ' stroke="%s" stroke-width="3"' % INK))
    o.append(rect(560, 438, 60, 160, "#b4bcc8", ' stroke="%s" stroke-width="3.5"' % INK))
    o.append(rect(556, 440, 68, 14, STEEL2, ' stroke="%s" stroke-width="3"' % INK))
    # two arrows pointing down: the tool is being lowered over the pipe
    for ax in (498, 682):
        o.append(path("M%d 252v44M%d 284l-12 -14M%d 284l12 -14" % (ax - 20 if ax < 590 else ax + 20, ax - 20 if ax < 590 else ax + 20, ax - 20 if ax < 590 else ax + 20), "none", "#fff", 5))
    o.append("</g>")
    o.append('<circle cx="590" cy="372" r="176" fill="none" stroke="#fff" stroke-width="7"/>')
    return svg("".join(o), defs)


def platform():
    """Wellbore Integrity Solutions: Mexico and Central America. An offshore platform in the Gulf."""
    defs = (grad("sky", [(0, "#79b4e3"), (0.55, "#d7e9f6"), (1, "#fde0b4")]) +
            grad("sea", [(0, "#58a6c9"), (1, "#235f8a")]) +
            '<radialGradient id="sun"><stop offset="0" stop-color="#fff3cf" stop-opacity=".95"/><stop offset=".4" stop-color="#fff3cf" stop-opacity=".5"/><stop offset="1" stop-color="#fff3cf" stop-opacity="0"/></radialGradient>')
    hy = 338
    o = ['<rect width="800" height="%d" fill="url(#sky)"/>' % hy]
    o.append(circ(600, hy - 12, 160, "url(#sun)"))
    o.append(circ(600, hy - 12, 34, "#fff3cf"))
    o += [cloud(150, 80, 1.1), cloud(470, 50, 0.8), cloud(690, 140, 0.9)]
    o.append(rect(0, hy, W, H - hy, "url(#sea)"))
    # reflection of the sun and little waves
    for i, w in enumerate((70, 56, 44, 34, 24, 16)):
        o.append(ell(600, hy + 10 + i * 17, w, 3, "#fff3cf", ' opacity=".55"'))
    rnd = random.Random(2)
    for _ in range(46):
        wx_, wy_ = rnd.uniform(0, W), rnd.uniform(hy + 14, H - 10)
        o.append(line(wx_, wy_, wx_ + rnd.uniform(14, 34), wy_, "#cfe8f3", 2.2, ' opacity=".5"'))
    # a platform far away
    o.append('<g opacity=".5" transform="translate(690 %d) scale(.34)">' % (hy + 8) + _jacket(0, 0, False) + "</g>")
    # the platform
    o.append(_jacket(290, 452, True))
    # supply boat
    bx, by = 600, 500
    o.append(poly([(bx - 70, by - 16), (bx + 86, by - 16), (bx + 66, by + 12), (bx - 56, by + 12)], "#243b53"))
    o.append(rect(bx - 70, by - 20, 156, 6, ACCENT))
    o.append(rect(bx - 38, by - 46, 50, 26, "#f3f4f6"))
    for k in range(3):
        o.append(rect(bx - 32 + k * 15, by - 40, 9, 8, "#5b7288"))
    o.append(rect(bx + 14, by - 36, 24, 16, "#e6e9ee"))
    o.append(rect(bx - 22, by - 58, 4, 12, INK))
    o.append(ell(bx + 8, by + 18, 90, 5, "#cfe8f3", ' opacity=".6"'))
    return svg("".join(o), defs)


def _jacket(x, ysea, big):
    """The platform: legs from the sea up to the deck, the rig, quarters, crane, helipad and flare boom."""
    dy = ysea - 150            # deck level
    g = []
    # legs and bracing
    legs = [x - 150, x - 50, x + 50, x + 150]
    for i in range(3):
        a, b = legs[i], legs[i + 1]
        g.append(path("M%s %sL%s %sM%s %sL%s %sM%s %sL%s %s" % (
            fmt(a), fmt(dy + 14), fmt(b), fmt(ysea - 50), fmt(b), fmt(dy + 14), fmt(a), fmt(ysea - 50),
            fmt(a), fmt(ysea - 50), fmt(b), fmt(ysea), ), "none", INK2, 3))
    for lx in legs:
        g.append(rect(lx - 5, dy + 10, 10, ysea - dy - 10, INK))
        g.append(rect(lx - 7, ysea - 8, 14, 6, "#6b7280"))
    for yy in (dy + 70, ysea - 50):
        g.append(rect(legs[0], yy, legs[-1] - legs[0], 5, INK2))
    # deck
    g.append(rect(x - 190, dy - 6, 380, 22, INK))
    g.append(rect(x - 170, dy - 28, 330, 22, "#d7dce4"))
    g.append(rect(x - 170, dy - 30, 330, 5, "#9aa3b2"))
    # quarters
    g.append(rect(x + 70, dy - 92, 96, 64, "#eef1f5"))
    g.append(rect(x + 70, dy - 100, 96, 10, ACCENT))
    for k in range(4):
        g.append(rect(x + 80 + k * 21, dy - 78, 14, 14, "#5b7288"))
        g.append(rect(x + 80 + k * 21, dy - 54, 14, 14, "#5b7288"))
    # derrick
    g.append(truss(x - 60, dy - 28, 190, 70, 22, 8, 3))
    g.append(rect(x - 75, dy - 232, 30, 14, ACCENT))
    g.append(rect(x - 68, dy - 82, 16, 12, ACCENT))
    g.append(rect(x - 100, dy - 44, 80, 16, INK2))
    # crane on the left
    g.append(rect(x - 150, dy - 70, 24, 42, INK2))
    g.append(path("M%s %sL%s %sL%s %s" % (fmt(x - 138), fmt(dy - 70), fmt(x - 92), fmt(dy - 150), fmt(x - 88), fmt(dy - 146)), "none", INK, 5))
    g.append(line(x - 92, dy - 148, x - 92, dy - 100, INK, 2))
    g.append(rect(x - 98, dy - 100, 12, 10, ACCENT))
    # helipad out to the left
    g.append(rect(x - 270, dy - 22, 100, 8, INK))
    g.append(path("M%s %sL%s %sM%s %sL%s %s" % (fmt(x - 260), fmt(dy - 14), fmt(x - 200), fmt(dy + 40), fmt(x - 172), fmt(dy - 14), fmt(x - 200), fmt(dy + 40)), "none", INK2, 3))
    g.append(ell(x - 220, dy - 24, 50, 9, "#6b7280"))
    g.append(rect(x - 227, dy - 29, 4, 10, "#fff", "") + rect(x - 217, dy - 29, 4, 10, "#fff", "") + rect(x - 227, dy - 25, 14, 3, "#fff", ""))
    # flare boom to the right
    g.append(path("M%s %sL%s %sM%s %sL%s %s" % (fmt(x + 160), fmt(dy - 24), fmt(x + 250), fmt(dy - 120), fmt(x + 160), fmt(dy - 4), fmt(x + 248), fmt(dy - 116)), "none", INK, 3))
    g.append(line(x + 160, dy - 4, x + 224, dy - 78, INK2, 2))
    fx, fy = x + 252, dy - 124
    g.append(circ(fx, fy - 26, 60, "#ffd98a", ' opacity=".35"'))
    g.append('<path d="M%s %sC%s %s %s %s %s %sC%s %s %s %s %s %sZ" fill="#f97316"/>' % (
        fmt(fx - 9), fmt(fy), fmt(fx - 17), fmt(fy - 26), fmt(fx - 2), fmt(fy - 42), fmt(fx + 3), fmt(fy - 68),
        fmt(fx + 10), fmt(fy - 44), fmt(fx + 18), fmt(fy - 26), fmt(fx + 9), fmt(fy)))
    g.append('<path d="M%s %sC%s %s %s %s %s %sC%s %s %s %s %s %sZ" fill="#fde047"/>' % (
        fmt(fx - 4), fmt(fy), fmt(fx - 8), fmt(fy - 15), fmt(fx), fmt(fy - 24), fmt(fx + 1), fmt(fy - 38),
        fmt(fx + 4), fmt(fy - 24), fmt(fx + 8), fmt(fy - 15), fmt(fx + 4), fmt(fy)))
    # waterline
    g.append(ell(x, ysea + 4, 190, 8, "#cfe8f3", ' opacity=".55"'))
    return "".join(g)


def landrig():
    """Nabors Drilling International: a land rig in the Andean foothills, with casing waiting on the rack."""
    gy = 470
    defs, base = ground_scene([(0, "#7fb8e6"), (0.7, "#cfe6f6"), (1, "#eaf5fb")], "#bcd3a5", "#9fbd84", "#86a46b", "#5d7a48", gy,
                              sun=(690, 120), clouds=((120, 80, 1.0), (470, 54, 0.8), (700, 200, 0.7)))
    o = [base]
    # snow-capped mountains behind the hills
    o.insert(1, poly([(-20, 330), (90, 240), (140, 262), (230, 170), (320, 262), (400, 226), (500, 300), (570, 232), (660, 292), (760, 214), (830, 300), (830, 380), (-20, 380)], "#9db6d2"))
    o.insert(2, poly([(230, 170), (190, 214), (214, 206), (230, 224), (250, 204), (272, 214)], "#fff"))
    o.insert(2, poly([(760, 214), (726, 252), (746, 246), (762, 262), (780, 244), (800, 252)], "#fff"))
    o.insert(2, poly([(90, 240), (66, 266), (84, 262), (96, 274), (110, 260)], "#fff"))
    o.append(hills(W, H, gy - 40, 20, "#9fbd84", 4.1))
    o.append(rect(0, gy - 6, W, H - gy + 6, "#86a46b"))
    o.append(rect(0, gy + 78, W, H - gy - 78, "#5d7a48"))
    # dirt road
    o.append(poly([(0, gy + 38), (W, gy + 26), (W, gy + 56), (0, gy + 72)], "#c9b08a"))
    # the rig
    x = 360
    o.append(rect(x - 130, gy - 58, 260, 58, INK2))
    o.append(path("M%s %sL%s %sM%s %sL%s %s" % (fmt(x - 120), fmt(gy - 4), fmt(x - 70), fmt(gy - 54), fmt(x - 70), fmt(gy - 4), fmt(x - 120), fmt(gy - 54)), "none", "#6b7280", 3))
    o.append(path("M%s %sL%s %sM%s %sL%s %s" % (fmt(x + 70), fmt(gy - 4), fmt(x + 120), fmt(gy - 54), fmt(x + 120), fmt(gy - 4), fmt(x + 70), fmt(gy - 54)), "none", "#6b7280", 3))
    o.append(rect(x - 140, gy - 66, 280, 9, INK))
    o.append(truss(x, gy - 66, 330, 72, 36, 9, 3.4))
    o.append(rect(x - 22, gy - 66 - 346, 44, 16, ACCENT))
    o.append(line(x - 6, gy - 66 - 332, x - 6, gy - 150, INK, 1.8))
    o.append(line(x + 6, gy - 66 - 332, x + 6, gy - 150, INK, 1.8))
    o.append(rect(x - 14, gy - 170, 28, 22, ACCENT))
    o.append(rect(x - 6, gy - 148, 12, 30, STEEL2, ' stroke="%s" stroke-width="2"' % INK))
    o.append(rect(x - 128, gy - 112, 54, 46, "#e6e9ee"))
    o.append(rect(x - 120, gy - 102, 20, 14, "#5b7288"))
    o.append(rect(x - 128, gy - 118, 54, 8, ACCENT))
    # pipe on the V-door ramp and stacks on the rack
    o.append(path("M%s %sL%s %s" % (fmt(x - 250), fmt(gy + 6), fmt(x - 128), fmt(gy - 70)), "none", INK, 12))
    o.append(path("M%s %sL%s %s" % (fmt(x - 250), fmt(gy + 6), fmt(x - 128), fmt(gy - 70)), "none", STEEL, 7))
    for r_, n_ in enumerate((5, 4, 3)):
        for k in range(n_):
            o.append(rect(30 + r_ * 8 + k * 0, gy + 6 - r_ * 13, 150 - r_ * 16, 11, STEEL, ' rx="5" stroke="%s" stroke-width="2.5"' % INK) if k == 0 else "")
    # mud tanks and a trailer
    o.append(rect(x + 150, gy - 40, 150, 40, "#6b7280", ' rx="3"'))
    o.append(rect(x + 150, gy - 44, 150, 6, INK2))
    o.append(path("M%s %sV%sM%s %sV%s" % (fmt(x + 200), fmt(gy - 40), fmt(gy), fmt(x + 250), fmt(gy - 40), fmt(gy)), "none", "#9ca3af", 3))
    o.append(rect(x + 306, gy - 34, 54, 34, "#e6e9ee"))
    o.append(rect(x + 314, gy - 26, 14, 12, "#5b7288"))
    o.append(rect(x + 306, gy - 38, 54, 6, ACCENT))
    o.append(palm(24, gy + 14, 170, 1))
    o.append(palm(770, gy + 16, 190, -1))
    # the crew
    o.append(person(300, gy + 66, 0.75, "#c68b59", "#ff7a1a"))
    o.append(person(338, gy + 68, 0.75, "#8a5a3b", "#ffb703", hat="#fff"))
    return svg("".join(o), defs)


def desk():
    """Independent work, 2017 to 2018: a desk with a laptop, and a derrick out of the window."""
    defs = grad("dawn", [(0, "#b9a8d6"), (0.55, "#f6c1c9"), (1, "#fbd9a0")]) + grad("wall", [(0, "#f6ead9"), (1, "#ecd9bf")]) + '<clipPath id="win"><rect x="418" y="66" width="308" height="258"/></clipPath>'
    o = ['<rect width="800" height="600" fill="url(#wall)"/>']
    # window
    o.append(rect(402, 50, 340, 290, "#f6f3ec"))
    o.append('<g clip-path="url(#win)">')
    o.append(rect(418, 66, 308, 258, "url(#dawn)"))
    o.append(circ(560, 262, 24, "#fff0cc"))
    o.append(hills(W, H, 300, 10, "#d3b0c0", 2.2))
    o.append(rect(418, 288, 308, 60, "#8f7284"))
    o.append(minirig(470, 290, 0.8).replace(INK2, "#5f4a5c").replace(INK, "#5f4a5c"))
    o.append(pumpjack(640, 292, 0.8, 1.0, False).replace(INK2, "#5f4a5c").replace(INK, "#5f4a5c"))
    o.append("</g>")
    o.append(rect(568, 66, 8, 258, "#f6f3ec"))
    o.append(rect(418, 192, 308, 8, "#f6f3ec"))
    o.append(rect(392, 324, 360, 14, "#e5dccb"))
    # desk
    o.append(rect(0, 420, 800, 22, "#b57b4c"))
    o.append(rect(0, 442, 800, 158, "#8c5f3b"))
    o.append(rect(0, 438, 800, 5, "#d09a6a"))
    # laptop
    o.append(poly([(86, 420), (404, 420), (430, 436), (60, 436)], "#aab2c0"))
    o.append(rect(110, 236, 270, 186, INK, ' rx="10"'))
    o.append(rect(124, 250, 242, 158, "#f2f6fa", ' rx="4"'))
    # chart on the screen: depth against time, two lines
    o.append(path("M140 266V396H350", "none", "#9aa3b2", 3))
    for gx in (186, 232, 278, 324):
        o.append(line(gx, 270, gx, 394, "#dde4ec", 2))
    for gy_ in (298, 330, 362):
        o.append(line(144, gy_, 352, gy_, "#dde4ec", 2))
    o.append(path("M144 276C190 290 230 330 262 346S320 380 348 388", "none", "#9aa3b2", 5, ' stroke-dasharray="2 9"'))
    o.append(path("M144 276C180 300 210 340 236 366S290 384 348 388", "none", ACCENT, 6))
    o.append(circ(236, 366, 8, "#fff", ' stroke="%s" stroke-width="5"' % ACCENT))
    # notebook, pen, hard hat, mug and plant
    o.append(poly([(450, 428), (574, 428), (590, 400), (466, 400)], "#fffdf8", ' stroke="#d8d1c2" stroke-width="2"'))
    for k in range(3):
        o.append(line(478 + k * 4, 412 - k * 0, 566 + k * 4 - 14, 412, "#cfd6e2", 2) if False else "")
    for yy in (408, 416, 424):
        o.append(line(470 + (428 - yy) * 0.7, yy, 560 + (428 - yy) * 0.7 - 12, yy, "#cfd6e2", 2))
    o.append(path("M520 392L580 350", "none", INK, 6))
    o.append(path("M520 392L514 400", "none", ACCENT, 6))
    o.append('<path d="M604 428A52 46 0 0 1 708 428Z" fill="#f5c518"/>')
    o.append(rect(596, 424, 120, 8, "#e0aa0c", ' rx="4"'))
    o.append(rect(646, 372, 14, 54, "#e0aa0c", ' opacity=".7"'))
    o.append(rect(726, 352, 46, 74, "#fff", ' rx="4"'))
    o.append(rect(726, 376, 46, 12, ACCENT))
    o.append(path("M772 366q20 0 20 18t-20 18", "none", "#fff", 7))
    o.append(path("M740 336q4 -14 0 -26M756 340q4 -14 0 -26", "none", "#fff", 4, ' opacity=".7"'))
    o.append(rect(30, 380, 52, 42, "#b45309", ' rx="4"'))
    o.append(path("M56 380V330M56 352c-18 0 -26 -10 -26 -26 18 0 26 10 26 26zM56 340c0 -16 10 -22 26 -22 0 16 -10 22 -26 22z", "none", "#2f6b4f", 5))
    o.append(path("M56 352c-18 0 -26 -10 -26 -26 18 0 26 10 26 26zM56 340c0 -16 10 -22 26 -22 0 16 -10 22 -26 22z", "#3f8f68", "#2f6b4f", 3))
    return svg("".join(o), defs)


def bits():
    """Schlumberger: drill bits and drilling tools."""
    defs = (grad("bg", [(0, "#dfe6fb"), (1, "#f4f6ff")]) + grad("floor", [(0, "#c5cbe0"), (1, "#aeb6d1")]) +
            grad("steel", [(0, "#8d97aa"), (0.5, "#c2c9d6"), (1, "#8d97aa")], 0, 0, 1, 0) +
            grad("steel2", [(0, "#5d6b86"), (0.5, "#8795b1"), (1, "#5d6b86")], 0, 0, 1, 0) +
            '<clipPath id="c1"><path d="M-30 0L30 0L20 150Q0 170 -20 150Z"/></clipPath>')
    o = ['<rect width="800" height="600" fill="url(#bg)"/>', rect(0, 470, W, 130, "url(#floor)")]
    # drill collars lying on a rack at the back, and a derrick on the wall of the picture
    for k, c in enumerate(("#9aa3b2", "#aab2c0", "#9aa3b2")):
        o.append(rect(70 + k * 6, 392 + k * 22 - 22, 660 - k * 12, 20, c, ' rx="10"'))
        o.append(rect(70 + k * 6, 392 + k * 22 - 22, 54, 20, "#7b8594", ' rx="8"'))
        o.append(rect(676 - k * 12, 392 + k * 22 - 22, 54, 20, "#7b8594", ' rx="8"'))
    o.append(rect(0, 468, W, 8, "#9aa3bd"))
    # a tricone bit: two cones tilted in and a third in front, so the bottom is rounded
    def cone(ang, cx, cy, ln=118):
        g = ['<g transform="translate(%s %s) rotate(%s)">' % (fmt(cx), fmt(cy), fmt(ang))]
        g.append('<path d="M-34 0L34 0L23 %d Q0 %d -23 %d Z" fill="url(#steel2)" stroke="%s" stroke-width="4" stroke-linejoin="round"/>' % (ln, ln + 22, ln, INK))
        g.append('<g clip-path="url(#c1)">')
        for yy in (30, 60, 90, 116):
            g.append('<path d="M-40 %d H40" stroke="#f4d28a" stroke-width="9" stroke-dasharray="0 14" stroke-linecap="round"/>' % yy)
        g.append("</g></g>")
        return "".join(g)
    tx = 260
    o.append(rect(tx - 56, 372, 112, 98, "#aab2c8"))
    o.append(rect(tx - 70, 462, 140, 10, "#8e97b6"))
    o.append(ell(tx, 470, 150, 16, "#8e97b6", ' opacity=".5"'))
    o.append(rect(tx - 34, 90, 68, 60, "url(#steel)", ' stroke="%s" stroke-width="4"' % INK))
    for yy in (104, 118, 132):
        o.append(line(tx - 34, yy, tx + 34, yy, INK, 3, ' opacity=".5"'))
    o.append(poly([(tx - 34, 150), (tx + 34, 150), (tx + 64, 196), (tx - 64, 196)], "url(#steel)", ' stroke="%s" stroke-width="4" stroke-linejoin="round"' % INK))
    o.append(cone(-22, tx - 64, 252))
    o.append(cone(22, tx + 64, 252))
    o.append(rect(tx - 84, 196, 168, 70, "url(#steel)", ' rx="12" stroke="%s" stroke-width="4"' % INK))
    o.append(cone(0, tx, 262, 128))
    o.append(rect(tx - 84, 196, 168, 12, "#e9eef4", ' rx="6" opacity=".5"'))
    o.append(rect(tx - 12, 214, 24, 8, ACCENT, ' rx="4"'))
    # a PDC bit: a domed body with blades, and rows of round cutters along each blade
    px = 570
    o.append(rect(px - 56, 372, 112, 98, "#aab2c8"))
    o.append(rect(px - 70, 462, 140, 10, "#8e97b6"))
    o.append(ell(px, 470, 130, 14, "#8e97b6", ' opacity=".5"'))
    o.append(rect(px - 34, 90, 68, 60, "url(#steel)", ' stroke="%s" stroke-width="4"' % INK))
    for yy in (104, 118, 132):
        o.append(line(px - 34, yy, px + 34, yy, INK, 3, ' opacity=".5"'))
    o.append(poly([(px - 34, 150), (px + 34, 150), (px + 64, 196), (px - 64, 196)], "url(#steel)", ' stroke="%s" stroke-width="4" stroke-linejoin="round"' % INK))
    o.append('<path d="M%d 196H%dV300Q%d 380 %d 392Q%d 380 %d 300Z" fill="url(#steel2)" stroke="%s" stroke-width="4" stroke-linejoin="round"/>' % (
        px - 84, px + 84, px + 84, px, px - 84, px - 84, INK))
    for k in range(5):
        bx = px - 66 + k * 33
        lim = 300 + 84 * math.sqrt(max(0.0, 1 - ((bx - px) / 84.0) ** 2)) - 10
        o.append(rect(bx - 11, 236, 22, lim - 236, "#7f8fb0", ' rx="10" stroke="%s" stroke-width="3"' % INK))
        yy = 262
        while yy < lim - 4:
            o.append(circ(bx, yy, 8, "#f4d28a", ' stroke="%s" stroke-width="2.5"' % INK))
            o.append(circ(bx, yy, 3, "#fff"))
            yy += 25
    for nx in (px - 50, px, px + 50):
        o.append(circ(nx, 218, 8, INK))
        o.append(circ(nx, 218, 3.5, "#6b7a99"))
    return svg("".join(o), defs)


def base():
    """Smith International: the service base, with its workshop, yard and pipe stacks."""
    gy = 470
    defs, b = ground_scene([(0, "#a9d3ee"), (0.7, "#dcecf7"), (1, "#f3f8fb")], "#c5d9b2", "#a9c48f", "#b8b3a6", "#8d897d", gy,
                           sun=(110, 110), clouds=((300, 70, 1.0), (620, 110, 0.9)))
    o = [b]
    o.append(rect(0, gy - 6, W, 90, "#c8c3b6"))
    # workshop
    o.append(rect(190, gy - 190, 380, 190, "#dfe3ea"))
    for xx in range(196, 568, 14):
        o.append(line(xx, gy - 186, xx, gy - 4, "#cfd5de", 2))
    o.append(poly([(176, gy - 190), (584, gy - 190), (566, gy - 222), (194, gy - 222)], "#6b7280"))
    o.append(rect(176, gy - 194, 408, 8, INK2))
    for dx in (214, 392):
        o.append(rect(dx, gy - 142, 150, 142, "#9aa4b4"))
        for yy in range(gy - 138, gy - 6, 14):
            o.append(line(dx + 4, yy, dx + 146, yy, "#7d8798", 3))
        o.append(rect(dx, gy - 142, 150, 6, INK2))
    o.append(rect(364 - 6, gy - 176, 56, 30, ACCENT))
    o.append('<g transform="translate(%d %d) scale(.5)" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">%s</g>' % (
        373, gy - 175, ICON_PATHS["derrick"].replace("{f}", "none")))
    # office container
    o.append(rect(606, gy - 76, 140, 76, "#6f86a8"))
    o.append(rect(606, gy - 80, 140, 8, INK2))
    o.append(rect(622, gy - 60, 40, 26, "#e7eef5"))
    o.append(rect(674, gy - 60, 56, 60, "#506583"))
    o.append(line(702, gy - 60, 702, gy, "#6f86a8", 3))
    # gantry crane
    o.append(path("M40 %d V%d H196 V%d" % (gy + 6, gy - 154, gy + 6), "none", ACCENT, 8))
    o.append(rect(30, gy - 160, 176, 10, INK2))
    o.append(line(118, gy - 150, 118, gy - 60, INK, 3))
    o.append(rect(106, gy - 60, 24, 16, ACCENT))
    o.append(rect(70, gy - 40, 100, 16, STEEL, ' rx="8" stroke="%s" stroke-width="2.5"' % INK))
    # pipe stack in front, seen end on
    cx0, cy0 = 612, gy + 64
    for r_ in range(4):
        for k in range(4 - r_):
            px_ = cx0 + 14 * r_ + k * 28
            py_ = cy0 - r_ * 25
            o.append(circ(px_, py_, 13, STEEL, ' stroke="%s" stroke-width="3"' % INK))
            o.append(circ(px_, py_, 7, "#7b8594"))
    # service truck
    tx, ty = 200, gy + 70
    o.append(rect(tx, ty - 58, 190, 40, "#f3f4f6", ' rx="3" stroke="%s" stroke-width="3"' % INK))
    o.append(rect(tx + 8, ty - 80, 160, 22, ACCENT, ' rx="2"'))
    o.append(rect(tx + 170, ty - 62, 78, 46, "#f3f4f6", ' stroke="%s" stroke-width="3"' % INK))
    o.append(poly([(tx + 170, ty - 62), (tx + 214, ty - 62), (tx + 248, ty - 36), (tx + 248, ty - 16), (tx + 170, ty - 16)], "#f3f4f6", ' stroke="%s" stroke-width="3" stroke-linejoin="round"' % INK))
    o.append(poly([(tx + 182, ty - 54), (tx + 212, ty - 54), (tx + 236, ty - 36), (tx + 182, ty - 36)], "#5b7288"))
    for wx_ in (tx + 38, tx + 118, tx + 204):
        o.append(circ(wx_, ty - 10, 20, INK))
        o.append(circ(wx_, ty - 10, 9, "#9ca3af"))
    for k in range(5):
        o.append(rect(tx + 14, ty - 74 - k * 0, 0, 0, "none"))
    o.append(rect(tx + 14, ty - 76, 150, 12, STEEL, ' rx="6" stroke="%s" stroke-width="2.5"' % INK))
    o.append(palm(790, gy + 14, 150, -1))
    return svg("".join(o), defs)


def directional():
    """Baker Hughes: directional wells from several rigs, each reaching its target in the pay zone."""
    defs = grad("sky", [(0, "#a9d3ee"), (1, "#e9f4fa")])
    top = 130
    o = ['<rect width="800" height="%d" fill="url(#sky)"/>' % top, cloud(180, 50, 0.8), cloud(600, 38, 0.7)]
    o.append(hills(W, H, top - 4, 10, "#bfd8b0", 2.2))
    o.append(strata([(top, 5, "#e6d1a6", "#c7aa78"), (230, 8, "#d3b283", "#a98a5c"), (330, 8, "#bd9467", "#8f6d49"),
                     (470, 8, "#a27a56", "#74553a"), (540, 6, "#866549", "#5e4630")], seed=11))
    # the pay zone
    o.append(path("M-20 392C140 372 300 360 450 366C600 372 720 392 820 404L820 454C700 436 580 426 440 428C300 430 140 442 -20 456Z", "#f2b24c"))
    o.append(path("M-20 392C140 372 300 360 450 366C600 372 720 392 820 404", "none", "#fbd48a", 4))
    rnd = random.Random(4)
    for _ in range(70):
        gx = rnd.uniform(10, 790)
        gy_ = 398 + 24 * math.sin(gx * 0.006) + rnd.uniform(-8, 14)
        o.append(circ(gx, gy_, rnd.uniform(1.6, 3), "#b9741a", ' opacity=".55"'))
    o.append(rect(0, top - 8, W, 14, "#7ea263"))
    wells = [(120, 380, 392, 292, 160, 244), (300, 440, 416, 330, 300, 270), (540, 700, 408, 276, 200, 230)]
    # each well: (x at the surface, x at the target, y of the target, y where it leaves the vertical)
    sets = [(120, 360, 392, 190), (300, 560, 408, 220), (500, 740, 420, 250)]
    for x0, xt, yt, yk in sets:
        d = "M%d %dL%d %dC%d %d %d %d %d %dL%d %d" % (x0, top, x0, yk, x0, yk + 110, xt - 120, yt, xt, yt, xt + 30, yt)
        o.append(path(d, "none", "#fff", 11))
        o.append(path(d, "none", INK, 5))
        o.append(circ(xt + 30, yt, 13, "#fff", ' stroke="%s" stroke-width="4"' % ACCENT))
        o.append(circ(xt + 30, yt, 5, ACCENT))
        o.append(minirig(x0, top + 2, 0.9))
    return svg("".join(o), defs)


def maracaibo():
    """PDVSA: Lake Maracaibo at dusk, with wells standing in the water and a workover barge."""
    defs = (grad("sky", [(0, "#a8cbe9"), (0.6, "#f9d9b0"), (1, "#f6a768")]) + grad("lake", [(0, "#f2b98c"), (0.45, "#a9a6b8"), (1, "#566b8f")]) +
            '<radialGradient id="sun"><stop offset="0" stop-color="#fff2cf" stop-opacity=".95"/><stop offset=".35" stop-color="#fff2cf" stop-opacity=".55"/><stop offset="1" stop-color="#fff2cf" stop-opacity="0"/></radialGradient>')
    hy = 318
    o = ['<rect width="800" height="%d" fill="url(#sky)"/>' % hy]
    o.append(circ(430, hy - 8, 200, "url(#sun)"))
    o.append(circ(430, hy - 8, 40, "#fff2cf"))
    o += [cloud(120, 80, 1.2), cloud(560, 58, 1.0), cloud(720, 150, 1.1)]
    o.append(hills(W, H, hy + 2, 8, "#d49a78", 3.3).replace("L820 600", "L820 %d" % (hy + 20)).replace("L-25 600Z", "L-25 %d Z" % (hy + 20)))
    o.append(rect(0, hy, W, H - hy, "url(#lake)"))
    for i, w in enumerate((90, 70, 54, 40, 28, 18)):
        o.append(ell(430, hy + 12 + i * 18, w, 3, "#fff2cf", ' opacity=".5"'))
    rnd = random.Random(7)
    for _ in range(40):
        wx_, wy_ = rnd.uniform(0, W), rnd.uniform(hy + 16, H - 8)
        o.append(line(wx_, wy_, wx_ + rnd.uniform(14, 34), wy_, "#e9d6c6", 2.2, ' opacity=".45"'))
    # wells in the lake, far to near. Each one: a platform on legs, a mast or a pumpjack, and its reflection.
    items = [(70, 346, 0.5, "d"), (210, 350, 0.55, "p"), (330, 345, 0.45, "d"), (560, 348, 0.5, "d"), (700, 352, 0.6, "p"),
             (150, 392, 0.8, "d"), (420, 398, 0.85, "p"), (640, 404, 0.8, "d")]
    for x, y, s, kind in items:
        o.append(_lake_well(x, y, s, kind, True))
    for x, y, s, kind in items:
        o.append(_lake_well(x, y, s, kind, False))
    # the workover barge in front
    bx, by = 262, 520
    o.append(ell(bx, by + 20, 190, 9, "#e9d6c6", ' opacity=".5"'))
    o.append(poly([(bx - 170, by - 18), (bx + 170, by - 18), (bx + 150, by + 18), (bx - 150, by + 18)], "#3b3e46"))
    o.append(rect(bx - 170, by - 22, 340, 7, ACCENT))
    o.append(truss(bx - 20, by - 22, 230, 52, 20, 7, 3.2))
    o.append(rect(bx - 32, by - 252, 24, 12, ACCENT))
    o.append(rect(bx + 70, by - 70, 70, 48, "#eef1f5"))
    o.append(rect(bx + 80, by - 58, 16, 14, "#5b7288"))
    o.append(rect(bx + 70, by - 78, 70, 8, ACCENT))
    o.append(rect(bx - 150, by - 40, 90, 18, "#6b7280"))
    o.append(palm(770, 470, 150, -1))
    return svg("".join(o), defs)


def _lake_well(x, y, s, kind, reflection):
    g = []
    if reflection:
        g.append('<g transform="translate(0 %s) scale(1 -1)" opacity=".28">' % fmt(2 * y + 6))
    for lx in (-34, 34):
        g.append(rect(x + lx * s - 3 * s, y - 2, 6 * s, 30 * s, INK2))
    g.append(rect(x - 44 * s, y - 8 * s, 88 * s, 9 * s, INK))
    if kind == "d":
        g.append(truss(x, y - 8 * s, 130 * s, 40 * s, 12 * s, 5, max(1.4, 2.6 * s)))
        g.append(rect(x - 8 * s, y - 146 * s, 16 * s, 8 * s, ACCENT))
    else:
        g.append(pumpjack(x, y - 8 * s, 1.0 * s * 1.1, 1.0 + x * 0.01, False))
    if reflection:
        g.append("</g>")
    return "".join(g)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def workover():
    """Drilling, fishing and remedial operations: a workover rig on a well pad."""
    gy = 470
    defs, b = ground_scene([(0, "#7fb8e6"), (0.7, "#cfe6f6"), (1, "#eaf5fb")], "#bcd3a5", "#9fbd84", "#86a46b", "#5d7a48", gy,
                           sun=(120, 110), clouds=((330, 80, 1.1), (640, 120, 0.9)))
    o = [b]
    o.append(pumpjack(80, gy - 18, 1.3, 2.2, False, 0.6))
    # guy lines first, so they pass behind the mast
    mx, my = 468, gy - 36
    ang = math.radians(7)
    tipx, tipy = mx + math.sin(ang) * 330, my - math.cos(ang) * 330
    for ax, ay in ((690, gy + 36), (610, gy + 62), (250, gy + 80)):
        o.append(line(tipx, tipy + 8, ax, ay, INK, 1.6, ' opacity=".7"'))
    # truck
    ty = gy + 52
    o.append(rect(160, ty - 86, 310, 24, "#6b7280", ' rx="3"'))
    o.append(rect(150, ty - 62, 330, 36, INK2, ' rx="4"'))
    o.append(rect(150, ty - 66, 330, 6, ACCENT))
    o.append(poly([(150, ty - 62), (150, ty - 112), (222, ty - 112), (256, ty - 80), (262, ty - 62)], "#f3f4f6", ' stroke="%s" stroke-width="3" stroke-linejoin="round"' % INK))
    o.append(poly([(162, ty - 104), (214, ty - 104), (238, ty - 82), (162, ty - 82)], "#5b7288"))
    for wx_ in (206, 340, 420):
        o.append(circ(wx_, ty - 24, 26, INK))
        o.append(circ(wx_, ty - 24, 11, "#9ca3af"))
    o.append(rect(282, ty - 112, 8, 26, "#6b7280"))
    # mast, tilted a little toward the well
    o.append('<g transform="rotate(7 %d %d)">' % (mx, my))
    o.append(truss(mx, my, 330, 38, 22, 9, 3))
    o.append(rect(mx - 15, my - 344, 30, 14, ACCENT))
    o.append(line(mx - 5, my - 330, mx - 5, my - 110, INK, 1.8))
    o.append(line(mx + 5, my - 330, mx + 5, my - 110, INK, 1.8))
    o.append(rect(mx - 11, my - 124, 22, 20, ACCENT))
    o.append(rect(mx - 5, my - 104, 10, 22, STEEL2, ' stroke="%s" stroke-width="2"' % INK))
    o.append("</g>")
    o.append(line(mx - 50, my + 6, mx - 4, my - 120, INK2, 5))
    # wellhead and flow line to a tank
    wx = 568
    o.append(rect(wx - 22, gy - 12, 44, 14, "#6b7280"))
    o.append(rect(wx - 11, gy - 52, 22, 42, STEEL, ' stroke="%s" stroke-width="2.5"' % INK))
    o.append(rect(wx - 16, gy - 36, 32, 8, "#6b7280"))
    o.append(rect(wx + 11, gy - 34, 46, 12, STEEL, ' stroke="%s" stroke-width="2.5"' % INK))
    o.append(circ(wx + 34, gy - 44, 8, ACCENT, ' stroke="%s" stroke-width="2.5"' % INK))
    o.append(circ(wx, gy - 62, 10, "#fff", ' stroke="%s" stroke-width="3"' % INK))
    o.append(line(wx, gy - 62, wx + 5, gy - 67, ACCENT, 2.5))
    o.append(path("M%d %dH%dV%d" % (wx + 57, gy - 28, 640, gy - 8), "none", INK2, 6))
    o.append(tank(640, gy + 8, 56, 84))
    o.append(tank(712, gy + 8, 56, 84))
    o.append(person(520, gy + 62, 0.78, "#c68b59", "#ff7a1a"))
    o.append(person(556, gy + 66, 0.78, "#8a5a3b", "#ffb703", hat="#fff"))
    o.append(palm(30, gy + 20, 170, 1))
    return svg("".join(o), defs)


def timedepth():
    """Drilling optimization: depth against days, with the optimized well finishing earlier."""
    defs = ""
    o = [rect(0, 0, W, H, "#def2ef"), rect(60, 52, 680, 500, "#fff", ' rx="6"')]
    o.append(rect(60, 52, 680, 16, "#c9e6e1", ' rx="6"'))
    # grid and axes
    for gx in range(190, 700, 80):
        o.append(line(gx, 104, gx, 456, "#e4ecf2", 2))
    for gy_ in range(144, 456, 64):
        o.append(line(130, gy_, 706, gy_, "#e4ecf2", 2))
    o.append(path("M130 100V456H710", "none", "#9aa3b2", 4))
    # the plan: dashed, with flat steps where the work stops
    plan = "M130 104L214 176H250L346 268H386L498 360H540L670 440"
    o.append(path(plan, "none", "#9aa3b2", 6, ' stroke-dasharray="2 12"'))
    best = "M130 104L196 180H212L300 268H316L404 354L526 440"
    o.append(path(best, "none", ICONS["gauge"][0], 8))
    o.append(circ(526, 440, 11, "#fff", ' stroke="%s" stroke-width="6"' % ICONS["gauge"][0]))
    o.append(circ(670, 440, 9, "#fff", ' stroke="#9aa3b2" stroke-width="5"'))
    # the time saved
    o.append(path("M530 490H666M534 478V502M662 478V502", "none", "#2e7d32", 6))
    o.append(path("M534 490l14 -10M534 490l14 10M662 490l-14 -10M662 490l-14 10", "none", "#2e7d32", 5))
    # a rig at the start
    o.append('<g transform="translate(76 84) scale(1.2)" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">%s</g>' % (
        ACCENT, ICON_PATHS["derrick"].replace("{f}", "#c2410c2e")))
    return svg("".join(o), defs)


def tender():
    """Tenders and contracts: papers, a signature and a seal."""
    defs = ""
    o = [rect(0, 0, W, H, "#e0e7fe")]
    o.append('<g transform="rotate(-7 320 285)">' + rect(160, 70, 300, 430, "#f4f6ff", ' stroke="#c5cbe8" stroke-width="3"') +
             "".join(rect(190, 120 + k * 36, 240 - (k % 3) * 40, 10, "#c5cbe8", ' rx="5"') for k in range(8)) + "</g>")
    o.append('<g transform="rotate(4 435 320)">')
    o.append(rect(292, 110, 310, 440, "#aeb7e6", ' opacity=".55"'))
    o.append(rect(280, 98, 310, 440, "#fff", ' stroke="#c5cbe8" stroke-width="3"'))
    o.append(rect(280, 98, 310, 64, "#3949ab"))
    o.append('<g transform="translate(298 106) scale(.95)" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">%s</g>' % ICON_PATHS["derrick"].replace("{f}", "none"))
    o.append(rect(358, 118, 150, 12, "#fff", ' rx="6"'))
    o.append(rect(358, 140, 100, 8, "#c5cbe8", ' rx="4"'))
    for k in range(4):
        o.append(rect(306, 188 + k * 26, 258 - (k % 2) * 60, 9, "#c5cbe8", ' rx="4.5"'))
    # a small table
    for r in range(4):
        o.append(rect(306, 306 + r * 30, 258, 26, "#eef0fb" if r % 2 == 0 else "#fff", ' stroke="#c5cbe8" stroke-width="2"'))
        o.append(rect(316, 315 + r * 30, 70, 8, "#9aa5dd", ' rx="4"'))
        o.append(rect(486, 315 + r * 30, 60, 8, "#c5cbe8", ' rx="4"'))
    # the signature
    o.append(line(306, 484, 450, 484, "#9aa5dd", 3))
    o.append(path("M312 470C322 440 336 440 338 462S350 484 360 462 372 440 384 470 398 470 420 454", "none", INK, 4))
    # the seal
    sx, sy = 520, 484
    o.append(poly([(sx - 22, sy + 14), (sx - 4, sy + 14), (sx - 26, sy + 62), (sx - 40, sy + 48)], "#a8360a"))
    o.append(poly([(sx + 22, sy + 14), (sx + 4, sy + 14), (sx + 26, sy + 62), (sx + 40, sy + 48)], "#a8360a"))
    for k in range(16):
        a = k * math.pi * 2 / 16
        o.append(circ(sx + 36 * math.cos(a), sy + 36 * math.sin(a), 9, ACCENT))
    o.append(circ(sx, sy, 38, ACCENT))
    o.append(circ(sx, sy, 28, "#d9531a", ' stroke="#fff" stroke-width="3"'))
    o.append(path("M%d %dl10 11 20 -22" % (sx - 15, sy), "none", "#fff", 7))
    o.append("</g>")
    # the pen
    o.append('<g transform="translate(646 328) rotate(40)">' + rect(-9, -150, 18, 150, "#3949ab", ' rx="9"') +
             rect(-9, -150, 18, 30, "#c5cbe8", ' rx="9"') + poly([(-9, 0), (9, 0), (0, 26)], "#f3f4f6") + poly([(-3, 18), (3, 18), (0, 26)], INK) + "</g>")
    return svg("".join(o), defs)


def assess():
    """Business and technology assessments: dials, bars and a magnifier."""
    defs = ""
    o = [rect(0, 0, W, H, "#f9e2ea"), rect(70, 70, 660, 470, "#fff", ' rx="6"'), rect(70, 70, 660, 16, "#f0c4d4", ' rx="6"')]

    def gauge(cx, cy, r, needle):
        g = []
        for i, col in enumerate(("#2e7d32", "#f2b24c", "#c2410c")):
            a0 = math.pi + i * math.pi / 3
            a1 = a0 + math.pi / 3 - 0.03
            g.append(path("M%s %sA%d %d 0 0 1 %s %s" % (fmt(cx + r * math.cos(a0)), fmt(cy + r * math.sin(a0)), r, r,
                                                      fmt(cx + r * math.cos(a1)), fmt(cy + r * math.sin(a1))), "none", col, 22))
        na = math.pi + needle * math.pi
        g.append(path("M%s %sL%s %s" % (fmt(cx), fmt(cy), fmt(cx + (r - 14) * math.cos(na)), fmt(cy + (r - 14) * math.sin(na))), "none", INK, 7))
        g.append(circ(cx, cy, 11, INK))
        g.append(circ(cx, cy, 4, "#fff"))
        return "".join(g)
    o.append(gauge(190, 230, 80, 0.22))
    o.append(gauge(380, 230, 80, 0.62))
    # bars
    base = 300
    for k, h in enumerate((60, 90, 70, 130, 110)):
        o.append(rect(480 + k * 46, base - h, 32, h, "#be185d" if k == 3 else "#e9a9c3"))
    o.append(line(466, base, 716, base, "#9aa3b2", 4))
    # rows
    for k, (col, wd) in enumerate((("#2e7d32", 300), ("#f2b24c", 220), ("#c2410c", 150))):
        yy = 356 + k * 54
        o.append(circ(114, yy + 12, 12, col))
        o.append(rect(146, yy, 300 + 40 * (k == 0), 24, "#eef0f5", ' rx="12"'))
        o.append(rect(146, yy, wd, 24, col, ' rx="12" opacity=".85"'))
        o.append(rect(480, yy + 4, 190 - k * 36, 16, "#e4e7ee", ' rx="8"'))
    # magnifier over the bars
    o.append(circ(600, 232, 84, "#fff", ' opacity=".35"'))
    o.append(circ(600, 232, 84, "none", ' stroke="#be185d" stroke-width="14"'))
    o.append(path("M660 292L730 362", "none", "#be185d", 22))
    o.append(path("M660 292L730 362", "none", "#f9e2ea", 4, ' opacity=".5"'))
    return svg("".join(o), defs)


def profit():
    """Operations and profitability: bars that keep rising, and the rigs behind them."""
    defs = grad("g", [(0, "#e8f5ea"), (1, "#cfe6d3")])
    o = [rect(0, 0, W, H, "url(#g)"), rect(0, 480, W, 120, "#a9cdb0")]
    for k, h in enumerate((70, 104, 146, 196, 254, 326)):
        shade = ("#b9dcc0", "#9ccfa7", "#7fc08e", "#5aa86f", "#3f9157", "#2e7d32")[k]
        o.append(rect(200 + k * 94, 480 - h, 68, h, shade))
        o.append(rect(200 + k * 94, 480 - h, 68, 8, "#fff", ' opacity=".35"'))
    pts = [(234 + k * 94, 440 - h * 0.95) for k, h in enumerate((70, 104, 146, 196, 254, 326))]
    o.append(path("M" + "L".join("%s %s" % (fmt(a), fmt(b)) for a, b in pts), "none", INK, 7))
    for a, b in pts[:-1]:
        o.append(circ(a, b, 10, "#fff", ' stroke="%s" stroke-width="6"' % INK))
    ex, ey = pts[-1]
    o.append(poly([(ex + 22, ey - 22), (ex - 14, ey - 18), (ex + 4, ey + 4)], INK))
    o.append(circ(ex - 2, ey - 2, 10, "#fff", ' stroke="%s" stroke-width="6"' % INK))
    o.append(pumpjack(96, 480, 1.35, 1.3, False))
    o.append(minirig(118, 480, 0.0001) if False else "")
    # coins at the foot of the bars
    for k in range(3):
        o.append(ell(98, 566 - k * 14, 36, 10, "#f2b24c", ' stroke="%s" stroke-width="3"' % INK))
        o.append(rect(62, 552 - k * 14, 72, 14, "#f2b24c"))
        o.append(ell(98, 552 - k * 14, 36, 10, "#fbd48a", ' stroke="%s" stroke-width="3"' % INK))
    return svg("".join(o), defs)


def _bust(x, y, s, skin, vest, hat):
    g = ['<g transform="translate(%s %s) scale(%s)">' % (fmt(x), fmt(y), fmt(s))]
    g.append(path("M-82 0Q-82 -72 -32 -82L32 -82Q82 -72 82 0Z", vest))
    g.append(poly([(-20, -82), (20, -82), (0, -44)], "#e8edf3"))
    g.append(rect(-80, -34, 160, 10, "#f3f4f6", ' opacity=".95"'))
    g.append(rect(-13, -102, 26, 24, skin))
    g.append(circ(-41, -132, 8, skin))
    g.append(circ(41, -132, 8, skin))
    g.append(circ(0, -132, 40, skin))
    g.append(circ(-14, -130, 4, INK))
    g.append(circ(14, -130, 4, INK))
    g.append(path("M-12 -114Q0 -104 12 -114", "none", INK, 3.5))
    g.append('<path d="M-46 -140A46 46 0 0 1 46 -140Z" fill="%s"/>' % hat)
    g.append(rect(-56, -144, 112, 10, hat, ' rx="5"'))
    g.append(rect(-5, -186, 10, 40, hat, ' opacity=".85"'))
    g.append("</g>")
    return "".join(g)


def team():
    """Teams and local talent: a crew in hard hats in front of a rig."""
    defs = grad("g", [(0, "#fdf1df"), (1, "#f8dcc0")])
    o = [rect(0, 0, W, H, "url(#g)"), rect(0, 470, W, 130, "#e8c9a3")]
    o.append(truss(560, 470, 400, 160, 44, 9, 5, "#efc39c"))
    o.append(rect(540, 56, 40, 18, "#efc39c"))
    o.append(rect(380, 440, 360, 30, "#efc39c"))
    o.append(circ(130, 110, 56, "#fff3cf", ' opacity=".9"'))
    o.append(_bust(160, 580, 1.0, "#8a5a3b", "#ffb703", "#ffffff"))
    o.append(_bust(650, 580, 1.0, "#c68b59", "#ff7a1a", "#f5c518"))
    o.append(_bust(470, 600, 1.12, "#e0ac82", "#ff7a1a", "#ffffff"))
    o.append(_bust(320, 600, 1.2, "#a8703f", "#ffb703", "#f5c518"))
    # a tablet in the hands of the one in front
    o.append('<g transform="translate(398 520) rotate(-10)">' + rect(-52, -34, 104, 70, INK, ' rx="8"') +
             rect(-44, -26, 88, 54, "#f2f6fa", ' rx="3"') + path("M-34 14L-16 -4 0 6 16 -14 34 -2", "none", ACCENT, 5) + "</g>")
    return svg("".join(o), defs)


CARDS = {
    # jobs
    "job-roku": fishing, "job-wis": platform, "job-nabors": landrig, "job-own": desk,
    "job-slb": bits, "job-smith": base, "job-bh": directional, "job-pdvsa": maracaibo,
    # services
    "svc-drilling": workover, "svc-optimize": timedepth, "svc-tender": tender,
    "svc-assess": assess, "svc-profit": profit, "svc-team": team,
}
