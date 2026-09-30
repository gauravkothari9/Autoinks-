"""More sports: tennis and ping pong rallies, golf, baseball, cricket, bowling, penalty kicks,
high jump, weightlifting and trampoline."""

import math
import random

from .scenes_sports import ball
from .stick import (GROUND, STAND, W, Figure, bezier, burst, clamp, ease_out, floor, keyframes, label, lerp, mix,
                    parabola, pop_text, pose, run, shade, shadow, smooth, walk)


def _dir(a, f):
    r = math.radians(a)
    return (f * math.sin(r), math.cos(r))


def _along(p, d, k):
    return (p[0] + d[0] * k, p[1] + d[1] * k)


def crowd(cv, pal, hue, t, y=640, rows=3, cheer=False):
    for row in range(rows):
        for i in range(-1, 13):
            bob = 8 * abs(math.sin(t * 7 + i * 1.3 + row)) if cheer else 0
            cv.circle((i * 90 + (row % 2) * 45, y + row * 55 - bob), 20, fill=pal.dim(hue + (i * 0.37 + row * 0.2) % 1, 0.25))


# -- tennis and ping pong -----------------------------------------------------------

READY = pose(lean=14, lt=-20, ls=30, rt=24, rs=34, lu=40, lf=60, ru=30, rf=50)
SWING = [(-0.35, pose(READY, ru=-60, rf=30, lean=4)), (0.0, pose(READY, ru=85, rf=10, lean=18)),
         (0.3, pose(READY, ru=150, rf=50, lean=10)), (0.6, READY)]
RALLY = {
    # x of players, player height, hit height, bounce x (A->B, B->A), ball radius/color, shot time, arc heights
    "tennis": dict(ax=150, bx=930, h=470, hit_y=GROUND - 300, bounce=(760, 320), r=16, color="#d4ff3a",
                   shot=1.15, arcs=(240, 150), title="TENNIS"),
    "pingpong": dict(ax=140, bx=940, h=480, hit_y=GROUND - 360, bounce=(700, 380), r=11, color="#ffffff",
                     shot=0.62, arcs=(110, 80), title="PING PONG"),
}


def rally(rng, pal, dur, kind="tennis"):
    c = RALLY[kind]
    hue = rng.random()
    A, B = Figure(pal.at(hue), height=c["h"]), Figure(pal.at(hue + 0.5), height=c["h"])
    table_y = GROUND - 250
    surface = table_y if kind == "pingpong" else GROUND
    shot = c["shot"]
    finale = 2.5
    hits, points = [], []  # hits: (time, hitter 0/1); points: (time, winner)
    t, server = 0.4, rng.randint(0, 1)
    while t < dur - finale - 3 * shot:
        n = rng.randint(3, 7)
        for i in range(n):
            hits.append((t + i * shot, (server + i) % 2))
        last = (server + n - 1) % 2
        points.append((t + n * shot, last))
        t += n * shot + 1.4
        server = 1 - server
    score = [0, 0]
    tallies = []
    for when, win in points:
        score[win] += 1
        tallies.append((when, tuple(score)))
    cp = {0: (c["ax"] + 150, c["hit_y"]), 1: (c["bx"] - 150, c["hit_y"])}

    def fmt(sc):
        if kind == "tennis":
            names = ["0", "15", "30", "40", "GAME"]
            return f"{names[min(sc[0], 4)]} - {names[min(sc[1], 4)]}"
        return f"{sc[0]} - {sc[1]}"

    def ball_at(t):
        for when, who in hits:
            winner_shot = any(abs(pt - (when + shot)) < 1e-6 for pt, _ in points)
            if when <= t < when + shot + (0.9 if winner_shot else 0):
                p0 = cp[who]
                bx = c["bounce"][who]
                p_b = (bx, surface - c["r"])
                u = (t - when) / shot
                if u < 0.62:
                    return parabola(p0, p_b, c["arcs"][0], u / 0.62)
                p1 = cp[1 - who]
                if winner_shot:  # skips past the other player
                    p1 = (p1[0] + (1 - 2 * who) * 450, surface + 200)
                return parabola(p_b, p1, c["arcs"][1], (u - 0.62) / 0.38)
        return None

    def player_pose(who, t):
        p = READY
        for when, h in hits:
            if h == who and -0.35 <= t - when <= 0.6:
                p = keyframes(SWING, t - when)
        return p

    def draw(cv, t):
        crowd(cv, pal, hue, t, cheer=any(0 < t - pt < 1.2 for pt, _ in points))
        floor(cv, pal)
        if kind == "pingpong":
            cv.rect((250, table_y, 830, table_y + 26), fill=pal.dim(hue + 0.4, 0.7), radius=4)
            cv.line([(540, table_y), (540, table_y - 40)], "#f4f4f8", 6)
            for lx in (300, 780):
                cv.line([(lx, table_y + 26), (lx, GROUND)], pal.dim(0.0, 0.6), 10)
        else:
            cv.line([(540, GROUND), (540, GROUND - 170)], "#f4f4f8", 8)
            for j in range(4):
                cv.line([(530, GROUND - 160 + j * 38), (550, GROUND - 160 + j * 38)], "#9aa0b8", 3, caps=False)
        for who, F, x, f in ((0, A, c["ax"], 1), (1, B, c["bx"], -1)):
            J = F.place(player_pose(who, t), x, facing=f)
            shadow(cv, pal, x, 80)
            F.draw(cv, J)
            d = _dir(J["rfore_angle"] + 10, f)
            hand = J["rhand"]
            if kind == "tennis":
                cv.line([hand, _along(hand, d, 60)], pal.dim(0.0, 0.9), 8)
                cv.circle(_along(hand, d, 105), 44, outline=F.color, width=6)
            else:
                cv.circle(_along(hand, d, 30), 30, fill="#e0303a" if who == 0 else "#20202a")
        b = ball_at(t)
        if b:
            cv.circle(b, c["r"], fill=c["color"])
        shown = (0, 0)
        for when, sc in tallies:
            if t >= when:
                shown = sc
        for when, win in points:
            if 0 <= t - when < 1.3:
                cv.text((W / 2, 620), "POINT!" if kind == "pingpong" else "WINNER!", 100, pal.at(hue + 0.5 * win, 1.2))
        label(cv, c["title"], pal, y=400, size=60)
        cv.text((W / 2, 500), fmt(shown), 80, pal.at(hue + 0.3, 1.1))

    return draw


