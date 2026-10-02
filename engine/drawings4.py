"""Twelve more speed-drawing pictures: waterfall, treehouse, city night, dinosaur, hedgehog, jellyfish, puppy,
pizza, bonsai, birthday cake, guitar and robot. Same conventions as drawings.py."""

import math

from .art import blob, circle, cloud, cubic, ellipse, jitter, lerp, quad, shade, spline, star, transform
from .drawings import CX, FX0, FX1, FY1, birds, frame, frame_clip, leaf, pine, rect, ribbon
from .drawings3 import _backdrop, _eyes, _smile
from .sketch import Sketch


def _ground(sk, rng, color, y=1290):
    sk.shape(spline([(CX - 405, y + 10), (CX, y - 20), (CX + 405, y + 10), (CX + 280, y + 120), (CX - 280, y + 120)], True, 8),
             jitter(color, rng))


def _note(sk, c, color, s=1.0):
    """An eighth note: head, stem and flag."""
    x, y = c
    sk.shape(ellipse((x, y), 24 * s, 18 * s, rot=-20), color, width=4)
    sk.line([(x + 21 * s, y - 6 * s), (x + 21 * s, y - 100 * s)], None, 5)
    sk.line(quad((x + 21 * s, y - 100 * s), (x + 60 * s, y - 80 * s), (x + 50 * s, y - 45 * s), 8), None, 5)


# -- scenery ----------------------------------------------------------------------------

