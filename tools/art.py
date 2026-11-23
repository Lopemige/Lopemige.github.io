#!/usr/bin/env python3
"""
Draws every picture on the site, so nothing depends on a stock photo or a licence.

  python3 tools/art.py [FOLDER_WITH_THE_NATURAL_EARTH_GEOJSON_FILES]

It writes:
  assets/scenes/*.svg        oil-field scenes used as the wide picture at the top of each page
  assets/about/profile-badge.svg   the round picture on the About page (swap it for a photo later)
  assets/about/americas-map.svg    the map of the countries where he has worked (needs the folder above)
  assets/icons/*.svg         the small icons on the tiles

build.py imports ICONS from this file, so the tile colours stay in one place.

Map data: Natural Earth (public domain, https://www.naturalearthdata.com), ne_50m_admin_0_countries.
To change the countries or pins on the map, edit WORKED and PINS below.
"""
import math
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK = "#2a2d34"
INK2 = "#3b3e46"
ACCENT = "#c2410c"

# icon name -> (line colour, tile colour). The tile colour is the pastel behind the icon on the page.
ICONS = {
    "derrick": ("#c2410c", "#ffe9dc"),
    "gauge": ("#0f766e", "#def2ef"),
    "contract": ("#3949ab", "#e0e7fe"),
    "magnifier": ("#be185d", "#f9e2ea"),
    "trend": ("#2e7d32", "#e2f1e5"),
    "sprout": ("#b45309", "#fdefdb"),
    "shield": ("#0f766e", "#def2ef"),
    "badge": ("#3949ab", "#e0e7fe"),
    "cycle": ("#c2410c", "#ffe9dc"),
    "people": ("#be185d", "#f9e2ea"),
    "cap": ("#3949ab", "#e0e7fe"),
    "speech": ("#0f766e", "#def2ef"),
    "clock": ("#b45309", "#fdefdb"),
    "pin": ("#c2410c", "#ffe9dc"),
}


def fmt(n):
    s = "%.1f" % n
    return s[:-2] if s.endswith(".0") else s


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# Pieces of a scene. Every piece is drawn on a ground line y, at x, in SVG units.
# ---------------------------------------------------------------------------

def hills(W, H, base, amp, color, seed, step=25):
    pts = []
    x = -step
    while x <= W + step:
        y = base - amp * (0.55 * math.sin(x * 0.0021 + seed) + 0.3 * math.sin(x * 0.0057 + seed * 2.1)
                          + 0.15 * math.sin(x * 0.013 + seed * 3.7))
        pts.append("%s %s" % (fmt(x), fmt(y)))
        x += step
    return '<path fill="%s" d="M%s L%d %d L%d %d Z"/>' % (color, " L".join(pts), W + step, H, -step, H)


