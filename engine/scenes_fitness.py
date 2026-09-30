"""Fitness and calm scenes: workouts with rep counters, pull-ups, jump rope, yoga, tai chi and meditation.

Exercise poses may carry extra keys that mix() blends: x (step offset), lift (px in the air) and
rot (whole-body tilt, e.g. 76 for a plank, -90 for lying on the back).
"""

import math

from .stick import (GROUND, STAND, W, Figure, Timeline, bezier, floor, keyframes, label, lerp, mix, pose,
                    run, shadow, smooth)

# -- exercises -----------------------------------------------------------------------

JACK_IN = pose(lu=6, lf=6, ru=-6, rf=6)
JACK_OUT = pose(lt=22, ls=0, rt=-22, rs=0, lu=-150, lf=-10, ru=150, rf=10, lift=60)
SQUAT_UP = pose(lu=12, lf=10, ru=12, rf=10)
SQUAT_DOWN = pose(lean=38, lt=88, ls=110, rt=84, rs=104, lu=58, lf=0, ru=52, rf=0)
PLANK = dict(lean=0, head=-8, lt=0, ls=0, rt=0, rs=0, lu=84, lf=0, ru=90, rf=0, rot=76, x=-60)
PUSH_DOWN = dict(PLANK, lu=-10, lf=110, ru=-4, rf=108, rot=86)
FLEX = pose(lt=14, ls=4, rt=-14, rs=4, lu=-95, lf=-100, ru=95, rf=100)
LYING = dict(STAND, lean=0, head=0, lt=45, ls=90, rt=45, rs=90, lu=165, lf=140, ru=160, rf=140, rot=-90)
SIT_UP = dict(LYING, lean=80, head=10)
CRUNCH = dict(LYING, lean=32, head=12)
SQUAT_HANDS = pose(SQUAT_DOWN, lean=50, lu=-20, ru=-15, lf=0, rf=0)
STAR = pose(lt=36, ls=0, rt=-36, rs=0, lu=-150, lf=0, ru=150, rf=0, lift=140)
LUNGE_R = pose(lean=4, rt=80, rs=82, lt=-42, ls=95, lu=10, lf=80, ru=10, rf=80)
LUNGE_L = pose(lean=4, lt=80, ls=82, rt=-42, rs=95, lu=10, lf=80, ru=10, rf=80)
SKATE_R = pose(lean=40, rt=50, rs=60, lt=-70, ls=60, lu=-60, lf=20, ru=70, rf=20, x=130)
SKATE_L = pose(SKATE_R, x=-130)


def _loop(frames):
    return lambda k: keyframes(frames, k)


def _high_knees(k):
    p = run(k)
    p.update(lean=2, lt=max(p["lt"], -10) * 1.6, rt=max(p["rt"], -10) * 1.6)
    p["lift"] = 18 * abs(math.sin(2 * math.pi * k))
    return p


def _climbers(k):
    s = math.sin(2 * math.pi * k)
    return dict(PLANK, lt=40 + 45 * s, ls=60 + 50 * s, rt=40 - 45 * s, rs=60 - 50 * s, rot=72)


def _plank_hold(k):
    return dict(PLANK, rot=80 + 1.2 * math.sin(k * 40))


EXERCISES = {  # name: (seconds per rep, pose function of rep progress 0..1)
    "JUMPING JACKS": (0.62, _loop([(0, JACK_IN), (0.5, JACK_OUT), (1, JACK_IN)])),
    "SQUATS": (1.25, _loop([(0, SQUAT_UP), (0.45, SQUAT_DOWN), (0.6, SQUAT_DOWN), (1, SQUAT_UP)])),
    "PUSH-UPS": (1.15, _loop([(0, PLANK), (0.5, PUSH_DOWN), (1, PLANK)])),
    "HIGH KNEES": (0.5, _high_knees),
    "SIT-UPS": (1.4, _loop([(0, LYING), (0.45, SIT_UP), (0.6, SIT_UP), (1, LYING)])),
    "CRUNCHES": (0.9, _loop([(0, LYING), (0.45, CRUNCH), (1, LYING)])),
    "MOUNTAIN CLIMBERS": (0.55, _climbers),
    "PLANK": (1.0, _plank_hold),
    "BURPEES": (1.8, _loop([(0, STAND), (0.2, SQUAT_HANDS), (0.35, PLANK), (0.55, PLANK), (0.7, SQUAT_HANDS),
                            (0.85, STAR), (1, STAND)])),
    "LUNGES": (1.4, _loop([(0, STAND), (0.25, LUNGE_R), (0.5, STAND), (0.75, LUNGE_L), (1, STAND)])),
    "STAR JUMPS": (1.1, _loop([(0, STAND), (0.35, SQUAT_DOWN), (0.6, STAR), (1, STAND)])),
    "SKATERS": (1.0, _loop([(0, SKATE_L), (0.5, SKATE_R), (1, SKATE_L)])),
}