def waterfall(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#b8e2ff", rng))
    sk.shape(circle((rng.uniform(FX0 + 120, FX1 - 120), rng.uniform(540, 590)), 60), jitter("#ffd166", rng))
    for _ in range(2):
        sk.shape(cloud((rng.uniform(FX0 + 160, FX1 - 160), rng.uniform(560, 690)), rng.uniform(170, 230), 55), "#ffffff")
    top, pool_y = rng.uniform(790, 840), 1250
    fx, fw = CX + rng.uniform(-40, 40), rng.uniform(110, 140)
    water = jitter("#5bb8e8", rng)
    sk.shape([(fx - fw, top - 10), (fx + fw, top - 10), (fx + fw + 30, pool_y), (fx - fw - 30, pool_y)], water)
    streaks = [[(fx + k * fw / 3, top + rng.uniform(30, 110)), (fx + k * (fw + 30) / 3, pool_y - rng.uniform(30, 150))]
               for k in (-2, -1, 0, 1, 2)]
    sk.line(streaks, "#e6f6ff", 6, phase="detail", tool="brush")
    rock = jitter("#8d7b68", rng)
    grass = jitter("#6cbf5a", rng)
    for s in (-1, 1):
        edge = fx + s * fw
        far = FX1 + 10 if s > 0 else FX0 - 10
        crest = [(far, top - rng.uniform(80, 150)), (lerp(far, edge, 0.5), top - rng.uniform(20, 70)), (edge - s * 6, top)]
        cliff = crest + [(edge + s * 24, pool_y + 10), (far, pool_y + 10)]
        sk.shape(frame_clip(cliff), shade(rock, 1 - 0.08 * (s > 0)))
        sk.shade(frame_clip([crest[2], (edge + s * 24, pool_y + 10), (edge + s * 110, pool_y + 10), (edge + s * 70, top + 40)]),
                 "#000000", 40)
        cracks = [[(lerp(edge, far, u) + s * 10, y), (lerp(edge, far, u) + s * 50, y + 30)]
                  for u, y in ((0.3, top + 120), (0.55, top + 260), (0.25, top + 330))]
        sk.line(cracks, shade(rock, 0.6), 4, together=True)
        sk.shape(frame_clip(crest + [(x, y + 34) for x, y in reversed(crest)]), grass, width=4)
        pine(sk, lerp(far, edge, 0.35), crest[1][1] + 10, rng.uniform(220, 280), jitter("#2f7d4f", rng))
    sk.shape(frame_clip(ellipse((fx, pool_y + 60), 340, 90)), shade(water, 0.85))
    sk.shape(cloud((fx, pool_y + 10), 2 * fw + 140, 70, bumps=5), "#ffffff")
    for _ in range(5):
        x, y = rng.uniform(fx - 280, fx + 220), rng.uniform(pool_y + 50, pool_y + 110)
        sk.line([(x, y), (x + rng.uniform(50, 90), y)], "#e6f6ff", 5, phase="detail", tool="brush")
    for x in (fx - 300, fx + 280):
        sk.shape(blob(rng, (x, pool_y + 110), 60, 6, 0.2), jitter("#9aa0a8", rng), width=4.5)
    ground = jitter("#7cc46a", rng)
    sk.shape(frame_clip(spline([(FX0 - 10, 1400), (CX - 120, 1370), (CX + 180, 1410), (FX1 + 10, 1380), (FX1 + 10, FY1 + 10),
                                (FX0 - 10, FY1 + 10)], True, 8)), ground)
    for _ in range(10):
        x, y = rng.uniform(FX0 + 40, FX1 - 40), rng.uniform(1440, FY1 - 30)
        sk.line([(x, y + 26), (x, y)], "#3e8e41", 4)
        sk.shape(circle((x, y), 11), pal.at(rng.random()), width=3)
    birds(sk, rng, 3, FX0 + 100, FX1 - 100, 500, 640)
    return sk.scene(dur, hold)


def treehouse(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#bfe6ff", rng))
    sk.shape(circle((rng.choice((FX0 + 110, FX1 - 110)), 540), 55), jitter("#ffd166", rng))
    sk.shape(cloud((rng.uniform(FX0 + 180, FX1 - 180), 560), 200, 50), "#ffffff")
    ground_y = 1390
    sk.shape(frame_clip(spline([(FX0 - 10, ground_y), (CX, ground_y - 40), (FX1 + 10, ground_y + 10), (FX1 + 10, FY1 + 10),
                                (FX0 - 10, FY1 + 10)], True, 8)), jitter("#7cc46a", rng))
    tx = CX + rng.uniform(-40, 40)
    bark = jitter("#8a5a3b", rng)
    trunk = cubic((tx, ground_y + 30), (tx - 40, 1250), (tx + 40, 1000), (tx, 760), 16)
    sk.shape(ribbon(trunk, 170, 90, False), bark)
    sk.shade(ribbon(cubic((tx + 30, ground_y + 20), (tx - 5, 1250), (tx + 75, 1000), (tx + 35, 780), 16), 50, 25, False),
             "#000000", 35)
    for s in (-1, 1):
        sk.shape(ribbon(cubic((tx, 900), (tx + s * 80, 860), (tx + s * 160, 800), (tx + s * 240, 760), 10), 50, 20), bark)
    green = jitter("#4caf50", rng)
    for (x, y, r) in ((tx - 230, 720, 145), (tx + 240, 715, 150), (tx, 640, 175), (tx - 110, 780, 135), (tx + 130, 780, 135)):
        sk.shape(blob(rng, (x, y), r, 8, 0.15), shade(green, rng.uniform(0.9, 1.1)))
        sk.shade(ellipse((x + r * 0.25, y + r * 0.35), r * 0.5, r * 0.3), "#1b4d2b", 50)
    for _ in range(8):
        x, y = tx + rng.uniform(-300, 300), rng.uniform(600, 820)
        sk.detail(circle((x, y), 13), "#e63946")
    wood = jitter("#c98b52", rng)
    sk.shape(rect(tx - 240, 1120, tx + 240, 1155, 6), shade(wood, 0.8))
    sk.shape(rect(tx - 170, 930, tx + 170, 1125), wood)
    sk.line([[(tx - 170, y), (tx + 170, y)] for y in (975, 1025, 1075)], shade(wood, 0.65), 3.5, together=True)
    roof = jitter(rng.choice(["#e63946", "#3d5a80", "#9b5de5"]), rng)
    sk.shape([(tx - 215, 945), (tx, 790), (tx + 215, 945)], roof)
    sk.shade([(tx, 790), (tx + 215, 945), (tx + 60, 945)], "#000000", 35)
    sk.shape(rect(tx - 120, 975, tx - 30, 1060, 8), "#ffe28a")
    sk.line([[(tx - 75, 975), (tx - 75, 1060)], [(tx - 120, 1017), (tx - 30, 1017)]], None, 4)
    sk.shape(rect(tx + 40, 990, tx + 120, 1125, 36), shade(wood, 0.6))
    sk.detail(circle((tx + 102, 1065), 7), "#ffd166")
    sk.line([(tx, 790), (tx, 720)], None, 5)
    sk.shape([(tx, 720), (tx + 60, 738), (tx, 756)], pal.at(rng.random()), width=4)
    lx = tx + 150
    rope = "#d9b382"
    sk.line([[(lx, 1155), (lx + 30, ground_y)], [(lx + 70, 1155), (lx + 100, ground_y)]], shade(wood, 0.7), 8)
    sk.line([[(lx + 6 + 30 * u, 1155 + (ground_y - 1155) * u), (lx + 76 + 30 * u, 1155 + (ground_y - 1155) * u)]
             for u in (0.15, 0.35, 0.55, 0.75, 0.95)], shade(wood, 0.7), 7, together=True)
    sx = tx - 190
    sk.line([[(sx, 1155), (sx, 1300)], [(sx + 80, 1155), (sx + 80, 1300)]], rope, 5)
    sk.shape(rect(sx - 20, 1295, sx + 100, 1320, 6), wood, width=4)
    for x in (FX0 + 70, FX1 - 70):
        sk.shape(frame_clip(blob(rng, (x, ground_y + 30), 90, 7, 0.15)), shade(green, 0.85))
    for _ in range(8):
        x, y = rng.uniform(FX0 + 40, FX1 - 40), rng.uniform(1450, FY1 - 30)
        sk.detail(star((x, y), 14, 6, 5), pal.at(rng.random()))
    birds(sk, rng, 2, FX0 + 100, FX1 - 100, 480, 540)
    return sk.scene(dur, hold)


def city_night(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#1d2b5c", rng))
    sk.shade(rect(FX0, 950, FX1, 1360), pal.at(rng.random()), 60)
    for _ in range(28):
        sk.detail(star((rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(470, 1000)), rng.uniform(6, 11), 3), "#ffffff")
    moon = (rng.uniform(FX0 + 140, FX1 - 140), rng.uniform(560, 640))
    sk.shape(circle(moon, 70), "#fdf3c4")
    for dx, dy, r in ((-20, -15, 14), (22, 18, 10), (-5, 30, 8)):
        sk.shade(circle((moon[0] + dx, moon[1] + dy), r), "#d9c98f", 200)
    base = 1360
    lamp = "#ffe27a"
    for row, (col, lo, hi, wmin, wmax) in enumerate((("#3b3f74", 760, 1000, 80, 130), ("#262a52", 920, 1180, 110, 170))):
        x = FX0 - rng.uniform(0, 60)
        while x < FX1:
            w = rng.uniform(wmin, wmax)
            top = rng.uniform(lo, hi)
            b_col = jitter(col, rng, 0.04)
            sk.shape(frame_clip(rect(x, top, x + w, base + 10)), b_col, width=4.5)
            if row == 0 and top < 820:
                sk.line([(x + w / 2, top), (x + w / 2, top - 70)], None, 4)
                sk.detail(circle((x + w / 2, top - 74), 8), "#ff4d6d")
            wins = []
            for wy in range(int(top + 30), base - 40, 52 if row else 64):
                for wx in range(int(x + 22), int(x + w - 20), 34 if row else 40):
                    if FX0 + 10 < wx < FX1 - 10 and rng.random() < (0.55 if row else 0.35):
                        wins.append([(wx, wy), (wx, wy + 14)])
            if wins:
                sk.line(wins, lamp if row else shade(lamp, 0.8), 13 if row else 10, phase="detail", together=True, tool="brush")
            x += w + rng.uniform(-10, 14 if row else 30)
    river = jitter("#16204a", rng)
    sk.shape(rect(FX0, base, FX1, FY1), river)
    for _ in range(14):
        x, y = rng.uniform(FX0 + 30, FX1 - 90), rng.uniform(base + 30, FY1 - 30)
        sk.line([(x, y), (x + rng.uniform(30, 70), y)], rng.choice((lamp, "#fdf3c4", pal.at(rng.random()))), 5,
                phase="detail", tool="brush")
    for x in (FX0 + 110, FX1 - 110):
        sk.line([(x, base), (x, base - 150)], "#4a4e69", 7)
        sk.shape(circle((x, base - 162), 16), lamp, width=4)
    return sk.scene(dur, hold)


# -- animals ---------------------------------------------------------------------------

def dinosaur(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    vx = CX - 250
    sk.shape([(vx - 130, 1290), (vx - 30, 1060), (vx + 30, 1060), (vx + 130, 1290)], jitter("#9c6b4a", rng))
    sk.shape(spline([(vx - 40, 1062), (vx - 10, 1100), (vx + 10, 1080), (vx + 40, 1062)], True, 4), "#ff7b39", width=4)
    for i in range(3):
        sk.shape(circle((vx + 20 * i, 1010 - 50 * i), 20 + 8 * i), "#d6d6de", width=4)
    _ground(sk, rng, "#86c977", 1300)
    skin = jitter(rng.choice(["#7bc96f", "#5fb8a6", "#9bc53d", "#a18cd1"]), rng)
    plates = pal.at(rng.random())
    c, rx, ry = (CX, 1150), 200, 145
    for k in range(6):
        a = math.radians(200 + k * 24)
        p0 = (c[0] + rx * math.cos(a - 0.12), c[1] + ry * math.sin(a - 0.12))
        p1 = (c[0] + rx * math.cos(a + 0.12), c[1] + ry * math.sin(a + 0.12))
        tip = (c[0] + (rx + 70) * math.cos(a), c[1] + (ry + 70) * math.sin(a))
        sk.shape([p0, tip, p1], plates, width=4.5)
    sk.shape(ribbon(cubic((CX - 120, 1180), (CX - 240, 1240), (CX - 330, 1250), (CX - 400, 1170), 18), 120, 12), skin)
    for x in (CX - 120, CX + 70):
        sk.shape(rect(x, 1230, x + 70, 1330, 30), shade(skin, 0.85))
    sk.shape(ellipse(c, rx, ry), skin)
    sk.shade(ellipse((c[0] + 20, c[1] + 60), 130, 70), "#fff3c4", 180)
    neck = cubic((CX + 120, 1110), (CX + 190, 1050), (CX + 200, 950), (CX + 210, 870), 12)
    sk.shape(ribbon(neck, 120, 110, False), skin)
    head = (CX + 260, 820)
    sk.shape(ellipse(head, 145, 105, rot=-8), skin)
    sk.shape(circle((head[0] + 10, head[1] - 25), 24), "#1d1d28")
    sk.detail(circle((head[0] + 2, head[1] - 34), 8), "#ffffff")
    sk.shade(ellipse((head[0] + 50, head[1] + 25), 26, 15), "#ff8fab", 140)
    sk.line(quad((head[0] + 50, head[1] + 55), (head[0] + 95, head[1] + 75), (head[0] + 130, head[1] + 35), 10), None, 4.5)
    sk.detail(circle((head[0] + 115, head[1] - 10), 6), shade(skin, 0.5))
    sk.shape(ribbon([(CX + 150, 1150), (CX + 200, 1170), (CX + 225, 1200)], 34, 26), skin, width=4.5)
    for x in (CX - 90, CX + 100):
        sk.shape(rect(x, 1240, x + 74, 1345, 30), skin)
        for k in range(3):
            sk.detail(circle((x + 15 + k * 22, 1340), 7), "#ffffff")
    eg = (CX + 320, 1330)
    sk.shape(ellipse(eg, 48, 62), "#fff6e0")
    for dx, dy in ((-15, -20), (18, 5), (-8, 28)):
        sk.shade(circle((eg[0] + dx, eg[1] + dy), 10), pal.at(rng.random()), 230)
    return sk.scene(dur, hold)


def hedgehog(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    _ground(sk, rng, "#a7c957", 1290)
    c, rx, ry = (CX - 40, 1180), 270, 210
    quills = jitter(rng.choice(["#8b5e3c", "#6f4e37", "#a0785a"]), rng)
    n = 30
    spikes = []
    for i in range(n + 1):
        a = math.pi * 0.92 + math.pi * 1.16 * i / n
        k = 1.0 if i % 2 == 0 else 0.84
        spikes.append((c[0] + rx * k * math.cos(a), c[1] + ry * k * math.sin(a)))
    sk.shape(spikes + [(c[0] + rx * 0.9, c[1] + 70), (c[0] - rx * 0.9, c[1] + 70)], quills)
    strokes = []
    for _ in range(26):
        a = rng.uniform(math.pi * 1.05, math.pi * 1.9)
        r = rng.uniform(0.3, 0.7)
        p = (c[0] + rx * r * math.cos(a), c[1] + ry * r * math.sin(a))
        strokes.append([p, (p[0] + 40 * math.cos(a), p[1] + 40 * math.sin(a))])
    sk.line(strokes, shade(quills, 0.6), 4, together=True, phase="shade", tool="brush")
    face = jitter("#f3d9b1", rng)
    for x in (c[0] - 120, c[0] + 60):
        sk.shape(ellipse((x, c[1] + 85), 50, 26), shade(face, 0.75))
    sk.shape(spline([(c[0] + 110, c[1] - 120), (c[0] + 260, c[1] - 40), (c[0] + 370, c[1] + 25), (c[0] + 320, c[1] + 80),
                     (c[0] + 160, c[1] + 95), (c[0] + 90, c[1] + 10)], True, 8), face)
    sk.shape(circle((c[0] + 170, c[1] - 100), 32), face)
    sk.shade(circle((c[0] + 170, c[1] - 100), 16), "#ff8fab", 170)
    sk.shape(circle((c[0] + 368, c[1] + 25), 22), "#1d1d28")
    sk.detail(circle((c[0] + 362, c[1] + 18), 7), "#ffffff")
    sk.shape(circle((c[0] + 235, c[1] - 15), 20), "#1d1d28")
    sk.detail(circle((c[0] + 229, c[1] - 22), 7), "#ffffff")
    sk.shade(ellipse((c[0] + 230, c[1] + 40), 26, 15), "#ff8fab", 140)
    sk.line(quad((c[0] + 280, c[1] + 55), (c[0] + 310, c[1] + 72), (c[0] + 340, c[1] + 55), 8), None, 4.5)
    ap = (c[0] - 40, c[1] - 235)
    sk.shape(circle(ap, 58), jitter("#e63946", rng))
    sk.shade(ellipse((ap[0] - 22, ap[1] - 18), 14, 22, rot=30), "#ffffff", 140)
    sk.line([(ap[0], ap[1] - 50), (ap[0] + 8, ap[1] - 85)], "#5b3b2a", 7)
    sk.shape(leaf((ap[0] + 6, ap[1] - 75), (ap[0] + 70, ap[1] - 100), 16), "#4caf50", width=4)
    for _ in range(6):
        x, y = CX + rng.uniform(-340, 340), rng.uniform(1330, 1380)
        a = rng.uniform(0, 2 * math.pi)
        sk.shape(leaf((x, y), (x + 50 * math.cos(a), y + 25 * math.sin(a)), 14),
                 rng.choice(["#f4a259", "#d1495b", "#edae49"]), width=3.5)
    return sk.scene(dur, hold)


def jellyfish(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, color=jitter("#4b7bd1", rng))
    _ground(sk, rng, "#f2d49b", 1320)
    sf = (CX + rng.choice((-1, 1)) * 260, 1360)
    sk.shape(star(sf, 50, 22, 5, rot=rng.uniform(-110, -70)), jitter("#ff8c42", rng), width=4)
    for x in (CX - 330, CX + 320):
        sk.shape(ribbon([(x + 22 * math.sin(i * 0.7), 1330 - i * 34) for i in range(9)], 34, 10), jitter("#3fa34d", rng))
    col = jitter(rng.choice(["#ff8fc7", "#c77dff", "#ffa8a8", "#7ad7f0"]), rng)
    cy = 900
    tent = []
    for k in range(6):
        x0 = CX - 150 + k * 60
        ph = rng.uniform(0, 6)
        tent.append([(x0 + 18 * math.sin(i * 0.6 + ph), cy + 50 + i * 30) for i in range(12)])
    sk.line(tent, shade(col, 0.75), 6)
    for k in range(3):
        x0 = CX - 90 + k * 90
        ph = rng.uniform(0, 6)
        arm = [(x0 + 26 * math.sin(i * 0.55 + ph), cy + 40 + i * 28) for i in range(10)]
        sk.shape(ribbon(arm, 54, 14), shade(col, 1.12))
    dome = ellipse((CX, cy + 20), 240, 230, a0=math.pi, a1=2 * math.pi, n=40)
    scallops = []
    for k in range(8):
        x0, x1 = CX + 240 - 60 * k, CX + 180 - 60 * k
        scallops += quad((x0, cy + 20), ((x0 + x1) / 2, cy + 70), (x1, cy + 20), 6)[1:]
    sk.shape(dome + scallops, col)
    sk.shade(ellipse((CX - 110, cy - 120), 50, 30, rot=-35), "#ffffff", 130)
    for _ in range(5):
        a = rng.uniform(math.pi * 1.1, math.pi * 1.9)
        r = rng.uniform(0.55, 0.85)
        sk.shade(circle((CX + 240 * r * math.cos(a), cy + 20 + 230 * r * math.sin(a)), rng.uniform(10, 18)), shade(col, 1.15), 200)
    _eyes(sk, CX, cy - 40, 70, 24, blush_dx=120)
    _smile(sk, CX, cy + 5, 26)
    for _ in range(9):
        b = (CX + rng.uniform(-330, 330), rng.uniform(620, 1200))
        if abs(b[0] - CX) > 270:
            ring = circle(b, rng.uniform(8, 16), n=16)
            sk.detail_line(ring + ring[:1], "#ffffff", 3.5)
    return sk.scene(dur, hold)


def puppy(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.6)
    sk.shade(ellipse((CX, 1440), 290, 40), "#000000", 30)
    fur = jitter(rng.choice(["#e0b07a", "#c68b59", "#f1e3cf", "#d9a066"]), rng)
    spot = shade(fur, 0.68)
    cream = "#fbf1e4"
    sk.shape(ribbon(cubic((CX + 170, 1400), (CX + 260, 1390), (CX + 300, 1320), (CX + 290, 1240), 12), 40, 26), fur)
    body = spline([(CX, 1040), (CX + 170, 1130), (CX + 210, 1380), (CX + 130, 1450), (CX - 130, 1450), (CX - 210, 1380),
                   (CX - 170, 1130)], True, 10)
    sk.shape(body, fur)
    sk.shade(ellipse((CX, 1260), 90, 130), cream, 220)
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 75, 1440), 62, 34), fur)
        sk.line([[(CX + s * 75 - 15, 1425), (CX + s * 75 - 15, 1452)], [(CX + s * 75 + 15, 1425), (CX + s * 75 + 15, 1452)]],
                None, 3.5)
    collar = ellipse((CX, 1010), 165, 75, a0=math.pi * 0.12, a1=math.pi * 0.88, n=20)
    sk.shape(ribbon(collar, 30, 30, False), jitter("#e63946", rng))
    sk.shape(circle((CX, 1110), 26), "#ffd166", width=4)
    head = (CX, 880)
    sk.shape(ellipse(head, 210, 180), fur)
    sk.shade(ellipse((CX - 85, 850), 70, 62), spot, 255)
    sk.shape(ellipse((CX, 965), 105, 72), cream)
    sk.shape(spline([(CX - 30, 920), (CX + 30, 920), (CX, 955)], True, 4), "#2b2d42", width=4)
    sk.detail(ellipse((CX - 8, 926), 9, 5), "#ffffff")
    sk.line(quad((CX, 955), (CX - 25, 1000), (CX - 55, 975), 8), None, 4.5)
    sk.line(quad((CX, 955), (CX + 25, 1000), (CX + 55, 975), 8), None, 4.5)
    sk.shape(ellipse((CX + 22, 1005), 22, 26), "#ff7aa2", width=4)
    _eyes(sk, CX, 850, 80, 25, blush_dx=135)
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 205, 900), 62, 135, rot=-s * 18), spot)
    bx = CX - 300
    bone = "#fff6e0"
    for dx in (-55, 55):
        for dy in (-17, 17):
            sk.shape(circle((bx + dx, 1395 + dy), 22), bone, width=4)
    sk.shape(rect(bx - 55, 1382, bx + 55, 1408), bone, width=4)
    return sk.scene(dur, hold)