def pumpjack(x, y, s, phase, flip=False, opacity=1.0):
    """A nodding pumpjack. phase picks where in the nod it is caught."""
    a = 0.11 * math.sin(phase)
    c, sn = math.cos(a), math.sin(a)
    px, py = 0.0, -62.0

    def rot(lx, ly):
        return px + lx * c - ly * sn, py + lx * sn + ly * c

    tail = rot(-38, 0)
    ang = math.radians(24)
    tip = rot(49 * math.cos(ang), 49 * math.sin(ang))
    th = phase + 0.5
    cx, cy, cr = -37.0, -24.0, 15.0
    pin = (cx + 9 * math.cos(th), cy + 9 * math.sin(th))
    cw0 = th + math.pi - 0.95
    cw1 = th + math.pi + 0.95
    cwa = (cx + cr * math.cos(cw0), cy + cr * math.sin(cw0))
    cwb = (cx + cr * math.cos(cw1), cy + cr * math.sin(cw1))
    o_a = (54 * math.cos(-ang), 54 * math.sin(-ang))
    o_b = (54 * math.cos(ang), 54 * math.sin(ang))
    i_a = (44 * math.cos(-ang), 44 * math.sin(-ang))
    i_b = (44 * math.cos(ang), 44 * math.sin(ang))
    g = []
    g.append('<rect x="-56" y="-5" width="108" height="5" fill="%s"/>' % INK)
    g.append('<rect x="-50" y="-16" width="26" height="16" fill="%s"/>' % INK2)
    g.append('<path d="M-17 -6L0 -62L17 -6M-10.9 -26H10.9M-5.5 -44H5.5" fill="none" stroke="%s" stroke-width="4" stroke-linejoin="round"/>' % INK)
    g.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fmt(cx), fmt(cy), fmt(cr), INK))
    g.append('<path d="M%s %sL%s %sA%s %s 0 0 1 %s %sZ" fill="%s"/>' % (
        fmt(cx), fmt(cy), fmt(cwa[0]), fmt(cwa[1]), fmt(cr), fmt(cr), fmt(cwb[0]), fmt(cwb[1]), ACCENT))
    g.append('<path d="M%s %sL%s %s" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (
        fmt(tail[0]), fmt(tail[1]), fmt(pin[0]), fmt(pin[1]), INK))
    g.append('<g transform="translate(0 -62) rotate(%s)"><rect x="-38" y="-3.5" width="86" height="7" rx="2" fill="%s"/>'
             '<path d="M%s %sA54 54 0 0 1 %s %sL%s %sA44 44 0 0 0 %s %sZ" fill="%s"/></g>' % (
                 fmt(math.degrees(a)), INK, fmt(o_a[0]), fmt(o_a[1]), fmt(o_b[0]), fmt(o_b[1]),
                 fmt(i_b[0]), fmt(i_b[1]), fmt(i_a[0]), fmt(i_a[1]), INK))
    g.append('<circle cx="0" cy="-62" r="5" fill="%s"/>' % ACCENT)
    g.append('<path d="M%s %sL%s -10" stroke="%s" stroke-width="1.8"/>' % (fmt(tip[0]), fmt(tip[1]), fmt(tip[0]), INK))
    g.append('<rect x="%s" y="-12" width="7" height="12" fill="%s"/>' % (fmt(tip[0] - 3.5), INK))
    sx = -s if flip else s
    op = ' opacity="%s"' % opacity if opacity < 1 else ""
    return '<g transform="translate(%s %s) scale(%s %s)"%s>%s</g>' % (fmt(x), fmt(y), fmt(sx), fmt(s), op, "".join(g))


def flare(x, y, h, s=1.0):
    w = 7 * s
    fy = y - h
    g = []
    g.append('<circle cx="%s" cy="%s" r="%s" fill="url(#glow)"/>' % (fmt(x), fmt(fy - 26 * s), fmt(110 * s)))
    g.append('<path d="M%s %sL%s %sM%s %sL%s %s" stroke="%s" stroke-width="1.6" opacity=".7"/>' % (
        fmt(x), fmt(y - h * 0.62), fmt(x - 90 * s), fmt(y), fmt(x), fmt(y - h * 0.62), fmt(x + 90 * s), fmt(y), INK))
    g.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (fmt(x - w / 2), fmt(fy), fmt(w), fmt(h), INK))
    g.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (fmt(x - 11 * s), fmt(y - h * 0.62), fmt(22 * s), fmt(4 * s), INK))
    g.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (fmt(x - 14 * s), fmt(fy - 3 * s), fmt(28 * s), fmt(5 * s), INK))
    g.append('<path d="M%s %sC%s %s %s %s %s %sC%s %s %s %s %s %sZ" fill="#f97316"/>' % (
        fmt(x - 10 * s), fmt(fy - 3 * s), fmt(x - 18 * s), fmt(fy - 30 * s), fmt(x - 2 * s), fmt(fy - 46 * s), fmt(x + 3 * s), fmt(fy - 74 * s),
        fmt(x + 10 * s), fmt(fy - 48 * s), fmt(x + 19 * s), fmt(fy - 30 * s), fmt(x + 10 * s), fmt(fy - 3 * s)))
    g.append('<path d="M%s %sC%s %s %s %s %s %sC%s %s %s %s %s %sZ" fill="#fde047"/>' % (
        fmt(x - 5 * s), fmt(fy - 3 * s), fmt(x - 9 * s), fmt(fy - 18 * s), fmt(x - 1 * s), fmt(fy - 28 * s), fmt(x + 1 * s), fmt(fy - 42 * s),
        fmt(x + 5 * s), fmt(fy - 28 * s), fmt(x + 9 * s), fmt(fy - 18 * s), fmt(x + 5 * s), fmt(fy - 3 * s)))
    return "".join(g)


