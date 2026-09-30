"""Music & life scenes: guitar solo, drummer, DJ set, pancake chef, lumberjack and juggler."""

import math

from .stick import (GROUND, W, Figure, blend, burst, clamp, ease_out, floor, keyframes, label, lerp, mix,
                    parabola, pop_text, pose, shade, shadow, smooth)


def _dir(a, f=1):
    r = math.radians(a)
    return (f * math.sin(r), math.cos(r))


def _along(p, d, k):
    return (p[0] + d[0] * k, p[1] + d[1] * k)


def note(cv, c, color, size=1.0):
    """A music note: head, stem and flag."""
    cv.ellipse(c, 16 * size, 12 * size, color)
    top = (c[0] + 14 * size, c[1] - 60 * size)
    cv.line([(c[0] + 14 * size, c[1]), top], color, 5 * size)
    cv.line([top, (top[0] + 22 * size, top[1] + 18 * size)], color, 5 * size)


def spotlights(cv, pal, hue, t, beat):
    for side, x0 in ((1, 80), (-1, W - 80)):
        a = math.radians(side * (20 + 18 * math.sin(t * 1.1 + side)))
        tip = (x0 + side * 900 * math.sin(abs(a) + 0.3), 250 + 1200 * math.cos(a))
        col = pal.dim(hue + int(t / beat) * 0.25 + (0.5 if side < 0 else 0), 0.16)
        cv.poly([(x0, 240), (tip[0] - 140, tip[1]), (tip[0] + 140, tip[1])], col)


# -- guitar solo -----------------------------------------------------------------------

G_PLAY = pose(lean=6, lt=-20, ls=24, rt=24, rs=24, lu=75, lf=35, ru=25, rf=95)
G_KNEEL = pose(lean=-35, head=-30, lt=95, ls=100, rt=0, rs=110, lu=80, lf=30, ru=30, rf=90)
G_JUMP = pose(lean=0, lt=60, ls=120, rt=-20, rs=90, lu=75, lf=35, ru=25, rf=95)
GUITAR_MOVES = {"SHRED": 3.0, "JUMP": 1.2, "KNEE SLIDE": 2.2, "WINDMILL": 2.0}


