"""More speed-drawing pictures: windmill, campfire, volcano, castle, fox, penguin, panda, sea turtle,
cupcake and tulips. Same conventions as drawings.py."""

import math

from .art import blend, circle, cloud, cubic, ellipse, jitter, lerp, quad, shade, spline, star, transform
from .drawings import CX, FX0, FX1, FY0, FY1, birds, frame, frame_clip, leaf, pine, rect, ribbon
from .sketch import Sketch


def _backdrop(sk, rng, pal, k=0.6):
    sk.shape(circle((CX, 990), 410, n=90), blend(pal.at(rng.random()), "#ffffff", k))


# -- scenery ----------------------------------------------------------------------------

def windmill(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#b9e3ff", rng))
    sk.shape(circle((rng.uniform(FX0 + 120, FX0 + 240), rng.uniform(560, 640)), 65), jitter("#ffd166", rng))
    for _ in range(2):
        sk.shape(cloud((rng.uniform(CX - 100, FX1 - 150), rng.uniform(540, 700)), rng.uniform(200, 260), 60), "#ffffff")
    sk.shape(frame_clip(spline([(FX0 - 10, 1180), (CX, 1120), (FX1 + 10, 1170), (FX1 + 10, FY1 + 10), (FX0 - 10, FY1 + 10)],
                               True, 10)), jitter("#9fd08a", rng))
    h0 = rng.random()
    rows = 5
    for i in range(rows):
        y0 = lerp(1200, FY1, i / rows)
        y1 = lerp(1200, FY1, (i + 1) / rows)
        col = pal.at(h0 + i * 0.21)
        sk.shape([(FX0, y0), (FX1, y0), (FX1, y1), (FX0, y1)], shade(col, 0.95), width=4)
        n = 7 + i * 2
        for k in range(n):
            x = lerp(FX0 + 30, FX1 - 30, (k + 0.5 * (i % 2)) / n)
            s = 8 + i * 3
            sk.shade(ellipse((x, (y0 + y1) / 2), s, s * 1.2), shade(col, 1.15), 255, phase="detail")
    mx = rng.uniform(CX - 60, CX + 60)
    base, top = 1220, 860
    tower = [(mx - 110, base), (mx - 70, top), (mx + 70, top), (mx + 110, base)]
    sk.shape(tower, jitter("#f2e8d5", rng))
    sk.shade([(mx + 20, top), (mx + 70, top), (mx + 110, base), (mx + 30, base)], "#000000", 30)
    sk.shape([(mx - 90, top + 10), (mx, top - 90), (mx + 90, top + 10)], jitter("#b5523b", rng))
    sk.shape(rect(mx - 30, base - 110, mx + 30, base, 30), "#6b4a35")
    sk.shape(circle((mx, top + 90), 26), "#9fd8ff", width=4)
    hub = (mx, top - 20)
    a0 = rng.uniform(0, 90)
    for k in range(4):
        blade = [(-14, 30), (-14, 250), (56, 250), (56, 70)]
        pts = transform([(hub[0] + x, hub[1] - y) for x, y in blade], hub, 1, a0 + 90 * k)
        sk.shape(pts, "#fdfbf6", width=4.5)
        lines = []
        for j in range(1, 5):
            y = lerp(70, 250, j / 5)
            lines.append(transform([(hub[0] - 14, hub[1] - y), (hub[0] + 56, hub[1] - y)], hub, 1, a0 + 90 * k))
        sk.line(lines, shade("#c9b79c", 0.8), 3, together=True)
    sk.shape(circle(hub, 24), "#6b4a35")
    birds(sk, rng, 3, FX0 + 100, FX1 - 100, 520, 720)
    return sk.scene(dur, hold)


def campfire(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#1d2552", rng))
    for _ in range(24):
        sk.detail(star((rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY0 + 30, 1000)), rng.uniform(6, 12), 3), "#fff3b0")
    sk.shape(circle((rng.uniform(FX0 + 140, FX1 - 140), rng.uniform(560, 660)), 55), "#fdf0c2")
    for x in (FX0 + 60, FX0 + 170, FX1 - 70, FX1 - 180):
        pine(sk, x, 1210, rng.uniform(320, 420), "#24493f")
    ground = jitter("#3d5a40", rng)
    sk.shape(rect(FX0, 1180, FX1, FY1), ground)
    side = rng.choice((-1, 1))
    tx = CX + side * 200
    tent = [(tx - 210, 1350), (tx, 1010), (tx + 210, 1350)]
    tcol = pal.at(rng.random())
    sk.shape(tent, tcol)
    sk.shade([(tx, 1010), (tx + 210, 1350), (tx + 40, 1350)], "#000000", 45)
    sk.shape([(tx - 70, 1350), (tx, 1160), (tx + 70, 1350)], shade(tcol, 0.45))
    sk.line([[(tx, 1010), (tx, 960)], [(tx - 210, 1350), (tx - 250, 1370)], [(tx + 210, 1350), (tx + 250, 1370)]], None, 4)
    fx = CX - side * 150
    fy = 1400
    sk.shade(ellipse((fx, fy + 10), 230, 70), "#ffb347", 70)
    for k in range(7):
        a = math.pi * k / 6
        sk.shape(ellipse((fx + 120 * math.cos(a), fy + 46 + 12 * math.sin(a)), 30, 20), "#8d8d99", width=4)
    for ang in (-20, 20):
        sk.shape(ribbon(transform([(fx - 110, fy + 20), (fx + 110, fy + 20)], (fx, fy + 20), 1, ang), 34, 34), "#7b4b2a")
    outer = spline([(fx - 80, fy), (fx - 70, fy - 110), (fx - 30, fy - 80), (fx, fy - 220), (fx + 35, fy - 90),
                    (fx + 70, fy - 140), (fx + 85, fy)], True, 8)
    sk.shape(outer, jitter("#ff7b29", rng))
    sk.shape(spline([(fx - 45, fy), (fx - 30, fy - 70), (fx, fy - 130), (fx + 30, fy - 70), (fx + 45, fy)], True, 8),
             "#ffd23f", width=4)
    for _ in range(6):
        sk.detail(circle((fx + rng.uniform(-90, 90), fy - rng.uniform(220, 380)), rng.uniform(4, 7)), "#ffb347")
    return sk.scene(dur, hold)


def volcano(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#ffcf99", rng))
    sk.shade(rect(FX0, FY0, FX1, 800, 22), "#ff7b54", 90)
    for i in range(3):
        sk.shape(circle((CX + rng.uniform(-200, 200), 640 - i * 40 + rng.uniform(-30, 30)), rng.uniform(70, 110)),
                 shade("#8d8a99", 1 + i * 0.08))
    lava = jitter("#ff4d2e", rng)
    for k in range(5):
        a = math.radians(-90 + (k - 2) * 25)
        p = (CX + 230 * math.cos(a) * 1.3, 860 + 230 * math.sin(a))
        sk.shape(circle(p, rng.uniform(26, 40)), lava, width=4)
    sk.shape(spline([(CX - 90, 900), (CX - 60, 780), (CX, 830), (CX + 60, 760), (CX + 90, 900)], True, 6), "#ffb627")
    cone = [(FX0 - 10, 1450), (CX - 120, 920), (CX - 60, 900), (CX + 60, 900), (CX + 120, 920), (FX1 + 10, 1450)]
    body = jitter("#6d4c41", rng)
    sk.shape(frame_clip(cone + [(FX1 + 10, FY1 + 10), (FX0 - 10, FY1 + 10)]), body)
    sk.shade([(CX + 60, 900), (CX + 120, 920), (FX1, 1450), (CX + 150, 1450)], "#000000", 45)
    for x_end, w in ((CX - 230, 46), (CX + 60, 54), (CX + 300, 40)):
        path = cubic((CX + (x_end - CX) * 0.1, 905), (CX + (x_end - CX) * 0.4, 1050), (x_end, 1200), (x_end + 20, 1450), 18)
        sk.shape(ribbon(path, w * 0.7, w, False), lava, width=4)
    sk.shape(rect(FX0, 1450, FX1, FY1), jitter("#4e7d4f", rng))
    for x in (FX0 + 90, FX1 - 90):
        trunk = cubic((x, FY1 - 20), (x - 10, FY1 - 120), (x + 20, FY1 - 200), (x + 10, FY1 - 260), 12)
        sk.shape(ribbon(trunk, 26, 16, False), "#8a5a3b", width=4)
        for ang in (-150, -110, -60, -20):
            a = math.radians(ang)
            tip = (x + 10 + 120 * math.cos(a), FY1 - 260 + 120 * math.sin(a) + 40)
            sk.shape(leaf((x + 10, FY1 - 260), tip, 22), "#3f9d4f", width=4)
    birds(sk, rng, 3, FX0 + 100, FX1 - 100, 1000, 1200, "#4a2a2a")
    return sk.scene(dur, hold)


def castle(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#c7e5ff", rng))
    for _ in range(2):
        sk.shape(cloud((rng.uniform(FX0 + 150, FX1 - 150), rng.uniform(520, 680)), 220, 60), "#ffffff")
    sk.shape(frame_clip(ellipse((CX, FY1 + 120), 560, 380)), jitter("#86c977", rng))
    stone = jitter(rng.choice(["#d9d4e7", "#e8dcc8", "#cfd8dc"]), rng)
    roof = jitter(rng.choice(["#5e60ce", "#d1495b", "#3a86ff", "#7b2cbf"]), rng)
    wall_top, base = 1050, 1360

    def towers(xs, top, w):
        for x in xs:
            sk.shape(rect(x - w, top, x + w, base), shade(stone, 0.95))
            sk.shape([(x - w - 18, top + 4), (x, top - w * 2.4), (x + w + 18, top + 4)], roof)
            sk.line([(x, top - w * 2.4), (x, top - w * 2.4 - 70)], None, 4)
            sk.shape([(x, top - w * 2.4 - 70), (x + 60, top - w * 2.4 - 52), (x, top - w * 2.4 - 34)], pal.at(rng.random()),
                     width=4)
            sk.shape(rect(x - 14, top + 50, x + 14, top + 100, 14), "#3d3a4b", width=4)

    towers((CX - 120, CX + 120), 820, 55)
    crenel = [(CX - 300, base), (CX - 300, wall_top)]
    x = CX - 300
    while x < CX + 300:
        crenel += [(x, wall_top - 40), (x + 40, wall_top - 40), (x + 40, wall_top), (min(x + 75, CX + 300), wall_top)]
        x += 75
    crenel += [(CX + 300, wall_top), (CX + 300, base)]
    sk.shape(crenel, stone)
    for row in range(5):
        y = wall_top + 40 + row * 60
        sk.line([(CX - 300, y), (CX + 300, y)], shade(stone, 0.75), 3)
    towers((CX - 330, CX + 330), 960, 60)
    gate = [(CX - 80, base), (CX - 80, 1240)] + ellipse((CX, 1240), 80, 80, a0=math.pi, a1=2 * math.pi, n=16)[1:-1] + \
        [(CX + 80, 1240), (CX + 80, base)]
    sk.shape(gate, "#5b3b2a")
    sk.line([[(CX - 50, 1180), (CX - 50, base)], [(CX, 1160), (CX, base)], [(CX + 50, 1180), (CX + 50, base)]],
            shade("#5b3b2a", 0.6), 4)
    sk.shape([(CX - 80, base), (CX + 80, base), (CX + 160, FY1), (CX - 160, FY1)], "#d8c39a")
    for _ in range(10):
        c = (rng.uniform(FX0 + 40, FX1 - 40), rng.uniform(1400, FY1 - 30))
        if abs(c[0] - CX) > 180:
            sk.detail(star(c, 12, 5, 5), pal.at(rng.random()))
    birds(sk, rng, 2, FX0 + 100, FX1 - 100, 700, 800)
    return sk.scene(dur, hold)


# -- animals ---------------------------------------------------------------------------

def fox(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.55)
    orange = jitter("#f07c2c", rng)
    cream = "#fdf3e3"
    side = rng.choice((-1, 1))
    tail = [(CX + side * 120, 1450), (CX + side * 380, 1420), (CX + side * 400, 1150), (CX + side * 300, 1080),
            (CX + side * 300, 1250), (CX + side * 200, 1380)]
    sk.shape(spline(tail, True, 8), orange)
    sk.shape(spline([(CX + side * 400, 1150), (CX + side * 300, 1080), (CX + side * 330, 1180), (CX + side * 395, 1210)],
                    True, 6), cream, width=4)
    body = spline([(CX, 1000), (CX + 160, 1120), (CX + 200, 1380), (CX + 150, 1480), (CX - 150, 1480), (CX - 200, 1380),
                   (CX - 160, 1120)], True, 10)
    sk.shape(body, orange)
    sk.shape(spline([(CX, 1060), (CX + 80, 1180), (CX + 70, 1350), (CX - 70, 1350), (CX - 80, 1180)], True, 8), cream, width=4)
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 80, 1455), 55, 36), "#3a2a2a")
    hy = 860
    for s in (-1, 1):
        ear = [(CX + s * 60, hy - 100), (CX + s * 170, hy - 280), (CX + s * 190, hy - 70)]
        sk.shape(ear, orange)
        sk.shape(transform(ear, (CX + s * 150, hy - 140), 0.55), "#3a2a2a", width=4)
    head = spline([(CX - 170, hy - 60), (CX - 110, hy - 130), (CX + 110, hy - 130), (CX + 170, hy - 60), (CX + 215, hy + 40),
                   (CX + 60, hy + 110), (CX, hy + 165), (CX - 60, hy + 110), (CX - 215, hy + 40)], True, 8)
    sk.shape(head, orange)
    sk.shape(spline([(CX - 205, hy + 42), (CX - 80, hy + 25), (CX, hy + 95), (CX + 80, hy + 25), (CX + 205, hy + 42),
                     (CX + 60, hy + 110), (CX, hy + 160), (CX - 60, hy + 110)], True, 8), cream, width=4)
    for s in (-1, 1):
        ex = CX + s * 80
        sk.shape(ellipse((ex, hy - 20), 24, 32), "#2b2d42")
        sk.detail(circle((ex - 8, hy - 32), 9), "#ffffff")
        sk.shade(ellipse((CX + s * 140, hy + 50), 30, 18), "#ff8fab", 110)
    sk.shape(ellipse((CX, hy + 140), 26, 18), "#2b2d42")
    sk.line(quad((CX - 30, hy + 175), (CX, hy + 195), (CX + 30, hy + 175), 8), None, 4)
    return sk.scene(dur, hold)