def derrick(x, y, h, s=1.0, opacity=1.0):
    bw, tw, n = 80 * s, 18 * s, 8
    lv = []
    for i in range(n + 1):
        half = (bw - (bw - tw) * i / n) / 2
        lv.append((y - h * i / n, half))
    d = ["M%s %sL%s %sM%s %sL%s %s" % (fmt(x - lv[0][1]), fmt(y), fmt(x - lv[-1][1]), fmt(lv[-1][0]),
                                          fmt(x + lv[0][1]), fmt(y), fmt(x + lv[-1][1]), fmt(lv[-1][0]))]
    for i, (ly, half) in enumerate(lv):
        d.append("M%s %sL%s %s" % (fmt(x - half), fmt(ly), fmt(x + half), fmt(ly)))
    for i in range(n):
        (y0, h0), (y1, h1) = lv[i], lv[i + 1]
        if i % 2 == 0:
            d.append("M%s %sL%s %s" % (fmt(x - h0), fmt(y0), fmt(x + h1), fmt(y1)))
        else:
            d.append("M%s %sL%s %s" % (fmt(x + h0), fmt(y0), fmt(x - h1), fmt(y1)))
    top = y - h
    g = []
    g.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (fmt(x - 64 * s), fmt(y - 34 * s), fmt(128 * s), fmt(34 * s), INK2))
    g.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (fmt(x - 70 * s), fmt(y - 38 * s), fmt(140 * s), fmt(6 * s), INK))
    g.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % ("".join(d), INK, fmt(max(2.2, 3.2 * s))))
    g.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (fmt(x - 17 * s), fmt(top - 14 * s), fmt(34 * s), fmt(14 * s), ACCENT))
    g.append('<path d="M%s %sL%s %sM%s %sL%s %s" stroke="%s" stroke-width="2"/>' % (
        fmt(x - 5 * s), fmt(top), fmt(x - 5 * s), fmt(y - h * 0.42), fmt(x + 5 * s), fmt(top), fmt(x + 5 * s), fmt(y - h * 0.42), INK))
    g.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (fmt(x - 9 * s), fmt(y - h * 0.42), fmt(18 * s), fmt(16 * s), ACCENT))
    # mud tanks and pipe rack on the ground beside the rig
    g.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="#6b7280"/>' % (fmt(x + 84 * s), fmt(y - 30 * s), fmt(110 * s), fmt(30 * s), fmt(3 * s)))
    g.append('<path d="M%s %sV%sM%s %sV%s" stroke="#9ca3af" stroke-width="%s"/>' % (
        fmt(x + 121 * s), fmt(y - 30 * s), fmt(y), fmt(x + 158 * s), fmt(y - 30 * s), fmt(y), fmt(2.5 * s)))
    g.append('<path d="M%s %sH%sM%s %sH%sM%s %sH%s" stroke="%s" stroke-width="%s"/>' % (
        fmt(x - 220 * s), fmt(y - 6 * s), fmt(x - 90 * s), fmt(x - 220 * s), fmt(y - 14 * s), fmt(x - 90 * s),
        fmt(x - 210 * s), fmt(y - 22 * s), fmt(x - 100 * s), INK, fmt(5 * s)))
    op = ' opacity="%s"' % opacity if opacity < 1 else ""
    return "<g%s>%s</g>" % (op, "".join(g))