WORKOUTS = {
    "full": ("WORKOUT DONE", ["JUMPING JACKS", "SQUATS", "PUSH-UPS", "HIGH KNEES"]),
    "abs": ("ABS ON FIRE", ["SIT-UPS", "CRUNCHES", "MOUNTAIN CLIMBERS", "PLANK"]),
    "hiit": ("HIIT COMPLETE", ["BURPEES", "LUNGES", "STAR JUMPS", "SKATERS"]),
}


def workout(rng, pal, dur, kind="full"):
    done_title, names = WORKOUTS[kind]
    fig = Figure(pal.at(rng.random()))
    totals = {}

    def exercise(cv, u, t, d, name, reps, start):
        rep_len = d / reps
        n = min(int(t / rep_len), reps - 1)
        k = (t - n * rep_len) / rep_len
        p = EXERCISES[name][1](k)
        x, lift, rot = W / 2 + p.get("x", 0), p.get("lift", 0), p.get("rot", 0)
        shadow(cv, pal, x + (40 if abs(rot) > 30 else 0), 150 if abs(rot) > 30 else 100, air=lift)
        fig.draw(cv, fig.place(p, x, lift=lift, rot=rot))
        label(cv, name, pal, y=400, size=62)
        count = f"{start + n + 1}s" if name == "PLANK" else f"x{start + n + (1 if k > 0.5 else 0)}"
        cv.text((W / 2, 520), count, 120, pal.at(0.55, 1.1))

    def flex(cv, u, t, d):
        p = keyframes([(0, STAND), (0.5, FLEX), (1.5, FLEX), (2, pose(FLEX, lean=-6, lu=-110, ru=110))], t)
        shadow(cv, pal, W / 2)
        fig.draw(cv, fig.place(p, W / 2))
        label(cv, done_title, pal, y=400, size=62)
        cv.text((W / 2, 520), f"{sum(totals.values())} REPS", 110, pal.at(0.55, 1.1))

    finale = 3.0
    tl = Timeline()
    order = names[:]
    rng.shuffle(order)
    i = 0
    while tl.total < dur - finale - 3:
        name = order[i % len(order)]
        i += 1
        rep = EXERCISES[name][0]
        reps = max(3, min(rng.randint(5, 10), int((dur - finale - tl.total) / rep)))
        tl.add(reps * rep, exercise, name=name, reps=reps, start=totals.get(name, 0))
        totals[name] = totals.get(name, 0) + reps
    tl.add(max(finale, dur - tl.total), flex)

    def draw(cv, t):
        floor(cv, pal)
        cv.rect((200, GROUND - 6, 880, GROUND + 10), fill=pal.dim(0.6, 0.45), radius=8)  # mat
        tl.play(cv, t)

    return draw


# -- pull-up bar -----------------------------------------------------------------------

BAR_Y = 760
HANG = dict(STAND, lean=0, lt=-8, ls=60, rt=-4, rs=70, lu=178, lf=0, ru=178, rf=0)
PULL_TOP = dict(HANG, lu=30, lf=150, ru=30, rf=150, head=-10)
LEG_RAISE = dict(HANG, lt=92, ls=0, rt=92, rs=0)
SUPPORT = dict(STAND, lean=12, lt=4, ls=10, rt=-4, rs=10, lu=2, lf=0, ru=2, rf=0)
PULLS = {
    "PULL-UPS": (1.5, [(0, HANG), (0.45, PULL_TOP), (0.6, PULL_TOP), (1, HANG)]),
    "LEG RAISES": (1.5, [(0, HANG), (0.45, LEG_RAISE), (0.6, LEG_RAISE), (1, HANG)]),
    "MUSCLE-UPS": (2.4, [(0, HANG), (0.3, PULL_TOP), (0.45, dict(PULL_TOP, lean=30, lu=-10, lf=120)),
                         (0.6, SUPPORT), (0.75, SUPPORT), (1, HANG)]),
}