def penguin(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sk.shape(circle((CX, 990), 410, n=90), jitter("#cfe9ff", rng))
    sk.shape(spline([(CX - 380, 1330), (CX - 100, 1290), (CX + 200, 1310), (CX + 390, 1350), (CX + 300, 1440), (CX - 300, 1440)],
                    True, 8), "#f4fbff")
    navy = jitter("#2d3250", rng)
    py = 1060
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 170, py + 40), 50, 150, rot=-s * 20), navy)
    sk.shape(ellipse((CX, py), 200, 290), navy)
    sk.shape(spline([(CX, py - 170), (CX + 120, py - 60), (CX + 140, py + 140), (CX, py + 260), (CX - 140, py + 140),
                     (CX - 120, py - 60)], True, 10), "#fdfdfb")
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 70, py + 290), 60, 26), "#ff9f1c")
    for s in (-1, 1):
        ex = CX + s * 60
        sk.shape(circle((ex, py - 140), 26), "#1d1d28")
        sk.detail(circle((ex - 8, py - 150), 9), "#ffffff")
        sk.shade(ellipse((CX + s * 100, py - 90), 26, 16), "#ff8fab", 130)
    sk.shape([(CX - 30, py - 105), (CX + 30, py - 105), (CX, py - 65)], "#ff9f1c")
    scarf = pal.at(rng.random())
    sk.shape(ribbon(spline([(CX - 150, py - 10), (CX, py + 30), (CX + 150, py - 10)], False, 8), 50, 50, False), scarf)
    sk.shape(ribbon([(CX + 100, py + 10), (CX + 130, py + 110), (CX + 120, py + 170)], 50, 44, False), shade(scarf, 0.9))
    for k in range(3):
        sk.line([(CX + 100 + k * 15, py + 150), (CX + 105 + k * 15, py + 180)], shade(scarf, 0.6), 4)
    for _ in range(14):
        c = (CX + rng.uniform(-360, 360), rng.uniform(640, 1250))
        if math.dist(c, (CX, 990)) < 380 and abs(c[0] - CX) > 230:
            sk.detail(star(c, 14, 4, 6, rot=0), "#ffffff")
    return sk.scene(dur, hold)


