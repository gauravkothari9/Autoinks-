"""More action scenes: archery, ninja fruit slicing, one-vs-all brawl and laser dodging."""

import math

from .scenes_action import K_FLY, K_GUARD, K_HIGH, K_JAB, K_SPIN
from .stick import (GROUND, STAND, W, Figure, bezier, blend, burst, clamp, ease_out, floor, keyframes, label, lerp,
                    mix, parabola, pop_text, pose, shade, shadow, smooth, stars, walk)

# -- archery ---------------------------------------------------------------------------

ARCH_REST = pose(lu=40, lf=20, ru=20, rf=60, lt=-14, ls=4, rt=16, rs=4)
ARCH_DRAW = pose(lu=90, lf=0, ru=-90, rf=176, lt=-14, ls=4, rt=16, rs=4, head=4)
TARGET = (900, 1010)
RING = 24


def archery(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=520)
    X = 170
    shot = 2.4
    finale = 2.6
    n = max(2, int((dur - finale) / shot))
    shot = (dur - finale) / n
    hits = []
    for i in range(n):
        spread = 70 * (1 - i / n) + 8
        dx, dy = rng.gauss(0, spread), rng.gauss(0, spread)
        if i == n - 1:
            dx, dy = rng.uniform(-3, 3), rng.uniform(-3, 3)  # the last one is always perfect
        hits.append((TARGET[0] - 30 + dx * 0.25, TARGET[1] + dy))
    scores = [max(0, 10 - 2 * int(math.hypot((h[0] - TARGET[0] + 30) * 4, h[1] - TARGET[1]) / RING)) for h in hits]

    def target(cv):
        cv.line([(TARGET[0] - 40, TARGET[1] + 60), (TARGET[0] - 90, GROUND)], pal.dim(0.1, 0.6), 12)
        cv.line([(TARGET[0] + 40, TARGET[1] + 60), (TARGET[0] + 90, GROUND)], pal.dim(0.1, 0.6), 12)
        for r in range(5, 0, -1):  # seen from the side it's a narrow ellipse
            col = "#ffd23f" if r == 1 else pal.at(hue + r * 0.15, 0.9) if r % 2 else "#f4f4f8"
            cv.ellipse(TARGET, 30 * r / 5 + 6, RING * r, col)

    def arrow(cv, tip, angle, color):
        d = (math.cos(angle), math.sin(angle))
        tail = (tip[0] - d[0] * 150, tip[1] - d[1] * 150)
        cv.line([tail, tip], "#e8e2d0", 5)
        for s in (1, -1):
            cv.line([tail, (tail[0] - d[0] * 24 - d[1] * 14 * s, tail[1] - d[1] * 24 + d[0] * 14 * s)], color, 5)

    def draw(cv, t):
        floor(cv, pal)
        target(cv)
        i = min(n - 1, int(t / shot))
        k = t - i * shot
        if t >= n * shot:
            i, k = n, t - n * shot
        stuck = hits[:i] + ([hits[i]] if i < n and k > 1.55 else [])
        for h in stuck:
            arrow(cv, h, 0.0, pal.at(hue + 0.5))
        if i < n:
            p = keyframes([(0, ARCH_REST), (0.6, ARCH_DRAW), (1.2, ARCH_DRAW), (1.3, pose(ARCH_DRAW, ru=-110, rf=160)),
                           (2.0, pose(ARCH_DRAW, ru=-110, rf=160)), (shot, ARCH_REST)], k)
        else:
            p = mix(ARCH_REST, pose(lu=150, lf=0, ru=-150, rf=0, lt=-14, rt=16), smooth(k / 0.6))
        J = fig.place(p, X)
        shadow(cv, pal, X, 90)
        fig.draw(cv, J)
        bow_hand = J["lhand"]
        top, bot = (bow_hand[0] - 30, bow_hand[1] - 150), (bow_hand[0] - 30, bow_hand[1] + 150)
        cv.line(bezier(top, (bow_hand[0] + 70, bow_hand[1]), bot), "#c98a4b", 10)
        drawn = i < n and 0.3 < k < 1.2
        string_pt = J["rhand"] if drawn else (top[0], bow_hand[1])
        cv.line([top, string_pt, bot], "#f4f4f8", 3, caps=False)
        if drawn:
            arrow(cv, (bow_hand[0] + 40, bow_hand[1]), 0.0, pal.at(hue + 0.5))
        if i < n and 1.2 <= k < 1.55:  # in flight
            u = (k - 1.2) / 0.35
            tip = parabola((bow_hand[0] + 40, bow_hand[1]), hits[i], 40, u)
            arrow(cv, tip, math.atan2(hits[i][1] - bow_hand[1] - 160 * (1 - 2 * u), hits[i][0] - bow_hand[0]),
                  pal.at(hue + 0.5))
        if i < n and 1.55 <= k < 2.3:
            sc = scores[i]
            word = "BULLSEYE!" if sc == 10 else f"+{sc}"
            burst(cv, hits[i], k - 1.55, pal.at(hue + 0.2, 1.2), seed=i, n=12, size=90, life=0.5)
            pop_text(cv, word, (TARGET[0] - 120, TARGET[1] - 180), k - 1.55, pal.at(hue + 0.15, 1.2), life=0.75)
        total = sum(scores[:i] + ([scores[i]] if i < n and k > 1.55 else []))
        if i >= n:
            label(cv, "PERFECT 10!", pal, y=430, size=80)
            cv.text((W / 2, 540), f"{total} POINTS", 70, pal.at(hue + 0.5, 1.1))
        else:
            label(cv, f"ARROW {i + 1}", pal, y=430, size=62)
            cv.text((W / 2, 540), f"{total} POINTS", 70, pal.at(hue + 0.5, 1.1))

    return draw