# -- golf -------------------------------------------------------------------------------

G_ADDRESS = pose(lean=32, lt=-8, ls=16, rt=8, rs=16, lu=-32, lf=0, ru=-32, rf=0, sw=-8)
G_BACK = pose(lean=22, lt=-8, ls=18, rt=8, rs=12, lu=-165, lf=-40, ru=-165, rf=-40, sw=-60)
G_FOLLOW = pose(lean=-8, lt=-4, ls=8, rt=16, rs=30, lu=150, lf=60, ru=150, rf=60, sw=40)
HOLE_X = 960


def golf(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=500)
    X, tee = 200, 318
    shot = 4.2
    finale = 2.4
    n = max(1, int((dur - finale) / shot))
    shot = (dur - finale) / n
    results = []
    for _ in range(n):
        ace = rng.random() < 0.4
        land = HOLE_X - rng.uniform(60, 180)
        stop = HOLE_X if ace else HOLE_X - rng.uniform(20, 70) * rng.choice([1, -1])
        results.append((ace, land, stop))

    def draw(cv, t):
        cv.poly([(-50, GROUND), (300, GROUND - 180), (650, GROUND)], pal.dim(hue + 0.35, 0.18))
        cv.poly([(400, GROUND), (800, GROUND - 240), (1200, GROUND)], pal.dim(hue + 0.4, 0.14))
        floor(cv, pal)
        cv.ellipse((HOLE_X, GROUND + 2), 22, 6, "#050505")
        cv.line([(HOLE_X, GROUND), (HOLE_X, GROUND - 260)], "#f4f4f8", 5)
        wave = 10 * math.sin(t * 5)
        cv.poly([(HOLE_X, GROUND - 260), (HOLE_X + 90, GROUND - 235 + wave), (HOLE_X, GROUND - 210)], "#ff3b3b")
        i = min(n - 1, int(t / shot))
        k = t - i * shot
        aces = sum(1 for j in range(n) if results[j][0] and (j < i or (j == i and k > 3.4)))
        if t >= n * shot:
            p = mix(G_FOLLOW, pose(lu=-150, lf=0, ru=150, rf=0, sw=0), smooth((t - n * shot) / 0.6))
        else:
            p = keyframes([(0, G_ADDRESS), (0.8, G_ADDRESS), (1.5, G_BACK), (1.72, G_ADDRESS),
                           (2.2, G_FOLLOW), (shot - 0.5, G_FOLLOW), (shot, G_ADDRESS)], k)
        J = fig.place(p, X)
        shadow(cv, pal, X, 90)
        fig.draw(cv, J)
        d = _dir(J["rfore_angle"] + p.get("sw", 0), 1)
        head = _along(J["rhand"], d, 300)
        cv.line([J["rhand"], head], "#dfe4ff", 6)
        cv.line([head, (head[0] + 26, head[1] + 4)], "#9aa0b8", 14)
        cv.line([(tee, GROUND), (tee, GROUND - 16)], "#f4f4f8", 4)
        if t < n * shot:
            ace, land, stop = results[i]
            R = 11
            if k < 1.72:
                bc = (tee, GROUND - 16 - R)
            elif k < 3.0:
                bc = parabola((tee, GROUND - 16 - R), (land, GROUND - R), 900, (k - 1.72) / 1.28)
            elif k < 3.4:
                v = ease_out((k - 3.0) / 0.4)
                bc = (lerp(land, stop, v), GROUND - R - 30 * math.sin(math.pi * clamp(v * 2)))
            else:
                bc = (stop, GROUND - R)
            if not (ace and k > 3.4):
                cv.circle(bc, R, fill="#ffffff")
            if 3.4 <= k < shot:
                word = "HOLE IN ONE!" if ace else f"{int(abs(stop - HOLE_X) / 10)} FT AWAY"
                cv.text((W / 2, 620), word, 90 if ace else 70, pal.at(hue + 0.15, 1.2))
                if ace:
                    burst(cv, (HOLE_X, GROUND - 60), (k - 3.4) % 0.6, pal.at(hue + 0.3, 1.2), n=14, size=120, life=0.6)
        label(cv, "GOLF", pal, y=400, size=60)
        cv.text((W / 2, 500), f"ACES {aces}", 70, pal.at(hue + 0.3, 1.1))

    return draw


