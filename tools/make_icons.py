# -*- coding: utf-8 -*-
"""App icon: a contraction on cardiotocograph paper."""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
from PIL import Image, ImageDraw

OUT = ROOT
GROUND = (142, 26, 30)      # deep oxblood
TRACE  = (252, 245, 243)    # paper white
SS     = 4                  # supersample factor

def blend(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))

def contraction(x, cx, w, amp, base):
    """A single bell-shaped uterine contraction."""
    return base - amp * math.exp(-(((x - cx) / w) ** 2))

def make(size, inset=0.0):
    """inset: fraction of the canvas kept clear at each edge (for maskable icons)."""
    S = size * SS
    img = Image.new("RGB", (S, S), GROUND)
    d = ImageDraw.Draw(img)

    pad = S * inset
    L, R = pad, S - pad
    span = R - L

    # --- CTG paper grid ---
    grid_soft = blend(GROUND, TRACE, 0.10)
    grid_hard = blend(GROUND, TRACE, 0.20)
    step = span / 12.0
    lw_soft = max(1, int(S / 260))
    lw_hard = max(1, int(S / 170))
    for i in range(13):
        p = L + i * step
        hard = (i % 3 == 0)
        d.line([(p, L), (p, R)], fill=grid_hard if hard else grid_soft,
               width=lw_hard if hard else lw_soft)
        d.line([(L, p), (R, p)], fill=grid_hard if hard else grid_soft,
               width=lw_hard if hard else lw_soft)

    # --- the trace ---
    base = L + span * 0.735          # resting tone
    amp  = span * 0.46               # peak height
    cx   = L + span * 0.40           # peak position
    w    = span * 0.20               # width of the contraction

    pts = []
    steps = 140
    for k in range(steps + 1):
        x = L + span * k / steps
        y = contraction(x, cx, w, amp, base)
        # a second contraction beginning at the right edge
        y = min(y, contraction(x, L + span * 1.18, w, amp, base))
        pts.append((x, y))

    # baseline tick marks, as on real tocograph paper
    tick = span * 0.028
    for i in range(1, 12):
        x = L + i * step
        d.line([(x, R - tick), (x, R)], fill=blend(GROUND, TRACE, 0.34),
               width=max(1, int(S / 200)))

    d.line(pts, fill=TRACE, width=max(2, int(S * 0.062)), joint="curve")

    return img.resize((size, size), Image.LANCZOS)

os.makedirs(OUT, exist_ok=True)
for name, size, inset in [
    ("icon-180.png", 180, 0.0),
    ("icon-192.png", 192, 0.0),
    ("icon-512.png", 512, 0.0),
    ("icon-maskable-512.png", 512, 0.11),
]:
    p = os.path.join(OUT, name)
    make(size, inset).save(p, "PNG", optimize=True)
    print("%-24s %6d bytes" % (name, os.path.getsize(p)))
