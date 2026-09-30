"""Action scenes: sword duel, kung fu fight, parkour run.

Fight choreography is keyframed per beat. Pose dicts carry extra keys that mix() blends
along with the joints: x (step offset, + toward the opponent), lift (px in the air),
rot (body spin) and sw (sword angle relative to the forearm).
"""

import math
import random

from .stick import (GROUND, STAND, W, Figure, blend, burst, clamp, ease_out, floor, keyframes, label, lerp,
                    mix, pop_text, pose, run, run_lift, seg, shade, shadow, smooth, speed_lines, stars, walk)


def _dir(a, f):
    r = math.radians(a)
    return (f * math.sin(r), math.cos(r))


class Fighter:
    def __init__(self, fig, x, facing):
        self.fig, self.x, self.f = fig, x, facing

    def place(self, p, ground=GROUND):
        return self.fig.place(p, self.x + self.f * p.get("x", 0), ground, p.get("lift", 0), self.f, p.get("rot", 0))


# -- sword duel ------------------------------------------------------------------

S_GUARD = pose(lean=6, lt=-22, ls=12, rt=26, rs=26, lu=-70, lf=80, ru=55, rf=35, sw=10)
S_RAISE = pose(S_GUARD, lean=-6, ru=175, rf=15, sw=0, x=40)
S_SLASH = pose(S_GUARD, lean=18, rt=50, rs=45, lt=-40, ls=0, ru=80, rf=0, sw=0, x=100)
S_PULL = pose(S_GUARD, x=-20, ru=30, rf=100, sw=-40, lean=0)
S_THRUST = pose(S_GUARD, lean=18, rt=72, rs=72, lt=-55, ls=0, ru=90, rf=0, sw=0, x=170, lu=-100, lf=0)
S_BLOCK_HI = pose(S_GUARD, lean=-4, lt=-26, ls=30, rt=30, rs=40, ru=165, rf=-75, sw=0)
S_PARRY = pose(S_GUARD, lean=-8, ru=55, rf=55, sw=35, x=-30)
S_CROUCH = pose(S_GUARD, lean=20, lt=40, ls=80, rt=60, rs=90, x=20)
S_KNEEL = pose(lean=4, rt=85, rs=85, lt=-10, ls=100, lu=150, lf=20, ru=150, rf=20, sw=0, x=-60)
S_WIN = pose(lt=10, ls=4, rt=-12, rs=4, lu=-30, lf=20, ru=172, rf=0, sw=0, lean=-4)

DUEL_MOVES = {
    # attacker frames, defender frames, impact time, duration
    "slash": ([(0, S_GUARD), (0.45, S_RAISE), (0.72, S_SLASH), (1.3, S_SLASH), (1.8, S_GUARD)],
              [(0, S_GUARD), (0.5, S_BLOCK_HI), (0.72, S_BLOCK_HI), (0.9, pose(S_BLOCK_HI, x=-40)),
               (1.3, pose(S_BLOCK_HI, x=-40)), (1.8, S_GUARD)], 0.72, 1.8),
    "thrust": ([(0, S_GUARD), (0.45, S_PULL), (0.72, S_THRUST), (1.25, S_THRUST), (1.8, S_GUARD)],
               [(0, S_GUARD), (0.55, S_PARRY), (0.72, S_PARRY), (0.95, pose(S_PARRY, x=-90, lean=-15)),
                (1.3, pose(S_PARRY, x=-90)), (1.8, S_GUARD)], 0.72, 1.8),
    "leap": ([(0, S_GUARD), (0.35, S_CROUCH), (0.7, pose(S_RAISE, lift=240, x=120, lt=40, ls=90, rt=60, rs=100)),
              (0.95, pose(S_SLASH, x=160)), (1.45, pose(S_SLASH, x=160)), (2.0, S_GUARD)],
             [(0, S_GUARD), (0.6, S_BLOCK_HI), (0.95, pose(S_BLOCK_HI, lt=10, ls=70, rt=50, rs=90, x=-30)),
              (1.45, pose(S_BLOCK_HI, x=-50)), (2.0, S_GUARD)], 0.95, 2.0),
}


