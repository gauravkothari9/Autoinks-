"""Dance scenes: dance crew, breakdance, moonwalk, ballet, dance battle and robot dance."""

import math

from .stick import (GROUND, STAND, W, Figure, Timeline, blend, clamp, ease_out, floor, keyframes, label, lerp, mix,
                    pose, seg, shade, shadow, smooth)

# Each move is a list of poses, one per beat, with the body lift (px) on that beat.
MOVES = {
    "FIST PUMP": [(pose(ru=165, rf=10, lu=20, lf=30, lt=12, ls=14, rt=-10, rs=14), 20),
                  (pose(lean=6, ru=70, rf=100, lu=10, lf=40, lt=20, ls=45, rt=-2, rs=45), 0)],
    "DISCO POINT": [(pose(ru=155, rf=0, lu=-30, lf=90, lt=4, ls=4, rt=-28, rs=40), 0),
                    (pose(ru=30, rf=0, lu=-30, lf=90, lt=18, ls=35, rt=-8, rs=6), 0)],
    "ARM SWING": [(pose(lean=-6, lu=100, lf=40, ru=120, rf=40, lt=18, ls=30, rt=-6, rs=6), 0),
                  (pose(lean=6, lu=-120, lf=-40, ru=-100, rf=-40, lt=6, ls=6, rt=-18, rs=30), 0)],
    "STAR JUMP": [(pose(lean=18, lt=40, ls=70, rt=36, rs=70, lu=-40, lf=10, ru=-30, rf=10), 0),
                  (pose(lt=28, ls=0, rt=-28, rs=0, lu=-150, lf=0, ru=150, rf=0), 120)],
    "ROBOT": [(pose(ru=90, rf=90, lu=-10, lf=90, lt=6, ls=0, rt=-6, rs=0, head=12), 0),
              (pose(ru=10, rf=90, lu=90, lf=90, lt=6, ls=0, rt=-6, rs=0, head=-12), 0)],
    "RUNNING MAN": [(pose(rt=62, rs=95, lt=-12, ls=10, lu=55, lf=95, ru=-30, rf=60), 10),
                    (pose(lt=62, ls=95, rt=-12, rs=10, ru=55, rf=95, lu=-30, lf=60), 10)],
    "WAVE": [(pose(lean=-4, lu=-90, lf=35, ru=90, rf=-35, lt=10, ls=20, rt=-10, rs=4), 0),
             (pose(lean=4, lu=-90, lf=-35, ru=90, rf=35, lt=10, ls=4, rt=-10, rs=20), 0)],
}
FINAL = pose(lt=24, ls=6, rt=-24, rs=6, lu=-145, lf=0, ru=145, rf=0, head=-10)


def dance_moves(rng, dur, beat, finale):
    """[(start, end, move name)] covering dur - finale, 8 beats per move."""
    names = list(MOVES)
    rng.shuffle(names)
    plan, t, i = [], 0.0, 0
    while t < dur - finale - 0.1:
        end = min(t + 8 * beat, dur - finale)
        plan.append((t, end, names[i % len(names)]))
        t, i = end, i + 1
    return plan


def dance_pose(plan, t, beat):
    for start, end, name in plan:
        if t < end:
            steps = MOVES[name]
            n = int((t - start) / beat)
            k = (t - start) / beat - n
            a, lift_a = steps[(n - 1) % len(steps)] if n else (STAND, 0)
            b, lift_b = steps[n % len(steps)]
            u = ease_out(seg(k, 0, 0.45))
            return mix(a, b, u), lerp(lift_a, lift_b, u) * math.sin(math.pi * min(1, k / 0.9)) if lift_b else 0.0, name
    return None, 0.0, None


