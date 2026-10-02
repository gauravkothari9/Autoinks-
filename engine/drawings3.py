"""Even more speed-drawing pictures: sailboat, rainbow, igloo, pyramids, mushroom house, bunny, frog, bee,
snail, octopus, strawberry, donut, watermelon, car, teacup and gift box. Same conventions as drawings.py."""

import math

from .art import blend, circle, cloud, cubic, ellipse, jitter, lerp, quad, shade, spline, star, transform
from .drawings import CX, FX0, FX1, FY0, FY1, birds, frame, frame_clip, leaf, pine, rect, ribbon
from .sketch import Sketch

CY = 990


def _backdrop(sk, rng, pal, k=0.6, color=None):
    sk.shape(circle((CX, CY), 410, n=90), color or blend(pal.at(rng.random()), "#ffffff", k))


def _band(c, rx, ry, x0, x1, n=16):
    """The slice of an ellipse between x0 and x1 (stripes on a bee, bands on a cup)."""
    def y(x, s):
        return c[1] + s * ry * math.sqrt(max(0.0, 1 - ((x - c[0]) / rx) ** 2))
    xs = [lerp(x0, x1, i / n) for i in range(n + 1)]
    return [(x, y(x, -1)) for x in xs] + [(x, y(x, 1)) for x in reversed(xs)]


def _arc_band(c, r_out, r_in, a0=math.pi, a1=2 * math.pi, n=40):
    """A curved band between two radii (rainbows, rims)."""
    return ellipse(c, r_out, r_out, a0=a0, a1=a1, n=n) + list(reversed(ellipse(c, r_in, r_in, a0=a0, a1=a1, n=n)))


def _eyes(sk, cx, y, gap, r, blush=True, blush_dx=None):
    for s in (-1, 1):
        ex = cx + s * gap
        sk.shape(circle((ex, y), r), "#1d1d28")
        sk.detail(circle((ex - r * 0.3, y - r * 0.35), r * 0.32), "#ffffff")
        if blush:
            sk.shade(ellipse((cx + s * (blush_dx or gap * 1.6), y + r * 1.6), r * 1.1, r * 0.65), "#ff8fab", 120)


def _smile(sk, cx, y, w, width=4.5):
    sk.line(quad((cx - w, y), (cx, y + w * 0.8), (cx + w, y), 10), None, width)


# -- scenery ----------------------------------------------------------------------------