WEAPONS = {  # title, impact word
    "sword": ("SWORD DUEL", "CLANG!"),
    "staff": ("STAFF BATTLE", "CRACK!"),
    "laser": ("LASER DUEL", "VZZT!"),
}


def draw_sword(cv, J, f, sw, color, blade="#f4f6ff", length=240, weapon="sword"):
    hand = J["rhand"]
    d = _dir(J["rfore_angle"] + sw, f)
    tip = (hand[0] + d[0] * length, hand[1] + d[1] * length)
    if weapon == "staff":  # held in the middle, reaches both ways
        cv.line([(hand[0] - d[0] * length * 0.8, hand[1] - d[1] * length * 0.8), tip], "#c98a4b", 13)
        return tip
    if weapon == "laser":
        cv.line([(hand[0] - d[0] * 34, hand[1] - d[1] * 34), (hand[0] + d[0] * 14, hand[1] + d[1] * 14)], "#9aa0b8", 14)
        start = (hand[0] + d[0] * 14, hand[1] + d[1] * 14)
        cv.line([start, tip], blade, 18)
        cv.line([start, tip], "#ffffff", 6)
        return tip
    cross = (-d[1] * 26, d[0] * 26)
    cv.line([(hand[0] - d[0] * 30, hand[1] - d[1] * 30), hand], color, 12)
    cv.line([(hand[0] + cross[0], hand[1] + cross[1]), (hand[0] - cross[0], hand[1] - cross[1])], color, 10)
    cv.line([hand, tip], blade, 8)
    return tip


def sword_duel(rng, pal, dur, weapon="sword"):
    title, word = WEAPONS[weapon]
    hue = rng.random()
    A = Fighter(Figure(pal.at(hue), height=540), 320, 1)
    B = Fighter(Figure(pal.at(hue + 0.5), height=540), 760, -1)
    blade = blend("#ffffff", pal.at(hue + 0.25), 0.15)
    finale = 3.2
    beats = []
    t = 0.6
    while t < dur - finale - 1.8:
        name = rng.choice(list(DUEL_MOVES))
        attacker = rng.choice("AB")
        beats.append((t, name, attacker))
        t += DUEL_MOVES[name][3] + rng.uniform(0.1, 0.4)
    fin_t = max(t, dur - finale)
    winner = rng.choice("AB")

    def state(t):
        """Poses for A and B, sword angles, and the latest impact (time, point)."""
        pa = pb = S_GUARD
        hit = None
        for start, name, att in beats:
            atk, dfn, imp, d = DUEL_MOVES[name]
            if start <= t < start + d:
                pa_, pb_ = keyframes(atk, t - start), keyframes(dfn, t - start)
                pa, pb = (pa_, pb_) if att == "A" else (pb_, pa_)
            if start + imp <= t:
                hit = (start + imp, name, att)
        if t >= fin_t:
            k = t - fin_t
            w, l = (A, B) if winner == "A" else (B, A)
            pw = keyframes([(0, S_GUARD), (0.35, S_RAISE), (0.6, S_SLASH), (1.2, S_SLASH), (1.8, S_WIN)], k)
            pl = keyframes([(0, S_GUARD), (0.6, S_PARRY), (0.8, pose(S_PARRY, x=-80, lean=-20)), (1.6, S_KNEEL)], k)
            pa, pb = (pw, pl) if winner == "A" else (pl, pw)
            hit = (fin_t + 0.6, "finale", winner)
        return pa, pb, hit

    def impact_point(when):
        pa, pb, _ = state(when)
        ta = draw_sword_tip(A, pa)
        tb = draw_sword_tip(B, pb)
        return ((ta[0] + tb[0]) / 2, (ta[1] + tb[1]) / 2)

    def draw_sword_tip(F, p):
        J = F.place(p)
        d = _dir(J["rfore_angle"] + p.get("sw", 0), F.f)
        return (J["rhand"][0] + d[0] * 200, J["rhand"][1] + d[1] * 200)

    def draw(cv, t):
        stars(cv, 11, 70)
        cv.circle((820, 640), 110, fill=pal.dim(hue + 0.1, 0.25))  # moon
        floor(cv, pal)
        pa, pb, hit = state(t)
        loser_disarmed = t >= fin_t + 0.6
        for F, p, who in ((A, pa, "A"), (B, pb, "B")):
            J = F.place(p)
            shadow(cv, pal, J["hip"][0], 110, air=p.get("lift", 0))
            F.fig.draw(cv, J)
            if not (loser_disarmed and who != winner):
                draw_sword(cv, J, F.f, p.get("sw", 0), F.fig.color,
                           shade(F.fig.color, 1.25) if weapon == "laser" else blade, weapon=weapon)
        if loser_disarmed:  # the loser's sword spins away
            L = B if winner == "A" else A
            k = t - fin_t - 0.6
            u = clamp(k / 1.1)
            start = (L.x, GROUND - 420)
            end = (L.x - L.f * 330, GROUND - 14)
            c = (lerp(start[0], end[0], u), lerp(start[1], end[1], u) - 4 * 380 * u * (1 - u))
            ang = math.radians(90 + 900 * ease_out(u))
            d = (math.cos(ang) * 120, math.sin(ang) * 120) if u < 1 else (120, 0)
            cv.line([(c[0] - d[0], c[1] - d[1]), (c[0] + d[0], c[1] + d[1])], blade, 8)
        if hit:
            when, _, _ = hit
            age = t - when
            if age < 0.6:
                pt = impact_point(when)
                burst(cv, pt, age, pal.at(hue + 0.2, 1.2), seed=int(when * 10), n=14, size=110)
                pop_text(cv, word, pt, age, pal.at(hue + 0.15, 1.2))
        if t >= fin_t + 1.4:
            label(cv, "VICTORY!", pal, y=430, size=90)
        else:
            label(cv, title, pal, y=430, size=62)

    return draw