# -- ninja fruit ---------------------------------------------------------------------

FRUITS = [("#3fbf5f", "#ff4d5e", 86), ("#ff9f1c", "#ffc56b", 62), ("#e63946", "#fff1d6", 58),
          ("#8e44ad", "#d7a4ff", 52)]  # skin, flesh, radius
NINJA_WIND = pose(lean=10, ru=-60, rf=90, lu=60, lf=100, lt=-24, ls=20, rt=30, rs=30)
NINJA_THROW = pose(lean=22, ru=100, rf=0, lu=-40, lf=60, lt=-30, ls=10, rt=40, rs=40)


def ninja_fruit(rng, pal, dur):
    hue = rng.random()
    fig = Figure(shade(pal.at(hue), 0.8), height=520)
    band = "#ff3b3b"
    X = 230
    finale = 2.4
    gap = 1.1
    fruits = []
    t = 0.3
    while t < dur - finale - 1.2:
        skin, flesh, r = rng.choice(FRUITS)
        x0 = rng.uniform(640, 960)
        apex = rng.uniform(520, 820)
        hit = t + rng.uniform(0.65, 0.85)
        fruits.append((t, x0, apex, skin, flesh, r, hit, rng.uniform(-1, 1)))
        t += gap
    fly = 0.25

    def fruit_pos(f, t):
        start, x0, apex, *_ = f
        u = (t - start) / 1.6
        return (x0 - 120 * u, lerp(GROUND + 80, GROUND + 80, u) - 4 * (GROUND + 80 - apex) * u * (1 - u))

    def draw(cv, t):
        stars(cv, 3, 50)
        cv.circle((850, 600), 120, fill=pal.dim(hue + 0.3, 0.3))
        floor(cv, pal)
        pending = [f for f in fruits if f[6] - fly <= t < f[6] + 0.1]
        throws = [f for f in fruits if f[6] - fly - 0.25 <= t < f[6]]
        if t >= fruits[-1][6] + 0.8:
            p = mix(STAND, pose(lean=45, head=10, lu=0, lf=120, ru=0, rf=120), smooth((t - fruits[-1][6] - 0.8) / 0.6))
        elif throws:
            f = throws[0]
            k = (t - (f[6] - fly - 0.25)) / 0.25
            p = mix(NINJA_WIND, NINJA_THROW, smooth(k))
            if fruits.index(f) % 2:
                p = dict(p, lu=p["ru"], lf=p["rf"], ru=p["lu"], rf=p["lf"])
        else:
            p = pose(NINJA_WIND, ru=40, rf=90)
        J = fig.place(p, X)
        shadow(cv, pal, X, 90)
        fig.draw(cv, J)
        hx, hy = J["head"]
        cv.line([(hx - fig.R, hy - fig.R * 0.3), (hx + fig.R, hy - fig.R * 0.3)], band, 10)  # headband
        for j in range(2):
            wave = 12 * math.sin(t * 12 + j)
            cv.line([(hx - fig.R, hy - fig.R * 0.3), (hx - fig.R - 50, hy - fig.R * 0.1 + wave + j * 14)], band, 7)
        sliced = 0
        for f in fruits:
            start, x0, apex, skin, flesh, r, hit, spin = f
            if t < start:
                continue
            if t < hit:
                c = fruit_pos(f, t)
                cv.circle(c, r, fill=skin)
                cv.circle((c[0] - r * 0.3, c[1] - r * 0.3), r * 0.25, fill=blend(skin, "#ffffff", 0.5))
            else:
                sliced += 1
                u = t - hit
                if u > 1.4:
                    continue
                c = fruit_pos(f, hit)
                for s in (-1, 1):  # two halves drifting apart and falling
                    cx, cy = c[0] + s * 90 * u, c[1] + 900 * u * u - 200 * u
                    a0 = math.radians(90 * s + 300 * u * s * spin)
                    pts = [(cx + r * math.cos(a0 + math.pi * j / 10), cy + r * math.sin(a0 + math.pi * j / 10))
                           for j in range(11)]
                    cv.poly(pts, skin)
                    cv.poly([(cx + (r - 8) * math.cos(a0 + math.pi * j / 10), cy + (r - 8) * math.sin(a0 + math.pi * j / 10))
                             for j in range(11)], flesh)
                burst(cv, c, u, flesh, seed=int(hit * 10), n=14, size=110, life=0.4)
        for f in pending:  # shuriken in flight
            u = clamp((t - (f[6] - fly)) / fly)
            target = fruit_pos(f, f[6])
            c = (lerp(J["rhand"][0], target[0], u), lerp(J["rhand"][1], target[1], u))
            for j in range(4):
                a = t * 30 + j * math.pi / 2
                cv.poly([c, (c[0] + 30 * math.cos(a), c[1] + 30 * math.sin(a)),
                         (c[0] + 12 * math.cos(a + 0.8), c[1] + 12 * math.sin(a + 0.8))], "#dfe4ff")
        if t >= fruits[-1][6] + 0.8:
            label(cv, "PERFECT!", pal, y=430, size=90)
        else:
            label(cv, f"x{sliced}", pal, y=430, size=110)

    return draw