def sailboat(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    sea_y = rng.uniform(1120, 1180)
    frame(sk, jitter("#a7dcff", rng))
    sk.shape(circle((rng.uniform(FX0 + 130, FX1 - 130), rng.uniform(560, 640)), 70), jitter("#ffd166", rng))
    for _ in range(2):
        sk.shape(cloud((rng.uniform(FX0 + 150, FX1 - 150), rng.uniform(560, 800)), rng.uniform(200, 260), 60), "#ffffff")
    sk.shape(frame_clip(_ridge_pts(rng, sea_y, 60)), jitter("#8fb9a8", rng))
    sea = jitter("#2f80c4", rng)
    sk.shape(rect(FX0, sea_y, FX1, FY1), sea)
    bx = rng.uniform(CX - 100, CX + 100)
    hull_y = sea_y + 40
    sk.shade(ellipse((bx, hull_y + 70), 230, 26), "#000000", 50)
    mast_top = hull_y - 560
    main = [(bx + 12, mast_top + 20), (bx + 12, hull_y - 60), (bx + 250, hull_y - 60)]
    jib = [(bx - 12, mast_top + 70), (bx - 12, hull_y - 60), (bx - 210, hull_y - 60)]
    sk.shape(main, "#fdfcf7")
    sk.shade([(bx + 12, mast_top + 20), (bx + 12, hull_y - 60), (bx + 90, hull_y - 60)], "#000000", 25)
    sk.shape(jib, pal.at(rng.random()))
    sk.line([(bx, mast_top), (bx, hull_y - 30)], "#5b3b2a", 10)
    sk.shape([(bx, mast_top), (bx + 70, mast_top + 22), (bx, mast_top + 44)], "#e63946", width=4)
    hull_col = jitter(rng.choice(["#c0392b", "#2c3e50", "#8e5b3a"]), rng)
    hull = spline([(bx - 270, hull_y - 60), (bx + 290, hull_y - 60), (bx + 220, hull_y + 40), (bx - 200, hull_y + 40)], True, 4)
    sk.shape(hull, hull_col)
    sk.line([(bx - 250, hull_y - 30), (bx + 270, hull_y - 30)], "#ffffff", 6)
    for _ in range(10):
        x, y = rng.uniform(FX0 + 30, FX1 - 140), rng.uniform(sea_y + 120, FY1 - 40)
        sk.line(quad((x, y), (x + 50, y - 14), (x + 100, y), 6), "#cfeaff", 4.5, phase="detail", tool="brush")
    birds(sk, rng, 3, FX0 + 100, FX1 - 100, 520, 700)
    return sk.scene(dur, hold)


def _ridge_pts(rng, base, amp):
    pts = [(FX0 - 10, base)] + [(lerp(FX0, FX1, i / 6), base - rng.uniform(10, amp)) for i in range(7)] + [(FX1 + 10, base)]
    return spline(pts, False, 8) + [(FX1 + 10, base + 5), (FX0 - 10, base + 5)]


def rainbow_hills(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#bfe8ff", rng))
    c = (CX, 1250)
    colors = ["#ff595e", "#ff924c", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93"]
    r = 470
    for col in colors:
        sk.shape(_arc_band(c, r, r - 46), col, width=4)
        r -= 46
    for x in (CX - 380, CX + 380):
        sk.shape(cloud((x, 1210), 300, 110, bumps=3), "#ffffff")
    hills = jitter("#7ccf6a", rng)
    sk.shape(frame_clip(ellipse((FX0 + 200, FY1 + 50), 480, 280)), hills)
    sk.shape(frame_clip(ellipse((FX1 - 150, FY1 + 70), 460, 260)), shade(hills, 0.9))
    for _ in range(14):
        x, y = rng.uniform(FX0 + 40, FX1 - 40), rng.uniform(1420, FY1 - 30)
        sk.line([(x, y + 30), (x, y)], "#3e8e41", 4)
        sk.shape(star((x, y), 16, 8, 5), pal.at(rng.random()), width=3)
    sk.shape(circle((rng.uniform(FX0 + 110, FX0 + 200), 560), 60), "#ffd166")
    birds(sk, rng, 3, FX0 + 150, FX1 - 100, 520, 640)
    return sk.scene(dur, hold)


def igloo(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#1c2b5a", rng))
    for k, col in enumerate(("#3ef0a0", "#5fd3ff")):
        band = [(x, 640 + 70 * k + 50 * math.sin(x / 110 + k)) for x in range(int(FX0), int(FX1) + 1, 20)]
        sk.shade(band + [(x, y + 90) for x, y in reversed(band)], col, 90)
    for _ in range(26):
        sk.detail(star((rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY0 + 30, 1050)), rng.uniform(6, 12), 3), "#ffffff")
    sk.shape(circle((rng.uniform(FX0 + 130, FX1 - 130), 540), 50), "#fdf3c4")
    for x in (FX0 + 70, FX1 - 70):
        pine(sk, x, 1240, 300, "#2d5d55")
    snow = "#f3f8ff"
    sk.shape(frame_clip(spline([(FX0 - 10, 1220), (CX, 1180), (FX1 + 10, 1230), (FX1 + 10, FY1 + 10), (FX0 - 10, FY1 + 10)],
                               True, 8)), snow)
    ix, base, R = CX + rng.uniform(-60, 60), 1420, 270
    dome = ellipse((ix, base), R, R * 0.9, a0=math.pi, a1=2 * math.pi, n=40)
    sk.shape(dome, "#e8f2ff")
    rows = 5
    lines = []
    for i in range(1, rows):
        y = base - R * 0.9 * i / rows
        hw = R * math.sqrt(1 - (i / rows) ** 2)
        lines.append([(ix - hw, y), (ix + hw, y)])
    for i in range(rows):
        y0 = base - R * 0.9 * i / rows
        y1 = base - R * 0.9 * (i + 1) / rows
        hw = R * math.sqrt(1 - ((i + 0.5) / rows) ** 2)
        k = 4 - i
        for j in range(1, k + 1):
            x = ix - hw + 2 * hw * (j - 0.5 * (i % 2)) / (k + 0.5)
            lines.append([(x, y0), (x, y1)])
    sk.line(lines, "#9fb7d9", 3.5)
    sk.shade(ellipse((ix + 120, base - 90), 100, 140), "#7d97c4", 50)
    door = ellipse((ix - 60, base), 75, 110, a0=math.pi, a1=2 * math.pi, n=20)
    sk.shape(door, "#26355c")
    for _ in range(16):
        c = (rng.uniform(FX0 + 30, FX1 - 30), rng.uniform(FY0 + 30, FY1 - 30))
        sk.detail(circle(c, rng.uniform(4, 7)), "#ffffff")
    return sk.scene(dur, hold)


def pyramids(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    frame(sk, jitter("#ffd9a0", rng))
    sk.shade(rect(FX0, FY0, FX1, 760, 22), "#ff9e6d", 90)
    sun = (rng.uniform(FX0 + 200, FX1 - 200), 760)
    sk.shape(circle(sun, 150), "#fff1a8")
    sand = jitter("#e9b96e", rng)
    sk.shape(frame_clip(spline([(FX0 - 10, 1130), (CX - 100, 1100), (FX1 + 10, 1140), (FX1 + 10, FY1 + 10), (FX0 - 10, FY1 + 10)],
                               True, 8)), shade(sand, 1.05))
    stone = jitter("#d7a35b", rng)
    for px, w, h in sorted(((CX - 220, 230, 300), (CX + 160, 300, 400), (CX + 380, 160, 200)), key=lambda p: p[2]):
        base = 1150
        pyr = [(px - w, base), (px, base - h), (px + w, base)]
        sk.shape(pyr, stone)
        sk.shade([(px, base - h), (px + w, base), (px + w * 0.15, base)], "#7a4a2a", 70)
        lines = []
        for k in range(1, 6):
            y = base - h * k / 6
            hw = w * (1 - k / 6)
            lines.append([(px - hw, y), (px + hw, y)])
        sk.line(lines, shade(stone, 0.7), 3, together=True)
    dune = jitter("#f0c27b", rng)
    sk.shape(frame_clip(spline([(FX0 - 10, 1300), (CX - 150, 1250), (CX + 200, 1320), (FX1 + 10, 1280), (FX1 + 10, FY1 + 10),
                                (FX0 - 10, FY1 + 10)], True, 8)), dune)
    ox = rng.choice((FX0 + 170, FX1 - 170))
    sk.shape(ellipse((ox, 1420), 130, 34), "#4aa3d8")
    trunk = cubic((ox + 60, 1420), (ox + 60, 1330), (ox + 80, 1270), (ox + 70, 1220), 12)
    sk.shape(ribbon(trunk, 24, 14, False), "#8a5a3b", width=4)
    for ang in (-160, -115, -65, -20):
        a = math.radians(ang)
        tip = (ox + 70 + 110 * math.cos(a), 1220 + 110 * math.sin(a) + 40)
        sk.shape(leaf((ox + 70, 1220), tip, 20), "#3f9d4f", width=4)
    for _ in range(6):
        x, y = rng.uniform(FX0 + 40, FX1 - 140), rng.uniform(1360, FY1 - 40)
        sk.line(quad((x, y), (x + 50, y - 12), (x + 100, y), 6), shade(dune, 0.8), 4, phase="detail", tool="brush")
    birds(sk, rng, 3, FX0 + 100, FX1 - 100, 520, 680, "#6a3b2a")
    return sk.scene(dur, hold)


def mushroom_house(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    grass = jitter("#7cc46a", rng)
    sk.shape(spline([(CX - 405, 1250), (CX, 1200), (CX + 405, 1240), (CX + 300, 1390), (CX - 300, 1390)], True, 8), grass)
    stem = spline([(CX - 150, 1300), (CX - 130, 1000), (CX + 130, 1000), (CX + 150, 1300)], True, 8)
    cream = "#fbf1dc"
    sk.shape([(CX + 120, 860), (CX + 180, 860), (CX + 180, 760), (CX + 120, 760)], "#b05a4a")
    sk.shape(stem, cream)
    sk.shade([(CX + 60, 1000), (CX + 130, 1000), (CX + 150, 1300), (CX + 80, 1300)], "#000000", 30)
    sk.shape(rect(CX - 50, 1160, CX + 50, 1300, 50), "#8a5a3b")
    sk.detail(circle((CX + 28, 1235), 7), "#ffd166")
    for wx, wy in ((CX - 90, 1060), (CX + 90, 1090)):
        sk.shape(circle((wx, wy), 32), "#ffe28a")
        sk.line([[(wx - 32, wy), (wx + 32, wy)], [(wx, wy - 32), (wx, wy + 32)]], None, 4)
    cap_col = jitter(rng.choice(["#e63946", "#ff6b6b", "#9b5de5", "#f15bb5"]), rng)
    cap = spline([(CX - 330, 1010), (CX - 280, 830), (CX, 700), (CX + 280, 830), (CX + 330, 1010), (CX, 1040)], True, 10)
    sk.shape(cap, cap_col)
    for x, y, r in ((CX - 180, 900, 40), (CX + 20, 790, 46), (CX + 200, 910, 36), (CX - 40, 960, 30), (CX + 120, 840, 22),
                    (CX - 110, 820, 24)):
        sk.shade(circle((x, y), r), "#ffffff", 255)
    sk.shade(spline([(CX + 120, 760), (CX + 300, 900), (CX + 320, 1000), (CX + 200, 1020)], True, 6), "#000000", 30)
    for i in range(4):
        sk.shape(circle((CX + 150 + 30 * i, 700 - 70 * i), 22 + i * 8), "#eef0f4", width=4)
    path = [(CX - 50, 1300), (CX + 50, 1300), (CX + 110, 1385), (CX - 120, 1385)]
    sk.shape(path, "#e2c79a", width=4)
    for x in (CX - 300, CX + 280):
        sk.shape(ellipse((x, 1250), 50, 30, a0=math.pi, a1=2 * math.pi, n=14), pal.at(rng.random()), width=4)
        sk.shape(rect(x - 10, 1250, x + 10, 1300), cream, width=4)
    for _ in range(8):
        x, y = rng.uniform(CX - 330, CX + 330), rng.uniform(1320, 1380)
        sk.detail(star((x, y), 13, 6, 5), pal.at(rng.random()))
    return sk.scene(dur, hold)


# -- animals ---------------------------------------------------------------------------

def bunny(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.6)
    fur = jitter(rng.choice(["#fafafa", "#e8d5c4", "#c8b6a6", "#f3e9e2"]), rng)
    pink = "#ffb3c6"
    hy = 900
    for s in (-1, 1):
        ear = ellipse((CX + s * 80, hy - 260), 52, 170, rot=s * 12)
        sk.shape(ear, fur)
        sk.shape(ellipse((CX + s * 80, hy - 250), 26, 120, rot=s * 12), pink, width=4)
    sk.shape(circle((CX + 190, 1400), 50), "#ffffff")
    body = spline([(CX, 1020), (CX + 180, 1150), (CX + 210, 1400), (CX + 140, 1470), (CX - 140, 1470), (CX - 210, 1400),
                   (CX - 180, 1150)], True, 10)
    sk.shape(body, fur)
    sk.shade(ellipse((CX, 1320), 100, 120), "#ffffff", 140)
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 90, 1450), 75, 38), fur)
    head = ellipse((CX, hy), 200, 170)
    sk.shape(head, fur)
    _eyes(sk, CX, hy - 10, 80, 26, blush_dx=120)
    sk.shape([(CX - 16, hy + 50), (CX + 16, hy + 50), (CX, hy + 66)], "#ff6f91", width=3.5)
    sk.line(quad((CX, hy + 66), (CX - 18, hy + 95), (CX - 40, hy + 80), 8), None, 4)
    sk.line(quad((CX, hy + 66), (CX + 18, hy + 95), (CX + 40, hy + 80), 8), None, 4)
    for s in (-1, 1):
        for k in range(2):
            sk.line([(CX + s * 90, hy + 60 + k * 18), (CX + s * 200, hy + 45 + k * 30)], None, 3)
    cx = CX - 250
    carrot = [(cx - 40, 1330), (cx + 40, 1330), (cx, 1470)]
    sk.shape(carrot, "#ff8c42")
    sk.line([[(cx - 25, 1360), (cx - 5, 1365)], [(cx + 20, 1400), (cx + 2, 1405)]], shade("#ff8c42", 0.7), 4)
    for a in (-30, 0, 30):
        sk.shape(leaf((cx, 1330), (cx + 70 * math.sin(math.radians(a)), 1250), 18), "#4caf50", width=4)
    return sk.scene(dur, hold)


def frog(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, color=jitter("#9bd4e6", rng))
    pad_c = (CX, 1300)
    notch = math.radians(rng.uniform(-60, -30))
    sk.shape([pad_c] + ellipse(pad_c, 330, 110, a0=notch + 0.3, a1=notch + 2 * math.pi - 0.3, n=40), jitter("#5cb85c", rng))
    green = jitter("#7bc950", rng)
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 190, 1250), 110, 50, rot=s * -10), shade(green, 0.9))
    body = ellipse((CX, 1080), 240, 200)
    sk.shape(body, green)
    sk.shape(ellipse((CX, 1150), 150, 110), "#e9f5c8")
    for s in (-1, 1):
        sk.shape(ellipse((CX + s * 110, 1250), 34, 60), green)
        for k in (-1, 0, 1):
            sk.shape(circle((CX + s * 110 + k * 22, 1305), 14), green, width=3.5)
    for s in (-1, 1):
        ex = CX + s * 120
        sk.shape(circle((ex, 900), 78), green)
        sk.shape(circle((ex, 900), 50), "#ffffff")
        sk.shape(circle((ex + s * 6, 905), 28), "#1d1d28")
        sk.detail(circle((ex - 4, 894), 9), "#ffffff")
    sk.line(quad((CX - 140, 1010), (CX, 1100), (CX + 140, 1010), 14), None, 6)
    for s in (-1, 1):
        sk.shade(ellipse((CX + s * 170, 1030), 34, 20), "#ff8fab", 130)
        sk.detail(circle((CX + s * 18, 975), 6), "#3a5a2a")
    fly = (CX + rng.choice((-1, 1)) * 280, 760)
    sk.shape(ellipse((fly[0] - 18, fly[1] - 20), 22, 12, rot=-30), "#e6f7ff", width=3)
    sk.shape(ellipse((fly[0] + 18, fly[1] - 20), 22, 12, rot=30), "#e6f7ff", width=3)
    sk.shape(circle(fly, 14), "#2b2d42", width=3)
    return sk.scene(dur, hold)