# -- baseball ---------------------------------------------------------------------------

BAT_STANCE = pose(lean=10, lt=-22, ls=24, rt=24, rs=24, lu=40, lf=140, ru=30, rf=150, sw=-30)
BAT_SWING = pose(lean=18, lt=-30, ls=10, rt=40, rs=30, lu=90, lf=10, ru=90, rf=0, sw=0)
BAT_FOLLOW = pose(lean=4, lt=-30, ls=10, rt=40, rs=30, lu=160, lf=60, ru=150, rf=60, sw=80)
PITCH_SET = pose(lu=40, lf=110, ru=40, rf=110)
PITCH_KICK = pose(rt=95, rs=95, lt=0, ls=4, lu=30, lf=110, ru=30, rf=110, lean=-8)
PITCH_BACK = pose(rt=30, rs=40, lt=-10, ls=10, ru=-150, rf=20, lu=60, lf=40, lean=-10)
PITCH_THROW = pose(rt=60, rs=60, lt=-40, ls=20, ru=110, rf=10, lu=-40, lf=40, lean=35)
PLATE = (330, GROUND - 250)


def baseball(rng, pal, dur):
    hue = rng.random()
    batter, pitcher = Figure(pal.at(hue), height=500), Figure(pal.at(hue + 0.5), height=440)
    catcher = Figure(pal.dim(hue + 0.7, 0.5), height=380)
    pitch = 3.4
    finale = 2.4
    n = max(1, int((dur - finale) / pitch))
    pitch = (dur - finale) / n
    outcomes = [rng.choice(["hr", "hr", "strike"]) for _ in range(n)]
    mound = GROUND - 30

    def draw(cv, t):
        crowd(cv, pal, hue, t, rows=4, cheer=True)
        cv.line([(0, 840), (W, 840)], pal.dim(hue + 0.3, 0.4), 10)  # outfield wall
        floor(cv, pal)
        cv.ellipse((880, GROUND), 170, 30, pal.dim(0.08, 0.4))
        i = min(n - 1, int(t / pitch))
        k = t - i * pitch
        out = outcomes[i]
        hrs = sum(1 for j in range(n) if outcomes[j] == "hr" and (j < i or (j == i and k > 1.5)))
        pp = keyframes([(0, PITCH_SET), (0.6, PITCH_KICK), (0.9, PITCH_BACK), (1.1, PITCH_THROW),
                        (1.6, PITCH_THROW), (2.2, PITCH_SET)], k)
        Jp = pitcher.place(pp, 880, ground=mound, facing=-1)
        pitcher.draw(cv, Jp)
        if t >= n * pitch:
            bp = mix(BAT_FOLLOW, pose(lu=-150, lf=0, ru=150, rf=0, sw=0), smooth((t - n * pitch) / 0.5))
        elif out == "hr":
            bp = keyframes([(0, BAT_STANCE), (1.38, BAT_STANCE), (1.5, BAT_SWING), (1.8, BAT_FOLLOW),
                            (2.8, BAT_FOLLOW), (pitch, BAT_STANCE)], k)
        else:
            bp = keyframes([(0, BAT_STANCE), (1.5, BAT_STANCE), (1.62, BAT_SWING), (1.9, BAT_FOLLOW),
                            (2.6, BAT_FOLLOW), (pitch, BAT_STANCE)], k)
        J = batter.place(bp, 260)
        shadow(cv, pal, 260, 90)
        catcher.draw(cv, catcher.place(pose(lean=30, lt=100, ls=140, rt=95, rs=140, ru=90, rf=30, lu=60, lf=60),
                                       110))
        batter.draw(cv, J)
        d = _dir(J["rfore_angle"] + bp.get("sw", 0), 1)
        cv.line([J["rhand"], _along(J["rhand"], d, 120)], "#c98a4b", 10)
        cv.line([_along(J["rhand"], d, 120), _along(J["rhand"], d, 260)], "#c98a4b", 20)
        if t < n * pitch:
            if 1.1 <= k < 1.5:
                bc = (lerp(Jp["rhand"][0], PLATE[0], (k - 1.1) / 0.4), lerp(Jp["rhand"][1], PLATE[1], (k - 1.1) / 0.4))
                cv.circle(bc, 12, fill="#ffffff")
            elif k >= 1.5 and out == "hr" and k < 2.8:
                bc = parabola(PLATE, (1500, -200), 500, (k - 1.5) / 1.3)
                cv.circle(bc, 12, fill="#ffffff")
            elif k >= 1.5 and out == "strike" and k < 1.7:
                cv.circle((lerp(PLATE[0], 150, (k - 1.5) / 0.2), PLATE[1] + 60 * (k - 1.5) / 0.2), 12, fill="#ffffff")
            if 1.5 <= k < 2.8:
                word = "HOME RUN!" if out == "hr" else "STRIKE!"
                cv.text((W / 2, 620), word, 100, pal.at(hue + 0.15, 1.2))
                if out == "hr":
                    for j in range(3):
                        burst(cv, (250 + j * 290, 720 + 60 * (j % 2)), (k - 1.5 - j * 0.2) % 0.8,
                              pal.at(hue + j * 0.3, 1.2), seed=j, n=16, size=120, life=0.8)
        label(cv, "BASEBALL", pal, y=400, size=60)
        cv.text((W / 2, 500), f"HOME RUNS {hrs}", 70, pal.at(hue + 0.3, 1.1))

    return draw