def palm(x, y, h, lean=1):
    tx, ty = x + lean * h * 0.16, y - h
    g = ['<path d="M%s %sQ%s %s %s %s" fill="none" stroke="#6b4f3a" stroke-width="%s" stroke-linecap="round"/>' % (
        fmt(x), fmt(y), fmt(x + lean * h * 0.02), fmt(y - h * 0.55), fmt(tx), fmt(ty), fmt(max(3, h * 0.035)))]
    L = h * 0.42
    for a in (-165, -130, -95, -55, -20, 15):
        r = math.radians(a)
        ex, ey = tx + L * math.cos(r), ty + L * math.sin(r) + L * 0.22
        cx1, cy1 = tx + L * 0.55 * math.cos(r), ty + L * 0.55 * math.sin(r) - L * 0.22
        cx2, cy2 = cx1, cy1 + L * 0.2
        g.append('<path d="M%s %sQ%s %s %s %sQ%s %s %s %sZ" fill="#2f6b4f"/>' % (
            fmt(tx), fmt(ty), fmt(cx1), fmt(cy1), fmt(ex), fmt(ey), fmt(cx2), fmt(cy2), fmt(tx), fmt(ty)))
    return "".join(g)


def tank(x, y, w, h):
    return ('<rect x="%s" y="%s" width="%s" height="%s" fill="#ece8df"/>'
            '<rect x="%s" y="%s" width="%s" height="%s" fill="#d5cfc2"/>'
            '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#f6f3ec"/>') % (
        fmt(x), fmt(y - h), fmt(w), fmt(h), fmt(x + w * 0.68), fmt(y - h), fmt(w * 0.32), fmt(h),
        fmt(x), fmt(y - h * 0.3), fmt(w), fmt(h * 0.08), ACCENT, fmt(x + w / 2), fmt(y - h), fmt(w / 2), fmt(w * 0.12))


def cloud(x, y, s, color="#fff", opacity=0.7):
    return ('<g fill="%s" opacity="%s"><ellipse cx="%s" cy="%s" rx="%s" ry="%s"/><ellipse cx="%s" cy="%s" rx="%s" ry="%s"/>'
            '<ellipse cx="%s" cy="%s" rx="%s" ry="%s"/><ellipse cx="%s" cy="%s" rx="%s" ry="%s"/></g>') % (
        color, opacity,
        fmt(x), fmt(y), fmt(90 * s), fmt(22 * s), fmt(x - 55 * s), fmt(y + 8 * s), fmt(55 * s), fmt(16 * s),
        fmt(x + 50 * s), fmt(y + 6 * s), fmt(60 * s), fmt(18 * s), fmt(x + 10 * s), fmt(y - 14 * s), fmt(50 * s), fmt(20 * s))


# ---------------------------------------------------------------------------
# Scenes. Positions are fractions of the width, sizes scale with the height, so the same
# scene can be drawn as a wide band (15 : 4) or as a card (4 : 3).
# ---------------------------------------------------------------------------