def dance_party(rng, pal, dur):
    beat = 60 / rng.uniform(112, 128)
    finale = 2.5
    plan = dance_moves(rng, dur, beat, finale)
    hue = rng.random()
    dancers = [  # (figure, x, ground, facing, beat delay)
        (Figure(pal.at(hue + 0.33), height=500), 230, GROUND - 60, 1, 0.0),
        (Figure(pal.at(hue + 0.66), height=500), 850, GROUND - 60, -1, 0.0),
        (Figure(pal.at(hue), height=600), W / 2, GROUND, 1, 0.0),
    ]
    end = plan[-1][1]

    def draw(cv, t):
        b = t / beat
        pulse = 1 - (b % 1)
        # swinging stage lights
        for side, x0 in ((1, -40), (-1, W + 40)):
            a = math.radians(side * (25 + 20 * math.sin(t * 1.3 + side)))
            tip = (x0 + side * 900 * math.sin(abs(a) + 0.4), 200 + 1300 * math.cos(a))
            col = pal.dim(hue + int(b) * 0.25 + (0.5 if side < 0 else 0), 0.18 + 0.12 * pulse)
            cv.poly([(x0, 180), (tip[0] - 150, tip[1]), (tip[0] + 150, tip[1])], col)
        # light-up floor tiles
        for i in range(9):
            lit = (i + int(b)) % 3 == 0
            col = pal.dim(hue + i / 9, 0.55 if lit else 0.14)
            cv.rect((i * 124 - 18, GROUND + 18, i * 124 + 98, GROUND + 130), fill=col, radius=10)
        floor(cv, pal, y=GROUND - 60, k=0.3)
        floor(cv, pal)
        if t < end:
            p, lift, name = dance_pose(plan, t, beat)
        else:
            last, _ = MOVES[plan[-1][2]][0]
            p, lift, name = mix(last, FINAL, smooth((t - end) / 0.6)), 0.0, "FREEZE!"
        for fig, x, ground, facing, _ in dancers:
            shadow(cv, pal, x, 100, y=ground, air=lift)
            fig.draw(cv, fig.place(p, x, ground, lift, facing))
        label(cv, name, pal, y=420, size=66 + 10 * pulse)

    return draw


# -- breakdance ------------------------------------------------------------------

def _toprock(k):
    step = [pose(rt=32, rs=24, lt=-24, ls=10, lu=-45, lf=40, ru=70, rf=80, lean=8),
            pose(lt=32, ls=24, rt=-24, rs=10, ru=-45, rf=40, lu=70, lf=80, lean=8)]
    n = int(k * 4)
    u = smooth((k * 4) % 1)
    return mix(step[n % 2], step[(n + 1) % 2], u), 0.0, 0.0, 70 * math.sin(k * 2 * math.pi)


def _headspin(k):
    w = k * 2 * math.pi * 5
    spread = 38 * math.cos(w)
    p = dict(lean=0, head=0, lt=18 + spread, ls=10, rt=-18 - spread, rs=10, lu=150, lf=40, ru=150, rf=40)
    return p, 180.0, 0.0, 0.0


def _windmill(k):
    w = k * 2 * math.pi * 3
    p = dict(lean=0, head=-10, lt=90 + 70 * math.sin(w), ls=0, rt=90 - 70 * math.sin(w), rs=0,
             lu=90, lf=0, ru=60, rf=30)
    return p, -90 + 25 * math.sin(w), 0.0, 0.0


def _freeze(k):
    p = dict(lean=0, head=10, lt=45, ls=95, rt=-35, rs=40, lu=100, lf=30, ru=178, rf=0)
    return p, 160 * smooth(seg(k, 0, 0.3)), 0.0, 0.0


def _backflip(k):
    crouch = pose(lean=25, lt=60, ls=90, rt=60, rs=90, lu=-40, ru=-40)
    tuck = dict(lean=10, head=0, lt=110, ls=140, rt=100, rs=140, lu=60, lf=80, ru=60, rf=80)
    air = seg(k, 0.25, 0.8)
    if k < 0.25:
        p = mix(STAND, crouch, smooth(k / 0.25))
    elif k < 0.8:
        p = mix(crouch, tuck, smooth(air * 3)) if air < 0.5 else mix(tuck, crouch, smooth((air - 0.5) * 2))
    else:
        p = mix(crouch, STAND, smooth((k - 0.8) / 0.2))
    return p, -360 * smooth(air), 330 * 4 * air * (1 - air), 0.0


BREAK_MOVES = {"TOPROCK": (_toprock, 4.0), "HEADSPIN": (_headspin, 3.0), "WINDMILL": (_windmill, 3.0),
               "FREEZE": (_freeze, 2.2), "BACKFLIP": (_backflip, 1.6)}