# -- kung fu -----------------------------------------------------------------------

K_GUARD = pose(lean=8, lt=-22, ls=16, rt=26, rs=22, lu=65, lf=110, ru=45, rf=120)
K_JAB = pose(K_GUARD, ru=92, rf=0, lean=16, x=30)
K_CROSS = pose(K_GUARD, lu=92, lf=0, ru=40, rf=120, lean=24, x=60, lt=-35, rt=40, rs=30)
K_HIGH = pose(K_GUARD, lean=-32, rt=118, rs=4, lt=-6, ls=6, lu=-40, lf=60, ru=10, rf=90, x=40)
K_FLY = pose(K_GUARD, lean=-20, rt=92, rs=0, lt=40, ls=120, lu=-60, lf=40, ru=30, rf=90)
K_HURT = pose(K_GUARD, lean=-24, head=-28, lu=20, lf=60, ru=-20, rf=60, x=-50)
K_DOWN = dict(STAND, lean=0, head=0, lt=20, ls=10, rt=-6, rs=30, lu=150, lf=20, ru=120, rf=40, rot=-90, x=-160)
K_BOW = pose(lean=55, head=10, lu=0, lf=0, ru=0, rf=0, x=-90)
K_SPIN = pose(K_GUARD, lean=-24, rt=105, rs=6, lt=-4, ls=4, lu=-50, lf=40, ru=20, rf=70, x=70)

