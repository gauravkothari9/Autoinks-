"""Sports scenes: basketball trick shots, football juggling, skateboarding and a sprint race."""

import math

from .stick import (GROUND, W, Figure, blend, burst, clamp, ease_out, floor, keyframes, label, lerp, mix,
                    parabola, pose, run, run_lift, seg, shadow, smooth, speed_lines, stars, walk)

ORANGE = "#ff8a2a"


def ball(cv, c, r, color=ORANGE, seam="#5a2a08", spin=0.0):
    cv.circle(c, r, fill=color)
    a = spin
    d = (math.cos(a) * r, math.sin(a) * r)
    cv.line([(c[0] - d[0], c[1] - d[1]), (c[0] + d[0], c[1] + d[1])], seam, 3, caps=False)
    d = (math.cos(a + math.pi / 2) * r * 0.9, math.sin(a + math.pi / 2) * r * 0.9)
    cv.line([(c[0] - d[0], c[1] - d[1]), (c[0] + d[0], c[1] + d[1])], seam, 3, caps=False)


# -- basketball ------------------------------------------------------------------

RIM_Y, RIM_X0, RIM_X1 = 760, 800, 905
B_DRIBBLE = pose(lean=16, lt=-14, ls=30, rt=28, rs=34, lu=60, lf=60, ru=30, rf=25)
B_GATHER = pose(lean=22, lt=48, ls=80, rt=52, rs=86, lu=90, lf=90, ru=95, rf=85)
B_SHOOT = pose(lean=-6, lt=-6, ls=8, rt=6, rs=8, lu=150, lf=40, ru=172, rf=18)
B_DUNK = pose(lean=-4, lt=-30, ls=70, rt=40, rs=80, lu=-30, lf=40, ru=160, rf=10)
B_HANG = pose(lean=-8, lt=-10, ls=20, rt=20, rs=30, lu=-20, lf=30, ru=178, rf=0)
B_CHEER = pose(lt=14, ls=4, rt=-14, rs=4, lu=-150, lf=0, ru=150, rf=0)