def pull_ups(rng, pal, dur):
    fig = Figure(pal.at(rng.random()), height=560)
    finale = 3.0
    tl = Timeline()
    names = list(PULLS)
    rng.shuffle(names)
    totals = {}
    i = 0
    while tl.total < dur - finale - 3:
        name = names[i % len(names)]
        i += 1
        rep, _ = PULLS[name]
        reps = max(2, min(rng.randint(4, 8), int((dur - finale - tl.total) / rep)))
        tl.add(reps * rep, None, name=name, reps=reps, start=totals.get(name, 0))
        totals[name] = totals.get(name, 0) + reps
    tl.add(max(finale, dur - tl.total), None, name="FINISH", reps=1, start=0)

    def draw(cv, t):
        floor(cv, pal)
        for x in (330, 750):
            cv.line([(x, GROUND), (x, BAR_Y - 20)], pal.dim(0.0, 0.7), 16)
        cv.line([(320, BAR_Y), (760, BAR_Y)], "#dfe4ff", 12)
        start, d, _, info = tl.at(t)
        name, reps = info["name"], info["reps"]
        if name == "FINISH":  # drop down and flex
            k = t - start
            if k < 0.6:
                J = fig.anchor(HANG, "rhand", (W / 2, BAR_Y + 6 + 400 * k * k))
            else:
                J = fig.place(mix(STAND, FLEX, smooth((k - 0.6) / 0.5)), W / 2)
            fig.draw(cv, J)
            label(cv, "BEAST MODE", pal, y=400, size=66)
            cv.text((W / 2, 520), f"{sum(totals.values())} REPS", 110, pal.at(0.55, 1.1))
            return
        rep_len = d / reps
        n = min(int((t - start) / rep_len), reps - 1)
        k = (t - start - n * rep_len) / rep_len
        p = keyframes(PULLS[name][1], k)
        J = fig.anchor(p, "rhand", (W / 2 + 10, BAR_Y + 6))
        shadow(cv, pal, W / 2, 90, air=GROUND - J["lankle"][1])
        fig.draw(cv, J)
        label(cv, name, pal, y=400, size=62)
        cv.text((W / 2, 520), f"x{info['start'] + n + (1 if k > 0.5 else 0)}", 120, pal.at(0.55, 1.1))

    return draw


# -- jump rope -------------------------------------------------------------------------

ROPE_TRICKS = {  # revolutions per jump, jump height, pose tweaks
    "BASIC BOUNCE": (1, 55, {}),
    "DOUBLE UNDERS": (2, 120, {}),
    "CRISS-CROSS": (1, 60, {"cross": True}),
    "ONE FOOT HOPS": (1, 55, {"rt": 40, "rs": 90}),
}