# -- cricket ---------------------------------------------------------------------------

CR_STANCE = pose(lean=22, lt=-10, ls=20, rt=16, rs=20, lu=-10, lf=20, ru=-10, rf=20, sw=-20)
CR_BACKLIFT = pose(lean=12, lt=-10, ls=20, rt=16, rs=20, lu=-120, lf=-30, ru=-120, rf=-30, sw=-40)
CR_LOFT = pose(lean=-10, lt=-20, ls=10, rt=40, rs=30, lu=150, lf=40, ru=150, rf=40, sw=20)
CR_DRIVE = pose(lean=40, lt=-40, ls=10, rt=60, rs=60, lu=60, lf=0, ru=60, rf=0, sw=-10)
CR_RUNUP = 1.2


def cricket(rng, pal, dur):
    hue = rng.random()
    bat_fig, bowler = Figure(pal.at(hue), height=500), Figure(pal.at(hue + 0.5), height=480)
    ball_len = 3.6
    finale = 2.4
    n = max(1, int((dur - finale) / ball_len))
    ball_len = (dur - finale) / n
    outcomes = [rng.choice(["six", "six", "four", "bowled"]) for _ in range(n)]
    X = 280
    bounce = (470, GROUND - 12)
    meet = (380, GROUND - 170)

    def draw(cv, t):
        crowd(cv, pal, hue, t, cheer=True)
        floor(cv, pal)
        cv.rect((150, GROUND - 4, 900, GROUND + 10), fill=pal.dim(0.1, 0.35))  # pitch strip
        i = min(n - 1, int(t / ball_len))
        k = t - i * ball_len
        out = outcomes[i] if t < n * ball_len else "done"
        runs = wickets = 0
        for j in range(n):
            if j < i or (j == i and k > 2.0) or t >= n * ball_len:
                runs += {"six": 6, "four": 4}.get(outcomes[j], 0)
                wickets += outcomes[j] == "bowled"
        # stumps (knocked flying on a wicket)
        hit = out == "bowled" and k > 2.0
        for s, sx in enumerate((175, 190, 205)):
            if hit:
                u = min(1.0, (k - 2.0) / 0.6)
                ang = math.radians(-60 * u * (s + 1) / 2)
                top = (sx - 200 * u * (s + 1) / 3 + 150 * math.sin(ang), GROUND - 150 + 300 * u * u - 250 * u)
                cv.line([(sx - 60 * u * s, GROUND - 200 * u * (1 - u)), top], "#f4e7c8", 7)
            else:
                cv.line([(sx, GROUND), (sx, GROUND - 150)], "#f4e7c8", 7)
        # bowler: run-up, delivery stride, follow-through
        if k < CR_RUNUP:
            bx = lerp(1150, 830, k / CR_RUNUP)
            bp = run(k * 2.4)
        else:
            bx = 830 - 60 * ease_out(clamp((k - CR_RUNUP) / 0.6))
            bp = keyframes([(0, pose(lt=40, ls=20, rt=-30, rs=40, ru=-100, rf=0, lu=150, lf=0, lean=-10)),
                            (0.25, pose(lt=-40, ls=10, rt=50, rs=40, ru=170, rf=0, lu=-60, lf=20, lean=20)),
                            (0.6, pose(lt=-30, ls=20, rt=40, rs=40, ru=20, rf=20, lu=-40, lf=30, lean=35)),
                            (1.4, STAND)], k - CR_RUNUP)
        Jb = bowler.place(bp, bx, facing=-1)
        shadow(cv, pal, bx, 80)
        bowler.draw(cv, Jb)
        if out == "done":
            p = mix(CR_LOFT, pose(lu=-150, lf=0, ru=150, rf=0, sw=0), smooth((t - n * ball_len) / 0.5))
        elif out == "bowled":
            p = keyframes([(0, CR_STANCE), (1.6, CR_STANCE), (1.9, CR_DRIVE), (2.6, CR_DRIVE),
                           (3.2, pose(CR_STANCE, head=30, lean=30))], k)
        else:
            shot = CR_LOFT if out == "six" else CR_DRIVE
            p = keyframes([(0, CR_STANCE), (1.5, CR_STANCE), (1.75, CR_BACKLIFT), (2.0, shot), (2.8, shot),
                           (ball_len, CR_STANCE)], k)
        J = bat_fig.place(p, X)
        shadow(cv, pal, X, 90)
        bat_fig.draw(cv, J)
        d = _dir(J["rfore_angle"] + p.get("sw", 0), 1)
        cv.line([J["rhand"], _along(J["rhand"], d, 60)], "#2a2a2a", 9)
        cv.line([_along(J["rhand"], d, 60), _along(J["rhand"], d, 230)], "#f1d39a", 24)
        if out != "done":
            rel = CR_RUNUP + 0.25
            release = (Jb["rhand"][0], Jb["rhand"][1])
            bc = None
            if rel <= k < rel + 0.3:
                u = (k - rel) / 0.3
                bc = (lerp(release[0], bounce[0], u), lerp(release[1], bounce[1], u * u))
            elif rel + 0.3 <= k < 2.0:
                u = (k - rel - 0.3) / (2.0 - rel - 0.3)
                target = meet if out != "bowled" else (200, GROUND - 120)
                bc = (lerp(bounce[0], target[0], u), lerp(bounce[1], target[1], u))
            elif k >= 2.0 and out == "six" and k < 3.3:
                bc = parabola(meet, (1400, 300), 700, (k - 2.0) / 1.3)
            elif k >= 2.0 and out == "four" and k < 3.0:
                u = (k - 2.0) / 1.0
                bc = (lerp(meet[0], 1200, u), GROUND - 12 - 60 * abs(math.sin(u * 9)) * (1 - u))
            if bc:
                cv.circle(bc, 12, fill="#e8322e")
            if 2.0 <= k < 3.3:
                word = {"six": "SIX!", "four": "FOUR!", "bowled": "BOWLED!"}[out]
                cv.text((W / 2, 620), word, 130, pal.at(hue + 0.15, 1.2))
        label(cv, "CRICKET", pal, y=400, size=60)
        cv.text((W / 2, 500), f"{runs}/{wickets}", 80, pal.at(hue + 0.3, 1.1))

    return draw