# -- one vs all ------------------------------------------------------------------------

HERO_MOVES = [("POW!", K_JAB), ("WHAM!", K_HIGH), ("SMACK!", K_SPIN), ("KA-POW!", K_FLY)]


def one_vs_all(rng, pal, dur):
    hue = rng.random()
    hero = Figure(pal.at(hue), height=560)
    finale = 2.6
    each = 2.0
    n = max(2, int((dur - finale) / each))
    each = (dur - finale) / n
    foes = []
    for i in range(n):
        side = -1 if i % 2 == 0 else 1
        if rng.random() < 0.3:
            side = -side
        word, move = rng.choice(HERO_MOVES)
        foes.append((side, word, move, Figure(pal.dim(hue + 0.5 + i * 0.07, 0.55), height=rng.uniform(500, 560))))

    def draw(cv, t):
        for i in range(8):  # warehouse pillars
            cv.rect((i * 150 - 20, 560, i * 150 + 20, GROUND), fill=pal.dim(hue + 0.6, 0.12))
        floor(cv, pal)
        i = min(n - 1, int(t / each))
        k = t - i * each
        if t >= n * each:
            p = keyframes([(0, K_GUARD), (0.5, pose(K_GUARD, lu=80, lf=60, ru=70, rf=30)), (1.2, K_GUARD)],
                          (t - n * each) % 1.2)
            hero.draw(cv, hero.place(p, W / 2))
            label(cv, "WHO'S NEXT?", pal, y=430, size=80)
            cv.text((W / 2, 540), f"KO x{n}", 80, pal.at(hue + 0.5, 1.1))
            return
        side, word, move, foe = foes[i]
        facing = side
        fx_stand = W / 2 + side * 240
        if k < 1.0:  # the foe charges in
            fx = lerp(W / 2 + side * 700, fx_stand, k)
            fp, frot, flift = walk(k * 3, 1.2), 0.0, 0.0
            fp.update(lu=80, lf=60, ru=60, rf=70)
        elif k < 1.2:
            fx, fp, frot, flift = fx_stand, K_GUARD, 0.0, 0.0
        else:  # launched away, spinning
            u = clamp((k - 1.2) / 0.7)
            fx = fx_stand + side * 700 * ease_out(u)
            fp, frot, flift = dict(K_GUARD, lu=-150, ru=150), 540 * u, 260 * math.sin(math.pi * u)
        hp = keyframes([(0, K_GUARD), (1.0, K_GUARD), (1.2, move), (1.5, move), (each, K_GUARD)], k)
        lift = 120 * math.sin(math.pi * clamp((k - 1.0) / 0.4)) if move is K_FLY else 0.0
        shadow(cv, pal, fx, 90, air=flift)
        foe.draw(cv, foe.place(fp, fx, lift=flift, facing=-side, rot=-frot))
        shadow(cv, pal, W / 2, 110, air=lift)
        hero.draw(cv, hero.place(hp, W / 2 + side * 40 * smooth(clamp((k - 1.0) / 0.2)), lift=lift, facing=facing))
        if 0 <= k - 1.2 < 0.6:
            pt = (fx_stand, GROUND - 420)
            burst(cv, pt, k - 1.2, pal.at(hue + 0.2, 1.2), seed=i, n=12, size=110)
            pop_text(cv, word, pt, k - 1.2, pal.at(hue + 0.12, 1.25))
        label(cv, "ONE VS ALL", pal, y=430, size=66)
        cv.text((W / 2, 540), f"KO x{i + (1 if k > 1.2 else 0)}", 80, pal.at(hue + 0.5, 1.1))

    return draw