# -- treats -----------------------------------------------------------------------------

def pizza(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    sk.shape(circle((CX, 1020), 360), "#ffffff")
    sk.shade(circle((CX, 1020), 300), "#000000", 18)
    tip_y, top_y, hw = 1330, 720, 270
    arc = [(CX + hw - 2 * hw * i / 20, top_y - 45 * math.sin(math.pi * i / 20)) for i in range(21)]
    cheese = jitter("#ffcf56", rng)
    sk.shape([(CX, tip_y)] + arc, cheese)
    for _ in range(6):
        y = rng.uniform(800, 1180)
        w = hw * (tip_y - y) / (tip_y - top_y) * 0.7
        sk.shade(ellipse((CX + rng.uniform(-w, w), y), rng.uniform(16, 26), rng.uniform(10, 16)), "#fff2b3", 200)
    spots = []
    for y, u in ((830, -0.5), (850, 0.45), (960, 0.0), (1080, -0.3), (1100, 0.4), (1210, 0.0)):
        w = hw * (tip_y - y) / (tip_y - top_y)
        spots.append((CX + u * w * 0.85 + rng.uniform(-10, 10), y + rng.uniform(-15, 15)))
    pep = jitter("#c0392b", rng)
    for i, p in enumerate(spots):
        r = rng.uniform(34, 44) * (1 - 0.25 * (p[1] > 1150))
        sk.shape(circle(p, r), pep, width=4.5)
        sk.shade(circle((p[0] - r * 0.3, p[1] - r * 0.3), r * 0.25), "#ffffff", 90)
    for _ in range(3):
        y = rng.uniform(880, 1150)
        w = hw * (tip_y - y) / (tip_y - top_y) * 0.6
        x = CX + rng.uniform(-w, w)
        a = rng.uniform(0, 2 * math.pi)
        sk.shape(leaf((x, y), (x + 50 * math.cos(a), y + 50 * math.sin(a)), 14), "#3f9d4f", width=3.5)
    crust = jitter("#d9944a", rng)
    sk.shape(ribbon(arc, 70, 70, False), crust)
    for i in (4, 9, 14):
        sk.shade(ellipse(arc[i], 22, 9, rot=-math.degrees(math.atan2(arc[i + 1][1] - arc[i][1], arc[i][0] - arc[i + 1][0]))),
                 "#ffffff", 80)
    for _ in range(6):
        a = rng.uniform(0, 2 * math.pi)
        p = (CX + 320 * math.cos(a), 1020 + 320 * math.sin(a))
        sk.detail(circle(p, rng.uniform(5, 8)), shade(crust, 0.85))
    return sk.scene(dur, hold)


def bonsai(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.7)
    bark = jitter("#7a5134", rng)
    flip = rng.choice((-1, 1))

    def X(dx):
        return CX + flip * dx

    trunk = cubic((X(20), 1230), (X(-180), 1080), (X(200), 950), (X(-30), 800), 24)
    sk.shape(ribbon(trunk, 95, 38, False), bark)
    sk.line([[trunk[i], trunk[i + 4]] for i in (2, 9, 15)], shade(bark, 0.6), 4, together=True)
    green = jitter(rng.choice(["#3f8f4f", "#4caf50", "#2d6a4f"]), rng)
    pads = ((-220, 900, 270), (210, 990, 250), (-40, 740, 320), (190, 800, 200))
    for dx, y, w in pads:
        sk.shape(ribbon(cubic(trunk[12], ((trunk[12][0] + X(dx)) / 2, y + 40), ((trunk[12][0] + X(dx)) / 2, y + 30), (X(dx), y + 10), 10),
                        28, 14), bark)
    for dx, y, w in pads:
        pad = transform(blob(rng, (X(dx), y), w / 2, 9, 0.12), (X(dx), y), sx=1, sy=0.5)
        sk.shape(pad, shade(green, rng.uniform(0.92, 1.1)))
        sk.shade(ellipse((X(dx), y + w * 0.14), w * 0.36, w * 0.08), "#000000", 45)
    if rng.random() < 0.5:
        for _ in range(10):
            dx, y, w = rng.choice(pads)
            sk.detail(circle((X(dx) + rng.uniform(-w / 3, w / 3), y + rng.uniform(-10, 25)), 9), "#ffb3c6")
    sk.shape(spline([(CX - 250, 1240), (CX - 120, 1195), (CX + 120, 1200), (CX + 250, 1240)], False, 6) + [(CX + 250, 1250), (CX - 250, 1250)],
             jitter("#6a994e", rng))
    pot = jitter(rng.choice(["#3d5a80", "#b5651d", "#6d597a", "#2a9d8f"]), rng)
    for x in (CX - 190, CX + 140):
        sk.shape(rect(x, 1370, x + 50, 1400, 6), shade(pot, 0.7))
    sk.shape([(CX - 260, 1250), (CX + 260, 1250), (CX + 210, 1380), (CX - 210, 1380)], pot)
    sk.shade([(CX + 140, 1250), (CX + 260, 1250), (CX + 210, 1380), (CX + 110, 1380)], "#000000", 40)
    sk.shape(rect(CX - 290, 1225, CX + 290, 1260, 10), shade(pot, 1.12))
    for _ in range(5):
        sk.detail(circle((CX + rng.uniform(-220, 220), rng.uniform(1205, 1218)), rng.uniform(6, 9)), "#c9ccd6")
    return sk.scene(dur, hold)


def birthday_cake(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    sk.shape(rect(CX - 50, 1370, CX + 50, 1430), "#e8e8ee")
    sk.shape(ellipse((CX, 1360), 330, 50), "#ffffff")
    h0 = rng.random()
    cream = "#fff6e8"

    def tier(x0, x1, y0, y1, color):
        sk.shape(rect(x0, y0, x1, y1, 14), color)
        sk.shade(rect(x1 - (x1 - x0) * 0.18, y0 + 10, x1 - 6, y1 - 6, 8), "#000000", 30)
        n = int((x1 - x0) / 55)
        bottom = []
        for k in range(n + 1):
            x = lerp(x1 + 4, x0 - 4, k / n)
            bottom.append((x, y0 + (60 if k % 2 else 36) + rng.uniform(-6, 6)))
        sk.shape([(x0 - 6, y0 - 8), (x1 + 6, y0 - 8)] + spline(bottom, False, 5), cream)
        for _ in range(int((x1 - x0) / 40)):
            x, y = rng.uniform(x0 + 25, x1 - 25), rng.uniform(y0 + 80, y1 - 20)
            b = rng.uniform(0, math.pi)
            sk.line([(x - 9 * math.cos(b), y - 9 * math.sin(b)), (x + 9 * math.cos(b), y + 9 * math.sin(b))],
                    pal.at(rng.random(), 1.05), 6, phase="detail", tool="brush")

    tier(CX - 260, CX + 260, 1110, 1350, pal.at(h0))
    tier(CX - 180, CX + 180, 910, 1110, pal.at(h0 + 0.35))
    n = rng.randint(3, 5)
    for k in range(n):
        x = lerp(CX - 120, CX + 120, k / (n - 1))
        cc = pal.at(h0 + 0.2 * k)
        sk.shape(rect(x - 13, 790, x + 13, 905, 5), cc, width=4)
        for y in (815, 855):
            sk.shade([(x - 13, y), (x + 13, y - 12), (x + 13, y + 2), (x - 13, y + 14)], "#ffffff", 170)
        sk.line([(x, 790), (x, 770)], None, 4)
        sk.shape(spline([(x, 690), (x + 22, 745), (x, 772), (x - 22, 745)], True, 6), "#ff9f1c", width=4)
        sk.shade(ellipse((x, 750), 8, 14), "#ffe066", 255)
    for _ in range(12):
        c = (CX + rng.uniform(-370, 370), rng.uniform(640, 1300))
        if math.dist(c, (CX, 990)) < 390 and not (CX - 290 < c[0] < CX + 290 and c[1] > 660):
            if rng.random() < 0.5:
                sk.detail(star(c, 16, 7), pal.at(rng.random()))
            else:
                sk.detail(circle(c, 8), pal.at(rng.random()))
    return sk.scene(dur, hold)


# -- things ------------------------------------------------------------------------------

def guitar(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    rot = rng.choice((-1, 1)) * rng.uniform(20, 30)

    def T(pts):
        return transform(pts, (CX, 1000), 1, rot)

    wood = jitter(rng.choice(["#d98c45", "#c0392b", "#e9b96e", "#3d5a80"]), rng)
    neck = "#7a4b2a"
    sk.shape(T([(CX - 50, 300), (CX + 50, 300), (CX + 40, 405), (CX - 40, 405)]), shade(neck, 0.85))
    for s in (-1, 1):
        for y in (325, 355, 385):
            sk.shape(T(circle((CX + s * 62, y), 11)), "#d6d6de", width=3)
    sk.shape(T(rect(CX - 32, 400, CX + 32, 830)), neck)
    sk.line([T([(CX - 32, y), (CX + 32, y)]) for y in (440, 490, 545, 605, 670, 740, 815)], "#d6d6de", 3, together=True)
    side = [(CX + 200, 1260), (CX + 185, 1110), (CX + 125, 1030), (CX + 150, 920), (CX + 95, 805)]
    body = [(CX, 1385)] + side + [(CX, 780)] + [(2 * CX - x, y) for x, y in reversed(side)]
    sk.shape(T(spline(body, True, 8)), wood)
    sk.shade(T(spline([(CX + 120, 1060), (CX + 175, 1120), (CX + 185, 1260), (CX + 90, 1340)], True, 6)), "#000000", 35)
    sk.shade(T(ellipse((CX - 110, 900), 22, 50)), "#ffffff", 90)
    hole = T(circle((CX, 960), 62))
    sk.shape(hole, "#2b1d14")
    ring = T(circle((CX, 960), 78))
    sk.detail_line(ring + ring[:1], shade(wood, 0.6), 6)
    sk.shape(T(rect(CX - 80, 1180, CX + 80, 1215, 8)), "#4a2c1a")
    sk.line([T([(CX + dx, 1197), (CX + dx, 400)]) for dx in (-20, -12, -4, 4, 12, 20)], "#f2f2f2", 2.5,
            phase="detail", together=True)
    s = 1 if rot < 0 else -1
    for c, k in (((CX + s * 270, 760), 1.0), ((CX + s * 320, 920), 0.75), ((CX - s * 300, 1280), 0.9)):
        _note(sk, c, pal.at(rng.random()), k)
    for _ in range(4):
        sk.detail(star((CX + rng.uniform(-340, 340), rng.uniform(650, 1350)), 14, 6), pal.at(rng.random()))
    return sk.scene(dur, hold)


def robot(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    sk.shade(ellipse((CX, 1405), 250, 34), "#000000", 30)
    metal = jitter(rng.choice(["#9fb4c7", "#b8c4d6", "#a0c4b8", "#c9b8d6"]), rng)
    accent = pal.at(rng.random())
    glow = "#6ff3ff"
    for x in (CX - 110, CX + 50):
        sk.shape(rect(x, 1250, x + 60, 1360), shade(metal, 0.85))
        sk.shape(rect(x - 30, 1350, x + 90, 1405, 22), accent)
    up = cubic((CX + 170, 1070), (CX + 260, 1050), (CX + 300, 970), (CX + 300, 890), 12)
    down = cubic((CX - 170, 1080), (CX - 250, 1120), (CX - 270, 1200), (CX - 260, 1260), 12)
    for arm in (up, down):
        sk.shape(ribbon(arm, 44, 40, False), shade(metal, 0.9))
        sk.shape(circle(arm[-1], 34), accent)
    sk.shape(rect(CX - 40, 970, CX + 40, 1035), shade(metal, 0.8))
    sk.shape(rect(CX - 180, 1020, CX + 180, 1270, 30), metal)
    sk.shade(rect(CX + 120, 1035, CX + 170, 1255, 20), "#000000", 30)
    sk.shape(rect(CX - 110, 1070, CX + 110, 1200, 16), shade(metal, 0.7))
    for i, col in enumerate(("#ff595e", "#ffca3a", "#8ac926")):
        sk.shape(circle((CX - 60 + 60 * i, 1110), 18), col, width=3.5)
    sk.line([(CX - 80 + 160 * i / 10, 1165 - (14 if i % 2 else 0)) for i in range(11)], glow, 5, phase="detail", tool="brush")
    for s in (-1, 1):
        sk.shape(rect(CX + s * 215 - 18, 800, CX + s * 215 + 18, 900, 10), accent)
    sk.shape(rect(CX - 200, 720, CX + 200, 990, 50), metal)
    sk.shape(rect(CX - 150, 770, CX + 150, 940, 36), "#1d2b3a")
    for s in (-1, 1):
        sk.shape(circle((CX + s * 65, 840), 30), glow, width=4)
        sk.detail(circle((CX + s * 65 - 9, 831), 9), "#ffffff")
    sk.line(quad((CX - 50, 890), (CX, 925), (CX + 50, 890), 10), glow, 7)
    for s in (-1, 1):
        for y in (745, 965):
            sk.detail(circle((CX + s * 175, y), 7), shade(metal, 0.6))
    sk.line([(CX, 720), (CX, 625)], None, 6)
    sk.shape(circle((CX, 612), 24), jitter("#ff4d6d", rng))
    for _ in range(5):
        c = (CX + rng.uniform(-340, 340), rng.uniform(620, 1300))
        if abs(c[0] - CX) > 260:
            sk.detail(star(c, 16, 6), pal.at(rng.random()))
    return sk.scene(dur, hold)
