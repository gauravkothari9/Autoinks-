"""Comedy scenes: slapstick fails (peels, poles, rocks, falling anvils, rakes, wet floors) and prank wars."""

import math

from .stick import (GROUND, STAND, W, Figure, blend, burst, clamp, ease_out, floor, label, lerp, mix,
                    parabola, pose, shadow, smooth, squash, stars, walk)

WALK_SPEED = 330.0
SPOT = 560.0  # where each fail happens
LYING_BACK = dict(STAND, lean=0, head=10, lt=20, ls=20, rt=-5, rs=40, lu=150, lf=30, ru=120, rf=40)
FLAIL = dict(lean=-20, head=-20, lt=70, ls=10, rt=40, rs=30, lu=-150, lf=40, ru=140, rf=60)
FACE_DOWN = dict(STAND, lean=0, head=-15, lt=-10, ls=60, rt=10, rs=80, lu=160, lf=10, ru=170, rf=10)
PHONE = dict(lu=10, lf=20, ru=40, rf=120)  # right hand up in front of the face
LOOK_UP = pose(head=-35, lean=-6, lu=20, lf=20, ru=-20, rf=20)
DIZZY_SITUP = pose(lean=10, lt=90, ls=20, rt=85, rs=30, lu=20, lf=30, ru=30, rf=30)
CHEER = pose(lt=14, ls=4, rt=-14, rs=4, lu=-150, lf=0, ru=150, rf=0)

GAGS = {  # word, fall rotation, pose lying down, sideways slide while falling, time of the hit
    "banana": ("WHOOPS!", -90, LYING_BACK, 60, 0.6),
    "pole": ("BONK!", -90, LYING_BACK, -120, 0.1),
    "rock": ("OOF!", 90, FACE_DOWN, 170, 0.6),
    "rake": ("THWACK!", -90, LYING_BACK, -110, 0.3),
    "puddle": ("SPLASH!", -90, LYING_BACK, 40, 1.2),
    "anvil": ("CLONK!", 0, STAND, 0, 0.55),
    "piano": ("KRRANG!", 0, STAND, 0, 0.55),
    "pot": ("BONK!", 0, STAND, 0, 0.55),
}
DROPS = ("anvil", "piano", "pot")
FAIL_SETS = {
    "classic": (("banana", "pole", "rock"), "STICK FAILS", "banana"),
    "drops": (DROPS, "CARTOON DROPS", "anvil"),
    "rakes": (("rake",), "RAKE TRAP", "rake"),
    "wet": (("puddle", "banana"), "WET FLOOR", "puddle"),
}


def dizzy_stars(cv, head, t, color):
    for i in range(3):
        a = t * 5 + i * 2 * math.pi / 3
        c = (head[0] + 70 * math.cos(a), head[1] - 60 + 20 * math.sin(a))
        pts = []
        for k in range(10):  # 5-point star: alternate outer and inner radius
            r, b = (20 if k % 2 == 0 else 8), math.pi / 2 + k * math.pi / 5 + t * 3
            pts.append((c[0] + r * math.cos(b), c[1] - r * math.sin(b)))
        cv.poly(pts, color)


def banana(cv, c, rot):
    pts = []
    for i in range(11):
        a = math.radians(rot + 200 + i * 14)
        pts.append((c[0] + 45 * math.cos(a), c[1] + 45 * math.sin(a) + 30))
    cv.line(pts, "#ffd23f", 14)


def drop_object(cv, kind, c):
    """Anvil, piano or flower pot with its bottom center at c."""
    x, y = c
    if kind == "anvil":
        cv.poly([(x - 110, y - 60), (x + 130, y - 60), (x + 60, y - 30), (x + 60, y - 10), (x + 90, y),
                 (x - 90, y), (x - 60, y - 10), (x - 60, y - 30)], "#6b7080")
        cv.line([(x - 110, y - 60), (x + 130, y - 60)], "#a4a9b8", 8)
    elif kind == "piano":
        cv.rect((x - 150, y - 180, x + 150, y), fill="#16161e", outline="#555566", width=4, radius=8)
        cv.rect((x - 130, y - 110, x + 130, y - 70), fill="#f2f2f2")
        for i in range(13):
            kx = x - 125 + i * 20
            cv.line([(kx, y - 110), (kx, y - 70)], "#16161e", 3, caps=False)
    else:
        cv.poly([(x - 60, y - 90), (x + 60, y - 90), (x + 42, y), (x - 42, y)], "#c8643c")
        for dx in (-30, 0, 30):
            cv.line([(x + dx, y - 90), (x + dx * 1.6, y - 170)], "#3fbf5f", 8)
            cv.circle((x + dx * 1.6, y - 175), 18, fill="#ff6fa8")