SCENES = {
    "dusk": {
        "sky": [(0, "#a8cbe9"), (0.55, "#f9d9b0"), (1, "#f6a768")],
        "sun": (0.70, 0.68, "#fff2cf"),
        "far": "#e3b48d", "mid": "#cf9b6a", "ground": "#b98757", "front": "#8c6240",
        "clouds": [(0.18, 0.2, 1.3), (0.52, 0.12, 1.0), (0.86, 0.24, 1.4)],
        "back": [("pj", 0.37, 1.0, 0.8, False), ("pj", 0.52, 0.9, 3.3, True), ("pj", 0.81, 0.95, 2.0, False)],
        "front_items": [("palm", 0.05, 190, 1), ("palm", 0.21, 150, -1), ("pj", 0.30, 2.7, 0.3, False),
                        ("pj", 0.45, 2.0, 2.2, True), ("flare", 0.60, 0.60), ("tank", 0.655, 0.04, 0.1),
                        ("pj", 0.80, 2.4, 4.0, False), ("pj", 0.915, 1.5, 1.1, True), ("palm", 0.97, 170, -1)],
        "pipeline": (0.22, 0.92),
    },
    "gold": {
        "sky": [(0, "#9cc6ea"), (0.5, "#fde3b7"), (1, "#f9b26b")],
        "sun": (0.50, 0.66, "#fff1c9"),
        "far": "#e6bf98", "mid": "#d3a074", "ground": "#bd8c5c", "front": "#8c6240",
        "clouds": [(0.12, 0.18, 1.3), (0.40, 0.1, 1.0), (0.74, 0.2, 1.2), (0.93, 0.1, 0.9)],
        "back": [("pj", 0.14, 1.0, 1.0, False), ("pj", 0.56, 0.9, 2.6, True), ("pj", 0.88, 1.0, 4.2, False)],
        "front_items": [("palm", 0.05, 170, 1), ("pj", 0.20, 2.2, 0.6, False), ("derrick", 0.36, 430),
                        ("flare", 0.64, 0.58), ("tank", 0.685, 0.04, 0.1), ("pj", 0.83, 2.4, 3.4, True),
                        ("palm", 0.95, 180, -1)],
        "pipeline": (0.12, 0.9),
    },
    "midday": {
        "sky": [(0, "#7fb8e6"), (0.7, "#cfe6f6"), (1, "#eaf5fb")],
        "sun": (0.84, 0.22, "#fff7d6"),
        "far": "#bcd3a5", "mid": "#9fbd84", "ground": "#86a46b", "front": "#5d7a48",
        "clouds": [(0.16, 0.2, 1.3), (0.44, 0.1, 1.1), (0.66, 0.26, 1.0), (0.92, 0.12, 1.2)],
        "back": [("pj", 0.14, 1.0, 1.4, False), ("pj", 0.84, 1.0, 3.0, True)],
        "front_items": [("palm", 0.05, 160, 1), ("pj", 0.22, 2.3, 2.4, False), ("derrick", 0.50, 500),
                        ("pj", 0.82, 2.3, 0.2, True), ("palm", 0.96, 170, -1)],
        "pipeline": (0.1, 0.92),
    },
    "dawn": {
        "sky": [(0, "#b9a8d6"), (0.55, "#f6c1c9"), (1, "#fbd9a0")],
        "sun": (0.45, 0.70, "#fff0cc"),
        "far": "#d3b0c0", "mid": "#b996a8", "ground": "#8f7284", "front": "#5f4a5c",
        "clouds": [(0.2, 0.22, 1.2), (0.62, 0.14, 1.0), (0.88, 0.26, 1.3)],
        "back": [("pj", 0.34, 0.9, 1.0, False), ("pj", 0.62, 0.9, 2.8, True)],
        "front_items": [("palm", 0.06, 170, 1), ("pj", 0.26, 2.4, 0.9, False), ("flare", 0.52, 0.56),
                        ("pj", 0.74, 2.5, 3.5, True), ("palm", 0.95, 170, -1)],
        "pipeline": (0.12, 0.92),
    },
}