def jump_rope(rng, pal, dur):
    fig = Figure(pal.at(rng.random()), height=580)
    rope = pal.at(rng.random() + 0.5, 1.1)
    jump_len = 0.55
    finale = 2.6
    names = list(ROPE_TRICKS)
    rng.shuffle(names)
    names.remove("BASIC BOUNCE")
    names.insert(0, "BASIC BOUNCE")
    tl = Timeline()
    i = 0
    while tl.total < dur - finale - 2:
        name = names[i % len(names)]
        i += 1
        jumps = max(3, min(rng.randint(5, 9), int((dur - finale - tl.total) / jump_len)))
        tl.add(jumps * jump_len, None, name=name, jumps=jumps)
    count_before = []
    c = 0
    for _, _, _, info in tl.beats:
        count_before.append(c)
        c += info["jumps"]
    tl.add(max(finale, dur - tl.total), None, name="FINISH", jumps=1)

    def draw(cv, t):
        floor(cv, pal)
        idx = next(i for i, b in enumerate(tl.beats) if t < b[0] + b[1] or i == len(tl.beats) - 1)
        start, d, _, info = tl.beats[idx]
        name = info["name"]
        base = pose(lu=-32, lf=-30, ru=32, rf=30, lt=4, ls=8, rt=-4, rs=8)
        if name == "FINISH":
            k = t - start
            p = mix(base, pose(lu=-150, lf=0, ru=150, rf=0, lt=14, rt=-14), smooth(k / 0.5))
            J = fig.place(p, W / 2)
            shadow(cv, pal, W / 2)
            cv.line(bezier(J["lhand"], (W / 2, GROUND + 40), J["rhand"]), rope, 6)
            fig.draw(cv, J)
            label(cv, "NEW RECORD!", pal, y=400, size=66)
            cv.text((W / 2, 520), f"{c} JUMPS", 110, pal.at(0.55, 1.1))
            return
        revs, height, tweak = ROPE_TRICKS[name]
        local = t - start
        n = int(local / jump_len)
        k = local / jump_len - n
        theta = 2 * math.pi * revs * k  # 0 = rope under the feet
        lift = height * math.sin(math.pi * k) if revs > 1 else height * (0.5 + 0.5 * math.cos(theta)) ** 2
        p = dict(base)
        p.update({kk: v for kk, v in tweak.items() if kk != "cross"})
        cross = tweak.get("cross") and n % 2 == 1
        if cross:
            p.update(lu=40, lf=10, ru=-40, rf=10)
        p["ls"] = p["rs"] = 8 + 30 * (1 - math.sin(math.pi * k)) if revs > 1 else p["ls"]
        J = fig.place(p, W / 2, lift=lift)
        top, bottom = J["head"][1] - fig.R - 70, GROUND + 6
        mid_x = (J["lhand"][0] + J["rhand"][0]) / 2
        target_y = lerp(bottom, top, 0.5 - 0.5 * math.cos(theta))
        hand_y = (J["lhand"][1] + J["rhand"][1]) / 2
        ctrl = (mid_x, 2 * target_y - hand_y)
        behind = math.sin(theta) > 0
        curve = bezier(J["lhand"], ctrl, J["rhand"])
        shadow(cv, pal, W / 2, 100, air=lift)
        if behind:
            cv.line(curve, rope, 6)
        fig.draw(cv, J)
        if not behind:
            cv.line(curve, rope, 6)
        label(cv, name, pal, y=400, size=58)
        cv.text((W / 2, 520), f"x{count_before[idx] + n + (1 if k > 0.5 else 0)}", 120, pal.at(0.55, 1.1))

    return draw


# -- yoga and tai chi ------------------------------------------------------------------

YOGA = {
    "MOUNTAIN": pose(lu=178, lf=0, ru=178, rf=0),
    "WARRIOR II": dict(lean=0, head=0, lt=-42, ls=0, rt=56, rs=56, lu=-90, lf=0, ru=90, rf=0),
    "TREE": dict(lean=0, head=0, lt=0, ls=0, rt=62, rs=150, lu=172, lf=10, ru=172, rf=10),
    "TRIANGLE": dict(lean=72, head=0, lt=-32, ls=0, rt=34, rs=0, lu=108, lf=0, ru=-72, rf=0),
    "DOWNWARD DOG": dict(lean=128, head=0, lt=-30, ls=0, rt=-30, rs=0, lu=-98, lf=0, ru=-98, rf=0),
    "CHAIR": dict(lean=28, head=0, lt=70, ls=80, rt=70, rs=80, lu=150, lf=0, ru=150, rf=0),
    "LOTUS": dict(lean=0, head=0, lt=90, ls=165, rt=86, rs=160, lu=30, lf=40, ru=26, rf=44),
}
TAI_CHI = {
    "COMMENCEMENT": pose(lt=10, ls=20, rt=-10, rs=20, lu=90, lf=10, ru=90, rf=10),
    "WHITE CRANE": pose(lt=22, ls=12, rt=-6, rs=24, lu=10, lf=30, ru=160, rf=25),
    "SINGLE WHIP": pose(lt=-30, ls=10, rt=36, rs=36, lu=92, lf=10, ru=-100, rf=-70),
    "PART THE MANE": pose(lt=-30, ls=6, rt=46, rs=46, lu=12, lf=30, ru=110, rf=12, lean=4),
    "CLOUD HANDS": pose(lt=-22, ls=34, rt=22, rs=34, lu=40, lf=70, ru=100, rf=60),
    "GOLDEN ROOSTER": pose(lt=0, ls=4, rt=95, rs=100, lu=10, lf=30, ru=150, rf=60),
    "REPULSE MONKEY": pose(lt=-26, ls=24, rt=18, rs=8, lu=-40, lf=30, ru=90, rf=0, lean=-5),
}
NAMASTE = pose(lu=24, lf=128, ru=24, rf=128)