KF_MOVES = {
    # attacker, defender, [(impact time, word)], duration
    "combo": ([(0, K_GUARD), (0.2, K_JAB), (0.38, K_GUARD), (0.6, K_CROSS), (0.9, K_CROSS), (1.3, K_GUARD)],
              [(0, K_GUARD), (0.2, K_GUARD), (0.28, pose(K_HURT, x=-15)), (0.45, K_GUARD), (0.6, K_GUARD),
               (0.7, K_HURT), (1.0, K_HURT), (1.3, K_GUARD)], [(0.2, "POW!"), (0.6, "BAM!")], 1.3),
    "high kick": ([(0, K_GUARD), (0.25, pose(K_GUARD, rt=60, rs=100, lean=-10)), (0.45, K_HIGH), (0.8, K_HIGH),
                   (1.2, K_GUARD)],
                  [(0, K_GUARD), (0.45, K_GUARD), (0.55, pose(K_HURT, x=-90, lean=-35)), (0.9, pose(K_HURT, x=-90)),
                   (1.2, K_GUARD)], [(0.45, "WHAM!")], 1.2),
    "flying kick": ([(0, K_GUARD), (0.3, pose(K_GUARD, lt=50, ls=90, rt=60, rs=100, lean=25)),
                     (0.6, pose(K_FLY, lift=230, x=170)), (0.9, pose(K_GUARD, x=200)), (2.4, pose(K_GUARD, x=200)),
                     (2.8, K_GUARD)],
                    [(0, K_GUARD), (0.6, K_GUARD), (0.75, pose(K_HURT, x=-110, lift=60, lean=-50)),
                     (1.1, pose(K_DOWN, x=-180)), (1.7, pose(K_DOWN, x=-180)),
                     (2.2, pose(K_GUARD, lt=60, ls=100, rt=40, rs=80, lean=30, x=-120)), (2.8, K_GUARD)],
                    [(0.62, "KA-POW!")], 2.8),
    "spin kick": ([(0, K_GUARD), (0.3, pose(K_GUARD, rt=-10, lt=10, lean=0, spin=1)), (0.5, K_SPIN),
                   (0.85, K_SPIN), (1.3, K_GUARD)],
                  [(0, K_GUARD), (0.5, K_GUARD), (0.6, pose(K_HURT, x=-80, head=-40)), (0.95, pose(K_HURT, x=-80)),
                   (1.3, K_GUARD)], [(0.5, "SMACK!")], 1.3),
}


G_BOX = pose(lean=14, lt=-20, ls=24, rt=24, rs=28, lu=50, lf=130, ru=40, rf=135)
BOX_JAB = pose(G_BOX, ru=92, rf=0, lean=20, x=40)
BOX_CROSS = pose(G_BOX, lu=92, lf=0, lean=28, x=70, lt=-35, rt=40, rs=30)
BOX_UPPER = pose(G_BOX, ru=155, rf=25, lean=4, x=60, rt=30, rs=30)
BOX_HOOK = pose(G_BOX, ru=95, rf=85, lean=26, x=50)
BOX_BODY = pose(G_BOX, lean=38, ru=72, rf=8, x=60, lt=-32, ls=40, rt=44, rs=64)
BOX_HURT = pose(K_HURT, lu=50, lf=120, ru=40, rf=120)

BOX_MOVES = {
    "combo": ([(0, G_BOX), (0.2, BOX_JAB), (0.38, G_BOX), (0.6, BOX_CROSS), (0.9, BOX_CROSS), (1.3, G_BOX)],
              [(0, G_BOX), (0.2, G_BOX), (0.28, pose(BOX_HURT, x=-15)), (0.45, G_BOX), (0.6, G_BOX),
               (0.7, BOX_HURT), (1.0, BOX_HURT), (1.3, G_BOX)], [(0.2, "JAB!"), (0.6, "BAM!")], 1.3),
    "uppercut": ([(0, G_BOX), (0.25, pose(G_BOX, lean=30, rt=40, rs=70, ru=20, rf=100)), (0.45, BOX_UPPER),
                  (0.8, BOX_UPPER), (1.2, G_BOX)],
                 [(0, G_BOX), (0.45, G_BOX), (0.55, pose(BOX_HURT, head=-45, lean=-32, x=-80)),
                  (0.9, pose(BOX_HURT, x=-80)), (1.2, G_BOX)], [(0.45, "UPPERCUT!")], 1.2),
    "hook": ([(0, G_BOX), (0.22, pose(G_BOX, ru=-20, rf=90, lean=0)), (0.4, BOX_HOOK), (0.75, BOX_HOOK),
              (1.1, G_BOX)],
             [(0, G_BOX), (0.4, G_BOX), (0.5, pose(BOX_HURT, head=-30, lean=-20, x=-60)),
              (0.8, pose(BOX_HURT, x=-60)), (1.1, G_BOX)], [(0.4, "WHAM!")], 1.1),
    "body shot": ([(0, G_BOX), (0.2, pose(G_BOX, lean=30, rt=40, rs=60)), (0.4, BOX_BODY), (0.75, BOX_BODY),
                   (1.1, G_BOX)],
                  [(0, G_BOX), (0.4, G_BOX), (0.5, pose(G_BOX, lean=45, head=20, x=-50, lu=20, ru=30)),
                   (0.85, pose(G_BOX, lean=40, x=-50)), (1.1, G_BOX)], [(0.4, "OOF!")], 1.1),
}