def basketball(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=540)
    R = 30
    finale = 2.4
    shots, t = [], 0.0
    while t < dur - finale - 3.0:
        kind = rng.choices(["jumper", "dunk", "brick"], [5, 3, 2])[0]
        x0 = rng.uniform(230, 420)
        d = 3.4 if kind != "dunk" else 3.3
        shots.append((t, d, kind, x0))
        t += d
    fin_t = max(t, dur - finale)
    rim_c = ((RIM_X0 + RIM_X1) / 2, RIM_Y)

    def made_before(t):
        return sum(1 for s, d, k, _ in shots if k != "brick" and s + (2.9 if k == "jumper" else 2.1) <= t)

    def shot_state(t):
        """Player pose/x/lift and ball center for time t."""
        for start, d, kind, x0 in shots:
            if t < start + d:
                k = t - start
                break
        else:
            return None
        drib_p = 0.5
        if kind == "dunk":
            if k < 1.5:  # dribble drive toward the hoop
                x = lerp(x0, 690, smooth(k / 1.5))
                p = mix(walk(k * 2.2, 1.1), B_DRIBBLE, 0.55)
                lift = 0
            elif k < 2.1:
                u = (k - 1.5) / 0.6
                x = lerp(690, 780, u)
                p = mix(B_GATHER, B_DUNK, smooth(u * 1.6))
                lift = 330 * math.sin(math.pi / 2 * u)
            elif k < 2.5:
                x, p, lift = 780, B_HANG, 330
            else:
                u = clamp((k - 2.5) / 0.4)
                x, p, lift = lerp(780, 740, u), mix(B_HANG, B_GATHER, u), 330 * (1 - ease_out(u) ** 0.5 * u)
            J = fig.place(p, x, lift=lift)
            if k < 1.5:
                v = abs(math.sin(math.pi * k / drib_p))
                bc = (J["rhand"][0] + 12, lerp(J["rhand"][1] + R, GROUND - R, v))
            elif k < 2.1:
                bc = (J["rhand"][0], J["rhand"][1] - R)
            else:
                u = clamp((k - 2.1) / 0.45)
                bc = (rim_c[0], lerp(RIM_Y - 10, GROUND - R, ease_out(u) if u < 1 else 1))
                if k > 2.55:
                    bc = (rim_c[0] - 120 * seg(k, 2.55, d), GROUND - R - 120 * abs(math.sin(math.pi * seg(k, 2.55, d) * 2)))
            return J, p, lift, bc, kind, k
        # jumper / brick
        if k < 1.4:
            x, p, lift = x0, B_DRIBBLE, 0.0
            J = fig.place(p, x)
            if k < 0.45:  # ball bounces back from the hoop
                bc = parabola((rim_c[0] - 60, GROUND - R), (J["rhand"][0], J["rhand"][1] + R), 180, k / 0.45)
            else:
                v = abs(math.sin(math.pi * (k - 0.45) / drib_p))
                bc = (J["rhand"][0] + 12, lerp(J["rhand"][1] + R, GROUND - R, v))
            return J, p, lift, bc, kind, k
        if k < 1.75:
            u = (k - 1.4) / 0.35
            p = mix(B_DRIBBLE, B_GATHER, smooth(u))
            J = fig.place(p, x0)
            return J, p, 0.0, (J["rhand"][0], J["rhand"][1] - R), kind, k
        u = clamp((k - 1.75) / 0.3)
        air = 150 * math.sin(math.pi * clamp((k - 1.75) / 0.7))
        p = mix(B_GATHER, B_SHOOT, smooth(u))
        J = fig.place(p, x0, lift=air)
        release = fig.place(B_SHOOT, x0, lift=150)["rhand"]
        if k < 2.05:
            bc = (J["rhand"][0], J["rhand"][1] - R)
        elif k < 2.9:
            v = (k - 2.05) / 0.85
            target = rim_c if kind == "jumper" else (RIM_X1 - 8, RIM_Y - 6)
            bc = parabola((release[0], release[1] - R), (target[0], target[1] - R), 250, v)
        elif kind == "jumper":
            v = clamp((k - 2.9) / 0.5)
            bc = (rim_c[0] - 30 * v, lerp(RIM_Y - R, GROUND - R, v * v))
        else:  # rim-out
            v = clamp((k - 2.9) / 0.5)
            bc = parabola((RIM_X1 - 8, RIM_Y - R), (RIM_X1 + 90, GROUND - R), 140, v)
        return J, p, air, bc, kind, k

    def draw(cv, t):
        floor(cv, pal)
        # court: key paint and three-point arc hint
        cv.rect((620, GROUND - 6, 1080, GROUND + 14), fill=pal.dim(hue + 0.5, 0.35))
        # hoop
        cv.line([(1000, GROUND), (1000, RIM_Y - 190)], pal.dim(0.0, 0.55), 18)
        cv.rect((930, RIM_Y - 210, 960, RIM_Y + 40), fill=pal.dim(hue + 0.3, 0.6), outline="#ffffff", width=5)
        cv.line([(960, RIM_Y - 150), (1000, RIM_Y - 150)], pal.dim(0.0, 0.55), 12)
        st = shot_state(t)
        net_shake = 0.0
        if st and st[4] != "brick":
            k = st[5]
            hit = 2.9 if st[4] == "jumper" else 2.1
            if 0 <= k - hit < 0.5:
                net_shake = math.sin((k - hit) * 40) * 14 * (1 - (k - hit) / 0.5)
        for i in range(6):  # net
            xa = lerp(RIM_X0, RIM_X1, i / 5)
            xb = lerp(RIM_X0 + 22, RIM_X1 - 22, i / 5) + net_shake
            cv.line([(xa, RIM_Y), (xb, RIM_Y + 110)], "#dde3ff", 3, caps=False)
        for j in (40, 80):
            cv.line([(RIM_X0 + j * 0.2, RIM_Y + j), (RIM_X1 - j * 0.2, RIM_Y + j)], "#dde3ff", 3, caps=False)
        if st:
            J, p, lift, bc, kind, k = st
            shadow(cv, pal, J["hip"][0], 100, air=lift)
            shadow(cv, pal, bc[0], 34, air=GROUND - bc[1])
            behind = kind == "dunk" and k > 2.1 or (kind == "jumper" and k > 2.85)
            if behind:
                ball(cv, bc, R, spin=t * 8)
            fig.draw(cv, J)
            if not behind:
                ball(cv, bc, R, spin=t * 8)
            cv.line([(RIM_X0 - 8, RIM_Y), (RIM_X1, RIM_Y)], ORANGE, 10)
            hit = 2.9 if kind == "jumper" else 2.1 if kind == "dunk" else 2.9
            word = {"jumper": "SWISH!", "dunk": "SLAM DUNK!", "brick": "CLANK!"}[kind]
            if 0 <= k - hit < 0.8:
                burst(cv, rim_c, k - hit, pal.at(hue + 0.2, 1.2), seed=int(t), n=14, size=120, life=0.5)
                cv.text((W / 2, 600), word, 100 * (0.7 + 0.3 * ease_out((k - hit) / 0.2)), pal.at(hue + 0.15, 1.2))
        else:
            k = t - fin_t
            p = mix(B_DRIBBLE, B_CHEER, smooth(k / 0.6))
            J = fig.place(p, 420, lift=40 * abs(math.sin(k * 6)) if k > 0.6 else 0)
            shadow(cv, pal, 420, 100)
            fig.draw(cv, J)
            ball(cv, (560, GROUND - R), R)
            cv.line([(RIM_X0 - 8, RIM_Y), (RIM_X1, RIM_Y)], ORANGE, 10)
        label(cv, f"SCORE  {made_before(t) * 2}", pal, y=430, size=70)

    return draw


