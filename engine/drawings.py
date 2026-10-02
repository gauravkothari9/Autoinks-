"""Speed-drawing pictures: each one is drawn stroke by stroke on paper, then colored in.

A picture is a function picture(rng, pal, duration, hold) that builds a Sketch back to front and returns
its scene. Sizes, colors, counts and positions come from rng, so every seed draws a different version.
"""

import math

from .art import (blend, circle, cloud, cubic, ellipse, hsv, jitter, lerp, mirror, quad, shade, spline, star,
                  transform)
from .sketch import Sketch

FX0, FY0, FX1, FY1 = 140, 430, 940, 1540   # picture frame inside the paper sheet
CX = (FX0 + FX1) / 2


def rect(x0, y0, x1, y1, r=0.0):
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        out += ellipse((cx, cy), r, r, a0=math.radians(a0), a1=math.radians(a0 + 90), n=6)
    return out


def ribbon(path, w0, w1=None, round_end=True):
    """Closed outline around a center line, w0 wide at the start and w1 at the end (tails, stems, trunks)."""
    w1 = w0 if w1 is None else w1
    n = len(path)
    left, right = [], []
    for i, p in enumerate(path):
        a, b = path[max(0, i - 1)], path[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = lerp(w0, w1, i / (n - 1)) / 2
        left.append((p[0] + nx * w, p[1] + ny * w))
        right.append((p[0] - nx * w, p[1] - ny * w))
    cap = []
    if round_end and w1 > 2:
        ex, ey = path[-1]
        dx, dy = path[-1][0] - path[-2][0], path[-1][1] - path[-2][1]
        a = math.atan2(dy, dx)
        cap = [(ex + w1 / 2 * math.cos(a + math.pi / 2 - math.pi * k / 8),
                ey + w1 / 2 * math.sin(a + math.pi / 2 - math.pi * k / 8)) for k in range(1, 8)]
    return left + cap + right[::-1]


def leaf(base, tip, width):
    """Pointed leaf from base to tip."""
    mx, my = (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * width, dx / d * width
    return quad(base, (mx + nx, my + ny), tip, 12) + quad(tip, (mx - nx, my - ny), base, 12)[1:-1]


def frame(sk, sky, r=22):
    sk.bounds = (FX0, FY0, FX1, FY1)  # everything after this stays inside the frame
    return sk.shape(rect(FX0, FY0, FX1, FY1, r), sky)


def frame_clip(pts):
    """Keep a shape's points inside the picture frame (for ground and water bands)."""
    return [(min(FX1, max(FX0, x)), min(FY1, max(FY0, y))) for x, y in pts]


def birds(sk, rng, n, x0, x1, y0, y1, color=None):
    for _ in range(n):
        x, y, s = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(16, 30)
        sk.line([quad((x - s, y - s * 0.3), (x - s * 0.45, y - s * 0.65), (x, y), 6),
                 quad((x, y), (x + s * 0.45, y - s * 0.65), (x + s, y - s * 0.3), 6)], color, 4.5)


def pine(sk, x, base, h, green):
    sk.shape(rect(x - h * 0.05, base - h * 0.2, x + h * 0.05, base), jitter("#7a5134", sk.rng, 0.03), width=4)
    for i in range(3):
        bottom = base - h * 0.14 - i * h * 0.24
        top = bottom - h * 0.4
        w = h * (0.34 - 0.07 * i)
        pts = [(x, top), (x + w, bottom), (x - w, bottom)]
        sk.shape(pts, shade(green, 1 + 0.06 * i), width=4.5)
        sk.shade([(x, top), (x + w, bottom), (x + w * 0.2, bottom)], "#000000", 40)


# -- landscapes ----------------------------------------------------------------------

def mountain_lake(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    lake_y = rng.uniform(1080, 1160)
    frame(sk, jitter("#a8daf5", rng))
    sk.shade(rect(FX0, lake_y - 300, FX1, lake_y), "#ffffff", 70)
    sun = (rng.uniform(FX0 + 200, FX1 - 200), rng.uniform(600, 720))
    sk.shape(circle(sun, rng.uniform(65, 90)), jitter("#ffd166", rng))
    for _ in range(rng.randint(2, 3)):
        sk.shape(cloud((rng.uniform(FX0 + 150, FX1 - 150), rng.uniform(530, 760)), rng.uniform(180, 260), 70), "#ffffff")
    for layer, (col, top, peaks) in enumerate(((jitter("#8fa6c9", rng), 720, 3), (jitter("#5d7aa8", rng), 820, 2))):
        xs = sorted(rng.uniform(FX0 + 60, FX1 - 60) for _ in range(peaks))
        ridge = [(FX0, lake_y - rng.uniform(150, 260))]
        for x in xs:
            ridge.append((x - rng.uniform(90, 150), lake_y - rng.uniform(140, 230)))
            ridge.append((x, top + rng.uniform(-40, 60) + layer * 30))
        ridge.append((FX1, lake_y - rng.uniform(150, 260)))
        ridge.sort()
        poly = ridge + [(FX1, lake_y), (FX0, lake_y)]
        sk.shape(poly, col)
        for i in range(1, len(ridge) - 1):
            ax, ay = ridge[i]
            if ay < ridge[i - 1][1] and ay < ridge[i + 1][1]:
                l, r = ridge[i - 1], ridge[i + 1]
                sk.shade([(ax, ay), r, (lerp(ax, r[0], 0.35), lake_y)], "#0b1d3a", 55)
                k = 0.3
                pl, pr = (lerp(ax, l[0], k), lerp(ay, l[1], k)), (lerp(ax, r[0], k), lerp(ay, r[1], k))
                cap = [(ax, ay), pr, (lerp(pl[0], pr[0], 0.75), pr[1] - 18), (lerp(pl[0], pr[0], 0.5), pl[1] + 14),
                       (lerp(pl[0], pr[0], 0.25), pl[1] - 12), pl]
                sk.shape(cap, "#ffffff", width=4)
    water = jitter("#4aa3d8", rng)
    sk.shape(rect(FX0, lake_y, FX1, FY1 - 160), water)
    for _ in range(7):
        x, y = rng.uniform(FX0 + 60, FX1 - 160), rng.uniform(lake_y + 30, FY1 - 200)
        sk.line([(x, y), (x + rng.uniform(60, 140), y)], "#ffffff", 5, phase="detail", tool="brush")
    sk.shade(rect(sun[0] - 50, lake_y + 10, sun[0] + 50, FY1 - 180), "#ffe9a8", 70)
    ground = jitter("#7cc46a", rng)
    shore = spline([(FX0 - 10, FY1 - 150), (CX - 150, FY1 - 190), (CX + 200, FY1 - 160), (FX1 + 10, FY1 - 200),
                    (FX1 + 10, FY1 + 10), (FX0 - 10, FY1 + 10)], True, 8)
    sk.shape(frame_clip(shore), ground)
    for x in (FX0 + rng.uniform(70, 120), FX1 - rng.uniform(70, 120), FX1 - rng.uniform(190, 240)):
        pine(sk, x, FY1 - rng.uniform(40, 90), rng.uniform(300, 380), jitter("#2f7d4f", rng))
    for _ in range(14):
        x, y = rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY1 - 120, FY1 - 25)
        sk.line([(x - 8, y), (x - 3, y - 18), (x, y), (x + 4, y - 22), (x + 9, y)], shade(ground, 0.6), 4,
                phase="detail", tool="brush")
    birds(sk, rng, rng.randint(2, 4), FX0 + 100, FX1 - 100, 520, 700)
    return sk.scene(dur, hold)


def sunset_beach(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sea_y = rng.uniform(1020, 1100)
    frame(sk, jitter("#ffb26b", rng))
    sk.shade(rect(FX0, FY0, FX1, FY0 + 260, 22), pal.at(rng.random()), 80)
    sk.shade(rect(FX0, sea_y - 220, FX1, sea_y), "#fff1a8", 110)
    sun = (rng.uniform(CX - 180, CX + 180), sea_y)
    sk.shape(ellipse(sun, 130, 130, a0=math.pi, a1=2 * math.pi, n=40), jitter("#fff06b", rng))
    for _ in range(rng.randint(2, 3)):
        sk.shape(cloud((rng.uniform(FX0 + 150, FX1 - 150), rng.uniform(520, 820)), rng.uniform(170, 250), 55),
                 jitter("#ffd6c9", rng))
    sea = jitter("#3d7fc4", rng)
    sk.shape(rect(FX0, sea_y, FX1, FY1), sea)
    for i in range(8):
        w = 140 - i * 8
        y = sea_y + 18 + i * 24
        sk.shade(rect(sun[0] - w, y, sun[0] + w, y + 9), "#ffe28a", 190)
    sand = jitter("#f2d49b", rng)
    beach = spline([(FX0 - 10, FY1 - 230), (CX - 100, FY1 - 280), (FX1 + 10, FY1 - 170), (FX1 + 10, FY1 + 10),
                    (FX0 - 10, FY1 + 10)], True, 10)
    sk.shape(frame_clip(beach), sand)
    for _ in range(5):
        x, y = rng.uniform(FX0 + 50, FX1 - 200), rng.uniform(sea_y + 40, FY1 - 320)
        sk.line(quad((x, y), (x + 50, y - 16), (x + 100, y), 8), "#ffffff", 5, phase="detail", tool="brush")
    # Palm tree leaning over the beach.
    side = rng.choice((-1, 1))
    bx = CX + side * rng.uniform(220, 290)
    top = (bx - side * rng.uniform(130, 190), rng.uniform(720, 800))
    trunk = cubic((bx, FY1 - 160), (bx, FY1 - 400), (top[0] + side * 60, top[1] + 200), top, 24)
    sk.shape(ribbon(trunk, 58, 30, False), jitter("#9a6b43", rng))
    for i in range(3, 22, 3):
        p, q = trunk[i], trunk[i + 1]
        sk.line([(p[0] - 24, p[1]), (q[0] + 4, q[1] + 6)], shade("#9a6b43", 0.6), 4)
    green = jitter("#3f9d4f", rng)
    for k, ang in enumerate((-160, -120, -60, -20, -95)):
        a = math.radians(ang + rng.uniform(-8, 8))
        tip = (top[0] + 260 * math.cos(a), top[1] + 260 * math.sin(a) + 90)
        mid = (top[0] + 150 * math.cos(a), top[1] + 150 * math.sin(a) - 40)
        pts = quad(top, (mid[0] - 30, mid[1] - 40), tip, 12) + quad(tip, (mid[0] + 25, mid[1] + 30), top, 12)[1:-1]
        sk.shape(pts, shade(green, 1 - 0.07 * (k % 2)), width=4.5)
    for c in ((top[0] - 18, top[1] + 22), (top[0] + 16, top[1] + 28)):
        sk.shape(circle(c, 22), "#6b4a2b", width=4)
    birds(sk, rng, 3, FX0 + 120, FX1 - 120, 560, 760, "#5a3550")
    return sk.scene(dur, hold)


def lighthouse(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sea_y = 1190
    frame(sk, jitter("#2c3e75", rng))
    sk.shade(rect(FX0, sea_y - 330, FX1, sea_y), "#ff9f6e", 120)
    for _ in range(18):
        sk.detail(star((rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY0 + 30, 760)), rng.uniform(7, 13), 3.5),
                  "#fff6c9")
    moon = (rng.uniform(FX0 + 130, CX - 100), rng.uniform(560, 650))
    sk.shape(circle(moon, 60), "#fdf3c4")
    sk.shape(rect(FX0, sea_y, FX1, FY1), jitter("#1f5d8c", rng))
    for _ in range(9):
        x, y = rng.uniform(FX0 + 30, FX1 - 140), rng.uniform(sea_y + 40, FY1 - 40)
        sk.line(quad((x, y), (x + 50, y - 14), (x + 100, y), 6), "#bfe3ff", 4.5, phase="detail", tool="brush")
    lx = rng.uniform(CX + 30, CX + 140)
    rock = spline([(lx - 230, sea_y + 140), (lx - 160, sea_y + 20), (lx + 40, sea_y - 20), (lx + 230, sea_y + 40),
                   (lx + 270, sea_y + 160), (lx, sea_y + 200)], True, 8)
    sk.shape(rock, jitter("#6d6875", rng))
    sk.shade(rock[len(rock) // 2:], "#000000", 50)
    base, tw, top_y, top_w = sea_y + 10, 90, 760, 60
    tower = [(lx - tw, base), (lx - top_w, top_y), (lx + top_w, top_y), (lx + tw, base)]
    sk.shape(tower, "#f7f3ea")
    red = jitter("#d6413b", rng)
    bands = 4
    for i in range(bands):
        y0 = lerp(top_y, base, (2 * i + 1) / (2 * bands))
        y1 = lerp(top_y, base, (2 * i + 2) / (2 * bands))

        def hw(y):
            return lerp(top_w, tw, (y - top_y) / (base - top_y))
        sk.shade([(lx - hw(y0), y0), (lx + hw(y0), y0), (lx + hw(y1), y1), (lx - hw(y1), y1)], red, 255)
    sk.shade([(lx + 10, top_y), (lx + top_w, top_y), (lx + tw, base), (lx + 20, base)], "#000000", 35)
    sk.shape(rect(lx - top_w - 22, top_y - 26, lx + top_w + 22, top_y), "#3a3a48")
    lamp = rect(lx - top_w + 8, top_y - 120, lx + top_w - 8, top_y - 26)
    sk.shape(lamp, "#ffe066")
    sk.line([(lx, top_y - 120), (lx, top_y - 26)], None, 4)
    sk.shape([(lx - top_w - 10, top_y - 118), (lx, top_y - 200), (lx + top_w + 10, top_y - 118)], red)
    sk.shape(rect(lx - 26, base - 120, lx + 26, base, 26), "#4b3b36")
    beam_y = top_y - 73
    sk.shade([(lx - 40, beam_y - 30), (FX0, beam_y - 150), (FX0, beam_y + 120), (lx - 40, beam_y + 30)], "#fff3a0", 90,
             phase="detail")
    sk.shade([(lx + 40, beam_y - 30), (FX1, beam_y - 110), (FX1, beam_y + 90), (lx + 40, beam_y + 30)], "#fff3a0", 70,
             phase="detail")
    birds(sk, rng, 3, FX0 + 150, CX, 800, 950, "#f5f0ff")
    return sk.scene(dur, hold)


def cottage(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#bfe6ff", rng))
    sk.shape(circle((rng.uniform(FX0 + 130, FX0 + 260), rng.uniform(560, 640)), 70), jitter("#ffd166", rng))
    sk.shape(cloud((rng.uniform(CX, FX1 - 150), rng.uniform(540, 640)), 240, 70), "#ffffff")
    far = jitter("#9ed49a", rng)
    sk.shape(frame_clip(ellipse((FX0 + 180, 1270), 420, 210)), far)
    sk.shape(frame_clip(ellipse((FX1 - 120, 1290), 460, 230)), shade(far, 0.92))
    ground = jitter("#79c267", rng)
    sk.shape(rect(FX0, 1250, FX1, FY1), ground)
    hx = rng.uniform(CX - 140, CX - 40)
    x0, x1, y0, y1 = hx - 190, hx + 190, 990, 1300
    wall = jitter(rng.choice(["#f6e3c4", "#fbd6d2", "#d9ecf2", "#fff1b5"]), rng)
    sk.shape(rect(x1 - 110, 790, x1 - 50, 960), "#b05a4a")  # chimney behind the roof
    for i in range(3):
        sk.shape(circle((x1 - 80 + i * 30, 740 - i * 70), 26 + i * 12), "#e9edf2", width=4)
    sk.shape(rect(x0, y0, x1, y1), wall)
    sk.shade(rect(x1 - 70, y0, x1, y1), "#000000", 30)
    roof = jitter(rng.choice(["#d1495b", "#3f72af", "#6a4c93", "#e76f51"]), rng)
    sk.shape([(x0 - 50, y0 + 10), (hx, 820), (x1 + 50, y0 + 10)], roof)
    for k in range(1, 4):
        sk.line([(lerp(x0 - 50, hx, k / 4), lerp(y0 + 10, 820, k / 4)), (lerp(x1 + 50, hx, k / 4), lerp(y0 + 10, 820, k / 4))],
                shade(roof, 0.7), 4)
    door = jitter(rng.choice(["#7b4b2a", "#2a6f97", "#c44536"]), rng)
    sk.shape(rect(hx - 50, y1 - 170, hx + 50, y1, 10), door)
    sk.detail(circle((hx + 30, y1 - 85), 8), "#ffd166")
    for wx in (x0 + 70, x1 - 70):
        win = rect(wx - 45, 1060, wx + 45, 1150, 6)
        sk.shape(win, "#9fd8ff")
        sk.line([[(wx, 1060), (wx, 1150)], [(wx - 45, 1105), (wx + 45, 1105)]], None, 4)
        sk.shade([(wx - 45, 1060), (wx - 10, 1060), (wx - 45, 1100)], "#ffffff", 120)
    path = [(hx - 50, y1), (hx + 50, y1), (hx + 150, FY1), (hx - 120, FY1)]
    sk.shape(path, "#e2c79a")
    tx = min(x1 + rng.uniform(150, 200), FX1 - 180)
    sk.shape(ribbon([(tx, 1340), (tx + 5, 1150), (tx, 1000)], 50, 34, False), "#8a5a3b")
    crown = jitter("#3e9b4f", rng)
    for dx, dy, r in ((-60, 940, 110), (70, 950, 100), (0, 860, 120)):
        sk.shape(circle((tx + dx, dy), r), shade(crown, 1 - 0.05 * (dx > 0)))
    for _ in range(5):
        sk.detail(circle((tx + rng.uniform(-110, 110), rng.uniform(850, 1000)), 13), "#e63946")
    for fx in range(int(FX0 + 30), int(x0 - 20), 48):
        sk.shape(rect(fx, 1290, fx + 26, 1400, 4), "#fff8ee", width=4)
    if x0 - 20 > FX0 + 60:
        sk.line([[(FX0 + 20, 1320), (x0 - 25, 1320)], [(FX0 + 20, 1370), (x0 - 25, 1370)]], None, 5)
    for _ in range(12):
        c = (rng.uniform(FX0 + 40, FX1 - 40), rng.uniform(1420, FY1 - 30))
        sk.detail(star(c, 13, 6, 5), pal.at(rng.random()))
    birds(sk, rng, 2, CX, FX1 - 80, 680, 780)
    return sk.scene(dur, hold)


# -- animals ---------------------------------------------------------------------------

def cute_cat(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    fur = jitter(rng.choice(["#f4a259", "#b8b8bf", "#f1d3a2", "#8d6e63", "#fafafa"]), rng)
    dark = shade(fur, 0.72)
    sk.shape(circle((CX, 990), 400), blend(pal.at(rng.random()), "#ffffff", 0.45))
    side = rng.choice((-1, 1))
    tail = cubic((CX + side * 140, 1450), (CX + side * 360, 1460), (CX + side * 380, 1180), (CX + side * 300, 1060), 24)
    sk.shape(ribbon(tail, 60, 50), fur)
    body = spline([(CX, 1000), (CX + 170, 1130), (CX + 220, 1380), (CX + 170, 1480), (CX - 170, 1480),
                   (CX - 220, 1380), (CX - 170, 1130)], True, 10)
    sk.shape(body, fur)
    sk.shade(ellipse((CX, 1320), 110, 140), "#ffffff", 120)
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 80, 1450), 62, 42), fur)
        sk.line([[(CX + s * 80 - 15, 1430), (CX + s * 80 - 15, 1470)], [(CX + s * 80 + 15, 1430), (CX + s * 80 + 15, 1470)]],
                None, 4)
    hy = 860
    for s in (-1, 1):
        ear = [(CX + s * 70, hy - 130), (CX + s * 185, hy - 260), (CX + s * 200, hy - 70)]
        sk.shape(ear, fur)
        sk.shape(transform(ear, (CX + s * 160, hy - 140), 0.55), "#ffb3c1", width=4)
    head = ellipse((CX, hy), 225, 185)
    sk.shape(head, fur)
    for k in range(3):
        x = CX + (k - 1) * 45
        sk.shade([(x - 14, hy - 185), (x + 14, hy - 185), (x, hy - 120)], dark, 200)
    for s in (-1, 1):
        sk.shade(ellipse((CX + s * 140, hy + 60), 40, 26), "#ff8fab", 110)
    eye_y = hy - 10
    closed = rng.random() < 0.25
    for s in (-1, 1):
        ex = CX + s * 88
        if closed:
            sk.line(quad((ex - 34, eye_y), (ex, eye_y + 30), (ex + 34, eye_y), 10), None, 7)
        else:
            sk.shape(ellipse((ex, eye_y), 36, 44), "#2b2d42")
            sk.detail(circle((ex - 11, eye_y - 15), 12), "#ffffff")
            sk.detail(circle((ex + 12, eye_y + 14), 5), "#ffffff")
    nose = [(CX - 18, hy + 40), (CX + 18, hy + 40), (CX, hy + 60)]
    sk.shape(nose, "#ff6f91", width=4)
    sk.line(quad((CX, hy + 60), (CX - 20, hy + 95), (CX - 46, hy + 75), 8) + [], None, 4.5)
    sk.line(quad((CX, hy + 60), (CX + 20, hy + 95), (CX + 46, hy + 75), 8), None, 4.5)
    for s in (-1, 1):
        for k in range(3):
            y = hy + 45 + k * 22
            sk.line([(CX + s * 120, y), (CX + s * 250, y - 25 + k * 25)], None, 3.5)
    for _ in range(3):
        c = (rng.uniform(FX0 + 60, FX1 - 60), rng.uniform(FY0 + 30, 560))
        sk.detail(star(c, 22, 9), pal.at(rng.random()))
    return sk.scene(dur, hold)


def owl(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#2b3a67", rng))
    for _ in range(22):
        sk.detail(star((rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY0 + 30, 1300)), rng.uniform(7, 12), 3), "#fff3b0")
    sk.shape(circle((CX + rng.uniform(-150, 150), 780), 230), "#fdf0c2")
    branch_y = 1370
    sk.shape(ribbon([(FX0 - 10, branch_y + 30), (CX, branch_y), (FX1 + 10, branch_y - 30)], 60, 40, False), "#6b4a2b")
    sk.shape(leaf((FX1 - 160, branch_y - 30), (FX1 - 60, branch_y - 130), 30), "#4caf50")
    sk.shape(leaf((FX0 + 140, branch_y + 20), (FX0 + 60, branch_y + 120), 30), "#4caf50")
    body_col = jitter(rng.choice(["#a47148", "#8d6e63", "#b08968", "#7f7f8f"]), rng)
    oy = 1060
    for s in (-1, 1):
        sk.shape([(CX + s * 90, oy - 240), (CX + s * 200, oy - 340), (CX + s * 190, oy - 180)], body_col)
    body = ellipse((CX, oy), 240, 300)
    sk.shape(body, body_col)
    sk.shape(ellipse((CX, oy + 100), 150, 170), blend(body_col, "#fff3e0", 0.6))
    for row in range(4):
        for k in range(3 + (row % 2)):
            x = CX - 75 + k * 50 - (row % 2) * 25
            y = oy + 30 + row * 50
            sk.line(quad((x - 18, y), (x, y + 18), (x + 18, y), 6), shade(body_col, 0.8), 4)
    for s in (-1, 1):
        wing = ellipse((CX + s * 210, oy + 60), 70, 190, rot=-s * 12)
        sk.shape(wing, shade(body_col, 0.85))
        sk.shade(ellipse((CX + s * 215, oy + 110), 35, 110, rot=-s * 12), "#000000", 40)
    for s in (-1, 1):
        sk.shape(circle((CX + s * 95, oy - 120), 98), blend(body_col, "#fff3e0", 0.75))
    for s in (-1, 1):
        ex = CX + s * 95
        sk.shape(circle((ex, oy - 120), 62), jitter("#ffc300", rng))
        sk.shape(circle((ex, oy - 115), 34), "#1d1d28")
        sk.detail(circle((ex - 12, oy - 128), 11), "#ffffff")
    sk.shape([(CX - 26, oy - 60), (CX + 26, oy - 60), (CX, oy - 10)], "#f4a261")
    for s in (-1, 1):
        for k in range(3):
            sk.shape(ellipse((CX + s * 70 + (k - 1) * 22, branch_y - 6), 14, 22), "#f4a261", width=4)
    return sk.scene(dur, hold)


def koi_pond(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    pc = (CX, 990)
    sk.shape(circle(pc, 410, n=90), jitter("#3fa7a3", rng))
    sk.shade(circle((CX - 90, 900), 260), "#ffffff", 35)
    for _ in range(rng.randint(3, 4)):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(250, 320)
        c = (pc[0] + r * math.cos(a), pc[1] + r * math.sin(a))
        rad = rng.uniform(70, 95)
        notch = rng.uniform(0, 2 * math.pi)
        pad = [c] + ellipse(c, rad, rad * 0.85, a0=notch + 0.35, a1=notch + 2 * math.pi - 0.35, n=24)
        sk.shape(pad, jitter("#5cb85c", rng))
        sk.line([[c, (c[0] + rad * 0.8 * math.cos(notch + k), c[1] + rad * 0.7 * math.sin(notch + k))] for k in (1.6, 3.1, 4.6)],
                shade("#5cb85c", 0.6), 3.5, together=True)
    if rng.random() < 0.8:
        a = rng.uniform(0, 2 * math.pi)
        c = (pc[0] + 260 * math.cos(a), pc[1] + 260 * math.sin(a))
        sk.shape(star(c, 46, 20, 6), "#ffb3c6")
        sk.shape(circle(c, 12), "#ffd166", width=4)
    base_a = rng.uniform(0, 360)
    for k in range(2):
        ang = base_a + 180 * k + rng.uniform(-20, 20)
        c = (pc[0] + 150 * math.cos(math.radians(ang + 90)), pc[1] + 150 * math.sin(math.radians(ang + 90)))
        _koi(sk, rng, c, ang, rng.uniform(150, 175), pal)
    for _ in range(6):
        c = (pc[0] + rng.uniform(-300, 300), pc[1] + rng.uniform(-300, 300))
        if math.dist(c, pc) < 360:
            ring = circle(c, rng.uniform(8, 14), n=16)
            sk.detail_line(ring + ring[:1], "#e8fbff", 3.5)
    return sk.scene(dur, hold)


def _koi(sk, rng, c, ang, size, pal):
    def T(pts):
        return transform([(c[0] + x * size, c[1] + y * size) for x, y in pts], c, 1, ang)
    white = "#fbf7f2"
    body_col = rng.choice([white, "#ff8c42", "#ffd166"])
    spot = rng.choice(["#e63946", "#ff6b35", "#1d1d28"])
    sk.shape(T(spline([(-0.7, 0), (-1.2, -0.38), (-1.08, 0), (-1.2, 0.38)], True, 8)), blend(body_col, spot, 0.3))
    for s in (-1, 1):
        sk.shape(T(ellipse((0.35, s * 0.3), 0.2, 0.09, rot=s * 35)), blend(body_col, spot, 0.2), width=4)
    top = [(1.0, 0), (0.85, -0.17), (0.5, -0.25), (0.0, -0.21), (-0.5, -0.11), (-0.78, -0.04)]
    body = top + [(x, -y) for x, y in reversed(top[1:])]
    sk.shape(T(spline(body, True, 8)), body_col)
    for _ in range(3):
        x = rng.uniform(-0.4, 0.55)
        sk.shade(T(ellipse((x, rng.uniform(-0.06, 0.06)), rng.uniform(0.1, 0.17), rng.uniform(0.07, 0.11), n=20)),
                 spot, 235)
    for s in (-1, 1):
        sk.detail(T(circle((0.75, s * 0.1), 0.035, n=12)), "#1d1d28")


def whale(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sea = jitter("#3a86c8", rng)
    sk.shape(circle((CX, 990), 410, n=90), jitter("#bde4ff", rng))
    water = [(x, 1130 + 18 * math.sin(x / 45)) for x in range(int(CX - 430), int(CX + 431), 12)]
    a = math.asin(140 / 409)
    sk.shape([p for p in water if math.dist(p, (CX, 990)) < 409] + ellipse((CX, 990), 409, 409, a0=a, a1=math.pi - a, n=40),
             sea)
    col = jitter(rng.choice(["#5b7fd6", "#6c63ff", "#4f9bd9", "#8e7dbe"]), rng)
    tail_x = CX + 250
    fluke = [(tail_x, 1000), (tail_x + 130, 830), (tail_x + 60, 900), (tail_x + 10, 930), (tail_x - 40, 860), (tail_x - 60, 990)]
    sk.shape(spline(fluke, True, 6), col)
    body = spline([(CX - 300, 1080), (CX - 260, 900), (CX - 80, 820), (CX + 120, 860), (tail_x + 10, 990),
                   (CX + 160, 1110), (CX - 120, 1150)], True, 10)
    sk.shape(body, col)
    belly = spline([(CX - 290, 1060), (CX - 120, 1120), (CX + 120, 1095), (CX - 50, 1150), (CX - 230, 1130)], True, 8)
    sk.shape(belly, blend(col, "#ffffff", 0.65), width=4)
    for k in range(4):
        x = CX - 230 + k * 60
        sk.line([(x, 1100 + k * 4), (x + 50, 1112 + k * 3)], shade(col, 0.6), 3.5)
    sk.shape(ellipse((CX - 40, 1060), 70, 30, rot=30), shade(col, 0.85))
    sk.shape(circle((CX - 190, 960), 20), "#1d1d28")
    sk.detail(circle((CX - 196, 952), 7), "#ffffff")
    sk.line(quad((CX - 290, 1020), (CX - 230, 1060), (CX - 170, 1030), 10), None, 5)
    sk.shade(ellipse((CX - 150, 1015), 26, 14), "#ff8fab", 140)
    sx, sy = CX - 110, 820
    for a in (-50, -20, 20, 50):
        r = math.radians(a - 90)
        end = (sx + 150 * math.cos(r), sy + 170 * math.sin(r))
        sk.line(quad((sx, sy), (sx + 30 * math.cos(r), end[1] + 40), end, 10), "#5fb4ff", 7)
        sk.detail(ellipse((end[0], end[1] + 18), 12, 17), "#8fd0ff")
    for _ in range(6):
        x = rng.uniform(CX - 330, CX + 330)
        y = rng.uniform(1190, 1330)
        sk.line(quad((x, y), (x + 40, y - 14), (x + 80, y), 6), "#ffffff", 4.5, phase="detail", tool="brush")
    return sk.scene(dur, hold)


def butterfly(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sk.shape(circle((CX, 990), 410, n=90), blend(pal.at(rng.random()), "#ffffff", 0.7))
    h0 = rng.random()
    c1, c2 = pal.at(h0), pal.at(h0 + 0.35)
    cy = 960
    for s in (-1, 1):
        up = spline([(CX, cy - 30), (CX + s * 120, cy - 260), (CX + s * 330, cy - 320), (CX + s * 360, cy - 150),
                     (CX + s * 220, cy + 10)], True, 10)
        lo = spline([(CX, cy + 10), (CX + s * 230, cy + 40), (CX + s * 290, cy + 230), (CX + s * 150, cy + 300),
                     (CX + s * 40, cy + 180)], True, 10)
        sk.shape(lo, c2)
        sk.shade(circle((CX + s * 180, cy + 170), 55), "#ffffff", 150)
        sk.shade(circle((CX + s * 180, cy + 170), 26), c1, 255)
        sk.shape(up, c1)
        sk.shade(spline([(CX + s * 60, cy - 60), (CX + s * 150, cy - 200), (CX + s * 260, cy - 230),
                         (CX + s * 200, cy - 100)], True, 8), shade(c1, 0.7), 140)
        for k in range(3):
            sk.shade(circle((CX + s * (230 + k * 40), cy - 260 + k * 50), 20 - k * 3), "#ffffff", 220)
    sk.shape(ellipse((CX, cy + 40), 24, 170), "#3d2c3e")
    sk.shape(circle((CX, cy - 150), 36), "#3d2c3e")
    for s in (-1, 1):
        end = (CX + s * 110, cy - 330)
        sk.line(quad((CX + s * 10, cy - 180), (CX + s * 20, cy - 300), end, 12), "#3d2c3e", 5)
        sk.detail(circle(end, 12), "#3d2c3e")
    for s in (-1, 1):
        sk.detail(circle((CX + s * 13, cy - 160), 7), "#ffffff")
    for _ in range(rng.randint(3, 4)):
        fx, fy = rng.uniform(CX - 320, CX + 320), rng.uniform(1300, 1360)
        if math.dist((fx, fy), (CX, 990)) < 360:
            sk.shape(star((fx, fy), 42, 26, 5), pal.at(rng.random(), 1.05), width=4)
            sk.shape(circle((fx, fy), 13), "#ffd166", width=4)
    return sk.scene(dur, hold)


# -- objects and plants ------------------------------------------------------------------

def sunflower(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sk.shape(circle((CX, 990), 410, n=90), blend(pal.at(rng.random()), "#ffffff", 0.65))
    fc = (CX + rng.uniform(-40, 40), 800)
    stem = cubic((CX, 1330), (CX - 30, 1150), (fc[0] + 40, 1000), (fc[0], fc[1] + 60), 20)
    sk.shape(ribbon(stem, 34, 28, False), "#4caf50")
    for s, y in ((-1, 1130), (1, 1210)):
        sk.shape(leaf((CX - 10 * s, y), (CX + s * 210, y - 90), 55), jitter("#57b65f", rng))
        sk.line(quad((CX - 10 * s, y), (CX + s * 100, y - 60), (CX + s * 190, y - 85), 8), shade("#57b65f", 0.6), 3.5)
    petal = jitter(rng.choice(["#ffd23f", "#ffb627", "#ff9f1c"]), rng)
    n = rng.randint(14, 18)
    for ring, (r, k) in enumerate(((150, 0.5), (140, 0.0))):
        for i in range(n):
            a = 360 * (i + k) / n
            ra = math.radians(a)
            pc = (fc[0] + r * math.cos(ra), fc[1] + r * math.sin(ra))
            sk.shape(ellipse(pc, 72, 30, rot=a, n=24), shade(petal, 0.88 if ring == 0 else 1.0), width=4)
    sk.shape(circle(fc, 105, n=60), jitter("#6b3e26", rng))
    golden = math.pi * (3 - math.sqrt(5))
    seeds = []
    for i in range(1, 70):
        rr = 9.5 * math.sqrt(i)
        if rr > 92:
            break
        seeds.append(circle((fc[0] + rr * math.cos(i * golden), fc[1] + rr * math.sin(i * golden)), 4.5, n=8))
    for p in seeds:
        sk.shade(p, "#3a2214", 255, phase="detail")
    pot = [(CX - 150, 1330), (CX + 150, 1330), (CX + 115, 1520), (CX - 115, 1520)]
    sk.shape(pot, jitter("#d9784f", rng))
    sk.shape(rect(CX - 175, 1300, CX + 175, 1370, 10), shade("#d9784f", 1.08))
    sk.shade([(CX + 40, 1370), (CX + 145, 1370), (CX + 115, 1520), (CX + 60, 1520)], "#000000", 35)
    return sk.scene(dur, hold)


def cactus(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sk.shape(circle((CX, 990), 410, n=90), blend(pal.at(rng.random()), "#ffffff", 0.6))
    green = jitter("#5aa469", rng)
    base = 1280
    trunk = [(CX, base), (CX, 700)]
    arms = []
    for s in (-1, 1):
        y = rng.uniform(980, 1120)
        x = CX + s * rng.uniform(150, 190)
        top = rng.uniform(780, 900)
        arms.append(spline([(CX, y + 30), (x - s * 20, y + 30), (x, y - 20), (x, top)], False, 8))
    for a in arms:
        sk.shape(ribbon(a, 76, 76), green)
    sk.shape(ribbon(spline(trunk + [(CX, 690)], False, 4), 150, 150), green)
    for x in (CX - 38, CX, CX + 38):
        sk.line([(x, 690), (x, base - 10)], shade(green, 0.75), 4)
    for _ in range(26):
        x, y = rng.uniform(CX - 60, CX + 60), rng.uniform(720, base - 40)
        sk.line([(x - 9, y - 9), (x + 9, y + 9)], "#f6f1e3", 3.5, phase="detail", tool="brush")
    fc = (CX + rng.uniform(-30, 30), 625)
    sk.shape(star(fc, 58, 30, 6), pal.at(rng.random()), width=4)
    sk.shape(circle(fc, 16), "#ffd166", width=4)
    pot_col = jitter(rng.choice(["#e07a5f", "#3d5a80", "#f2cc8f", "#81b29a"]), rng)
    sk.shape([(CX - 220, 1270), (CX + 220, 1270), (CX + 175, 1530), (CX - 175, 1530)], pot_col)
    sk.shape(rect(CX - 245, 1240, CX + 245, 1310, 10), shade(pot_col, 1.1))
    for k in range(3):
        y = 1370 + k * 50
        sk.line([(CX - 180 + k * 8, y), (CX + 180 - k * 8, y)], shade(pot_col, 0.7), 5)
    sk.shade(ellipse((CX, 1400), 35, 25), "#ffffff", 80)
    return sk.scene(dur, hold)


def ice_cream(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sk.shape(circle((CX, 990), 410, n=90), blend(pal.at(rng.random()), "#ffffff", 0.55))
    top_y, tip_y, half = 1060, 1530, 150
    cone = [(CX - half, top_y), (CX + half, top_y), (CX, tip_y)]
    sk.shape(cone, "#e9b872")
    L, R, A = cone
    lines = []
    for k in range(1, 6):
        f = k / 6
        p = (lerp(L[0], R[0], f), top_y)
        lines.append([p, (lerp(R[0], A[0], 1 - f), lerp(R[1], A[1], 1 - f))])
        q = (lerp(R[0], L[0], f), top_y)
        lines.append([q, (lerp(L[0], A[0], 1 - f), lerp(L[1], A[1], 1 - f))])
    sk.line(lines, shade("#e9b872", 0.65), 4)
    h0 = rng.random()
    scoops = rng.randint(2, 3)
    cols = [pal.at(h0 + 0.27 * i, 1.0) for i in range(scoops)]
    for i, col in enumerate(cols):
        y = top_y - 40 - i * 150
        top = ellipse((CX, y - 40), 175 - i * 12, 130, a0=math.pi, a1=2 * math.pi, n=24)
        drips = [(CX + 175 - i * 12, y)]
        k = 7
        for j in range(k + 1):
            x = lerp(CX + 175 - i * 12, CX - 175 + i * 12, j / k)
            drips.append((x, y + (40 if j % 2 else 10) + (rng.uniform(10, 50) if j % 2 and i == 0 else 0)))
        sk.shape(spline(top + drips[1:], True, 4), col)
        sk.shade(ellipse((CX - 70, y - 90), 40, 22, rot=-25), "#ffffff", 150)
    ty = top_y - 40 - (scoops - 1) * 150 - 160
    sk.line(quad((CX, ty), (CX + 10, ty - 60), (CX + 50, ty - 90), 8), "#4b7f52", 5)
    sk.shape(circle((CX, ty + 10), 40), "#e63946")
    sk.detail(circle((CX - 13, ty - 3), 10), "#ffffff")
    for _ in range(18):
        i = rng.randrange(scoops)
        x, y = CX + rng.uniform(-120, 120), top_y - 40 - i * 150 + rng.uniform(-120, -10)
        a = rng.uniform(0, math.pi)
        sk.line([(x - 12 * math.cos(a), y - 12 * math.sin(a)), (x + 12 * math.cos(a), y + 12 * math.sin(a))],
                hsv(rng.random(), 0.6, 1.0), 7, phase="detail", tool="brush")
    return sk.scene(dur, hold)


def hot_air_balloon(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#9ad7f5", rng))
    sk.shade(rect(FX0, 1100, FX1, FY1), "#ffffff", 60)
    for _ in range(3):
        sk.shape(cloud((rng.uniform(FX0 + 150, FX1 - 150), rng.uniform(560, 1250)), rng.uniform(170, 240), 60), "#ffffff")
    for _ in range(2):
        c = (rng.choice((rng.uniform(FX0 + 80, FX0 + 180), rng.uniform(FX1 - 180, FX1 - 80))), rng.uniform(600, 1100))
        sk.shape(ellipse(c, 38, 46), pal.at(rng.random()), width=4)
        sk.shape(rect(c[0] - 12, c[1] + 62, c[0] + 12, c[1] + 80), "#8a5a3b", width=3)
    hills = jitter("#7fc97f", rng)
    sk.shape(frame_clip(ellipse((FX0 + 250, FY1 + 60), 420, 200)), hills)
    sk.shape(frame_clip(ellipse((FX1 - 200, FY1 + 80), 400, 230)), shade(hills, 0.9))
    cx, cy, R = CX + rng.uniform(-40, 40), 820, 250
    bottom = 1160

    def hw(y):
        if y <= cy:
            return math.sqrt(max(0.0, R * R - (y - cy) ** 2))
        u = (y - cy) / (bottom - cy)
        return lerp(R, 70, u ** 1.4)

    ys = [cy - R + (bottom - cy + R) * i / 60 for i in range(61)]
    env = [(cx + hw(y), y) for y in ys] + [(cx - hw(y), y) for y in reversed(ys)]
    h0 = rng.random()
    sk.shape(env, pal.at(h0))
    gores = 6
    for g in range(gores):
        if g % 2:
            k0, k1 = -1 + 2 * g / gores, -1 + 2 * (g + 1) / gores
            stripe = [(cx + k0 * hw(y), y) for y in ys] + [(cx + k1 * hw(y), y) for y in reversed(ys)]
            sk.shade(stripe, pal.at(h0 + 0.4), 255)
    sk.line([[(cx + (-1 + 2 * g / gores) * hw(y), y) for y in ys] for g in range(1, gores)], None, 4, together=True)
    sk.shade([(cx + 0.45 * hw(y), y) for y in ys] + [(cx + hw(y), y) for y in reversed(ys)], "#000000", 35)
    sk.shade(ellipse((cx - 120, cy - 120), 45, 80, rot=30), "#ffffff", 110)
    by = bottom + 110
    sk.line([[(cx - 68, bottom), (cx - 55, by)], [(cx + 68, bottom), (cx + 55, by)]], None, 4)
    basket = rect(cx - 70, by, cx + 70, by + 100, 10)
    sk.shape(basket, "#b5835a")
    sk.line([[(cx - 70, by + 33), (cx + 70, by + 33)], [(cx - 70, by + 66), (cx + 70, by + 66)]], shade("#b5835a", 0.6), 4)
    sk.shape(rect(cx - 72, bottom - 6, cx + 72, bottom + 18, 6), shade(pal.at(h0 + 0.4), 0.8), width=4)
    birds(sk, rng, 3, FX0 + 100, FX1 - 100, 1150, 1300)
    return sk.scene(dur, hold)


def rocket(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#1b1f4b", rng))
    for _ in range(26):
        sk.detail(star((rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY0 + 30, FY1 - 30)), rng.uniform(7, 13), 3), "#fff6c9")
    pc = (rng.uniform(FX0 + 170, FX0 + 260), rng.uniform(1270, 1360))
    pcol = pal.at(rng.random())
    sk.shape(circle(pc, 120), pcol)
    sk.shade(circle((pc[0] + 30, pc[1] + 30), 100), "#000000", 50)
    ring = ellipse(pc, 200, 46, rot=-15, a0=0, a1=math.pi, n=30) + ellipse(pc, 150, 28, rot=-15, a0=math.pi, a1=0, n=30)
    sk.shape(ring, blend(pcol, "#ffffff", 0.5))
    mc = (rng.uniform(FX1 - 230, FX1 - 140), rng.uniform(560, 660))
    sk.shape(circle(mc, 80), "#d8d8e0")
    for dx, dy, r in ((-25, -15, 18), (20, 25, 13), (30, -30, 9)):
        sk.shade(circle((mc[0] + dx, mc[1] + dy), r), "#9a9aab", 200)
    c, ang = (CX + 40, 940), rng.uniform(25, 38)

    def T(pts):
        return transform([(c[0] + x, c[1] + y) for x, y in pts], c, 1, ang)
    sk.shape(T(spline([(-50, 260), (0, 470), (50, 260), (0, 320)], True, 8)), "#ff9f1c")
    sk.shape(T(spline([(-28, 270), (0, 390), (28, 270), (0, 300)], True, 8)), "#ffe066")
    body_col = "#f1f1f4"
    accent = pal.at(rng.random())
    for s in (-1, 1):
        sk.shape(T([(s * 70, 120), (s * 150, 260), (s * 150, 300), (s * 60, 250)]), accent)
    sk.shape(T(rect(-50, 240, 50, 285, 10)), "#7a7a8c")
    body = spline([(0, -320), (85, -150), (95, 100), (75, 250), (-75, 250), (-95, 100), (-85, -150)], True, 10)
    sk.shape(T(body), body_col)
    sk.shade(T([(30, -260), (85, -150), (95, 100), (75, 250), (35, 250)]), "#000000", 30)
    sk.shape(T(spline([(0, -320), (65, -200), (0, -185), (-65, -200)], True, 8)), accent)
    sk.shape(T(circle((0, -60), 52)), "#5f6c7b", width=5)
    sk.shape(T(circle((0, -60), 36)), "#8fd3ff", width=4)
    sk.shade(T(ellipse((-10, -72), 14, 9)), "#ffffff", 220)
    sk.shape(T(ellipse((0, 140), 12, 70)), accent, width=4)
    for k in range(3):
        p = transform([(c[0] + rng.uniform(-40, 40), c[1] + 420 + k * 55)], c, 1, ang)[0]
        if FX0 + 60 < p[0] < FX1 - 60 and p[1] < FY1 - 60:
            sk.shape(circle(p, 30 + k * 6), "#e9e9f0", width=4)
    return sk.scene(dur, hold)