FIGHT_MODES = {  # moves, guard, title, finale title
    "kungfu": (KF_MOVES, K_GUARD, "KUNG FU FIGHT", "RESPECT"),
    "boxing": (BOX_MOVES, G_BOX, "BOXING", "K.O.!"),
}


def kung_fu(rng, pal, dur, mode="kungfu"):
    moves, guard, title, end_title = FIGHT_MODES[mode]
    boxing = mode == "boxing"
    hue = rng.random()
    A = Fighter(Figure(pal.at(hue), height=560), 360, 1)
    B = Fighter(Figure(pal.at(hue + 0.45), height=560), 720, -1)
    gloves = {"A": "#ff3b3b", "B": "#3b7bff"}
    finale = 3.0
    beats, t = [], 0.5
    names = list(moves)
    while t < dur - finale - 1.3:
        name = rng.choice(names)
        if moves[name][3] > dur - finale - t:
            name = "combo"
        beats.append((t, name, rng.choice("AB")))
        t += moves[name][3] + rng.uniform(0.2, 0.5)
    fin_t = max(t, dur - finale)
    winner = rng.choice("AB")
    hits = []  # (time, word, attacker)
    for start, name, att in beats:
        for imp, word in moves[name][2]:
            hits.append((start + imp, word, att))
    if boxing:
        hits.append((fin_t + 0.45, "K.O.!", winner))

    def state(t):
        pa = pb = guard
        for start, name, att in beats:
            atk, dfn, _, d = moves[name]
            if start <= t < start + d:
                a_, d_ = keyframes(atk, t - start), keyframes(dfn, t - start)
                pa, pb = (a_, d_) if att == "A" else (d_, a_)
        if t >= fin_t and boxing:  # knockout uppercut
            atk, _, _, _ = BOX_MOVES["uppercut"]
            k = t - fin_t
            pw = keyframes(atk[:3] + [(1.0, BOX_UPPER), (1.6, pose(lu=-150, lf=0, ru=150, rf=0, lt=14, rt=-14))], k)
            pl = keyframes([(0, G_BOX), (0.45, G_BOX), (0.6, pose(BOX_HURT, head=-50, lean=-40, x=-100, lift=40)),
                            (1.0, pose(K_DOWN, x=-200)), (9, pose(K_DOWN, x=-200))], k)
            pa, pb = (pw, pl) if winner == "A" else (pl, pw)
        elif t >= fin_t:
            bow = keyframes([(0, guard), (0.6, pose(x=-90)), (1.2, K_BOW), (2.0, K_BOW), (2.6, pose(x=-90))], t - fin_t)
            pa = pb = bow
        if boxing:  # bob and weave
            pa = dict(pa, x=pa.get("x", 0) + 10 * math.sin(t * 5))
            pb = dict(pb, x=pb.get("x", 0) + 10 * math.sin(t * 5 + 2))
        return pa, pb

    def fist_or_foot(F, p):
        J = F.place(p)
        if p.get("rt", 0) > 80:
            return J["rankle"]
        return J["lhand"] if p.get("lu", 0) > 85 else J["rhand"]

    def backdrop(cv):
        if boxing:
            cv.rect((-20, GROUND, W + 20, GROUND + 70), fill=pal.dim(hue + 0.6, 0.3))
            for x in (30, W - 30):
                cv.line([(x, GROUND), (x, GROUND - 420)], pal.dim(0.0, 0.8), 22)
            for i, h in enumerate((150, 270, 390)):
                cv.line([(30, GROUND - h), (W - 30, GROUND - h)], pal.at(hue + 0.2 + i * 0.3, 0.8), 7, caps=False)
            for i in range(-1, 12):  # crowd
                cv.circle((i * 100 + 50, 900 + 20 * (i % 2)), 34, fill=pal.dim(hue + i * 0.13, 0.18))
        else:
            for i in range(5):
                cv.rect((40 + i * 205, 600, 220 + i * 205, GROUND - 160), outline=pal.dim(hue + 0.6, 0.25), width=5)
            cv.line([(0, GROUND - 150), (W, GROUND - 150)], pal.dim(hue + 0.6, 0.3), 6)
        floor(cv, pal)

    def draw(cv, t):
        backdrop(cv)
        pa, pb = state(t)
        for F, p, who in ((A, pa, "A"), (B, pb, "B")):
            f = F.f * (-1 if 0.35 < p.get("spin", 0) < 0.99 else 1)
            J = F.fig.place(p, F.x + F.f * p.get("x", 0), GROUND, p.get("lift", 0), f, p.get("rot", 0))
            shadow(cv, pal, J["hip"][0], 110, air=p.get("lift", 0))
            F.fig.draw(cv, J)
            if boxing:
                for hand in ("lhand", "rhand"):
                    cv.circle(J[hand], 30, fill=shade(gloves[who], 0.7 if hand == "lhand" else 1.0))
        for when, word, att in hits:
            age = t - when
            if 0 <= age < 0.6:
                F = A if att == "A" else B
                pt = fist_or_foot(F, state(when)[0 if att == "A" else 1])
                burst(cv, pt, age, pal.at(hue + 0.2, 1.2), seed=int(when * 10), n=12, size=100)
                pop_text(cv, word, pt, age, pal.at(hue + 0.12, 1.25))
        big = t >= fin_t + (0.6 if boxing else 1.0)
        label(cv, end_title if big else title, pal, y=430, size=110 if big and boxing else 66)

    return draw