# -- bowling ---------------------------------------------------------------------------

PIN_X = [850, 905, 960, 1015]


def pin(cv, c, rot, color="#f7f7fb", s=2.0):
    ang = math.radians(rot)
    up = (math.sin(ang), -math.cos(ang))

    def at(k):
        return (c[0] + up[0] * k * s, c[1] + up[1] * k * s)
    cv.line([at(8), at(40)], color, 34 * s)
    cv.line([at(40), at(62)], color, 16 * s)
    cv.circle(at(74), 13 * s, fill=color)
    cv.line([at(52), at(56)], "#e8322e", 18 * s, caps=False)


def bowling(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=520)
    ball_col = pal.at(hue + 0.5)
    frame = 4.4
    finale = 2.2
    n = max(1, int((dur - finale) / frame))
    frame = (dur - finale) / n
    rolls = []
    for _ in range(n):
        strike = rng.random() < 0.65
        standing = set() if strike else set(rng.sample(range(4), rng.randint(1, 2)))
        seed = rng.random()
        rolls.append((strike, standing, seed))
    release, impact = 1.9, 3.0

    def draw(cv, t):
        floor(cv, pal)
        cv.rect((60, GROUND - 4, 1080, GROUND + 14), fill=pal.dim(0.12, 0.5))  # lane
        for i in range(5):
            cv.poly([(300 + i * 110, GROUND + 14), (320 + i * 110, GROUND + 4), (340 + i * 110, GROUND + 14)],
                    pal.at(hue + 0.2, 0.7))  # arrows
        i = min(n - 1, int(t / frame))
        k = t - i * frame
        done = t >= n * frame
        strike, standing, seed = rolls[i]
        strikes = sum(1 for j in range(n) if rolls[j][0] and (j < i or (j == i and k > impact) or done))
        r = random.Random(seed)
        for c_i, px in enumerate(PIN_X):
            for row in range(2 if c_i < 2 else 3 - (c_i == 3)):
                base = (px + row * 16, GROUND)
                if k > impact and c_i not in standing and not done:
                    u = k - impact
                    vx, vy, spin = r.uniform(150, 600), r.uniform(-900, -400), r.uniform(-900, 900)
                    pc = (base[0] + vx * u, base[1] + vy * u + 1200 * u * u)
                    pin(cv, (pc[0], min(pc[1], GROUND)), spin * u)
                else:
                    r.random(), r.random(), r.random()
                    pin(cv, base, 0)
        if done:
            p = mix(STAND, pose(lu=-150, lf=0, ru=150, rf=0), smooth((t - n * frame) / 0.5))
            x = 420
        elif k < 1.4:  # approach
            x = lerp(100, 380, k / 1.4)
            p = walk(x / 150, 1.1)
            p.update(ru=-20 - 120 * clamp((k - 0.8) / 0.6), rf=0)
        elif k < release:
            u = (k - 1.4) / (release - 1.4)
            x = lerp(380, 440, ease_out(u))
            p = mix(pose(ru=-140, rf=0, lean=30, rt=50, rs=60, lt=-50, ls=40),
                    pose(ru=40, rf=0, lean=48, rt=75, rs=80, lt=-70, ls=10, lu=-90, lf=0), smooth(u))
        else:
            x = 440
            low = pose(ru=40, rf=0, lean=48, rt=75, rs=80, lt=-70, ls=10, lu=-90, lf=0)
            after = pose(lu=-150, lf=0, ru=150, rf=0) if strike else pose(lean=50, head=30, lu=10, ru=10)
            p = keyframes([(0, low), (impact - release, low), (impact - release + 0.5, after), (9, after)], k - release)
        J = fig.place(p, x)
        shadow(cv, pal, x, 90)
        fig.draw(cv, J)
        R = 48
        if not done:
            if k < release:
                bc = (J["rhand"][0], J["rhand"][1] + R * 0.6)
            elif k < impact + 0.8:
                u = (k - release) / (impact - release)
                bc = (lerp(J["rhand"][0] if u <= 0 else 470, 1300, u * 0.65 if u < 1 else 0.65 + (u - 1) * 0.5),
                      GROUND - R)
            else:
                bc = None
            if bc:
                cv.circle(bc, R, fill=ball_col)
                a = -k * 12
                for j in range(3):
                    cv.circle((bc[0] + 14 * math.cos(a + j * 0.5), bc[1] + 14 * math.sin(a + j * 0.5)), 4,
                              fill=shade(ball_col, 0.4))
            if impact <= k < impact + 1.2:
                word = "STRIKE!" if strike else f"{10 - 3 * len(standing)} PINS"
                cv.text((W / 2, 620), word, 110, pal.at(hue + 0.15, 1.2))
                burst(cv, (950, GROUND - 60), k - impact, pal.at(hue + 0.2, 1.2), seed=i, n=14, size=130, life=0.5)
        label(cv, "BOWLING", pal, y=400, size=60)
        cv.text((W / 2, 500), f"STRIKES {strikes}", 70, pal.at(hue + 0.3, 1.1))

    return draw