def panda(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sk.shape(circle((CX, 990), 410, n=90), jitter("#d4f1c5", rng))
    green = jitter("#6ab04c", rng)
    for x in (CX - 300, CX + 260, CX + 330):
        sk.shape(rect(x - 18, 620, x + 18, 1380, 10), green, width=4)
        sk.line([[(x - 18, y), (x + 18, y)] for y in range(720, 1380, 130)], shade(green, 0.7), 4, together=True)
        sk.shape(leaf((x, 760), (x + 120, 700), 26), shade(green, 1.1), width=4)
    black = "#26252b"
    py = 1220
    sk.shape(ellipse((CX, py), 230, 230), "#fbfbf8")
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 180, py - 20), 70, 120, rot=s * 25), black)
        sk.shape(ellipse((CX + s * 120, py + 210), 85, 60), black)
        sk.shade(circle((CX + s * 120, py + 215), 26), "#5a5960", 255)
    hy = 880
    for s in (-1, 1):
        sk.shape(circle((CX + s * 150, hy - 130), 62), black)
    sk.shape(ellipse((CX, hy), 230, 195), "#fbfbf8")
    for s in (-1, 1):
        ex = CX + s * 85
        sk.shape(ellipse((ex, hy - 5), 52, 70, rot=s * 30), black)
        sk.shape(circle((ex + s * 5, hy - 15), 20), "#ffffff", width=3)
        sk.detail(circle((ex + s * 5, hy - 12), 10), black)
        sk.shade(ellipse((CX + s * 145, hy + 70), 32, 18), "#ff9fb0", 140)
    sk.shape(ellipse((CX, hy + 60), 30, 20), black)
    sk.line(quad((CX, hy + 80), (CX - 18, hy + 112), (CX - 44, hy + 95), 8), None, 4.5)
    sk.line(quad((CX, hy + 80), (CX + 18, hy + 112), (CX + 44, hy + 95), 8), None, 4.5)
    return sk.scene(dur, hold)