# -- parkour -----------------------------------------------------------------------

ZOMBIE = "#7fd67a"


def parkour(rng, pal, dur, chasers=False):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=500)
    zombies = [Figure(blend(ZOMBIE, pal.background[0], 0.15 + 0.12 * i), height=480 - 20 * i) for i in range(3)]
    speed = 640.0
    finale = 2.6
    stop_t = max(1.0, dur - finale)
    stop_x = speed * stop_t + speed * 0.5  # after decelerating for 1 s
    screen_x = 360
    obstacles = []  # (kind, x, width, height)
    x = 1100.0
    while x < stop_x - 900:
        kind = rng.choice(["crate", "crate", "wall", "gap", "gap"])
        w, h = {"crate": (200, 180), "wall": (80, 280), "gap": (280, 0)}[kind]
        obstacles.append((kind, x, w, h))
        x += w + rng.uniform(900, 1400)
    r = random.Random(rng.random())
    skyline = []
    bx = -400.0
    while bx < stop_x * 0.35 + 2000:
        bw = r.uniform(120, 260)
        skyline.append((bx, bw, r.uniform(250, 650)))
        bx += bw + r.uniform(10, 50)

    def runner_x(t):
        if t < stop_t:
            return speed * t
        k = min(1.0, t - stop_t)
        return speed * stop_t + speed * (k - k * k / 2)

    def draw(cv, t):
        X = runner_x(t)
        cv.cam = (X - screen_x, 0)
        # parallax skyline
        cam0 = cv.cam
        cv.cam = (cam0[0] * 0.35, 0)
        cv.circle((cv.cam[0] + 800, 620), 90, fill="#8a2a2a" if chasers else pal.dim(hue + 0.3, 0.3))
        for bx, bw, bh in skyline:
            cv.rect((bx, GROUND - 80 - bh, bx + bw, GROUND - 80), fill=pal.dim(hue + 0.6, 0.08))
            for wy in range(int(GROUND - 60 - bh), int(GROUND - 110), 60):
                for wx in range(int(bx + 20), int(bx + bw - 20), 44):
                    if (wx * 7 + wy * 3) % 5 == 0:
                        cv.rect((wx, wy, wx + 18, wy + 26), fill=pal.dim(hue + 0.15, 0.2))
        cv.cam = cam0
        # ground with gaps
        segs, left = [], -2000.0
        for kind, ox, w, h in obstacles:
            if kind == "gap":
                segs.append((left, ox))
                left = ox + w
        segs.append((left, stop_x + 3000))
        for a, b in segs:
            cv.line([(a, GROUND), (b, GROUND)], pal.dim(0.1, 0.6), 7, caps=False)
            cv.rect((a, GROUND + 4, b, GROUND + 40), fill=pal.dim(0.1, 0.18))
        for kind, ox, w, h in obstacles:
            if kind == "crate":
                cv.rect((ox, GROUND - h, ox + w, GROUND), fill=pal.dim(hue + 0.4, 0.3), outline=pal.at(hue + 0.4),
                        width=6, radius=6)
                cv.line([(ox, GROUND - h), (ox + w, GROUND)], pal.at(hue + 0.4, 0.7), 5)
            elif kind == "wall":
                cv.rect((ox, GROUND - h, ox + w, GROUND), fill=pal.dim(hue + 0.7, 0.3), outline=pal.at(hue + 0.7),
                        width=6, radius=4)
        if t < stop_t:
            speed_lines(cv, pal.dim(hue, 0.3), t, y0=560, y1=GROUND - 40)
        # runner
        p = run(X / 330)
        lift = run_lift(X / 330) if t < stop_t else 0.0
        rot = 0.0
        for kind, ox, w, h in obstacles:
            a, b = ox - 260, ox + w + 200
            if a <= X <= b:
                u = (X - a) / (b - a)
                air = {"crate": h + 80, "wall": h + 50, "gap": 170}[kind]
                blend_in = smooth(seg(u, 0, 0.18)) * (1 - smooth(seg(u, 0.85, 1)))
                if kind == "gap":
                    trick = dict(lean=10, head=0, lt=110, ls=140, rt=100, rs=140, lu=60, lf=80, ru=60, rf=80)
                    rot = 360 * smooth(seg(u, 0.12, 0.88))
                elif kind == "wall":
                    trick = dict(lean=55, head=-10, lt=40, ls=60, rt=70, rs=40, lu=80, lf=0, ru=100, rf=0)
                else:
                    trick = dict(lean=20, head=-6, lt=95, ls=120, rt=80, rs=110, lu=-40, lf=60, ru=110, rf=40)
                p = mix(p, trick, blend_in)
                lift = max(lift, air * 4 * u * (1 - u))
        if t >= stop_t:
            k = t - stop_t
            p = mix(p, STAND, smooth(k / 0.8))
            p = mix(p, pose(lu=-150, lf=0, ru=150, rf=0, lt=14, rt=-14), smooth((k - 1.0) / 0.5))
        J = fig.place(p, X, GROUND, lift, 1, rot)
        if chasers:
            for i, z in enumerate(zombies):
                zt = min(t, stop_t)
                zx = speed * zt - 330 - i * 120 + 25 * math.sin(t * 2 + i)
                zp = walk(zx / 140, 0.9)
                zp.update(lean=18, head=12, lu=88, lf=0, ru=84, rf=0)
                rot = 0.0
                if t > stop_t:  # they trip over each other and fall flat
                    k = clamp((t - stop_t - 0.2 * i) / 0.6)
                    zx += 160 * ease_out(k)
                    zp, rot = mix(zp, dict(STAND, lu=160, lf=0, ru=170, rf=0), k), 88 * smooth(k)
                shadow(cv, pal, zx, 80)
                z.draw(cv, z.place(zp, zx, rot=rot))
        shadow(cv, pal, X, 90, air=lift)
        fig.draw(cv, J)
        cv.cam = (0, 0)
        title = ("ZOMBIE ESCAPE", "ESCAPED!") if chasers else ("PARKOUR", "NAILED IT!")
        label(cv, title[0] if t < stop_t + 1 else title[1], pal, y=430, size=70)
        cv.text((W / 2, 520), f"{int(X / 100)} m", 48, pal.dim(hue + 0.2, 0.9))

    return draw