# -- penalty kick ------------------------------------------------------------------------

K_GK = pose(lean=12, lt=-24, ls=30, rt=24, rs=30, lu=-80, lf=30, ru=80, rf=30)
K_DIVE_HI = pose(lean=-10, lt=-20, ls=10, rt=20, rs=10, lu=-170, lf=0, ru=170, rf=0)
K_DIVE_LO = pose(lean=0, lt=-10, ls=10, rt=20, rs=20, lu=170, lf=0, ru=160, rf=0)
KICK_RUN_END = 1.1


def penalty(rng, pal, dur):
    hue = rng.random()
    kicker, keeper = Figure(pal.at(hue), height=520), Figure(pal.at(hue + 0.5), height=480)
    kick = 3.4
    finale = 2.4
    n = max(1, int((dur - finale) / kick))
    kick = (dur - finale) / n
    shots = []
    for _ in range(n):
        aim = rng.choice(["high", "low"])
        dive = aim if rng.random() < 0.35 else ("low" if aim == "high" else "high")
        shots.append((aim, dive))
    spot = (520, GROUND - 26)

    def draw(cv, t):
        crowd(cv, pal, hue, t, rows=4, cheer=True)
        floor(cv, pal)
        i = min(n - 1, int(t / kick))
        k = t - i * kick
        done = t >= n * kick
        aim, dive = shots[i]
        goals = sum(1 for j in range(n) if shots[j][0] != shots[j][1] and (j < i or (j == i and k > 1.5) or done))
        saves = sum(1 for j in range(n) if shots[j][0] == shots[j][1] and (j < i or (j == i and k > 1.5) or done))
        scored = aim != dive
        # goal frame and net
        bulge = 30 * math.sin(clamp((k - 1.5) / 0.4) * math.pi) if scored and k > 1.5 and not done else 0
        post = "#f4f4f8"
        cv.line([(800, GROUND), (800, GROUND - 330), (1060, GROUND - 330)], post, 14)
        for j in range(7):
            cv.line([(800, GROUND - 330 + j * 55), (1070 + bulge, GROUND - 320 + j * 55)], pal.dim(hue + 0.5, 0.4), 3,
                    caps=False)
        # keeper
        if done or k < 1.1:
            kp, lift, rot = K_GK, 0.0, 0.0
        else:
            u = clamp((k - 1.1) / 0.4)
            if dive == "high":
                kp, lift, rot = mix(K_GK, K_DIVE_HI, smooth(u)), 220 * math.sin(math.pi * clamp(u * 0.8)), 0.0
            else:
                kp, lift, rot = mix(K_GK, K_DIVE_LO, smooth(u)), 0.0, -80 * smooth(u)
        keeper.draw(cv, keeper.place(kp, 930, lift=lift, facing=-1, rot=rot))
        # kicker
        if done:
            kpose, kx = mix(STAND, pose(lu=-150, lf=0, ru=150, rf=0), smooth((t - n * kick) / 0.5)), 470
        elif k < KICK_RUN_END:
            kx = lerp(160, 460, k / KICK_RUN_END)
            kpose = run(k * 2.2)
        else:
            kx = 460
            kpose = keyframes([(0, pose(rt=-50, rs=90, lean=-10, lu=-70, ru=50)),
                               (0.15, pose(rt=95, rs=5, lean=-20, lu=-100, ru=40)), (0.6, STAND)], k - KICK_RUN_END)
        J = kicker.place(kpose, kx)
        shadow(cv, pal, kx, 90)
        kicker.draw(cv, J)
        if not done:
            target = (990, GROUND - 270) if aim == "high" else (990, GROUND - 60)
            hit_t = KICK_RUN_END + 0.15
            if k < hit_t:
                bc = spot
            elif k < 1.5:
                bc = parabola(spot, target, 60, (k - hit_t) / (1.5 - hit_t))
            elif scored:
                v = clamp((k - 1.5) / 0.5)
                bc = (target[0] + 50 * v, lerp(target[1], GROUND - 26, v * v))
            else:
                bc = parabola(target, (700, GROUND - 26), 160, clamp((k - 1.5) / 0.7))
            ball(cv, bc, 26, color="#f4f6ff", seam="#1a1a2e", spin=k * 9)
            if 1.5 <= k < 2.8:
                cv.text((W / 2, 620), "GOAL!" if scored else "SAVED!", 130, pal.at(hue + (0 if scored else 0.5), 1.2))
        label(cv, "PENALTY KICK", pal, y=400, size=58)
        cv.text((W / 2, 500), f"GOALS {goals}  SAVES {saves}", 60, pal.at(hue + 0.3, 1.1))

    return draw


# -- high jump -------------------------------------------------------------------------