def guitar_solo(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    body_col = pal.at(hue + 0.5)
    beat = 60 / rng.uniform(130, 150)
    finale = 2.4
    beats, t, x, i = [], 0.0, 420.0, 0
    while t < dur - finale - 1:
        move = "SHRED" if i % 2 == 0 else rng.choice(["JUMP", "KNEE SLIDE", "WINDMILL"])
        length = GUITAR_MOVES[move]
        x1 = (x + 260 if x < W / 2 else x - 260) if move == "KNEE SLIDE" else x
        beats.append((t, length, move, x, x1))
        t, x, i = t + length, x1, i + 1
    beats.append((t, max(finale, dur - t), "ENCORE!", x, x))

    def guitar(cv, J, p):
        hip = J["hip"]
        up = _dir(180 - p.get("lean", 0))
        fwd = (-up[1], up[0])  # perpendicular to the torso, toward the front
        body = (hip[0] + fwd[0] * 40 - up[0] * 10, hip[1] + fwd[1] * 40 - up[1] * 10)
        neck_end = J["lhand"]
        nd = (neck_end[0] - body[0], neck_end[1] - body[1])
        n = math.hypot(*nd) or 1
        head = (neck_end[0] + nd[0] / n * 70, neck_end[1] + nd[1] / n * 70)
        cv.line([body, head], "#2a2a2a", 12)
        cv.line([neck_end, head], shade(body_col, 0.6), 18)
        cv.circle((body[0] - fwd[0] * 20, body[1] - fwd[1] * 20), 62, fill=body_col)
        cv.circle((body[0] + nd[0] / n * 40, body[1] + nd[1] / n * 40), 46, fill=body_col)
        cv.circle(body, 16, fill="#1a1a22")
        return body

    def draw(cv, t):
        spotlights(cv, pal, hue, t, beat)
        for ax in (60, 900):  # amp stacks
            for j in range(2):
                y0 = GROUND - 200 - j * 200
                cv.rect((ax, y0, ax + 150, y0 + 190), fill="#15151c", outline=pal.dim(0.0, 0.6), width=5, radius=8)
                for sx in (ax + 40, ax + 110):
                    cv.circle((sx, y0 + 95), 30 + 4 * (1 - (t / beat) % 1), fill="#2a2a36")
        floor(cv, pal)
        start, length, move, x0, x1 = next((b for b in beats if t < b[0] + b[1]), beats[-1])
        k = clamp((t - start) / length)
        b = t / beat
        bang = math.sin(b * math.pi)
        x, lift = lerp(x0, x1, ease_out(k)), 0.0
        f = 1 if x1 >= x0 else -1
        p = dict(G_PLAY, head=20 * bang, rf=95 + 25 * math.sin(b * 2 * math.pi), ls=24 + 10 * abs(bang),
                 rs=24 + 10 * abs(bang))
        if move == "JUMP":
            p, lift = mix(p, G_JUMP, math.sin(math.pi * k)), 230 * math.sin(math.pi * k)
        elif move == "KNEE SLIDE":
            p = mix(p, G_KNEEL, smooth(k * 4) * (1 - smooth((k - 0.8) * 5)))
        elif move == "WINDMILL":
            a = k * 720 * 2
            p = dict(p, ru=a % 360, rf=0)
        elif move == "ENCORE!":
            p = mix(p, dict(G_PLAY, ru=170, rf=0), smooth(k * 3))
        J = fig.place(p, x, lift=lift, facing=f)
        shadow(cv, pal, x, 100, air=lift)
        fig.draw(cv, J)
        body = guitar(cv, J, p)
        for j in range(4):  # notes floating up
            age = (b * 0.5 + j / 4) % 1
            note(cv, (body[0] + 60 + 120 * age + 30 * math.sin(age * 9 + j), body[1] - 80 - 520 * age),
                 pal.at(hue + j * 0.2, 1.1), 1.2 - 0.6 * age)
        label(cv, move, pal, y=420, size=70)

    return draw


# -- drummer ---------------------------------------------------------------------------

SEAT_Y = GROUND - 230
D_SEAT = pose(lean=4, lt=85, ls=85, rt=80, rs=80, lu=40, lf=90, ru=40, rf=90)


def drummer(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=520)
    beat = 60 / rng.uniform(110, 130)
    X = 390
    finale = 2.4
    drums = {"snare": (560, SEAT_Y - 30, 70, 16), "tom": (660, SEAT_Y - 130, 55, 14),
             "floor": (250, SEAT_Y + 10, 70, 18)}
    cymbal = (760, SEAT_Y - 280)
    hihat = (470, SEAT_Y - 90)

    def hits_at(t):
        """Which drums are hit on the current 8th note, and how long ago."""
        e = t / (beat / 2)
        n = int(e)
        bar_pos = n % 8
        fill = (n // 8) % 4 == 3
        age = (e - n) * beat / 2
        if fill:
            order = ["snare", "tom", "tom", "floor", "snare", "tom", "floor", "crash"]
            return {order[bar_pos]}, age, bar_pos % 2 == 0
        hit = {"hat"}
        if bar_pos in (2, 6):
            hit.add("snare")
        kick = bar_pos in (0, 4, 5)
        if bar_pos == 0 and (n // 8) % 4 == 0:
            hit.add("crash")
        return hit, age, kick

    def draw(cv, t):
        spotlights(cv, pal, hue, t, beat)
        floor(cv, pal)
        done = t > dur - finale
        hit, age, kick = hits_at(t)
        swing = clamp(age / (beat / 2))  # 0 at the hit, 1 when raised for the next
        cv.line([(X - 40, SEAT_Y + 40), (X + 40, SEAT_Y + 40)], pal.dim(0.0, 0.6), 14)  # stool
        cv.line([(X, SEAT_Y + 40), (X, GROUND)], pal.dim(0.0, 0.6), 10)
        pulse = 1 + (0.15 if kick and age < 0.12 and not done else 0)
        cv.circle((620, GROUND - 130), 125 * pulse, fill=pal.dim(hue + 0.5, 0.5))  # bass drum
        cv.circle((620, GROUND - 130), 95 * pulse, fill=pal.dim(hue + 0.5, 0.25))
        for name, (dx, dy, rx, ry) in drums.items():
            glow = 1.3 if name in hit and age < 0.1 and not done else 0.8
            cv.line([(dx, dy + ry), (dx, GROUND)], pal.dim(0.0, 0.5), 6)
            cv.rect((dx - rx, dy - ry, dx + rx, dy + ry + 30), fill=pal.at(hue + 0.3, glow * 0.6), radius=8)
            cv.ellipse((dx, dy - ry), rx, ry, "#e8e8f0")
        wob = 0.2 if "crash" in hit and age < 0.4 and not done else 0.0
        cv.line([(cymbal[0], cymbal[1]), (cymbal[0], GROUND)], pal.dim(0.0, 0.5), 5)
        cv.line([(cymbal[0] - 110, cymbal[1] + 20 * math.sin(t * 40) * wob * 5), (cymbal[0] + 110, cymbal[1] - 10)],
                "#ffd166", 10)
        cv.line([(hihat[0] - 70, hihat[1]), (hihat[0] + 70, hihat[1])], "#ffd166", 8)
        # arms: right hand plays hat / crash / tom, left plays snare / floor tom
        r_target = "crash" if "crash" in hit else ("tom" if "tom" in hit else "hat")
        l_target = "floor" if "floor" in hit else "snare"
        r_hit = {"hat": pose(ru=55, rf=60), "crash": pose(ru=120, rf=40), "tom": pose(ru=85, rf=40)}[r_target]
        l_hit = {"snare": pose(lu=60, lf=40), "floor": pose(lu=-20, lf=60)}[l_target]
        raise_r = pose(ru=r_hit["ru"] + 30, rf=r_hit["rf"] + 70)
        raise_l = pose(lu=l_hit["lu"] + 30, lf=l_hit["lf"] + 70)
        l_active = l_target in hit or "snare" in hit
        p = dict(D_SEAT)
        ur = smooth(swing)
        p.update(ru=lerp(r_hit["ru"], raise_r["ru"], ur), rf=lerp(r_hit["rf"], raise_r["rf"], ur))
        ul = smooth(swing) if l_active else 0.7
        p.update(lu=lerp(l_hit["lu"], raise_l["lu"], ul), lf=lerp(l_hit["lf"], raise_l["lf"], ul))
        p["rt"] = 80 - (10 if kick and age < 0.1 else 0)
        p["head"] = 10 * math.sin(t / beat * math.pi)
        if done:
            k = t - (dur - finale)
            p.update(ru=150, rf=20, lu=150, lf=20, head=-10)
        J = fig.place(p, X, ground=GROUND)
        fig.draw(cv, J)
        for side in "lr":  # sticks (twirling in the finale)
            ang = J[side + "fore_angle"] + (k * 1440 if done else 10)
            d = _dir(ang)
            cv.line([J[side + "hand"], _along(J[side + "hand"], d, 130)], "#f1d39a", 7)
        if "crash" in hit and age < 0.3 and not done:
            burst(cv, cymbal, age, pal.at(hue + 0.15, 1.2), seed=int(t), n=10, size=100, life=0.3)
        label(cv, "DRUM SOLO" if not done else "THANK YOU!", pal, y=420, size=70)
        cv.text((W / 2, 520), f"{int(60 / beat)} BPM", 50, pal.dim(hue + 0.3, 0.9))

    return draw


# -- dj set ----------------------------------------------------------------------------

DJ_BASE = pose(lean=12, lu=60, lf=40, ru=70, rf=40, head=10)


def dj_set(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    beat = 60 / rng.uniform(124, 130)
    drop = max(4.0, dur * 0.45)
    X = W / 2
    deck_y = GROUND - 330
    crowd = [(i * 95 + rng.uniform(-20, 20), rng.uniform(0, 6.28), rng.uniform(0.8, 1.2)) for i in range(-1, 13)]

    def draw(cv, t):
        b = t / beat
        pulse = 1 - (b % 1)
        dropped = t >= drop
        for j in range(12):  # lasers fanning from the booth
            if dropped or j % 3 == 0:
                a = math.radians(-70 + j * 12.7 + 10 * math.sin(t * 2 + j))
                end = (X + 1400 * math.sin(a), deck_y - 1400 * math.cos(a))
                cv.line([(X, deck_y - 40), end], pal.dim(hue + j * 0.08 + int(b) * 0.2, 0.3 + 0.2 * pulse), 5)
        for j in range(14):  # equalizer wall
            h = 60 + 220 * abs(math.sin(b * math.pi / 2 + j * 0.9)) * (1.4 if dropped else 0.6)
            cv.rect((60 + j * 70, deck_y - 80 - h, 110 + j * 70, deck_y - 80), fill=pal.dim(hue + j * 0.05, 0.35))
        floor(cv, pal)
        # the DJ, hidden from the waist down by the booth
        if dropped:
            p = pose(DJ_BASE, lu=170 if int(b) % 2 == 0 else 140, lf=0, head=20 * math.sin(b * math.pi))
            lift = 20 * abs(math.sin(b * math.pi))
        else:
            scratch = math.sin(t * 14)
            p = pose(DJ_BASE, rf=40 + 30 * scratch, head=8 * math.sin(b * math.pi), lu=110, lf=90)
            lift = 0.0
        J = fig.place(p, X - 40, lift=lift)
        fig.draw(cv, J)
        hx, hy = J["head"]
        cv.line([(hx - fig.R - 6, hy), (hx - fig.R, hy - fig.R), (hx + fig.R, hy - fig.R), (hx + fig.R + 6, hy)],
                "#20202a", 10)  # headphones
        cv.circle((hx - fig.R - 4, hy + 6), 20, fill="#20202a")
        cv.rect((250, deck_y, 830, GROUND), fill="#12121a", outline=pal.at(hue + 0.5, 0.8), width=6, radius=12)
        cv.text((540, deck_y + 150), "DJ", 110, pal.at(hue + 0.5, 0.5 + 0.5 * pulse))
        for dx in (360, 720):  # decks
            cv.ellipse((dx, deck_y - 8), 110, 22, "#2a2a36")
            a = t * 9 * (1 if dx < 500 else -1)
            cv.line([(dx, deck_y - 8), (dx + 90 * math.cos(a), deck_y - 8 + 18 * math.sin(a))], "#e8e8f0", 4)
        for cx, ph, s in crowd:  # crowd in front, jumping after the drop
            jump = (40 if dropped else 10) * abs(math.sin((b + ph) * math.pi))
            y = 1560 - jump
            cv.circle((cx, y), 46 * s, fill=blend(pal.background[1], "#000000", 0.3))
            if dropped:
                cv.line([(cx - 30, y + 30), (cx - 60, y - 90 - jump)], blend(pal.background[1], "#000000", 0.3), 18)
                cv.line([(cx + 30, y + 30), (cx + 60, y - 90 - jump)], blend(pal.background[1], "#000000", 0.3), 18)
        if not dropped and drop - t < 3:
            n = int(drop - t) + 1
            cv.text((W / 2, 620), f"DROP IN {n}", 90, pal.at(hue + 0.2, 1.2))
        elif dropped and t - drop < 1.0:
            cv.text((W / 2, 620), "DROP!", 170 * (0.7 + 0.3 * ease_out((t - drop) / 0.2)), pal.at(hue + 0.2, 1.2))
        label(cv, "DJ SET", pal, y=420, size=70)

    return draw


# -- pancake chef ----------------------------------------------------------------------

C_COOK = pose(lean=12, ru=60, rf=30, lu=40, lf=60, lt=-10, rt=12)
C_FLIP = pose(lean=4, ru=95, rf=10, lu=40, lf=60, lt=-10, rt=12)


def pancake_chef(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=540)
    X = 330
    counter_y = GROUND - 330
    flip = 2.4
    finale = 2.6
    n = max(1, int((dur - finale) / flip))
    flip = (dur - finale) / n
    oops = rng.randrange(n) if n >= 3 else -1
    CAKE = "#e8b264"

    def pan_pos(J):
        d = _dir(J["rfore_angle"] - 20)
        return _along(J["rhand"], d, 150), d

    def cake(cv, c, spin=0.0, color=CAKE):
        ry = 8 + 30 * abs(math.sin(spin))
        cv.ellipse(c, 70, ry, color)
        cv.ellipse((c[0], c[1] - 2), 60, max(4, ry - 6), shade(color, 1.12))

    def draw(cv, t):
        floor(cv, pal)
        cv.rect((450, counter_y, 780, GROUND), fill=pal.dim(0.6, 0.18), radius=8)  # stove
        cv.rect((490, counter_y - 12, 560, counter_y), fill="#ff6b3d")
        cv.rect((820, counter_y + 40, 1060, GROUND), fill=pal.dim(0.1, 0.16), radius=8)  # table
        cv.ellipse((940, counter_y + 36), 110, 14, "#f4f4f8")  # plate
        i = min(n - 1, int(t / flip))
        k = t - i * flip
        done = t >= n * flip
        stack = i + (1 if k > 2.0 else 0) - (1 if 0 <= oops < i or (oops == i and k > 2.0) else 0)
        for j in range(max(0, stack if not done else n - (1 if oops >= 0 else 0))):
            cake(cv, (940, counter_y + 26 - j * 18))
        if done:
            p = mix(C_COOK, pose(lu=-110, lf=0, ru=110, rf=0), smooth((t - n * flip) / 0.5))
        else:
            p = keyframes([(0, C_COOK), (0.8, C_COOK), (1.0, C_FLIP), (1.3, C_COOK), (flip, C_COOK)], k)
            p["rf"] += 6 * math.sin(k * 30) if k < 0.8 else 0
        J = fig.place(p, X)
        shadow(cv, pal, X, 90)
        fig.draw(cv, J)
        hx, hy = J["head"]  # chef's hat
        cv.rect((hx - 34, hy - fig.R - 70, hx + 34, hy - fig.R + 4), fill="#f4f4f8", radius=10)
        for dx in (-26, 0, 26):
            cv.circle((hx + dx, hy - fig.R - 72), 28, fill="#f4f4f8")
        pan, d = pan_pos(J)
        cv.line([J["rhand"], pan], "#2a2a2a", 10)
        cv.ellipse((pan[0] + d[0] * 60, pan[1] + d[1] * 60), 85, 16, "#3a3a46")
        rest = (pan[0] + d[0] * 60, pan[1] + d[1] * 60 - 14)
        if done:
            label(cv, "BON APPETIT!", pal, y=420, size=76)
        else:
            if k < 1.0:
                cake(cv, rest)
            elif k < 1.8:
                u = (k - 1.0) / 0.8
                high = i == oops
                if high:  # flies too high and lands on the chef's head
                    c = parabola(rest, (hx, hy - fig.R - 90), 520, u)
                else:
                    c = parabola(rest, rest, 420, u)
                cake(cv, c, spin=u * math.pi * 2)
            elif i == oops:
                cake(cv, (hx, hy - fig.R - 90))
                pop_text(cv, "OOPS!", (hx + 120, hy - 200), k - 1.8, pal.at(hue + 0.5, 1.2), life=0.9)
            elif k < 2.0:
                cake(cv, rest)
            elif k < 2.3:
                u = (k - 2.0) / 0.3
                cake(cv, parabola(rest, (940, counter_y + 26 - stack * 18), 120, u))
            label(cv, "PANCAKE FLIP", pal, y=420, size=66)
        cv.text((W / 2, 520), f"STACK x{max(0, stack)}", 70, pal.at(hue + 0.3, 1.1))

    return draw


# -- lumberjack ------------------------------------------------------------------------

L_READY = pose(lean=14, lt=-24, ls=20, rt=26, rs=24, lu=60, lf=20, ru=60, rf=20, sw=10)
L_RAISE = pose(lean=-8, lt=-24, ls=20, rt=26, rs=24, lu=185, lf=-30, ru=185, rf=-30, sw=-20)
L_CHOP = pose(lean=34, lt=-30, ls=30, rt=36, rs=40, lu=80, lf=0, ru=80, rf=0, sw=0)
STUMP = (640, GROUND - 120)


def lumberjack(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    X = 360
    chop = 1.7
    finale = 2.4
    n = max(1, int((dur - finale) / chop))
    chop = (dur - finale) / n
    hit_t = 0.95
    wood = "#c98a4b"

    def draw(cv, t):
        for j in range(7):  # forest
            tx = j * 170 + 20
            cv.poly([(tx - 80, GROUND - 140), (tx + 80, GROUND - 140), (tx, GROUND - 620 - 60 * (j % 2))],
                    pal.dim(hue + 0.35, 0.15))
        floor(cv, pal)
        cv.rect((STUMP[0] - 80, STUMP[1], STUMP[0] + 80, GROUND), fill=shade(wood, 0.7), radius=6)
        cv.ellipse(STUMP, 80, 14, shade(wood, 1.1))
        i = min(n - 1, int(t / chop))
        k = t - i * chop
        done = t >= n * chop
        logs = i + (1 if k > hit_t else 0) if not done else n
        for j in range(logs):  # woodpile
            cv.circle((900 + (j % 4) * 44 + (j // 4 % 2) * 22, GROUND - 24 - (j // 4) * 40), 22, fill=shade(wood, 0.9))
            cv.circle((900 + (j % 4) * 44 + (j // 4 % 2) * 22, GROUND - 24 - (j // 4) * 40), 10, fill=shade(wood, 1.3))
        if done:
            p = mix(L_READY, pose(lean=0, lu=100, lf=120, ru=20, rf=20, sw=-100), smooth((t - n * chop) / 0.6))
        else:
            p = keyframes([(0, L_READY), (0.6, L_RAISE), (hit_t, L_CHOP), (1.3, L_CHOP), (chop, L_READY)], k)
        J = fig.place(p, X)
        shadow(cv, pal, X, 100)
        fig.draw(cv, J)
        hx, hy = J["head"]
        cv.poly([(hx - fig.R * 0.2, hy + fig.R * 0.2), (hx + fig.R * 1.0, hy + fig.R * 0.1),
                 (hx + fig.R * 0.5, hy + fig.R * 1.4)], "#8a4b2a")  # beard
        d = _dir(J["rfore_angle"] + p.get("sw", 0))
        end = _along(J["rhand"], d, 270)
        cv.line([_along(J["rhand"], d, -30), end], wood, 11)
        side = (-d[1], d[0])
        cv.poly([_along(end, side, 10), _along(_along(end, side, 10), d, -60),
                 _along(_along(end, side, -60), d, -80), _along(_along(end, side, -60), d, 20)], "#c8ccd8")
        if not done:
            if k < hit_t:  # whole log on the stump
                cv.rect((STUMP[0] - 34, STUMP[1] - 170, STUMP[0] + 34, STUMP[1]), fill=wood, radius=6)
                cv.ellipse((STUMP[0], STUMP[1] - 170), 34, 8, shade(wood, 1.3))
            else:  # the halves fly apart
                u = min(1.0, (k - hit_t) / 0.5)
                for s in (-1, 1):
                    cx = STUMP[0] + s * 180 * u
                    cy = STUMP[1] - 85 - 200 * u + 360 * u * u
                    ang = s * 90 * u
                    a = math.radians(ang)
                    dx, dy = math.sin(a) * 85, -math.cos(a) * 85
                    cv.line([(cx - dx, min(cy - dy, GROUND - 17)), (cx + dx, min(cy + dy, GROUND - 17))], wood, 34)
                burst(cv, (STUMP[0], STUMP[1] - 60), k - hit_t, "#f1d39a", seed=i, n=14, size=120, life=0.4)
                pop_text(cv, "CHOP!", (STUMP[0], STUMP[1] - 300), k - hit_t, pal.at(hue + 0.15, 1.2))
        label(cv, "TIMBER!" if done else "LUMBERJACK", pal, y=420, size=70)
        cv.text((W / 2, 520), f"LOGS x{logs}", 70, pal.at(hue + 0.3, 1.1))

    return draw


# -- juggler ---------------------------------------------------------------------------

J_POSE = pose(lu=-20, lf=-70, ru=20, rf=70, lt=10, ls=6, rt=-10, rs=6)


def juggler(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    X = W / 2
    finale = 2.4
    counts = [3, 4, 5]
    seg = (dur - finale) / len(counts)
    p_throw = 0.34
    dwell = 0.2
    g = 2000.0
    colors = [pal.at(hue + j / 5 + 0.1, 1.15) for j in range(5)]

    def hand_points(J, t):
        bob = 12 * math.sin(t / p_throw * math.pi)
        return {0: (J["lhand"][0], J["lhand"][1] + bob), 1: (J["rhand"][0], J["rhand"][1] - bob)}

    def ball_pos(j, n, t, hands):
        """Cascade (odd n) crosses hands; fountain (even n) keeps each ball on one side."""
        period = n * p_throw
        m = math.floor((t - j * p_throw) / period)
        throw_t = j * p_throw + m * period
        from_h = (j + m * n) % 2
        to_h = 1 - from_h if n % 2 else from_h
        flight = period - dwell
        u = (t - throw_t) / flight
        a, b = hands[from_h], hands[to_h]
        if u <= 1:
            inward = 40 if from_h == 0 else -40
            start = (a[0] + inward, a[1] - 10)
            end = (b[0] - (40 if to_h == 0 else -40) * 0, b[1] - 10)
            height = g * flight * flight / 8
            return parabola(start, end, height, u)
        v = (t - throw_t - flight) / dwell  # carried in the hand, scooping inward
        c = hands[to_h]
        inward = 40 if to_h == 0 else -40
        return (lerp(c[0], c[0] + inward, v), c[1] - 10 + 18 * math.sin(math.pi * v))

    def draw(cv, t):
        for j in range(12):  # circus tent stripes
            a0, a1 = math.radians(j * 15 - 90), math.radians(j * 15 - 82.5)
            cv.poly([(W / 2, 200), (W / 2 + 1600 * math.sin(a0), 200 + 1600 * math.cos(a0)),
                     (W / 2 + 1600 * math.sin(a1), 200 + 1600 * math.cos(a1))], pal.dim(hue + 0.55, 0.12))
        cv.ellipse((X, GROUND + 10), 240, 40, pal.dim(hue + 0.1, 0.35))
        floor(cv, pal, k=0.35)
        done = t >= dur - finale
        J = fig.place(J_POSE if not done else mix(J_POSE, pose(lu=-150, lf=0, ru=150, rf=0), smooth(
            (t - dur + finale) / 0.5)), X)
        shadow(cv, pal, X, 100)
        fig.draw(cv, J)
        if done:
            label(cv, "TA-DA!", pal, y=420, size=90)
            return
        s = min(len(counts) - 1, int(t / seg))
        n = counts[s]
        hands = hand_points(J, t)
        local = t - s * seg + n * p_throw * 2  # start mid-pattern so balls are already flying
        for j in range(n):
            cv.circle(ball_pos(j, n, local, hands), 24, fill=colors[j])
        label(cv, f"{n} BALLS", pal, y=420, size=76)

    return draw