def stick_fail(rng, pal, dur, kind="classic"):
    gag_names, title, dodge = FAIL_SETS[kind]
    hue = rng.random()
    finale = 4.2
    walk_in = (SPOT + 150) / WALK_SPEED
    gag_len = walk_in + 3.6
    n = max(1, int((dur - finale) / gag_len))
    order = list(gag_names)
    rng.shuffle(order)
    gags = [(i * gag_len, order[i % len(order)], Figure(pal.at(hue + i * 0.29), height=500)) for i in range(n)]
    fin_t = n * gag_len
    fin_fig = Figure(pal.at(hue + n * 0.29), height=500)

    def prop(cv, name, k, fig):
        """Draw the obstacle; k is seconds into the gag."""
        if name == "banana":
            if k < walk_in:
                c, rot = (SPOT + 40, GROUND - 14), 0.0
            else:
                u = clamp((k - walk_in) / 1.0)
                c, rot = parabola((SPOT + 40, GROUND - 14), (SPOT + 330, GROUND - 14), 330, ease_out(u)), 720 * u
            banana(cv, c, rot)
        elif name == "pole":
            cv.line([(SPOT + 70, GROUND), (SPOT + 70, GROUND - 720)], pal.dim(0.0, 0.7), 18)
            cv.line([(SPOT + 70, GROUND - 720), (SPOT + 190, GROUND - 720)], pal.dim(0.0, 0.7), 14)
            cv.circle((SPOT + 190, GROUND - 690), 34, fill="#ffe8a3")
        elif name == "rock":
            cv.poly([(SPOT - 10, GROUND), (SPOT + 20, GROUND - 60), (SPOT + 80, GROUND - 70), (SPOT + 120, GROUND)],
                    pal.dim(0.6, 0.6))
        elif name == "rake":
            pivot = (SPOT + 40, GROUND - 8)
            u = clamp((k - walk_in) / 0.3) if k > walk_in else 0.0
            back = clamp((k - walk_in - 0.8) / 0.5)
            ang = math.radians(lerp(0, 118, ease_out(u)) * (1 - smooth(back)))
            tip = (pivot[0] + 470 * math.cos(ang), pivot[1] - 470 * math.sin(ang))
            cv.line([pivot, tip], "#c98a4b", 12)
            for i in range(6):
                tx = pivot[0] - 20 + i * 10
                cv.line([(tx - 30, GROUND), (tx - 30, GROUND - 26)], "#b8bcc8", 5)
            cv.line([(pivot[0] - 55, GROUND - 26), (pivot[0] + 5, GROUND - 26)], "#b8bcc8", 7)
        elif name == "puddle":
            cv.ellipse((SPOT + 40, GROUND + 4), 170, 18, blend("#6fc3ff", pal.background[0], 0.35))
            sx = SPOT + 300
            cv.poly([(sx - 60, GROUND), (sx, GROUND - 190), (sx + 60, GROUND)], "#ffd23f")
            cv.text((sx, GROUND - 70), "!", 80, "#222222")
        elif name in DROPS:
            hit = walk_in + GAGS[name][4]
            if k < hit:  # falls from the sky, its shadow growing underneath
                u = clamp((k - walk_in + 0.35) / (GAGS[name][4] + 0.35))
                y = lerp(-200, GROUND - fig.h - 10, u * u)
                cv.ellipse((SPOT, GROUND + 6), 60 + 90 * u, 10 + 6 * u, blend(pal.background[1], "#000000", 0.6))
                if u > 0:
                    drop_object(cv, name, (SPOT, y))
            else:
                v = clamp((k - hit - 0.9) / 0.5)  # rests on the squashed figure, then slides off
                y = lerp(GROUND - fig.h * 0.4, GROUND, v)
                drop_object(cv, name, (SPOT + 260 * smooth(v), y))

    def gag(cv, t, name, fig):
        word, fall_rot, fall_pose, slide, hit_at = GAGS[name]
        looking = name == "pole"
        if t < walk_in:  # stroll in
            prop(cv, name, t, fig)
            x = -150 + WALK_SPEED * t
            p = walk(x / 170)
            if looking:
                p.update(PHONE, head=15)
            J = fig.place(p, x)
            shadow(cv, pal, x)
            fig.draw(cv, J)
            if looking:
                cv.rect((J["rhand"][0] - 6, J["rhand"][1] - 40, J["rhand"][0] + 22, J["rhand"][1] + 6),
                        fill="#dfe7ff", radius=4)
            return
        k = t - walk_in
        x0 = -150 + WALK_SPEED * walk_in
        x_end = x0 + slide
        stars_on = False
        if name in DROPS:
            prop(cv, name, t, fig)
            if k < hit_at:
                p, sy = mix(walk(x0 / 170), LOOK_UP, smooth(k / 0.3)), 1.0
            elif k < hit_at + 1.2:
                p, sy = LOOK_UP, lerp(1.0, 0.3, ease_out((k - hit_at) / 0.08))
                stars_on = True
            elif k < hit_at + 1.6:  # pop back up with a wobble
                u = (k - hit_at - 1.2) / 0.4
                p, sy = STAND, 1 + 0.25 * math.sin(u * math.pi * 3) * (1 - u)
                stars_on = True
            else:
                u = k - hit_at - 1.6
                p, sy = walk(u * 2, 0.8), 1.0
                x0 += WALK_SPEED * 0.8 * u
            J = squash(fig.place(p, x0), GROUND, sy)
            shadow(cv, pal, x0, 110)
            fig.draw(cv, J)
            if stars_on:
                dizzy_stars(cv, J["head"], k, "#ffe066")
            if 0 <= k - hit_at < 0.7:
                burst(cv, (SPOT, GROUND - fig.h * 0.4), k - hit_at, pal.at(hue + 0.15, 1.2), seed=int(t * 3), n=14,
                      size=140, life=0.5)
                cv.text((W / 2, 620), word, 120 * (0.7 + 0.3 * ease_out((k - hit_at) / 0.2)), pal.at(hue + 0.1, 1.2))
            return
        prop(cv, name, t, fig)
        fail_len = 1.4 if name == "puddle" else 0.7
        if name == "puddle" and k < 0.8:  # legs windmill on the wet floor
            x, lift, rot = x0 + 30 * k, 30 * abs(math.sin(k * 14)), 0.0
            p = dict(walk(k * 5, 1.4), lu=-150 + 40 * math.sin(k * 20), ru=150, lean=-10)
        elif k < fail_len:  # the fail
            u = (k - (0.8 if name == "puddle" else 0)) / 0.7
            x = lerp(x0, x_end, ease_out(u))
            lift = {"pole": 120, "rock": 140, "rake": 110}.get(name, 230) * 4 * u * (1 - u)
            p = mix(mix(walk(x0 / 170), FLAIL, smooth(u * 2)), fall_pose, smooth((u - 0.5) * 2))
            rot = fall_rot * smooth(u)
        elif k < 2.3 + (fail_len - 0.7):  # lying there, seeing stars
            x, p, rot, lift = x_end, fall_pose, fall_rot, 0.0
            rise = 1.7 + (fail_len - 0.7)
            if k > rise:
                u = (k - rise) / 0.6
                p, rot = mix(fall_pose, DIZZY_SITUP, smooth(u)), fall_rot * (1 - smooth(u))
            stars_on = True
        else:  # get up and limp away
            u = k - 2.3 - (fail_len - 0.7)
            up = smooth(u / 0.5)
            x = x_end + (WALK_SPEED * 0.8) * max(0.0, u - 0.5)
            p, rot, lift = mix(DIZZY_SITUP, walk(x / 170, 0.8), up), 0.0, 0.0
        J = fig.place(p, x, lift=lift, rot=rot)
        shadow(cv, pal, J["hip"][0], 120, air=lift)
        fig.draw(cv, J)
        if stars_on or 0.35 <= k < fail_len:
            dizzy_stars(cv, J["head"], k, "#ffe066")
        if 0 <= k - hit_at < 0.7:
            where = (SPOT + 40, GROUND - 480) if name in ("pole", "rake") else (J["hip"][0], GROUND - 60)
            burst(cv, where, k - hit_at, pal.at(hue + 0.15, 1.2), seed=int(t * 3), n=12, size=110, life=0.5)
            cv.text((W / 2, 620), word, 120 * (0.7 + 0.3 * ease_out((k - hit_at) / 0.2)), pal.at(hue + 0.1, 1.2))

    def finale_beat(cv, k, fig):
        """The last one spots the trap and dodges it."""
        jump_at = (SPOT - 170 + 150) / WALK_SPEED
        if dodge == "banana":
            banana(cv, (SPOT + 40, GROUND - 14), 0)
        elif dodge in DROPS:
            drop_object(cv, dodge, (SPOT + 40, GROUND))
        else:
            prop(cv, dodge, 0, fig)
        if k < jump_at:
            x = -150 + WALK_SPEED * k
            p, lift = walk(x / 170), 0.0
        elif k < jump_at + 0.8:
            u = (k - jump_at) / 0.8
            x = lerp(SPOT - 170, SPOT + 260, u)
            lift = (330 if dodge in DROPS else 220) * 4 * u * (1 - u)
            p = mix(walk(x / 170), pose(lt=60, ls=100, rt=-30, rs=60, lu=-140, lf=20, ru=140, rf=20),
                    math.sin(math.pi * u))
        else:
            u = k - jump_at - 0.8
            x = SPOT + 260
            lift = 50 * abs(math.sin(u * 6)) if u > 0.5 else 0.0
            p = mix(STAND, CHEER, smooth(u / 0.5))
        shadow(cv, pal, x, 110, air=lift)
        fig.draw(cv, fig.place(p, x, lift=lift))
        if k > jump_at + 0.9:
            cv.text((W / 2, 620), "NOT TODAY!", 110, pal.at(hue + 0.4, 1.2))

    def draw(cv, t):
        stars(cv, 21, 40)
        cv.line([(90, GROUND - 90), (300, GROUND - 90)], pal.dim(0.3, 0.4), 14)  # park bench
        cv.line([(110, GROUND - 90), (110, GROUND)], pal.dim(0.3, 0.4), 10)
        cv.line([(280, GROUND - 90), (280, GROUND)], pal.dim(0.3, 0.4), 10)
        for bx in (880, 990):
            cv.circle((bx, GROUND - 60), 70, fill=pal.dim(0.5, 0.2))
        floor(cv, pal)
        if t < fin_t:
            i = min(n - 1, int(t / gag_len))
            start, name, fig = gags[i]
            gag(cv, t - start, name, fig)
            label(cv, f"FAIL #{i + 1}", pal, y=430, size=70)
        else:
            finale_beat(cv, t - fin_t, fin_fig)
            label(cv, title, pal, y=430, size=70)

    return draw