def scene(kind, W=2500, H=667):
    sc = SCENES[kind]
    k = H / 667.0
    gy = H * 0.855            # the line the equipment stands on
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" preserveAspectRatio="xMidYMid slice">' % (W, H, W, H)]
    stops = "".join('<stop offset="%s" stop-color="%s"/>' % (o, c) for o, c in sc["sky"])
    out.append('<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">%s</linearGradient>'
               '<radialGradient id="glow"><stop offset="0" stop-color="#ffd98a" stop-opacity=".8"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient>'
               '<radialGradient id="sun"><stop offset="0" stop-color="%s" stop-opacity=".95"/><stop offset=".35" stop-color="%s" stop-opacity=".55"/><stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient></defs>'
               % (stops, sc["sun"][2], sc["sun"][2], sc["sun"][2]))
    out.append('<rect width="%d" height="%d" fill="url(#sky)"/>' % (W, H))
    sx, sy, scol = sc["sun"]
    out.append('<circle cx="%s" cy="%s" r="%s" fill="url(#sun)"/>' % (fmt(sx * W), fmt(sy * H), fmt(260 * k)))
    out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (fmt(sx * W), fmt(sy * H), fmt(46 * k), scol))
    for cx, cy, cs in sc["clouds"]:
        out.append(cloud(cx * W, cy * H, cs * k))
    out.append(hills(W, H, H * 0.70, 34 * k, sc["far"], 1.3))
    out.append(hills(W, H, H * 0.77, 30 * k, sc["mid"], 4.1))
    # small equipment far away, on the middle hills
    for it in sc["back"]:
        if it[0] == "pj":
            out.append(pumpjack(it[1] * W, H * 0.79, it[2] * k * 0.9, it[3], it[4], 0.55))
    out.append('<rect y="%s" width="%d" height="%s" fill="%s"/>' % (fmt(gy - 6 * k), W, fmt(H - gy + 6 * k), sc["ground"]))
    out.append(hills(W, H, gy + 6 * k, 6 * k, sc["ground"], 7.7))
    out.append('<rect y="%s" width="%d" height="%s" fill="%s"/>' % (fmt(H * 0.935), W, fmt(H - H * 0.935), sc["front"]))
    pl = sc.get("pipeline")
    if pl:
        a, b = pl[0] * W, pl[1] * W
        out.append('<path d="M%s %sH%s" stroke="%s" stroke-width="%s" opacity=".55"/>' % (fmt(a), fmt(gy + 16 * k), fmt(b), INK, fmt(4 * k)))
        x = a + 40 * k
        sup = []
        while x < b:
            sup.append("M%s %sV%s" % (fmt(x), fmt(gy + 16 * k), fmt(gy + 30 * k)))
            x += 110 * k
        out.append('<path d="%s" stroke="%s" stroke-width="%s" opacity=".45"/>' % ("".join(sup), INK, fmt(3 * k)))
    for it in sc["front_items"]:
        kind_ = it[0]
        if kind_ == "pj":
            out.append(pumpjack(it[1] * W, gy, it[2] * k, it[3], it[4]))
        elif kind_ == "flare":
            out.append(flare(it[1] * W, gy, it[2] * H, k))
        elif kind_ == "derrick":
            out.append(derrick(it[1] * W, gy, it[2] * k, k))
        elif kind_ == "palm":
            out.append(palm(it[1] * W, gy + 4 * k, it[2] * k, it[3]))
        elif kind_ == "tank":
            out.append(tank(it[1] * W, gy, it[2] * W, 74 * k))
            out.append(tank(it[1] * W + it[2] * W * 1.25, gy, it[2] * W, 74 * k))
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# The round picture on the About page
# ---------------------------------------------------------------------------