MAT_X0, MAT_X1, MAT_H = 640, 1000, 70
FLOP = pose(lean=-45, head=-30, lt=-20, ls=60, rt=-10, rs=70, lu=-30, lf=20, ru=-40, rf=20)
FLOP_KICK = pose(lean=-10, head=10, lt=60, ls=0, rt=70, rs=0, lu=40, lf=10, ru=30, rf=10)
LYING = dict(STAND, lean=0, head=10, lt=20, ls=30, rt=10, rs=40, lu=150, lf=30, ru=130, rf=40)


def high_jump(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=500)
    attempt = 3.4
    finale = 2.2
    n = max(1, int((dur - finale) / attempt))
    attempt = (dur - finale) / n
    heights, h, results = [], 2.00, []
    for j in range(n):
        ok = rng.random() < 0.75 or j == n - 1
        heights.append(h)
        results.append(ok)
        if ok:
            h = round(h + 0.05, 2)
    px_per_m = 170

    def draw(cv, t):
        crowd(cv, pal, hue, t, cheer=True)
        floor(cv, pal)
        cv.rect((MAT_X0, GROUND - MAT_H, MAT_X1, GROUND), fill=pal.dim(hue + 0.55, 0.55), radius=16)
        i = min(n - 1, int(t / attempt))
        k = t - i * attempt
        done = t >= n * attempt
        bar_y = GROUND - heights[i] * px_per_m
        for sx in (590, 690):
            cv.line([(sx, GROUND), (sx, bar_y - 40)], pal.dim(0.0, 0.7), 8)
        knocked = not results[i] and k > 1.95 and not done
        if knocked:
            u = clamp((k - 1.95) / 0.4)
            cv.line([(600, lerp(bar_y, GROUND - MAT_H - 8, u * u)), (690, lerp(bar_y, GROUND - MAT_H - 8, u) + 20 * u)],
                    pal.at(hue + 0.1, 1.1), 10)
        else:
            cv.line([(590, bar_y), (690, bar_y)], pal.at(hue + 0.1, 1.1), 10)
        if done:
            k2 = t - n * attempt
            p = mix(LYING, pose(lu=-150, lf=0, ru=150, rf=0), smooth(k2 / 0.8))
            J = fig.place(p, 800, ground=GROUND - MAT_H, rot=-90 * (1 - smooth(k2 / 0.8)))
        elif k < 1.3:
            x = lerp(60, 520, k / 1.3)
            J = fig.place(run(x / 330), x)
            shadow(cv, pal, x, 80)
        elif k < 2.1:
            u = (k - 1.3) / 0.8
            x = lerp(520, 820, u)
            peak = GROUND - bar_y + 10
            lift = peak * 4 * u * (1 - u)
            p = mix(FLOP, FLOP_KICK, smooth((u - 0.5) * 2))
            ground = GROUND - MAT_H if x > MAT_X0 else GROUND
            J = fig.place(p, x, ground=ground, lift=max(0.0, lift - (GROUND - ground) * u), rot=-100 * smooth(u))
        else:
            J = fig.place(LYING, 820, ground=GROUND - MAT_H, rot=-90)
        fig.draw(cv, J)
        if not done and 2.0 <= k < attempt:
            cv.text((W / 2, 620), "CLEARED!" if results[i] else "KNOCKED IT!", 100,
                    pal.at(hue + (0.15 if results[i] else 0.5), 1.2))
        label(cv, "HIGH JUMP", pal, y=400, size=60)
        cv.text((W / 2, 500), f"{heights[i]:.2f} m", 80, pal.at(hue + 0.3, 1.1))

    return draw


# -- weightlifting ---------------------------------------------------------------------

WL_GRIP = pose(lean=48, lt=95, ls=118, rt=92, rs=115, lu=-48, lf=0, ru=-48, rf=0)
WL_PULL = pose(lean=20, lt=30, ls=30, rt=28, rs=30, lu=-20, lf=0, ru=-20, rf=0)
WL_RACK = pose(lean=4, lt=40, ls=60, rt=36, rs=58, lu=40, lf=150, ru=40, rf=150)
WL_STAND = pose(lean=0, lt=4, ls=4, rt=-4, rs=4, lu=40, lf=150, ru=40, rf=150)
WL_DIP = pose(WL_STAND, lt=20, ls=35, rt=16, rs=35)
WL_JERK = pose(lean=0, lt=-40, ls=30, rt=45, rs=42, lu=178, lf=0, ru=178, rf=0)
WL_OVER = pose(lean=0, lt=6, ls=4, rt=-6, rs=4, lu=178, lf=0, ru=178, rf=0)