# -- football juggling -------------------------------------------------------------

TOUCHES = {
    "RIGHT FOOT": (pose(rt=48, rs=42, lt=-4, ls=6, lean=-4, lu=-55, lf=30, ru=45, rf=30), "rtoe"),
    "LEFT FOOT": (pose(lt=48, ls=42, rt=-4, rs=6, lean=-4, lu=-55, lf=30, ru=45, rf=30), "ltoe"),
    "KNEE": (pose(rt=95, rs=95, lt=-2, ls=6, lean=-2, lu=-60, lf=40, ru=50, rf=40), "rknee"),
    "HEAD": (pose(lean=-10, head=-20, lt=8, ls=20, rt=-8, rs=20, lu=-70, lf=30, ru=70, rf=30), "head"),
}
READY = pose(lean=2, lt=8, ls=14, rt=-8, rs=14, lu=-40, lf=30, ru=40, rf=30)
KICK_BACK = pose(lean=-12, rt=-60, rs=100, lt=4, ls=10, lu=-80, lf=20, ru=60, rf=30)
KICK = pose(lean=-24, rt=100, rs=0, lt=6, ls=14, lu=-100, lf=10, ru=40, rf=30)


def soccer(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    X = 400
    R = 28
    gap = 0.62
    finale = 3.4
    n = max(4, int((dur - finale - 0.8) / gap))
    names = list(TOUCHES)
    seq = [rng.choice(names[:3]) for _ in range(n)]
    for i in range(3, n, rng.randint(3, 5)):
        seq[i] = rng.choice(names)
    times = [0.8 + i * gap for i in range(n)]
    kick_t = times[-1] + gap * 1.6
    goal = (950, GROUND - 170)

    def contact(i):
        p, joint = TOUCHES[seq[i]]
        J = fig.place(p, X, lift=12 if seq[i] == "HEAD" else 0)
        pt = J[joint]
        off = fig.R + R if joint == "head" else R + 10
        return (pt[0] + 6, pt[1] - off)

    contacts = [contact(i) for i in range(n)]
    kick_pt = fig.place(KICK, X)["rtoe"]
    kick_ball = (kick_pt[0] + 10, kick_pt[1] - R)

    def draw(cv, t):
        floor(cv, pal)
        # goal on the right
        post = pal.dim(0.0, 0.9)
        k_goal = t - (kick_t + 0.45)
        bulge = 30 * math.sin(clamp(k_goal / 0.5) * math.pi) if k_goal > 0 else 0
        cv.line([(900, GROUND), (900, GROUND - 300), (1080, GROUND - 300)], post, 14)
        for i in range(7):
            y = GROUND - 300 + i * 50
            cv.line([(900, y), (1080 + bulge, y + 10)], pal.dim(hue + 0.5, 0.4), 3, caps=False)
        for i in range(5):
            x = 900 + i * 45
            cv.line([(x + bulge * i / 4, GROUND - 300), (x + bulge * i / 4, GROUND)], pal.dim(hue + 0.5, 0.4), 3,
                    caps=False)
        # player pose and ball
        frames = [(0, READY)]
        for i, tt in enumerate(times):
            frames += [(tt - gap * 0.45, READY), (tt, TOUCHES[seq[i]][0])]
        frames += [(times[-1] + gap * 0.5, READY), (kick_t - 0.35, KICK_BACK), (kick_t, KICK),
                   (kick_t + 0.6, KICK), (kick_t + 1.2, pose(lu=-150, lf=0, ru=150, rf=0, lt=14, rt=-14))]
        p = keyframes(frames, t)
        head_lift = 0
        for i, tt in enumerate(times):
            if seq[i] == "HEAD":
                head_lift = max(head_lift, 12 * (1 - clamp(abs(t - tt) / 0.25)))
        celebrate = t > kick_t + 1.2
        lift = 50 * abs(math.sin((t - kick_t) * 6)) if celebrate else head_lift
        J = fig.place(p, X, lift=lift)
        if t < times[0]:
            bc = parabola((X + 160, GROUND - R), contacts[0], 260, t / times[0])
        elif t < times[-1]:
            i = max(j for j, tt in enumerate(times) if tt <= t)
            u = (t - times[i]) / gap
            a, b = contacts[i], contacts[i + 1]
            bc = parabola(a, b, 170 + (a[1] - min(a[1], b[1])) * 0.3, u)
        elif t < kick_t:
            u = (t - times[-1]) / (kick_t - times[-1])
            bc = parabola(contacts[-1], kick_ball, 380, u)
        else:
            u = clamp((t - kick_t) / 0.45)
            if u < 1:
                bc = parabola(kick_ball, goal, 80, ease_out(u))
            else:
                v = clamp((t - kick_t - 0.45) / 0.6)
                bc = (goal[0] + 50 * v, lerp(goal[1], GROUND - R, v * v))
        shadow(cv, pal, X, 100, air=lift)
        shadow(cv, pal, bc[0], 30, air=GROUND - bc[1])
        fig.draw(cv, J)
        ball(cv, bc, R, color="#f4f6ff", seam="#1a1a2e", spin=t * 7)
        done = sum(1 for tt in times if tt <= t)
        if t < kick_t + 0.45:
            label(cv, f"x{done}", pal, y=440, size=110)
            if 0 < done <= n:
                cv.text((W / 2, 560), seq[done - 1], 44, pal.dim(hue + 0.3, 0.9))
        else:
            k = t - kick_t - 0.45
            cv.text((W / 2, 470), "GOAL!", 150 * (0.6 + 0.4 * ease_out(k / 0.25)), pal.at(hue + 0.15, 1.2))
            for j in range(3):
                burst(cv, (300 + j * 240, 700 + 80 * (j % 2)), (k - j * 0.25) % 0.9, pal.at(hue + j * 0.3, 1.2),
                      seed=j, n=16, size=130, life=0.9)
            cv.text((W / 2, 610), f"{n} touches", 46, pal.dim(hue + 0.3, 0.9))

    return draw


# -- skateboard --------------------------------------------------------------------

SKATE = dict(lean=8, head=0, lt=-22, ls=30, rt=24, rs=30, lu=-70, lf=20, ru=60, rf=20)
SK_CROUCH = dict(SKATE, lean=18, lt=-30, ls=80, rt=40, rs=80, lu=-80, ru=80)
SK_AIR = dict(SKATE, lean=10, lt=-10, ls=90, rt=50, rs=100, lu=-110, lf=10, ru=100, rf=10)
SK_PUSH = dict(SKATE, lt=-40, ls=10, lean=14)


def board(cv, c, length, color, wheel, flip=0.0, spin=0.0):
    """Deck centered at c. flip spins it about its long axis (kickflip), spin about the vertical (shuvit)."""
    half = length / 2 * abs(math.cos(spin))
    thick = 7 + 22 * abs(math.sin(flip))
    under = math.cos(flip) >= 0
    x0, x1, y = c[0] - half, c[0] + half, c[1]
    cv.line([(x0 - 26 * abs(math.cos(spin)), y - 16), (x0, y), (x1, y), (x1 + 26 * abs(math.cos(spin)), y - 16)],
            color if under else blend(color, "#ffffff", 0.5), thick)
    if half > 30:
        wy = y + (22 if under else -22)
        for wx in (x0 + half * 0.35, x1 - half * 0.35):
            cv.circle((wx, wy), 13, fill=wheel)


SNOW = "#e8f1ff"


def skateboard(rng, pal, dur, snow=False):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=500)
    deck_col, wheel_col = pal.at(hue + 0.5), "#e8e8f0"
    speed = 560.0
    finale = 2.8
    stop_t = max(1.0, dur - finale)
    screen_x = 420
    obstacles = []
    x = 1000.0
    while x < speed * stop_t - 900:
        kind = rng.choice(["cone", "rail", "cone", "gap"])
        w = {"cone": 160 if snow else 60, "rail": 520, "gap": 240}[kind]
        air_tricks = ["BACKFLIP", "FRONTFLIP", "360", "INDY GRAB"] if snow else ["OLLIE", "KICKFLIP", "360 SHUVIT"]
        trick = rng.choice(air_tricks) if kind != "rail" else ("BOARDSLIDE" if snow else "50-50 GRIND")
        obstacles.append((kind, x, w, trick))
        x += w + rng.uniform(800, 1200)
    BOARD_UP = 16 if snow else 44  # board top above the ground when rolling

    def rider_x(t):
        if t < stop_t:
            return speed * t
        k = min(1.4, t - stop_t)
        return speed * stop_t + speed * (k - k * k / 2.8)

    def draw(cv, t):
        X = rider_x(t)
        cv.cam = (X - screen_x, 0)
        cam0 = cv.cam
        cv.cam = (cam0[0] * 0.3, 0)
        stars(cv, 5, 50, parallax=0)
        for i in range(-1, int(X * 0.3 / 400) + 6):  # ramps (or pine trees) in the distance
            bx = i * 400
            if snow:
                for j, (dx, h) in enumerate(((0, 300), (150, 380), (270, 260))):
                    cv.poly([(bx + dx - 70, GROUND - 80), (bx + dx + 70, GROUND - 80), (bx + dx, GROUND - 80 - h)],
                            pal.dim(hue + 0.35 + j * 0.05, 0.16))
            else:
                cv.poly([(bx, GROUND - 90), (bx + 160, GROUND - 260), (bx + 260, GROUND - 260), (bx + 400, GROUND - 90)],
                        pal.dim(hue + 0.6, 0.09))
        cv.cam = cam0
        segs, left = [], -2000.0
        for kind, ox, w, _ in obstacles:
            if kind == "gap":
                segs.append((left, ox))
                left = ox + w
        segs.append((left, X + 3000))
        for a, b in segs:
            if snow:
                cv.rect((a, GROUND, b, GROUND + 90), fill=blend(SNOW, pal.background[0], 0.35))
            cv.line([(a, GROUND), (b, GROUND)], SNOW if snow else pal.dim(0.1, 0.6), 7, caps=False)
            cv.rect((a, GROUND + 4, b, GROUND + 40), fill=pal.dim(0.1, 0.18))
        for kind, ox, w, _ in obstacles:
            if kind == "cone" and snow:  # snow kicker
                cv.poly([(ox, GROUND), (ox + w * 0.75, GROUND - 90), (ox + w, GROUND - 90), (ox + w, GROUND)],
                        blend(SNOW, pal.background[0], 0.2))
            elif kind == "cone":
                cv.poly([(ox, GROUND), (ox + w, GROUND), (ox + w / 2, GROUND - 95)], ORANGE)
                cv.line([(ox + 16, GROUND - 40), (ox + w - 16, GROUND - 40)], "#ffffff", 8, caps=False)
            elif kind == "rail":
                cv.line([(ox, GROUND - 120), (ox + w, GROUND - 120)], "#cfd6ff", 10)
                for px in (ox + 30, ox + w - 30):
                    cv.line([(px, GROUND - 120), (px, GROUND)], pal.dim(0.0, 0.7), 8)
        if snow:  # falling snow
            for i in range(40):
                sx = (i * 197 + cam0[0] * 0.2) % (W + 40) + cam0[0] - 20
                sy = 300 + (i * 131 + t * (60 + i % 5 * 20)) % (GROUND - 300)
                cv.circle((sx + 20 * math.sin(t + i), sy), 3 + i % 3, fill="#ffffff")
        elif t < stop_t:
            speed_lines(cv, pal.dim(hue, 0.3), t, y0=600, y1=GROUND - 60, speed=2000)
        p = dict(SKATE)
        if snow:
            p.update(lt=-26, ls=40, rt=26, rs=40, lean=6)
        push = (t % 3.0) / 0.8
        if push < 1 and t < stop_t and not snow:
            p = mix(SKATE, SK_PUSH, math.sin(math.pi * push))
        lift, flip, spin, drop, trick_name, grind, rot, facing = 0.0, 0.0, 0.0, 0.0, None, False, 0.0, 1
        for kind, ox, w, trick in obstacles:
            a, b = ox - 240, ox + w + 200
            if a <= X <= b:
                u = (X - a) / (b - a)
                trick_name = trick
                inb = smooth(seg(u, 0, 0.15)) * (1 - smooth(seg(u, 0.85, 1)))
                if kind == "rail":
                    ga, gb = (ox - a) / (b - a), (ox + w - a) / (b - a)
                    rail_lift = 120 + 22 - BOARD_UP  # wheels resting on the rail
                    if u < ga:  # ollie up onto the rail
                        v = u / ga
                        lift = rail_lift * smooth(v) + 90 * math.sin(math.pi * v)
                    elif u < gb:
                        lift, grind = rail_lift, True
                    else:  # hop off
                        v = (u - gb) / (1 - gb)
                        lift = rail_lift * (1 - smooth(v)) + 70 * math.sin(math.pi * v)
                    p = mix(p, SK_CROUCH, inb * 0.6)
                else:
                    lift = (230 if kind == "gap" else 190) * 4 * u * (1 - u)
                    p = mix(p, SK_AIR, inb)
                    air = seg(u, 0.2, 0.8)
                    if trick in ("BACKFLIP", "FRONTFLIP"):
                        rot = (-360 if trick == "BACKFLIP" else 360) * smooth(air)
                        lift *= 1.25
                    elif trick == "360":
                        facing = -1 if 0.3 < smooth(air) < 0.7 else 1
                    elif trick == "INDY GRAB":
                        p = mix(p, dict(SK_AIR, ru=-20, rf=10, lean=30), math.sin(math.pi * air))
                    if trick == "KICKFLIP":
                        flip = 2 * math.pi * smooth(air)
                    elif trick == "360 SHUVIT":
                        spin = 2 * math.pi * smooth(air)
                    drop = 50 * math.sin(math.pi * air)
        if t >= stop_t:
            k = t - stop_t
            p = mix(p, SKATE, smooth(k))
            p = mix(p, dict(SKATE, lu=-150, lf=0, ru=150, rf=0, lean=0), smooth((k - 1.4) / 0.5))
        deck_y = GROUND - BOARD_UP - lift
        if snow:  # the board is strapped to the feet, so it turns with the rider
            hip = fig.place(p, X, deck_y - 8, facing=facing)["hip"]
            J = fig.joints(p, hip[0], hip[1], facing, rot)
            a, b = J["lankle"], J["rankle"]
            v = (b[0] - a[0], b[1] - a[1])
            n = math.hypot(*v) or 1
            v = (v[0] / n, v[1] / n)
            d = (J["hip"][0] - J["neck"][0], J["hip"][1] - J["neck"][1])  # body "down"
            n = math.hypot(*d) or 1
            d = (d[0] / n * 14, d[1] / n * 14)
            ends = [(a[0] - v[0] * 90 + d[0], a[1] - v[1] * 90 + d[1]), (b[0] + v[0] * 90 + d[0], b[1] + v[1] * 90 + d[1])]
            shadow(cv, pal, X, 140, air=lift)
            cv.line(ends, deck_col, 16)
            fig.draw(cv, J)
        else:
            J = fig.place(p, X, deck_y - 8)
            board(cv, (X + 6, deck_y + drop), 280, deck_col, wheel_col, flip, spin)
            shadow(cv, pal, X, 140, air=lift)
            fig.draw(cv, J)
        if grind:
            burst(cv, (X - 60, GROUND - 120), (t * 3) % 0.3, "#ffd166", seed=int(t * 10), n=8, size=60, life=0.3)
        cv.cam = (0, 0)
        idle, done_text = ("SNOWBOARD", "STOMPED IT!") if snow else ("SKATE SESSION", "CLEAN LANDING!")
        label(cv, trick_name or (idle if t < stop_t + 1 else done_text), pal, y=430, size=68)

    return draw