def sea_turtle(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sk.shape(circle((CX, 990), 410, n=90), jitter("#7fd1e8", rng))
    for x in (CX - 300, CX - 240, CX + 280):
        pts = [(x + 25 * math.sin(k * 0.9), 1390 - k * 50) for k in range(9)]
        sk.line(spline(pts, False, 6), "#2f9e6b", 8)
    sk.shape(spline([(CX - 410, 1300), (CX - 150, 1260), (CX + 180, 1290), (CX + 410, 1250), (CX + 300, 1420), (CX - 300, 1420)],
                    True, 8), "#f2d49b")
    skin = jitter("#8fbf6a", rng)
    c, ang = (CX, 960), rng.uniform(-20, 20)

    def T(pts):
        return transform([(c[0] + x, c[1] + y) for x, y in pts], c, 1, ang)
    for sx, sy, l, w in ((1, -1, 230, 60), (1, 1, 200, 52), (-1, -1, 150, 44), (-1, 1, 140, 40)):
        base = (sx * 100, sy * 120)
        tip = (sx * 100 + sx * l * 0.5, sy * 120 + sy * l * 0.85)
        sk.shape(T(leaf(base, tip, w)), skin)
    sk.shape(T(ellipse((0, -270), 70, 85)), skin)
    sk.detail(T(circle((-25, -295), 12)), "#1d1d28")
    sk.detail(T(circle((25, -295), 12)), "#1d1d28")
    shell = jitter("#5b8c51", rng)
    sk.shape(T(ellipse((0, 0), 190, 230)), shell)
    hexa = [(90 * math.cos(math.radians(60 * k + 30)) * 0.8, 90 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    sk.shape(T(hexa), shade(shell, 1.18), width=4.5)
    spokes = [T([p, (p[0] * 2.05, p[1] * 2.3)]) for p in hexa]
    sk.line(spokes, shade(shell, 0.6), 4.5, together=True)
    for _ in range(8):
        b = (CX + rng.uniform(-330, 330), rng.uniform(640, 1200))
        if math.dist(b, (CX, 990)) < 370 and math.dist(b, c) > 300:
            ring = circle(b, rng.uniform(8, 16), n=16)
            sk.detail_line(ring + ring[:1], "#ffffff", 3.5)
    return sk.scene(dur, hold)


# -- treats and plants ---------------------------------------------------------------------

def cupcake(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.55)
    wrap = pal.at(rng.random())
    top, bottom = 1130, 1450
    sk.shape([(CX - 220, top), (CX + 220, top), (CX + 160, bottom), (CX - 160, bottom)], wrap)
    sk.line([[(lerp(CX - 220, CX + 220, k / 8), top), (lerp(CX - 160, CX + 160, k / 8), bottom)] for k in range(1, 8)],
            shade(wrap, 0.7), 4, together=True)
    icing = pal.at(rng.random() + 0.4)
    for i, (y, w, h) in enumerate(((1100, 250, 90), (1000, 200, 90), (905, 140, 80))):
        pts = spline([(CX - w, y + 30), (CX - w * 0.8, y - h * 0.6), (CX, y - h), (CX + w * 0.8, y - h * 0.6), (CX + w, y + 30),
                      (CX, y + h * 0.55)], True, 8)
        sk.shape(pts, shade(icing, 1 - 0.05 * i))
        sk.shade(ellipse((CX - w * 0.45, y - h * 0.45), w * 0.22, 14, rot=-15), "#ffffff", 150)
    sk.shape(spline([(CX - 20, 820), (CX, 760), (CX + 30, 790), (CX + 10, 830)], True, 6), "#ffffff", width=4)
    sk.shape(circle((CX + 5, 760), 42), "#e63946")
    sk.detail(circle((CX - 8, 745), 10), "#ffffff")
    sk.line(quad((CX + 5, 720), (CX + 20, 670), (CX + 60, 650), 8), "#4b7f52", 5)
    for _ in range(22):
        x, y = CX + rng.uniform(-200, 200), rng.uniform(870, 1110)
        a = rng.uniform(0, math.pi)
        sk.line([(x - 11 * math.cos(a), y - 11 * math.sin(a)), (x + 11 * math.cos(a), y + 11 * math.sin(a))],
                pal.at(rng.random(), 1.05), 7, phase="detail", tool="brush")
    return sk.scene(dur, hold)


def tulip_vase(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.7)
    n = rng.randint(3, 5)
    green = jitter("#4caf50", rng)
    heads = []
    for k in range(n):
        u = (k + 0.5) / n
        hx = lerp(CX - 230, CX + 230, u) + rng.uniform(-20, 20)
        hy = 760 + abs(u - 0.5) * 220 + rng.uniform(-30, 30)
        heads.append((hx, hy))
        stem = quad((CX + (u - 0.5) * 80, 1200), (hx + (CX - hx) * 0.2, (hy + 1200) / 2), (hx, hy + 60), 14)
        sk.line(stem, green, 12)
    for s in (-1, 1):
        sk.shape(leaf((CX + s * 20, 1150), (CX + s * 230, 900), 45), shade(green, 1.08))
    h0 = rng.random()
    for k, (hx, hy) in enumerate(heads):
        col = pal.at(h0 + k * 0.17)
        cup = spline([(hx - 62, hy - 70), (hx - 25, hy - 30), (hx, hy - 85), (hx + 25, hy - 30), (hx + 62, hy - 70), (hx + 55, hy + 20),
                      (hx, hy + 65), (hx - 55, hy + 20)], True, 6)
        sk.shape(cup, col)
        sk.shade(spline([(hx - 10, hy - 60), (hx + 25, hy - 30), (hx + 55, hy - 60), (hx + 50, hy + 15), (hx + 5, hy + 55)], True, 6),
                 "#000000", 30)
    glass = jitter("#bfe6f2", rng)
    vase = spline([(CX - 90, 1150), (CX + 90, 1150), (CX + 70, 1200), (CX + 170, 1350), (CX + 120, 1500), (CX - 120, 1500),
                   (CX - 170, 1350), (CX - 70, 1200)], True, 8)
    sk.shape(vase, glass)
    sk.shade(ellipse((CX - 90, 1360), 20, 70, rot=10), "#ffffff", 170)
    sk.shade(spline([(CX - 165, 1370), (CX + 165, 1370), (CX + 120, 1495), (CX - 120, 1495)], True, 4), "#4aa3d8", 70)
    return sk.scene(dur, hold)