def weightlifting(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=560)
    plate_col = pal.at(hue + 0.5)
    lift_len = 5.2
    finale = 2.0
    n = max(1, int((dur - finale) / lift_len))
    lift_len = (dur - finale) / n
    start_kg = rng.choice([120, 140, 160])
    X = W / 2
    frames = [(0, STAND), (0.6, WL_GRIP), (1.0, WL_GRIP), (1.5, WL_PULL), (1.8, WL_RACK), (2.4, WL_STAND),
              (2.8, WL_DIP), (3.05, WL_JERK), (3.6, WL_JERK), (4.0, WL_OVER), (4.6, WL_OVER)]
    PLATE_R = 110

    def draw(cv, t):
        cv.rect((200, GROUND - 8, 880, GROUND + 14), fill=pal.dim(0.1, 0.45))  # platform
        floor(cv, pal)
        i = min(n - 1, int(t / lift_len))
        k = t - i * lift_len
        done = t >= n * lift_len
        kg = start_kg + 10 * i
        if done:
            p = mix(STAND, pose(lu=-100, lf=-100, ru=100, rf=100), smooth((t - n * lift_len) / 0.5))
            J = fig.place(p, X)
            fig.draw(cv, J)
            cv.circle((X + 250, GROUND - PLATE_R), PLATE_R, fill=plate_col)
            label(cv, "NEW RECORD!", pal, y=400, size=76)
            cv.text((W / 2, 500), f"{kg} KG", 80, pal.at(hue + 0.3, 1.1))
            return
        p = keyframes(frames, k)
        J = fig.place(p, X)
        shadow(cv, pal, X, 110)
        fig.draw(cv, J)
        hands = ((J["lhand"][0] + J["rhand"][0]) / 2, (J["lhand"][1] + J["rhand"][1]) / 2)
        if k < 0.6:
            bar = (X + 40, GROUND - PLATE_R)
        elif k < 4.6:
            bar = (hands[0], min(hands[1], GROUND - PLATE_R))
        else:  # drop it
            u = clamp((k - 4.6) / 0.35)
            top = fig.place(WL_OVER, X)["rhand"]
            bar = (top[0] + 60 * u, lerp(top[1], GROUND - PLATE_R, u * u))
        cv.circle(bar, PLATE_R, fill=plate_col)
        cv.circle(bar, PLATE_R * 0.55, fill=shade(plate_col, 0.6))
        cv.circle(bar, 16, fill="#dfe4ff")
        if 3.6 <= k < lift_len:  # judges' lights
            for j in range(3):
                cv.circle((W / 2 - 110 + j * 110, 600), 36, fill="#ffffff")
            pop_text(cv, "GOOD LIFT!", (W / 2, 760), k - 3.6, pal.at(hue + 0.15, 1.2), life=1.2, size=90)
        label(cv, "WEIGHTLIFTING", pal, y=400, size=58)
        cv.text((W / 2, 500), f"{kg} KG", 80, pal.at(hue + 0.3, 1.1))

    return draw


# -- trampoline ------------------------------------------------------------------------

T_TUCK = pose(lean=10, lt=115, ls=140, rt=110, rs=140, lu=60, lf=80, ru=60, rf=80)
T_PIKE = pose(lean=70, lt=95, ls=0, rt=95, rs=0, lu=60, lf=0, ru=60, rf=0)
T_STRAIGHT = pose(lu=178, lf=0, ru=178, rf=0, lt=2, rt=-2)
TRICKS = {"STRAIGHT JUMP": (T_STRAIGHT, 0, False), "FRONT FLIP": (T_TUCK, 360, False),
          "BACKFLIP": (T_TUCK, -360, False), "PIKE": (T_PIKE, 0, False), "DOUBLE BACK": (T_TUCK, -720, False),
          "FULL TWIST": (T_STRAIGHT, 0, True)}
BED_Y = GROUND - 150


def trampoline(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=460)
    bounce = 1.35
    finale = 2.0
    n = max(2, int((dur - finale) / bounce))
    bounce = (dur - finale) / n
    seq = ["STRAIGHT JUMP"] + [rng.choice(list(TRICKS)[1:]) for _ in range(n - 1)]
    X = W / 2

    def draw(cv, t):
        floor(cv, pal)
        for lx in (320, 760):
            cv.line([(lx, BED_Y), (lx + (-30 if lx < W / 2 else 30), GROUND)], pal.dim(0.0, 0.7), 10)
        i = min(n - 1, int(t / bounce))
        k = (t - i * bounce) / bounce
        done = t >= n * bounce
        contact = 0.14
        if done:
            dip = 0.0
            p, lift, rot, f = mix(T_STRAIGHT, pose(lu=-150, lf=0, ru=150, rf=0), smooth((t - n * bounce) / 0.4)), 0, 0, 1
            name = "STUCK IT!"
        elif k < contact:  # in the bed
            dip = 60 * math.sin(math.pi * k / contact)
            p, lift, rot, f = pose(lt=10, ls=30, rt=-10, rs=30, lu=-30, ru=30), -dip, 0.0, 1
            name = seq[i]
        else:
            dip = 0.0
            u = (k - contact) / (1 - contact)
            height = 260 + 25 * min(i, 8)
            lift = height * 4 * u * (1 - u)
            shape, spin, twist = TRICKS[seq[i]]
            w = math.sin(math.pi * u)
            p = mix(T_STRAIGHT, shape, clamp(w * 1.6))
            rot = spin * smooth((u - 0.1) / 0.8)
            f = -1 if twist and 0.3 < u < 0.7 else 1
            name = seq[i]
        cv.line(bezier_bed(dip), "#dfe4ff", 8)
        J = fig.place(p, X, ground=BED_Y, lift=lift, facing=f, rot=rot)
        shadow(cv, pal, X, 110, y=BED_Y, air=max(0.0, lift))
        fig.draw(cv, J)
        label(cv, name, pal, y=400, size=64)
        cv.text((W / 2, 500), f"COMBO x{i + (1 if done else 0)}", 70, pal.at(hue + 0.3, 1.1))

    return draw


def bezier_bed(dip):
    return bezier((320, BED_Y), (W / 2, BED_Y + 2 * dip), (760, BED_Y))