# -- sprint race -------------------------------------------------------------------

CROUCH = dict(lean=72, head=-20, lt=10, ls=110, rt=92, rs=120, lu=-70, lf=0, ru=-66, rf=0)
LANES = [(1130, 340), (1240, 370), (1350, 400), (1460, 430)]  # (ground y, height), back to front


HURDLE_POSE = dict(lean=30, head=-10, lt=-70, ls=95, rt=95, rs=5, lu=40, lf=30, ru=-40, rf=40)


def race(rng, pal, dur, hurdles=False):
    hue = rng.random()
    hurdle_xs = [400 + i * 330 for i in range(7)] if hurdles else []
    runners = [Figure(pal.at(hue + i / 4), height=h) for i, (_, h) in enumerate(LANES)]
    heats = max(1, round(dur / 12))
    heat_len = dur / heats
    count, cheer = 1.6, 2.6
    track = 2600.0
    plans = []
    for h in range(heats):
        run_time = max(4.0, heat_len - count - cheer)
        order = list(range(4))
        rng.shuffle(order)
        finish = {lane: run_time * (1 + 0.035 * rank + rng.uniform(0, 0.02) * (rank > 0))
                  for rank, lane in enumerate(order)}
        wobble = {lane: (rng.uniform(0.04, 0.09), rng.uniform(0, 6.28)) for lane in range(4)}
        plans.append((h * heat_len, run_time, order[0], finish, wobble))

    def pos(plan, lane, tr):
        _, run_time, _, finish, wobble = plan
        T = finish[lane]
        if tr <= 0:
            return 0.0, 0.0
        if tr < T:
            u = tr / T
            a, ph = wobble[lane]  # each runner surges and fades differently, so the lead changes
            g = u - 0.06 * (1 - u) * math.sin(math.pi * u) + a * math.sin(2 * math.pi * u + ph) * u * (1 - u)
            return track * clamp(g, 0, 1), track / T
        k = tr - T  # coast after the line
        return track + (track / T) * (k - k * k / 3.0 if k < 1.5 else 0.75), max(0.0, track / T * (1 - k / 1.5))

    def draw(cv, t):
        hi = min(heats - 1, int(t / heat_len))
        plan = plans[hi]
        start, run_time, winner, finish, _ = plan
        tr = t - start - count
        xs = [pos(plan, lane, tr) for lane in range(4)]
        lead = max(x for x, _ in xs)
        cam_x = clamp(lead - 560, -300, track + 200)
        cv.cam = (cam_x, 0)
        # stands in the back with parallax crowd dots
        cam0 = cv.cam
        cv.cam = (cam0[0] * 0.4, 0)
        for i in range(int(cv.cam[0] / 70) - 2, int(cv.cam[0] / 70) + 20):
            for row in range(4):
                cx = i * 70 + (row % 2) * 35
                bob = 6 * math.sin(t * 8 + i * 1.7 + row) if tr > run_time - 0.5 else 0
                cv.circle((cx, 800 + row * 55 + bob), 16, fill=pal.dim(hue + (i * 0.37 + row * 0.2) % 1, 0.3))
        cv.cam = cam0
        cv.rect((cam_x - 50, 1010, cam_x + W + 50, 1500), fill=pal.dim(0.95, 0.12))
        for y, _ in LANES:
            cv.line([(cam_x - 50, y + 12), (cam_x + W + 50, y + 12)], pal.dim(0.1, 0.4), 4, caps=False)
        cv.line([(0, 1010), (0, 1500)], "#ffffff", 8)  # start line
        for j in range(11):  # checkered finish
            cv.rect((track + 30, 1010 + j * 44, track + 52, 1032 + j * 44), fill="#ffffff")
            cv.rect((track + 52, 1032 + j * 44, track + 74, 1054 + j * 44), fill="#ffffff")
        wx = xs[winner][0]
        if wx < track:
            cv.line([(track + 52, 1040), (track + 52, 1480)], pal.at(hue + 0.1, 1.2), 5)  # tape
        else:
            k = clamp((wx - track) / 300)
            cv.line([(track + 52, 1040), (track + 52 - 60 * k, 1040 + 300 * k)], pal.at(hue + 0.1, 1.2), 5)
            cv.line([(track + 52, 1480), (track + 52 + 80 * k, 1480 - 40 * k)], pal.at(hue + 0.1, 1.2), 5)
        for lane in range(4):
            fig = runners[lane]
            gy, _ = LANES[lane]
            x, v = xs[lane]
            hh = fig.h * 0.2  # hurdle height scales with the lane's depth
            for hx in hurdle_xs:
                cv.line([(hx, gy), (hx, gy - hh)], "#dfe4ff", 5)
                cv.line([(hx - 16, gy - hh), (hx + 16, gy - hh)], pal.at(hue + 0.5, 1.1), 12)
            if tr <= 0:
                p, lift = CROUCH, 0.0
            else:
                phase = x / (fig.h * 0.95)
                p = run(phase)
                lift = run_lift(phase, 14)
                if tr < 0.35:
                    p = mix(CROUCH, p, smooth(tr / 0.35))
                for hx in hurdle_xs:
                    u = (x - (hx - 150)) / 300
                    if 0 <= u <= 1 and x < track:
                        p = mix(p, HURDLE_POSE, math.sin(math.pi * u))
                        lift = max(lift, hh * 1.1 * math.sin(math.pi * u))
                if x >= track:
                    k = clamp((tr - finish[lane]) / 1.2)
                    end = pose(lu=-150, lf=0, ru=150, rf=0) if lane == winner else pose(lean=40, lu=20, ru=20,
                                                                                           lt=10, rt=-10)
                    p = mix(p, end, smooth(k))
                    lift *= 1 - k
            shadow(cv, pal, x, 70, y=gy, air=lift)
            fig.draw(cv, fig.place(p, x, gy, lift))
        cv.cam = (0, 0)
        if tr < 0:
            n = int(-tr / (count / 3)) + 1
            cv.text((W / 2, 600), str(min(3, n)), 200, pal.at(hue + 0.15, 1.2))
        elif tr < 0.6:
            cv.text((W / 2, 600), "GO!", 200 * (1 - tr / 1.2), pal.at(hue + 0.4, 1.2))
        if wx >= track:
            cv.text((W / 2, 600), f"LANE {winner + 1} WINS!", 100, runners[winner].color)
        name = "110 M HURDLES" if hurdles else "100 M DASH"
        label(cv, f"HEAT {hi + 1}" if heats > 1 else name, pal, y=430, size=62)

    return draw