def breakdance(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    crowd = [(Figure(pal.dim(hue + 0.2 + i * 0.13, 0.4), height=rng.uniform(300, 360), feet=False),
              60 + i * 160 + rng.uniform(-30, 30), rng.random()) for i in range(7)]
    finale = 2.5
    tl = Timeline()
    order = ["TOPROCK", "HEADSPIN", "TOPROCK", "WINDMILL", "BACKFLIP", "FREEZE"]
    extra = ["HEADSPIN", "WINDMILL", "BACKFLIP", "FREEZE"]
    rng.shuffle(extra)
    order[1], order[3] = extra[0], extra[1]
    i = 0
    while tl.total < dur - finale - 1.5:
        name = order[i % len(order)] if i < len(order) else rng.choice(list(BREAK_MOVES))
        i += 1
        fn, length = BREAK_MOVES[name]
        tl.add(length, None, name=name)
    tl.add(max(finale, dur - tl.total), None, name="FINAL FREEZE")

    def draw(cv, t):
        start, d, _, info = tl.at(t)
        k = clamp((t - start) / d)
        name = info["name"]
        hype = name in ("HEADSPIN", "WINDMILL", "BACKFLIP", "FREEZE", "FINAL FREEZE")
        for cf, cx, ph in crowd:  # crowd behind a rail
            bob = 12 * abs(math.sin((t + ph) * 5))
            arms = pose(lu=-150, lf=0, ru=150, rf=0) if hype and math.sin(t * 6 + ph * 9) > -0.3 else pose(lu=20, ru=-20)
            cf.draw(cv, cf.place(arms, cx, GROUND - 230, bob, 1 if cx < W / 2 else -1))
        cv.line([(0, GROUND - 220), (W, GROUND - 220)], pal.dim(hue, 0.3), 8)
        cv.rect((120, GROUND - 14, 960, GROUND + 22), fill=pal.dim(hue + 0.5, 0.3), radius=10)  # cardboard floor
        floor(cv, pal)
        if name == "FINAL FREEZE":
            p, rot, lift, dx = _freeze(min(1, k * d / 1.2))
        else:
            p, rot, lift, dx = BREAK_MOVES[name][0](k)
        x = W / 2 + dx
        shadow(cv, pal, x, 130, air=lift)
        fig.draw(cv, fig.place(p, x, lift=lift, rot=rot))
        label(cv, name, pal, y=420, size=70)

    return draw


# -- moonwalk -------------------------------------------------------------------------

def fedora(cv, J, fig, color, tip=0.0):
    """Hat on the head; tip lifts it off."""
    hx, hy = J["head"]
    hy -= fig.R * (0.55 + tip)
    cv.line([(hx - fig.R * 1.5, hy + fig.R * 0.2), (hx + fig.R * 1.5, hy + fig.R * 0.2)], color, 10)
    cv.rect((hx - fig.R * 0.9, hy - fig.R * 0.9, hx + fig.R * 0.9, hy + fig.R * 0.25), fill=color, radius=8)


MJ_A = pose(lt=-8, ls=0, rt=10, rs=42, lu=20, lf=70, ru=30, rf=60, lean=-4)
MJ_B = pose(rt=-8, rs=0, lt=10, ls=42, lu=20, lf=70, ru=30, rf=60, lean=-4)
MJ_SPIN = pose(lt=4, ls=10, rt=-4, rs=10, lu=-40, lf=60, ru=70, rf=90)
MJ_TOE = pose(lt=0, ls=0, rt=0, rs=0, lu=-20, lf=40, ru=40, rf=60)
MJ_KICK = pose(rt=92, rs=12, lt=-6, ls=8, lu=-60, lf=40, ru=160, rf=20, lean=-10)
MJ_LEAN = pose(lt=0, ls=0, rt=0, rs=0, lu=10, lf=20, ru=10, rf=20)
MJ_HAT = pose(lt=6, ls=6, rt=-6, rs=6, lu=10, lf=30, ru=150, rf=95, head=10)
MJ_MOVES = {"MOONWALK": 3.2, "SPIN": 1.2, "TOE STAND": 1.6, "KICK": 1.1, "LEAN": 2.0, "HAT TIP": 1.6}


def moonwalk(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    hat_col = shade(pal.at(hue + 0.5), 0.8)
    finale = 2.4
    beats = []  # (start, length, move, x0, x1, facing at start)
    t, x, facing = 0.0, 760.0, 1
    extras = [m for m in MJ_MOVES if m != "MOONWALK"]
    i = 0
    while t < dur - finale - 1:
        move = "MOONWALK" if i % 2 == 0 else rng.choice(extras)
        length = MJ_MOVES[move]
        x1 = x
        if move == "MOONWALK":  # glide back toward the far side, facing away from where we go
            step = -420 if x > W / 2 else 420
            facing, x1 = (1 if step < 0 else -1), x + step
        beats.append((t, length, move, x, x1, facing))
        if move == "SPIN":
            facing = -facing
        t, x, i = t + length, x1, i + 1
    beats.append((t, max(finale, dur - t), "TOE STAND", x, x, facing))

    def draw(cv, t):
        start, length, move, x0, x1, f = next((b for b in beats if t < b[0] + b[1]), beats[-1])
        k = clamp((t - start) / length)
        x, lift, rot, tip = lerp(x0, x1, k), 0.0, 0.0, 0.0
        if move == "MOONWALK":
            s = (t - start) / 0.55
            p = mix(MJ_A, MJ_B, smooth(s % 1)) if int(s) % 2 == 0 else mix(MJ_B, MJ_A, smooth(s % 1))
        elif move == "SPIN":  # quick flips of facing read as a spin; ends facing the other way
            p = MJ_SPIN
            f = -f if k > 0.9 or int(k * 10) % 2 == 1 else f
        elif move == "TOE STAND":
            p, lift = mix(STAND, MJ_TOE, smooth(k * 3)), 34 * smooth(k * 3)
        elif move == "KICK":
            p = keyframes([(0, STAND), (0.35, MJ_KICK), (0.7, MJ_KICK), (1, STAND)], k)
        elif move == "LEAN":
            p, rot = MJ_LEAN, 42 * math.sin(math.pi * k)
        else:
            p, tip = keyframes([(0, STAND), (0.4, MJ_HAT), (0.8, MJ_HAT), (1, STAND)], k), 0.6 * math.sin(math.pi * k)
        cv.ellipse((x, GROUND + 8), 190, 34, pal.dim(hue + 0.1, 0.35))  # spotlight on the floor
        floor(cv, pal, k=0.4)
        J = fig.place(p, x, lift=lift, facing=f, rot=rot)
        if rot:  # lean from the ankles, not the hip
            dx = x - J["rankle"][0]
            J = {kk: (v if kk.endswith("_angle") else (v[0] + dx, v[1])) for kk, v in J.items()}
        shadow(cv, pal, x, 90, air=lift)
        fig.draw(cv, J)
        cv.circle(J["rhand"], 16, fill="#ffffff")  # the glove
        fedora(cv, J, fig, hat_col, tip)
        label(cv, move, pal, y=420, size=70)

    return draw


# -- ballet ---------------------------------------------------------------------------

B_PLIE = pose(lt=-14, ls=40, rt=14, rs=40, lu=-70, lf=30, ru=70, rf=30)
B_PASSE = pose(lt=0, ls=0, rt=68, rs=140, lu=165, lf=-45, ru=165, rf=45, head=-6)
B_ARAB = pose(lean=38, lt=-98, ls=0, rt=0, rs=0, lu=-100, lf=0, ru=110, rf=0, head=-20)
B_JETE = pose(lean=8, lt=-78, ls=0, rt=82, rs=0, lu=-120, lf=0, ru=150, rf=0, head=-10)
B_BOW = pose(lean=32, lt=-30, ls=40, rt=10, rs=30, lu=-80, lf=20, ru=80, rf=20, head=20)
BALLET = {"PLIE": 1.8, "PIROUETTE": 1.4, "ARABESQUE": 2.2, "GRAND JETE": 1.4}


def ballet(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    tutu = blend("#ffffff", pal.at(hue), 0.45)
    curtain = pal.dim(hue + 0.55, 0.35)
    finale = 2.6
    beats, t, x, i = [], 0.0, 380.0, 0
    order = list(BALLET)
    while t < dur - finale - 1:
        move = order[i % len(order)] if i < len(order) else rng.choice(order)
        length = BALLET[move]
        x1 = (700 if x < W / 2 else 380) if move == "GRAND JETE" else x
        beats.append((t, length, move, x, x1))
        t, x, i = t + length, x1, i + 1
    beats.append((t, max(finale, dur - t), "BOW", x, x))

    def draw(cv, t):
        start, length, move, x0, x1 = next((b for b in beats if t < b[0] + b[1]), beats[-1])
        k = clamp((t - start) / length)
        f = 1 if x1 >= x0 else -1
        x, lift = lerp(x0, x1, smooth(k)), 0.0
        if move == "PLIE":
            p = keyframes([(0, STAND), (0.5, B_PLIE), (1, STAND)], k)
        elif move == "PIROUETTE":
            p = keyframes([(0, STAND), (0.2, B_PASSE), (0.85, B_PASSE), (1, STAND)], k)
            if 0.2 < k < 0.85:
                f = 1 if int(k * 16) % 2 == 0 else -1
        elif move == "ARABESQUE":
            p = keyframes([(0, STAND), (0.35, B_ARAB), (0.8, B_ARAB), (1, STAND)], k)
        elif move == "GRAND JETE":
            p, lift = mix(STAND, B_JETE, math.sin(math.pi * k)), 200 * math.sin(math.pi * k)
        else:
            p = keyframes([(0, STAND), (0.8, B_BOW), (9, B_BOW)], t - start)
        for side in (1, -1):  # curtains
            x_edge = 0 if side == 1 else W
            cv.poly([(x_edge, 250), (x_edge + 170 * side, 250), (x_edge + 110 * side, GROUND), (x_edge, GROUND)],
                    curtain)
            for j in range(3):
                fx = x_edge + (40 + j * 40) * side
                cv.line([(fx, 250), (fx - 10 * side, GROUND)], shade(curtain, 0.7), 5)
        cv.poly([(x - 30, 250), (x + 30, 250), (x + 200, GROUND), (x - 200, GROUND)], pal.dim(hue + 0.1, 0.12))
        floor(cv, pal)
        J = fig.place(p, x, lift=lift, facing=f)
        shadow(cv, pal, x, 90, air=lift)
        fig.draw(cv, J)
        hip = J["hip"]
        cv.poly([(hip[0] - 100, hip[1] + 6), (hip[0] - 30, hip[1] - 22), (hip[0] + 30, hip[1] - 22),
                 (hip[0] + 100, hip[1] + 6), (hip[0], hip[1] + 26)], tutu)
        label(cv, move, pal, y=420, size=70)

    return draw


# -- dance battle ---------------------------------------------------------------------

ARMS_CROSSED = pose(lu=40, lf=120, ru=40, rf=125, lt=6, rt=-6)


def dance_battle(rng, pal, dur):
    beat = 60 / rng.uniform(100, 118)
    hue = rng.random()
    crews = [
        [(Figure(pal.at(hue), height=460), 170, 1), (Figure(pal.at(hue + 0.08), height=460), 340, 1)],
        [(Figure(pal.at(hue + 0.5), height=460), 740, -1), (Figure(pal.at(hue + 0.58), height=460), 910, -1)],
    ]
    finale = 3.0
    names = list(MOVES)
    rng.shuffle(names)
    turns = max(2, int((dur - finale) / (8 * beat)))
    turn = (dur - finale) / turns
    winner = rng.randint(0, 1)

    def draw(cv, t):
        b = t / beat
        pulse = 1 - (b % 1)
        for i in range(10):  # graffiti wall
            cv.rect((i * 115 - 20, 620 + 40 * (i % 3), i * 115 + 80, GROUND - 200 - 30 * (i % 2)),
                    fill=pal.dim(hue + i * 0.17, 0.12), radius=18)
        cv.rect((470, GROUND - 120, 610, GROUND), fill=pal.dim(0.0, 0.5), radius=10)  # boombox
        for sx in (505, 575):
            cv.circle((sx, GROUND - 60), 26 + 6 * pulse, fill=pal.at(hue + 0.3, 0.6))
        floor(cv, pal)
        if t < turns * turn:
            n = int(t / turn)
            active = n % 2
            p_active, lift, move = dance_pose([(0.0, turn, names[n % len(names)])], t - n * turn, beat)
            title = f"CREW {active + 1}: {move}"
        else:
            active = None
            p_active, lift = mix(STAND, FINAL, smooth((t - turns * turn) / 0.6)), 0.0
            title = f"CREW {winner + 1} WINS!"
        for c, crew in enumerate(crews):
            for fig, x, f in crew:
                if active is None:
                    p, lf = (p_active, 40 * abs(math.sin(t * 6))) if c == winner else (ARMS_CROSSED, 0.0)
                elif c == active:
                    p, lf = p_active, lift
                else:
                    p, lf = pose(ARMS_CROSSED, head=8 * math.sin(b * math.pi)), 0.0
                shadow(cv, pal, x, 80, air=lf)
                fig.draw(cv, fig.place(p, x, lift=lf, facing=f))
        label(cv, title, pal, y=420, size=58)

    return draw


# -- robot dance ----------------------------------------------------------------------

def snap(u):
    return smooth(seg(u, 0, 0.3))


ROBOT_STEPS = {
    "ROBOT ARMS": [pose(ru=90, rf=90, lu=-10, lf=90, head=12), pose(ru=10, rf=90, lu=90, lf=90, head=-12)],
    "TUTTING": [pose(ru=90, rf=90, lu=90, lf=-90), pose(ru=0, rf=90, lu=180, lf=90),
                pose(ru=-90, rf=-90, lu=90, lf=90), pose(ru=180, rf=-90, lu=0, lf=-90)],
    "BODY POP": [pose(lean=10, lt=10, ls=30, rt=-6, rs=10, ru=40, rf=40, lu=-20, lf=40),
                 pose(lean=-8, lt=-6, ls=10, rt=10, rs=30, ru=-20, rf=40, lu=40, lf=40)],
}
ROBOT_NAMES = ["ROBOT ARMS", "TUTTING", "BODY POP", "ARM WAVE", "GLIDE"]


def robot_dance(rng, pal, dur):
    hue = rng.random()
    fig = Figure(blend("#ffffff", pal.at(hue), 0.55), height=580, head="box")
    beat = 60 / rng.uniform(96, 110)
    finale = 2.6
    names = ROBOT_NAMES[:]
    rng.shuffle(names)
    n = max(1, int((dur - finale) / (8 * beat)))
    seg_len = (dur - finale) / n

    def draw(cv, t):
        for i in range(-8, 9):  # glowing grid floor in perspective
            cv.line([(W / 2 + i * 40, GROUND), (W / 2 + i * 260, 1920)], pal.dim(hue + 0.5, 0.3), 3, caps=False)
        for j in range(6):
            y = GROUND + j * j * 14
            cv.line([(0, y), (W, y)], pal.dim(hue + 0.5, 0.25), 3, caps=False)
        floor(cv, pal)
        x = W / 2
        if t >= n * seg_len:
            p = mix(STAND, pose(lean=38, head=40, lu=-5, lf=0, ru=5, rf=0, lt=6, ls=20, rt=-6, rs=20),
                    smooth((t - n * seg_len) / 0.8))
            name = "POWER DOWN"
        else:
            i = int(t / seg_len)
            name = names[i % len(names)]
            local = t - i * seg_len
            b = local / beat
            if name == "ARM WAVE":
                w = b * math.pi
                p = pose(lu=-90 + 25 * math.sin(w), lf=50 * math.sin(w - 0.9), ru=90 + 25 * math.sin(w - 1.8),
                         rf=50 * math.sin(w - 2.7), lean=4 * math.sin(w - 1.3))
            elif name == "GLIDE":
                a = pose(lt=12, ls=40, rt=-8, rs=0, lu=-30, ru=30)
                c = pose(rt=12, rs=40, lt=-8, ls=0, lu=-30, ru=30)
                p = mix(a, c, snap(b % 1)) if int(b) % 2 == 0 else mix(c, a, snap(b % 1))
                x = W / 2 + 200 * math.sin(local / seg_len * 2 * math.pi)
            else:
                steps = ROBOT_STEPS[name]
                j = int(b)
                p = mix(steps[(j - 1) % len(steps)], steps[j % len(steps)], snap(b % 1))
        shadow(cv, pal, x, 100)
        J = fig.place(p, x)
        fig.draw(cv, J)
        hx, hy = J["head"]
        cv.rect((hx - fig.R * 0.2, hy - fig.R * 0.35, hx + fig.R * 0.85, hy - fig.R * 0.05),
                fill=pal.at(hue + 0.5, 1.2), radius=4)  # visor
        label(cv, name, pal, y=420, size=66)

    return draw