def bee(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    honey = jitter("#ffc53d", rng)
    side = rng.choice((-1, 1))
    for i in range(-1, 3):
        for j in range(-1, 2):
            hx = CX + side * (-200 + j * 104 + (i % 2) * 52)
            hy = 790 + i * 90
            hexa = [(hx + 58 * math.cos(math.radians(60 * k + 30)), hy + 58 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            sk.shape(hexa, shade(honey, 1 - 0.05 * ((i + j) % 2)), width=4)
    c = (CX + side * 40, 1080)
    rx, ry = 190, 140
    for s, rot in ((-1, -25), (1, 25)):
        sk.shape(ellipse((c[0] + s * 50, c[1] - 170), 75, 120, rot=rot), "#e8f7ff", width=4)
    sk.shape([(c[0] - side * 190, c[1] - 12), (c[0] - side * 250, c[1]), (c[0] - side * 190, c[1] + 12)], "#2b2d42", width=4)
    sk.shape(ellipse(c, rx, ry), jitter("#ffd23f", rng))
    for k in range(3):
        x0 = c[0] - side * (40 + k * 60) - 20
        sk.shade(_band(c, rx, ry, x0, x0 + 34), "#2b2d42", 255)
    hc = (c[0] + side * 190, c[1] - 30)
    sk.shape(circle(hc, 110), jitter("#ffd23f", rng))
    for s in (-1, 1):
        end = (hc[0] + s * 70, hc[1] - 190)
        sk.line(quad((hc[0] + s * 25, hc[1] - 100), (hc[0] + s * 30, hc[1] - 160), end, 10), "#2b2d42", 5)
        sk.detail(circle(end, 12), "#2b2d42")
    _eyes(sk, hc[0], hc[1] - 15, 40, 18, blush_dx=70)
    _smile(sk, hc[0], hc[1] + 30, 28)
    for _ in range(3):
        f = (CX + rng.uniform(-300, 300), rng.uniform(1310, 1360))
        sk.shape(star(f, 40, 24, 6), pal.at(rng.random()), width=4)
        sk.shape(circle(f, 12), "#ffd166", width=3)
    trail = [(c[0] - side * (260 + k * 22), c[1] + 120 + 30 * math.sin(k * 0.9)) for k in range(7)]
    sk.line([trail[i:i + 2] for i in range(0, 6, 2)], None, 3.5)
    return sk.scene(dur, hold)


def snail(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    sk.shape(spline([(CX - 405, 1300), (CX, 1270), (CX + 405, 1300), (CX + 280, 1400), (CX - 280, 1400)], True, 8),
             jitter("#86c977", rng))
    lf = leaf((CX + 120, 1290), (CX + 380, 1150), 70)
    sk.shape(lf, jitter("#4caf50", rng))
    skin = jitter("#c9e4a5", rng)
    body = ribbon(cubic((CX + 260, 1260), (CX + 100, 1270), (CX - 160, 1280), (CX - 300, 1230), 20), 90, 130, True)
    sk.shape(body, skin)
    sx = CX - 290
    for s, dx in ((-1, -40), (1, 30)):
        tip = (sx + dx, 1030)
        sk.line([(sx, 1200), tip], None, 6)
        sk.shape(circle(tip, 18), skin, width=4)
        sk.detail(circle((tip[0] + 3, tip[1] + 3), 8), "#1d1d28")
    _smile(sk, sx + 10, 1230, 26)
    sk.shade(ellipse((sx + 50, 1225), 18, 11), "#ff8fab", 140)
    shell_c = (CX + 30, 1110)
    shell_col = pal.at(rng.random())
    sk.shape(circle(shell_c, 190), shell_col)
    spiral = []
    for i in range(140):
        a = i / 140 * 4.2 * math.pi
        r = 175 * (1 - i / 150)
        spiral.append((shell_c[0] + r * math.cos(-a), shell_c[1] + r * math.sin(-a)))
    sk.line(spiral, shade(shell_col, 0.55), 7)
    sk.shade(ellipse((shell_c[0] - 70, shell_c[1] - 90), 40, 22, rot=-30), "#ffffff", 140)
    for _ in range(4):
        c = (CX + rng.uniform(-300, 300), rng.uniform(700, 900))
        sk.detail(star(c, 18, 7), pal.at(rng.random()))
    return sk.scene(dur, hold)


def octopus(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, color=jitter("#6ec6e6", rng))
    sk.shape(spline([(CX - 405, 1310), (CX, 1280), (CX + 405, 1310), (CX + 280, 1420), (CX - 280, 1420)], True, 8), "#f2d49b")
    col = jitter(rng.choice(["#ff7aa2", "#b57edc", "#ff8c61", "#ef476f"]), rng)
    tent = []
    for k in range(6):
        x0 = CX - 150 + k * 60
        dirx = (k - 2.5) * 70
        pts = cubic((x0, 1060), (x0 + dirx * 0.3, 1200), (x0 + dirx, 1220), (x0 + dirx * 1.4, 1290 - 40 * (k % 2)), 18)
        tent.append(pts)
        end = pts[-1]
        curl = [(end[0] + 26 * math.cos(a), end[1] - 26 + 26 * math.sin(a)) for a in [math.pi / 2 - i * 0.5 * (1 if dirx > 0 else -1)
                                                                                  for i in range(8)]]
        sk.shape(ribbon(pts + curl[1:], 64, 26), col)
    for pts in tent:
        for i in range(4, 16, 4):
            sk.shade(circle(pts[i], 9), "#ffe3ec", 255, phase="detail")
    head = spline([(CX - 210, 1080), (CX - 230, 870), (CX - 120, 700), (CX + 120, 700), (CX + 230, 870), (CX + 210, 1080)],
                  True, 10)
    sk.shape(head, col)
    sk.shade(ellipse((CX - 100, 800), 50, 30, rot=-30), "#ffffff", 130)
    _eyes(sk, CX, 960, 80, 30, blush_dx=140)
    _smile(sk, CX, 1020, 34)
    for _ in range(8):
        b = (CX + rng.uniform(-330, 330), rng.uniform(640, 1200))
        if math.dist(b, (CX, 990)) < 370 and abs(b[0] - CX) > 260:
            ring = circle(b, rng.uniform(8, 16), n=16)
            sk.detail_line(ring + ring[:1], "#ffffff", 3.5)
    return sk.scene(dur, hold)


# -- treats --------------------------------------------------------------------------------

def strawberry(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)

    def berry(c, s):
        x, y = c
        body = spline([(x, y - 180 * s), (x + 190 * s, y - 150 * s), (x + 170 * s, y + 40 * s), (x, y + 240 * s),
                       (x - 170 * s, y + 40 * s), (x - 190 * s, y - 150 * s)], True, 10)
        sk.shape(body, jitter("#e63946", rng))
        sk.shade(ellipse((x - 90 * s, y - 60 * s), 30 * s, 60 * s, rot=20), "#ffffff", 110)
        for i in range(5):
            for j in range(4 - abs(i - 2) // 2 + (i % 2)):
                sx = x - 120 * s + j * 75 * s + (i % 2) * 37 * s
                sy = y - 90 * s + i * 60 * s
                if abs(sx - x) < (160 - i * 25) * s:
                    sk.shade(ellipse((sx, sy), 7 * s, 11 * s), "#ffe066", 255, phase="detail")
        for k in range(6):
            a = math.radians(-90 + (k - 2.5) * 32)
            sk.shape(leaf((x, y - 170 * s), (x + 150 * s * math.cos(a), y - 170 * s + 90 * s * math.sin(a) + 40 * s), 26 * s),
                     "#4caf50", width=4)
        sk.shape(rect(x - 10 * s, y - 260 * s, x + 10 * s, y - 175 * s, 6), "#3e8e41", width=4)

    berry((CX + 150, 1150), 0.6)
    berry((CX - 60, 1000), 1.0)
    f = (CX + 260, 760)
    sk.shape(star(f, 50, 30, 5), "#ffffff", width=4)
    sk.shape(circle(f, 16), "#ffd166", width=3)
    return sk.scene(dur, hold)


def donut(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    bg = blend(pal.at(rng.random()), "#ffffff", 0.6)
    _backdrop(sk, rng, pal, color=bg)
    sk.shape(ellipse((CX, 1180), 330, 90), "#ffffff")
    sk.shade(ellipse((CX, 1185), 260, 60), "#000000", 20)
    c = (CX, 1060)
    sk.shape(ellipse(c, 270, 190), jitter("#e0a96d", rng))
    icing = pal.at(rng.random() + 0.5)
    wavy = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        r = 1 + (0.08 if i % 6 in (0, 1) and math.sin(a) > 0 else 0.0)
        wavy.append((c[0] + 235 * r * math.cos(a), c[1] - 15 + 160 * r * math.sin(a)))
    sk.shape(spline(wavy, True, 3), icing)
    sk.shade(ellipse((c[0] - 120, c[1] - 90), 60, 22, rot=-20), "#ffffff", 130)
    sk.shape(ellipse((c[0], c[1] - 10), 80, 52), bg)
    for _ in range(26):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.55, 0.88)
        x, y = c[0] + 230 * r * math.cos(a), c[1] - 15 + 155 * r * math.sin(a)
        b = rng.uniform(0, math.pi)
        sk.line([(x - 11 * math.cos(b), y - 11 * math.sin(b)), (x + 11 * math.cos(b), y + 11 * math.sin(b))],
                pal.at(rng.random(), 1.05), 7, phase="detail", tool="brush")
    return sk.scene(dur, hold)


def watermelon(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.7)

    def slice_(c, r, rot):
        def T(pts):
            return transform(pts, c, 1, rot)
        sk.shape(T(ellipse(c, r, r, a0=0, a1=math.pi, n=30)), "#3a9d5d")
        sk.shape(T(ellipse(c, r * 0.9, r * 0.9, a0=0, a1=math.pi, n=30)), "#eaf7d2", width=4)
        sk.shape(T(ellipse(c, r * 0.83, r * 0.83, a0=0, a1=math.pi, n=30)), jitter("#ff4d6d", rng))
        for k in range(7):
            a = math.pi * (k + 0.5) / 7
            for rr in (0.45, 0.65):
                if (k + int(rr * 10)) % 2:
                    p = (c[0] + r * rr * math.cos(a), c[1] + r * rr * math.sin(a))
                    sk.shade(T(ellipse(p, 8, 14, rot=math.degrees(a) + 90)), "#1d1d28", 255, phase="detail")
        sk.shade(T(ellipse((c[0] - r * 0.3, c[1] + r * 0.2), r * 0.12, r * 0.05)), "#ffffff", 110)

    slice_((CX - 30, 880), 330, rng.uniform(-12, -4))
    slice_((CX + 120, 1170), 220, rng.uniform(4, 14))
    return sk.scene(dur, hold)


# -- things --------------------------------------------------------------------------------

def car(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, color=jitter("#bfe6ff", rng))
    for _ in range(2):
        sk.shape(cloud((CX + rng.uniform(-220, 220), rng.uniform(700, 820)), 180, 50), "#ffffff")
    sk.shape(frame_clip(ellipse((CX - 200, 1220), 400, 160)), "#9fd08a")
    road = [p for p in ellipse((CX, CY), 410, 410, a0=0.55, a1=math.pi - 0.55, n=30)]
    sk.shape([(CX + 410 * math.cos(0.55), 1250)] + road + [(CX - 410 * math.cos(0.55), 1250)], "#5f6470")
    sk.line([[(x, 1300), (x + 50, 1300)] for x in range(int(CX - 300), int(CX + 300), 100)], "#ffffff", 6, together=True)
    body_col = pal.at(rng.random())
    sk.shape(spline([(CX - 170, 1000), (CX - 110, 900), (CX + 100, 900), (CX + 170, 1000)], True, 6), shade(body_col, 0.95))
    for x0, x1 in ((CX - 120, CX - 10), (CX + 10, CX + 120)):
        sk.shape([(x0 + 15, 920), (x1 - 10, 920), (x1, 1000), (x0, 1000)], "#bfe8ff", width=4)
    sk.shade([(CX - 95, 925), (CX - 70, 925), (CX - 95, 975)], "#ffffff", 160)
    body = spline([(CX - 300, 1080), (CX - 280, 1000), (CX + 280, 1000), (CX + 310, 1080), (CX + 290, 1170), (CX - 290, 1170)], True, 6)
    sk.shape(body, body_col)
    sk.line([(CX, 1010), (CX, 1160)], shade(body_col, 0.6), 4)
    sk.line([[(CX - 60, 1060), (CX - 30, 1060)], [(CX + 30, 1060), (CX + 60, 1060)]], None, 4)
    sk.shape(ellipse((CX + 280, 1060), 20, 26), "#fff3a0", width=4)
    sk.shape(rect(CX - 310, 1100, CX - 270, 1130, 8), "#ff6b6b", width=4)
    for x in (CX - 180, CX + 180):
        sk.shape(circle((x, 1170), 68), "#2b2d42")
        sk.shape(circle((x, 1170), 30), "#c9ccd6", width=4)
    return sk.scene(dur, hold)


def teacup(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    sk.shape(ellipse((CX, 1290), 300, 70), "#ffffff")
    sk.shade(ellipse((CX, 1290), 180, 36), "#000000", 25)
    cup_col = pal.at(rng.random())
    handle = ellipse((CX + 210, 1120), 80, 90, a0=-math.pi * 0.6, a1=math.pi * 0.6, n=20)
    sk.shape(ribbon(handle, 34, 34, False), cup_col)
    cup = [(CX - 220, 1000), (CX + 220, 1000)] + [(CX + 220 * math.cos(a), 1000 + 280 * math.sin(a))
                                                  for a in [math.pi * i / 24 for i in range(1, 24)]]
    sk.shape(cup, cup_col)
    stripe = [(CX - 214, 1060), (CX + 214, 1060), (CX + 205, 1110), (CX - 205, 1110)]
    sk.shade(stripe, "#ffffff", 200)
    heart = spline([(CX, 1200), (CX - 50, 1150), (CX - 40, 1120), (CX, 1135), (CX + 40, 1120), (CX + 50, 1150)], True, 6)
    sk.shade(heart, shade(cup_col, 0.7), 255)
    sk.shape(ellipse((CX, 1000), 220, 46), "#ffffff")
    sk.shape(ellipse((CX, 1006), 190, 34), jitter("#a0522d", rng))
    sk.shade(ellipse((CX - 60, 1000), 50, 9), "#ffffff", 90)
    for k in (-1, 0, 1):
        x = CX + k * 80
        sk.line([(x + 20 * math.sin(i / 2.2 + k), 930 - i * 22) for i in range(12)], "#9aa4b5", 5)
    ck = (CX - 230, 1290)
    sk.shape(circle(ck, 50), "#d9a066", width=4)
    for _ in range(5):
        sk.detail(circle((ck[0] + rng.uniform(-28, 28), ck[1] + rng.uniform(-28, 28)), 7), "#5a3a2a")
    return sk.scene(dur, hold)


def gift_box(rng, pal, dur, hold=3.0):
    sk = Sketch(rng, pal)
    _backdrop(sk, rng, pal, 0.65)
    h0 = rng.random()
    box_col, rib = pal.at(h0), pal.at(h0 + 0.5)
    sk.shape(rect(CX - 220, 1030, CX + 220, 1360, 10), box_col)
    sk.shade(rect(CX + 120, 1030, CX + 220, 1360, 10), "#000000", 30)
    sk.shape(rect(CX - 40, 1030, CX + 40, 1360), rib)
    sk.shape(rect(CX - 250, 950, CX + 250, 1040, 12), shade(box_col, 1.08))
    sk.shape(rect(CX - 40, 950, CX + 40, 1040), rib)
    for s in (-1, 1):
        loop = spline([(CX, 945), (CX + s * 90, 820), (CX + s * 200, 830), (CX + s * 170, 920)], True, 8)
        sk.shape(loop, rib)
        sk.shape(ribbon([(CX + s * 10, 950), (CX + s * 80, 1000), (CX + s * 110, 1060)], 40, 36, False), shade(rib, 0.9), width=4)
    sk.shape(ellipse((CX, 935), 42, 34), shade(rib, 0.85))
    tag = transform([(CX + 160, 1100), (CX + 260, 1100), (CX + 290, 1140), (CX + 260, 1180), (CX + 160, 1180)],
                    (CX + 160, 1140), 1, 15)
    sk.shape(tag, "#fff6e0", width=4)
    sk.line([(CX + 40, 1100), tag[0]], None, 3)
    for _ in range(18):
        c = (CX + rng.uniform(-360, 360), rng.uniform(650, 1350))
        if math.dist(c, (CX, CY)) < 380 and not (CX - 270 < c[0] < CX + 300 and 800 < c[1] < 1370):
            if rng.random() < 0.5:
                sk.detail(star(c, 16, 7), pal.at(rng.random()))
            else:
                sk.detail(circle(c, 8), pal.at(rng.random()))
    return sk.scene(dur, hold)