FLOWS = {  # poses, start pose, closing pose, hold, move, breathing cue
    "yoga": (YOGA, "MOUNTAIN", "NAMASTE", 3.2, 1.6, True),
    "taichi": (TAI_CHI, "COMMENCEMENT", "CLOSING", 1.8, 2.6, False),
}


def yoga(rng, pal, dur, style="yoga"):
    poses, first, closing, hold, move, breathe = FLOWS[style]
    fig = Figure(pal.at(rng.random()))
    names = [n for n in poses if n != first]
    rng.shuffle(names)
    finale = 3.0
    seq = [first]
    while (len(seq) + 1) * (hold + move) < dur - finale:
        seq.append(names[(len(seq) - 1) % len(names)])
    frames = [(0.0, STAND, first)]  # (time, pose, name)
    t = 0.0
    for name in seq:
        t += move
        frames.append((t, poses[name], name))
        t += hold
        frames.append((t, poses[name], name))
    end = max(t, dur - finale) + move
    frames.append((end, STAND, closing))
    frames.append((end + 1.0, NAMASTE, closing))
    track = [(ft, fp) for ft, fp, _ in frames]

    def draw(cv, t):
        if style == "taichi":  # moon and drifting mist
            cv.circle((780, 700), 130, fill=pal.dim(0.2, 0.3))
            for i in range(5):
                y = 820 + i * 110
                x = (t * (18 + 6 * i) + i * 300) % (W + 600) - 300
                cv.ellipse((x, y), 420, 26, pal.dim(0.6 + i * 0.05, 0.1))
        else:
            for k in range(6, 0, -1):  # soft sun behind the figure
                cv.circle((W / 2, 900), 120 + k * 40, fill=pal.dim(0.3, 0.05 + 0.04 * (6 - k)))
        floor(cv, pal)
        cv.rect((230, GROUND - 5, 850, GROUND + 9), fill=pal.dim(0.6, 0.45), radius=8)
        name = next((fn for ft, _, fn in reversed(frames) if t >= ft - move), first)
        breath = 0.5 + 0.5 * math.sin(t * 1.4)
        shadow(cv, pal, W / 2, 120)
        fig.draw(cv, fig.place(keyframes(track, t), W / 2))
        cv.text((W / 2, 420), name, 60 if len(name) < 14 else 50, pal.at(0.2, lerp(0.75, 1.1, breath)))
        if breathe:
            cv.text((W / 2, 500), "breathe in" if breath > 0.5 else "breathe out", 34, pal.dim(0.5, 0.8))

    return draw


# -- meditation -------------------------------------------------------------------------

MEDITATE = dict(YOGA["LOTUS"], lu=20, lf=70, ru=18, rf=74)


def meditation(rng, pal, dur):
    hue = rng.random()
    fig = Figure(pal.at(hue), height=600)
    cycle = 8.0  # 4 s in, 4 s out

    def draw(cv, t):
        phase = (t % cycle) / cycle
        inhale = phase < 0.5
        size = smooth(phase * 2) if inhale else 1 - smooth((phase - 0.5) * 2)
        center = (W / 2, 1000)
        for k in range(7, 0, -1):  # breathing orb
            r = (150 + 260 * size) * k / 7
            cv.circle(center, r, fill=pal.dim(hue + 0.1 + k * 0.03, 0.05 + 0.035 * (8 - k)))
        for i in range(18):  # rising motes
            x = (i * 173) % W
            y = GROUND - ((t * (30 + i % 4 * 12) + i * 97) % 1000)
            cv.circle((x + 14 * math.sin(t + i), y), 3 + i % 3, fill=pal.dim(hue + i * 0.05, 0.6))
        floor(cv, pal, k=0.3)
        lift = 70 + 22 * math.sin(t * 2 * math.pi / cycle)
        J = fig.place(MEDITATE, W / 2, lift=lift)
        shadow(cv, pal, W / 2, 150, air=lift)
        fig.draw(cv, J)
        n = 4 - int((phase % 0.5) * 8)
        cv.text((W / 2, 420), "BREATHE IN" if inhale else "BREATHE OUT", 62, pal.at(hue + 0.2, 1.05))
        cv.text((W / 2, 520), str(max(1, n)), 110, pal.at(hue + 0.5, 1.0))
        if t > dur - 2.5:
            cv.text((W / 2, 1560), "be here now", 48, pal.dim(hue + 0.3, 0.9))

    return draw