# -- laser dodge ---------------------------------------------------------------------

DUCK = pose(lean=40, lt=90, ls=120, rt=88, rs=118, lu=60, lf=120, ru=60, rf=120, head=10)
TUCK = pose(lean=15, lt=110, ls=140, rt=105, rs=140, lu=60, lf=80, ru=60, rf=80)
MATRIX = pose(lean=-72, head=-20, lt=45, ls=95, rt=40, rs=90, lu=-120, lf=40, ru=-60, rf=40)
LASERS = {"high": (DUCK, "DUCK!", 0), "low": (TUCK, "JUMP!", 220), "mid": (MATRIX, "MATRIX!", 0)}


def laser_dodge(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    beam = "#ff2d55"
    speed = 1500.0
    X = 460
    finale = 2.6
    gap = 1.5
    shots = []
    t = 1.0
    while t < dur - finale - 0.5:
        kind = rng.choice(list(LASERS))
        shots.append((t, kind))  # t = when the beam passes the agent
        t += gap + rng.uniform(-0.2, 0.3)
    heights = {"high": GROUND - fig.h * 0.9, "low": GROUND - 70, "mid": GROUND - fig.h * 0.62}

    def draw(cv, t):
        for i in range(12):  # vault wall grid
            cv.line([(0, 520 + i * 80), (W, 520 + i * 80)], pal.dim(hue + 0.6, 0.12), 2, caps=False)
        floor(cv, pal)
        p, lift, done = pose(K_GUARD, lu=30, ru=30), 0.0, 0
        for when, kind in shots:
            pz, _, air = LASERS[kind]
            a = t - when  # hold the dodge until the beam's tail has passed
            if -0.45 < a < 0.7:
                w = smooth((a + 0.45) / 0.3) * (1 - smooth((a - 0.4) / 0.3))
                p = mix(p, pz, w)
                lift = max(lift, air * w)
            if t > when + 0.1:
                done += 1
        if shots and t > shots[-1][0] + 1.0:
            k = t - shots[-1][0] - 1.0
            p = mix(STAND, pose(ru=110, rf=120, lu=10), smooth(k / 0.5))
        for y in heights.values():  # emitters on the right wall
            cv.rect((W - 40, y - 26, W + 10, y + 26), fill=pal.dim(0.0, 0.6), radius=6)
        shadow(cv, pal, X, 100, air=lift)
        fig.draw(cv, fig.place(p, X, lift=lift))
        for when, kind in shots:
            y = heights[kind]
            if when - 1.0 < t < when - 0.45:  # warning glow
                cv.circle((W - 30, y), 30 + 8 * math.sin(t * 30), fill=beam)
            head_x = X + (when - t) * speed
            if -200 < head_x < W + 400:
                tail_x = min(W, head_x + 420)
                cv.line([(head_x, y), (tail_x, y)], blend(beam, pal.background[0], 0.4), 22)
                cv.line([(head_x, y), (tail_x, y)], "#ffe0e6", 6)
            if 0 <= t - when < 0.5:
                pop_text(cv, LASERS[kind][1], (X, GROUND - 700), t - when, pal.at(hue + 0.2, 1.2))
        if shots and t > shots[-1][0] + 1.0:
            label(cv, "TOO EASY", pal, y=430, size=80)
        else:
            label(cv, "LASER DODGE", pal, y=430, size=66)
        cv.text((W / 2, 540), f"DODGED x{done}", 70, pal.at(hue + 0.5, 1.1))

    return draw