# -- prank wars ------------------------------------------------------------------------

SIT = pose(lean=10, lt=88, ls=92, rt=86, rs=90, lu=20, lf=60, ru=20, rf=60)
FLOOR_SIT = dict(SIT, lt=80, ls=20, rt=75, rs=30, lean=-20, lu=-40, lf=20, ru=40, rf=20)
LAUGH = pose(lean=-22, head=-25, lu=20, lf=110, ru=30, rf=110, lt=8, rt=-8)
SNEAK = pose(lean=25, lt=30, ls=60, rt=-20, rs=40, lu=60, lf=90, ru=70, rf=90)
SCARE = pose(lt=30, ls=20, rt=-20, rs=20, lu=-150, lf=40, ru=150, rf=40, lean=-10)
STARTLED = pose(lt=40, ls=60, rt=-40, rs=60, lu=-160, lf=20, ru=160, rf=20, head=-20)


def prank_wars(rng, pal, dur):
    hue = rng.random()
    A = Figure(pal.at(hue), height=500)
    B = Figure(pal.at(hue + 0.5), height=500)
    finale = 2.5
    round_len = 5.0
    rounds = max(1, int((dur - finale) / round_len))
    kinds = ["chair", "boo"]
    first = rng.randint(0, 1)
    plan = [(kinds[(i + first) % 2], "AB"[i % 2]) for i in range(rounds)]
    chair_x = 600

    def chair(cv, x):
        cv.line([(x - 60, GROUND - 170), (x + 60, GROUND - 170)], pal.dim(0.6, 0.8), 12)
        cv.line([(x + 60, GROUND - 170), (x + 60, GROUND - 330)], pal.dim(0.6, 0.8), 12)
        for lx in (x - 55, x + 55):
            cv.line([(lx, GROUND - 170), (lx, GROUND)], pal.dim(0.6, 0.8), 9)

    def draw(cv, t):
        stars(cv, 9, 30)
        floor(cv, pal)
        i = min(rounds - 1, int(t / round_len))
        kind, prankster = plan[i]
        P, V = (A, B) if prankster == "A" else (B, A)
        k = t - i * round_len
        if t >= rounds * round_len:  # truce: high five
            k = t - rounds * round_len
            u = smooth(k / 0.6)
            pa = mix(STAND, pose(ru=150, rf=10), u)
            A.draw(cv, A.place(pa, lerp(300, 450, u)))
            B.draw(cv, B.place(pa, lerp(780, 630, u), facing=-1))
            if k > 0.6:
                burst(cv, (540, GROUND - 560), k - 0.6, pal.at(hue + 0.2, 1.2), n=14, size=110, life=0.5)
            label(cv, "TRUCE!", pal, y=430, size=80)
            return
        if kind == "chair":
            # victim walks to the chair and sits; prankster yanks it away just in time
            yank = 2.0
            cx = chair_x + (220 * ease_out((k - yank) / 0.3) if k > yank else 0)
            chair(cv, cx)
            vx = lerp(200, chair_x - 10, smooth(k / 1.4))
            if k < 1.4:
                pv, rot = walk(vx / 170), 0.0
            elif k < yank + 0.1:
                pv, rot = mix(STAND, SIT, smooth((k - 1.4) / 0.6)), 0.0
            elif k < 4.0:
                pv, rot = FLOOR_SIT, -10 * math.sin(clamp((k - yank) / 0.3) * math.pi)
            else:
                pv, rot = mix(FLOOR_SIT, STAND, smooth(k - 4.0)), 0.0
            V.draw(cv, V.place(pv, vx, rot=rot))
            px = chair_x + 170 + (140 * ease_out((k - yank) / 0.3) if k > yank else 0)
            pp = LAUGH if k > yank + 0.3 else SNEAK
            if k > yank + 0.3:
                pp = dict(LAUGH, lean=-22 + 8 * math.sin(k * 25))
            P.draw(cv, P.place(pp, px, facing=-1))
            if 0 <= k - yank - 0.1 < 0.7:
                burst(cv, (vx, GROUND - 40), k - yank - 0.1, pal.at(hue + 0.15, 1.2), n=12, size=100)
                cv.text((W / 2, 620), "THUD!", 120, pal.at(hue + 0.1, 1.2))
            if k > yank + 0.4:
                cv.text((min(px, W - 140), GROUND - 620), "HA HA!", 60, P.color)
        else:
            # prankster hides behind a box and jumps out; victim leaps out of their skin
            boo = 1.8
            vx = lerp(150, 470, smooth(k / boo))
            if k < boo:
                pv, lift = walk(vx / 170), 0.0
            else:
                u = k - boo
                lift = 280 * math.sin(math.pi * clamp(u / 0.7))
                pv = STARTLED if u < 0.7 else walk(u * 3, 1.3)
                vx = 470 - (0 if u < 0.7 else 700 * (u - 0.7))
            V.draw(cv, V.place(pv, vx, lift=lift, facing=1 if k < boo + 0.7 else -1))
            pop = smooth((k - boo + 0.2) / 0.2)
            pp = mix(pose(lean=40, lt=60, ls=110, rt=60, rs=110), SCARE, pop)
            if k > boo + 1.0:
                pp = dict(LAUGH, lean=-22 + 8 * math.sin(k * 25))
            J = P.place(pp, 740, ground=GROUND, lift=0, facing=-1)
            J = {kk: (v if kk.endswith("_angle") else (v[0], v[1] + 200 * (1 - pop))) for kk, v in J.items()}
            P.draw(cv, J)
            cv.rect((620, GROUND - 260, 860, GROUND), fill=pal.dim(0.1, 0.45), outline=pal.at(0.1, 0.8), width=6,
                    radius=8)
            if 0 <= k - boo < 0.8:
                cv.text((W / 2, 620), "BOO!", 140 * (0.7 + 0.3 * ease_out((k - boo) / 0.2)), pal.at(hue + 0.1, 1.2))
        label(cv, f"PRANK #{i + 1}", pal, y=430, size=70)

    return draw