def badge():
    s = "#fff"
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" width="640" height="640">
<defs><linearGradient id="b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9531a"/><stop offset="1" stop-color="#a8360a"/></linearGradient></defs>
<rect width="640" height="640" fill="url(#b)"/>
<circle cx="320" cy="560" r="330" fill="#fff" opacity=".1"/>
<g fill="none" stroke="%(s)s" stroke-width="16" stroke-linecap="round" stroke-linejoin="round">
<path d="M190 540L282 120h76l92 420"/><path d="M226 400h188M252 280h136"/><path d="M190 540L414 400M450 540L226 400M226 400L388 280M414 400L252 280"/><path d="M150 540h340"/>
</g>
<rect x="286" y="92" width="68" height="34" fill="%(s)s"/>
<path d="M300 126v240M340 126v240" stroke="%(s)s" stroke-width="8"/>
</svg>""" % {"s": s}


# ---------------------------------------------------------------------------
# Icons: 48 x 48, drawn with a rounded line in one colour and a soft fill
# ---------------------------------------------------------------------------

ICON_PATHS = {
    "derrick": '<path d="M13 43L21 8h6l8 35" fill="{f}"/><path d="M17 31h14M20 19h8M9 43h30"/><path d="M17 31l14 12M31 31L17 43"/>',
    "gauge": '<path d="M8 36a16 16 0 1 1 32 0" fill="{f}"/><path d="M24 36l8-11"/><circle cx="24" cy="36" r="2.5"/><path d="M12 24l3 2M24 14v3M36 24l-3 2"/>',
    "contract": '<path d="M12 6h18l8 8v28H12z" fill="{f}"/><path d="M30 6v8h8M18 22h14M18 29h14M18 36l3 3 6-7"/>',
    "magnifier": '<circle cx="21" cy="21" r="12" fill="{f}"/><path d="M30 30l12 12M16 26v-5M21 26v-9M26 26v-6"/>',
    "trend": '<path d="M8 8v32h32"/><path d="M13 32l8-9 7 5 11-14M31 14h8v8" fill="none"/><path d="M13 32l8-9 7 5 11-14V32z" fill="{f}" stroke="none"/>',
    "sprout": '<path d="M24 43V22"/><path d="M24 27c-9 0-14-5-14-14 9 0 14 5 14 14z" fill="{f}"/><path d="M24 32c0-8 5-12 14-12 0 9-5 12-14 12z" fill="{f}"/>',
    "shield": '<path d="M24 5l15 5v12c0 10-6 17-15 21-9-4-15-11-15-21V10z" fill="{f}"/><path d="M17 24l5 5 9-10"/>',
    "badge": '<circle cx="24" cy="21" r="12" fill="{f}"/><path d="M18 31l-3 12 9-4 9 4-3-12M18 21l5 5 8-9"/>',
    "cycle": '<path d="M36 18a14 14 0 0 0-24 4M12 30a14 14 0 0 0 24-4M36 9v9h-9M12 39v-9h9"/>',
    "people": '<circle cx="24" cy="16" r="6" fill="{f}"/><path d="M12 41c0-8 5-12 12-12s12 4 12 12z" fill="{f}"/><circle cx="9" cy="21" r="4"/><circle cx="39" cy="21" r="4"/><path d="M3 37c0-6 3-9 7-9M45 37c0-6-3-9-7-9"/>',
    "cap": '<path d="M24 9L4 19l20 10 20-10z" fill="{f}"/><path d="M12 24v10c3 4 9 6 12 6s9-2 12-6V24M44 19v12"/>',
    "speech": '<path d="M8 8h32a4 4 0 0 1 4 4v18a4 4 0 0 1-4 4H22l-9 8v-8H8a4 4 0 0 1-4-4V12a4 4 0 0 1 4-4z" fill="{f}"/><path d="M15 21h.01M24 21h.01M33 21h.01" stroke-width="4"/>',
    "clock": '<circle cx="24" cy="24" r="17" fill="{f}"/><path d="M24 13v11l7 5"/>',
    "pin": '<path d="M24 44s-14-13-14-25a14 14 0 0 1 28 0c0 12-14 25-14 25z" fill="{f}"/><circle cx="24" cy="19" r="5"/>',
}


def icon(name):
    col, _ = ICONS[name]
    body = ICON_PATHS[name].replace("{f}", col + "2e").replace('fill="%s2e"' % col, 'fill="%s" fill-opacity=".18"' % col)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" fill="none" stroke="%s" '
            'stroke-width="3" stroke-linecap="round" stroke-linejoin="round">%s</svg>') % (col, body)


# ---------------------------------------------------------------------------
# The map of the Americas
# ---------------------------------------------------------------------------

WORKED = {"Venezuela", "Colombia", "Ecuador", "Peru", "Brazil", "Argentina", "Bolivia", "Trinidad and Tobago",
          "Mexico", "Guatemala", "Belize", "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama"}
PINS = [("Venezuela", -66.2, 7.6), ("Colombia", -74.1, 4.7), ("Ecuador", -78.4, -1.3), ("Peru", -75.0, -10.0),
        ("Brazil", -52.0, -10.5), ("Argentina", -63.0, -34.0), ("Bolivia", -64.7, -16.5),
        ("Trinidad and Tobago", -61.3, 10.5), ("Mexico", -101.5, 23.0), ("Central America", -86.5, 14.6)]


def ne1(lon, lat):
    lam, phi = math.radians(lon), math.radians(lat)
    p2 = phi * phi
    p4 = p2 * p2
    x = lam * (0.8707 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4)))
    y = phi * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)))
    return x, y


def americas(geo_folder):
    W, H = 760, 860
    lon0, lon1, lat0, lat1 = -118.0, -30.0, -57.0, 33.0
    corners = [ne1(lo, la) for lo in (lon0, lon1) for la in (lat0, lat1)]
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    pad = 20
    S = min((W - 2 * pad) / (max(xs) - min(xs)), (H - 2 * pad) / (max(ys) - min(ys)))
    ox = W / 2 - S * (max(xs) + min(xs)) / 2
    oy = H / 2 + S * (max(ys) + min(ys)) / 2

    def proj(lon, lat):
        x, y = ne1(lon, lat)
        return ox + x * S, oy - y * S

    def ring(r):
        pts = [proj(lo, la) for lo, la in r]
        if max(p[0] for p in pts) < -5 or min(p[0] for p in pts) > W + 5 or max(p[1] for p in pts) < -5 or min(p[1] for p in pts) > H + 5:
            return None
        out = [(round(pts[0][0]), round(pts[0][1]))]
        for p in pts[1:-1]:
            q = (round(p[0]), round(p[1]))
            if abs(q[0] - out[-1][0]) + abs(q[1] - out[-1][1]) >= 1.5:
                out.append(q)
        if len(out) < 3:
            return None
        return "M%d %dl%sz" % (out[0][0], out[0][1], " ".join("%d %d" % (b[0] - a[0], b[1] - a[1]) for a, b in zip(out, out[1:])))

    data = json.load(open(os.path.join(geo_folder, "ne_50m_admin_0_countries.geojson")))
    worked, other = [], []
    for f in data["features"]:
        name = f["properties"]["ADMIN"]
        if name == "Antarctica":
            continue
        geom = f["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        parts = []
        for poly in polys:
            for r in poly:
                d = ring(r)
                if d:
                    parts.append(d)
        if parts:
            (worked if name in WORKED else other).append("".join(parts))
    R = 15.0
    tx, ty = 0.879 * R, 1.624 * R
    pins = sorted((proj(lo, la) for _, lo, la in PINS), key=lambda p: p[1])
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="Map of the Americas with a pin on each country where Miguel has worked">' % (W, H, W, H)]
    svg.append('<defs><linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d4e7f4"/><stop offset="1" stop-color="#b3d1e9"/></linearGradient>'
               '<g id="pin"><ellipse cx="0" cy="0.5" rx="%.1f" ry="%.1f" fill="#1a3a52" opacity=".28"/>'
               '<path d="M0 0L%.2f %.2fA%s %s 0 1 1 %.2f %.2fZ" fill="%s" stroke="#fff" stroke-width="3.4" stroke-linejoin="round"/>'
               '<circle cx="0" cy="%.2f" r="%.2f" fill="#fff"/></g></defs>' % (
                   R * 0.62, R * 0.2, -tx, -ty, R, R, tx, -ty, ACCENT, -2.1 * R, R * 0.38))
    svg.append('<rect width="%d" height="%d" fill="url(#sea)"/>' % (W, H))
    svg.append('<g fill-rule="evenodd" stroke="#fff" stroke-width="1.4" stroke-linejoin="round">')
    svg.append('<path fill="#efe5c8" d="%s"/>' % "".join(other))
    svg.append('<path fill="#f5c9a2" d="%s"/>' % "".join(worked))
    svg.append("</g>")
    for x, y in pins:
        svg.append('<use href="#pin" transform="translate(%.1f %.1f)"/>' % (x, y))
    svg.append("</svg>")
    return "\n".join(svg)


def main():
    for kind in SCENES:
        write("assets/scenes/%s.svg" % kind, scene(kind))
    write("assets/scenes/dawn-card.svg", scene("dawn", 800, 600))
    write("assets/scenes/midday-card.svg", scene("midday", 800, 600))
    write("assets/scenes/dusk-card.svg", scene("dusk", 800, 600))
    write("assets/about/profile-badge.svg", badge())
    for name in ICONS:
        write("assets/icons/%s.svg" % name, icon(name))
    geo = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/nvkelso/natural-earth-vector/geojson"
    if os.path.exists(os.path.join(geo, "ne_50m_admin_0_countries.geojson")):
        write("assets/about/americas-map.svg", americas(geo))
    else:
        print("Natural Earth files not found in %s, the map was not redrawn" % geo)
    print("art drawn")


if __name__ == "__main__":
    main()
