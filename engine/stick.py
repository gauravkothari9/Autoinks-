"""2D stick-figure toolkit: palettes, a drawing canvas, a posable skeleton and animation helpers.

Coordinates are logical pixels on a 1080x1920 canvas, (0, 0) top-left, y pointing down.
Every scene redraws the whole frame from scratch at time t, so animation is a pure
function of time and the seed.

Pose angles are in degrees, for a figure facing right (facing=-1 mirrors it):
    lean      torso tilt, + forward
    head      extra head tilt, + forward
    lt, rt    left/right thigh from straight down, + forward
    ls, rs    left/right knee bend (shin swings back), usually >= 0
    lu, ru    left/right upper arm from straight down (along the torso), + forward, 180 = up
    lf, rf    left/right elbow bend (forearm swings forward/up), usually >= 0
The "left" limbs are drawn behind the body in a darker shade, which gives the figure depth.
"""

import colorsys
import math
import random

from PIL import ImageDraw, ImageFont

W, H = 1080, 1920
GROUND = 1440  # default floor line

PALETTES = {
    "Neon Dream": (["#ff00c8", "#7b2cff", "#00e5ff", "#00ff95"], ("#0b0420", "#02010a")),
    "Sunset Blaze": (["#ff4e50", "#fc913a", "#f9d423", "#ff2e97"], ("#1a0619", "#050108")),
    "Aurora": (["#00f5a0", "#00d9f5", "#7f5af0", "#2cb67d"], ("#03121b", "#010608")),
    "Cyberpunk": (["#f72585", "#b5179e", "#7209b7", "#4361ee", "#4cc9f0"], ("#0a0118", "#000000")),
    "Royal Gold": (["#ffd166", "#ffb703", "#fb8500", "#ffe8a3"], ("#140c02", "#030201")),
    "Deep Ocean": (["#00b4d8", "#48cae4", "#90e0ef", "#0077b6", "#caf0f8"], ("#020b18", "#00040a")),
    "Rainbow": ([
        "#%02x%02x%02x" % tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h / 7, 0.85, 1))
        for h in range(7)
    ], ("#0d0d14", "#020203")),
    "Candy Pop": (["#ff99c8", "#fcf6bd", "#d0f4de", "#a9def9", "#e4c1f9"], ("#140a1c", "#05030a")),
    "Inferno": (["#ff0a54", "#ff5400", "#ffbd00", "#ff477e"], ("#160304", "#030001")),
}


def hex_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def shade(color, k):
    """Scale a hex color's brightness (k < 1 darker, k > 1 lighter)."""
    return rgb_hex(c * k for c in hex_rgb(color))


def blend(a, b, u):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex(x + (y - x) * u for x, y in zip(ra, rb))


class Palette:
    def __init__(self, name):
        self.name = name
        self.colors, self.background = PALETTES[name]
        self.rgb = [hex_rgb(c) for c in self.colors]

    def at(self, x, k=1.0):
        """Cyclic gradient lookup; x wraps every 1.0."""
        x = (x % 1.0) * len(self.rgb)
        i = int(x)
        f = x - i
        a, b = self.rgb[i], self.rgb[(i + 1) % len(self.rgb)]
        return rgb_hex((a[j] + (b[j] - a[j]) * f) * k for j in range(3))

    def dim(self, x, k=0.35):
        """A palette color pushed toward the background, for scenery."""
        return blend(self.background[0], self.at(x), k)


# -- easing and math ---------------------------------------------------------

def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def lerp(a, b, u):
    return a + (b - a) * u


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = clamp(u)
    return u ** 3


def seg(u, a, b):
    """Local 0..1 progress of u inside [a, b]."""
    return clamp((u - a) / (b - a)) if b > a else float(u >= b)


def parabola(p0, p1, height, u):
    """Point on a jump/throw arc from p0 to p1 peaking `height` px above the straight line."""
    return (lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) - 4 * height * u * (1 - u))


# -- poses ---------------------------------------------------------------------

POSE_KEYS = ("lean", "head", "lt", "ls", "rt", "rs", "lu", "lf", "ru", "rf")
STAND = dict(lean=0, head=0, lt=4, ls=2, rt=-4, rs=2, lu=8, lf=12, ru=-8, rf=12)


def pose(base=None, **kw):
    p = dict(STAND if base is None else base)
    p.update(kw)
    return p


def mix(a, b, u):
    """Blend two poses. Extra numeric keys (x offset, lift, rot, prop angles...) blend too, default 0."""
    keys = set(POSE_KEYS) | set(a) | set(b)
    return {k: lerp(a.get(k, STAND.get(k, 0)), b.get(k, STAND.get(k, 0)), u) for k in keys}


def keyframes(frames, t, ease=smooth):
    """frames: [(time, pose), ...] sorted by time. Returns the eased pose at time t."""
    if t <= frames[0][0]:
        return dict(frames[0][1])
    for (t0, a), (t1, b) in zip(frames, frames[1:]):
        if t <= t1:
            return mix(a, b, ease((t - t0) / (t1 - t0)) if t1 > t0 else 1)
    return dict(frames[-1][1])


def walk(phase, speed=1.0):
    """Walk cycle; phase counts steps (1.0 = one full left+right stride)."""
    w = 2 * math.pi * phase
    a = 26 * speed
    s = math.sin(w)
    return dict(lean=4 * speed, head=0,
                lt=a * s, ls=6 + 38 * max(0.0, math.cos(w)),
                rt=-a * s, rs=6 + 38 * max(0.0, -math.cos(w)),
                lu=-24 * speed * s, lf=18, ru=24 * speed * s, rf=18)


def run(phase):
    w = 2 * math.pi * phase
    s = math.sin(w)
    return dict(lean=16, head=-4,
                lt=48 * s, ls=18 + 85 * max(0.0, math.cos(w)),
                rt=-48 * s, rs=18 + 85 * max(0.0, -math.cos(w)),
                lu=-55 * s + 10, lf=95, ru=55 * s + 10, rf=95)


def run_lift(phase, height=18):
    """Small airborne bounce twice per stride."""
    return height * abs(math.sin(2 * math.pi * phase))


# -- canvas ------------------------------------------------------------------

_FONTS = {}


def font(size):
    size = max(8, int(size))
    if size not in _FONTS:
        for name in ("seguibl.ttf", "arialbd.ttf", "seguisb.ttf", "DejaVuSans-Bold.ttf"):
            try:
                _FONTS[size] = ImageFont.truetype(name, size)
                break
            except OSError:
                continue
        else:
            _FONTS[size] = ImageFont.load_default()
    return _FONTS[size]


class Canvas:
    """Thin ImageDraw wrapper in logical coordinates with an optional camera offset."""

    def __init__(self, img, scale):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.s = scale
        self.cam = (0.0, 0.0)

    def P(self, p):
        return ((p[0] - self.cam[0]) * self.s, (p[1] - self.cam[1]) * self.s)

    def line(self, pts, color, width, caps=True):
        pts = [self.P(p) for p in pts]
        w = max(1, round(width * self.s))
        self.d.line(pts, fill=color, width=w, joint="curve")
        if caps and w >= 3:
            r = w / 2
            for x, y in pts:
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def circle(self, c, r, fill=None, outline=None, width=0):
        x, y = self.P(c)
        r *= self.s
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline,
                       width=max(1, round(width * self.s)) if outline else 0)

    def ellipse(self, c, rx, ry, fill):
        x, y = self.P(c)
        self.d.ellipse((x - rx * self.s, y - ry * self.s, x + rx * self.s, y + ry * self.s), fill=fill)

    def poly(self, pts, fill):
        self.d.polygon([self.P(p) for p in pts], fill=fill)

    def rect(self, box, fill=None, outline=None, width=0, radius=0):
        (x0, y0), (x1, y1) = self.P(box[:2]), self.P(box[2:])
        if x1 <= x0 or y1 <= y0:
            return
        self.d.rounded_rectangle((x0, y0, x1, y1), radius=radius * self.s, fill=fill, outline=outline,
                                 width=max(1, round(width * self.s)) if outline else 0)

    def text(self, c, text, size, color, anchor="mm"):
        self.d.text(self.P(c), text, font=font(size * self.s), fill=color, anchor=anchor)


# -- the figure --------------------------------------------------------------

def _dir(a, f):
    r = math.radians(a)
    return (f * math.sin(r), math.cos(r))


def _add(p, v, k):
    return (p[0] + v[0] * k, p[1] + v[1] * k)


class Figure:
    def __init__(self, color, height=620, far_shade=0.62, feet=True, head="circle"):
        self.color = color
        self.head = head  # "circle", or "box" for robots
        self.far = shade(color, far_shade)
        self.h = height
        self.width = height * 0.038
        self.feet = feet
        u = height
        self.T, self.N, self.R = 0.30 * u, 0.035 * u, 0.085 * u
        self.Lt, self.Ls, self.Lu, self.Lf = 0.25 * u, 0.25 * u, 0.17 * u, 0.17 * u

    def joints(self, p, x=0.0, y=0.0, facing=1, rot=0.0):
        """Joint positions for pose p with the hip at (x, y); rot spins the body about the hip (+ = forward)."""
        g = lambda k: p.get(k, STAND[k])  # noqa: E731
        f = facing
        hip = (0.0, 0.0)
        up = _dir(180 - g("lean"), f)
        J = {"hip": hip}
        J["neck"] = _add(hip, up, self.T)
        J["shoulder"] = _add(hip, up, self.T * 0.9)
        J["head"] = _add(J["neck"], _dir(180 - g("lean") - g("head"), f), self.N + self.R)
        for side in "lr":
            thigh, knee = g(side + "t"), g(side + "s")
            J[side + "knee"] = _add(hip, _dir(thigh, f), self.Lt)
            J[side + "ankle"] = _add(J[side + "knee"], _dir(thigh - knee, f), self.Ls)
            J[side + "toe"] = _add(J[side + "ankle"], _dir(thigh - knee + 90, f), self.h * 0.06)
            upper = g(side + "u") + g("lean")
            fore = upper + g(side + "f")
            J[side + "elbow"] = _add(J["shoulder"], _dir(upper, f), self.Lu)
            J[side + "hand"] = _add(J[side + "elbow"], _dir(fore, f), self.Lf)
            J[side + "fore_angle"] = fore  # for props held in the hand
        rad = math.radians(rot * f)
        c, s = math.cos(rad), math.sin(rad)
        out = {}
        for k, v in J.items():
            if k.endswith("_angle"):
                out[k] = v + rot
            else:
                out[k] = (x + v[0] * c - v[1] * s, y + v[0] * s + v[1] * c)
        return out

    def lowest(self, p, facing=1, rot=0.0):
        J = self.joints(p, 0, 0, facing, rot)
        ys = [v[1] for k, v in J.items() if not k.endswith("_angle")]
        ys.append(J["head"][1] + self.R)
        return max(ys) + self.width / 2

    def place(self, p, x, ground=GROUND, lift=0.0, facing=1, rot=0.0):
        """Joints for pose p standing on `ground` (lift raises it into the air)."""
        y = ground - self.lowest(p, facing, rot) - lift
        return self.joints(p, x, y, facing, rot)

    def anchor(self, p, key, point, facing=1, rot=0.0):
        """Joints for pose p moved so joint `key` sits at `point` (e.g. hands gripping a bar)."""
        J = self.joints(p, 0, 0, facing, rot)
        dx, dy = point[0] - J[key][0], point[1] - J[key][1]
        return {k: (v if k.endswith("_angle") else (v[0] + dx, v[1] + dy)) for k, v in J.items()}

    def draw(self, cv, J, color=None, far=None):
        color = color or self.color
        far = far or self.far
        w = self.width

        def limb(side, col):
            cv.line([J["shoulder"], J[side + "elbow"], J[side + "hand"]], col, w)
            leg = [J["hip"], J[side + "knee"], J[side + "ankle"]] + ([J[side + "toe"]] if self.feet else [])
            cv.line(leg, col, w)

        limb("l", far)
        cv.line([J["hip"], J["neck"]], color, w * 1.08)
        if self.head == "box":
            hx, hy = J["head"]
            cv.rect((hx - self.R, hy - self.R, hx + self.R, hy + self.R), fill=color, radius=self.R * 0.3)
        else:
            cv.circle(J["head"], self.R, fill=color)
        limb("r", color)
        return J

    def pose_at(self, cv, p, x, ground=GROUND, lift=0.0, facing=1, rot=0.0, color=None):
        return self.draw(cv, self.place(p, x, ground, lift, facing, rot), color)


# -- scenery and effects -----------------------------------------------------

def floor(cv, pal, y=GROUND, x0=-2000, x1=4000, k=0.55):
    cv.line([(x0, y), (x1, y)], pal.dim(0.1, k), 6, caps=False)


def shadow(cv, pal, x, width=110, y=GROUND, air=0.0):
    k = clamp(1 - air / 500, 0.25, 1)
    cv.ellipse((x, y + 8), width * k, 10 * k, blend(pal.background[1], "#000000", 0.6))


def stars(cv, seed, n=60, color="#ffffff", top=320, bottom=1250, parallax=0.0):
    r = random.Random(seed)
    for _ in range(n):
        x = r.uniform(0, W * 2) - cv.cam[0] * parallax
        x = (x % (W + 40)) - 20 + cv.cam[0]
        y = r.uniform(top, bottom)
        cv.circle((x, y), r.uniform(1.2, 3.2), fill=blend(color, "#000000", r.uniform(0.55, 0.85)))


def burst(cv, center, age, color, seed=0, n=12, size=90, life=0.45, width=6):
    """Radiating spark lines for impacts; age in seconds since the hit."""
    if not 0 <= age < life:
        return
    u = age / life
    r = random.Random(seed)
    for i in range(n):
        a = 2 * math.pi * (i + r.random() * 0.6) / n
        d0 = size * (0.25 + 0.8 * ease_out(u))
        d1 = d0 + size * 0.55 * (1 - u) * r.uniform(0.6, 1.2)
        v = (math.cos(a), math.sin(a))
        cv.line([_add(center, v, d0), _add(center, v, d1)], color, width * (1 - u * 0.6))


def speed_lines(cv, color, t, y0=500, y1=1300, n=10, seed=3, speed=2600, length=220):
    r = random.Random(seed)
    for _ in range(n):
        y = r.uniform(y0, y1)
        x = (r.uniform(0, W + 600) - t * speed * r.uniform(0.7, 1.3)) % (W + 600) - 300 + cv.cam[0]
        cv.line([(x, y), (x + length * r.uniform(0.5, 1.2), y)], color, 3)


def squash(J, ground, sy, sx=None):
    """Cartoon squash: scale a placed figure vertically toward the ground (sy < 1 flattens it)."""
    sx = sx if sx is not None else 1 + (1 - sy) * 0.6
    cx = J["hip"][0]
    return {k: (v if k.endswith("_angle") else (cx + (v[0] - cx) * sx, ground - (ground - v[1]) * sy))
            for k, v in J.items()}


def bezier(p0, c, p1, n=16):
    """Points on a quadratic curve from p0 to p1 bent toward c (ropes, strings, arcs)."""
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1]) for u in (i / n for i in range(n + 1))]


def pop_text(cv, text, center, age, color, life=0.6, size=86):
    """Comic-style word that pops in and drifts up, e.g. POW! at an impact."""
    if 0 <= age < life:
        s = size * (0.6 + 0.6 * ease_out(age / 0.15)) * (1 - 0.3 * (age / life))
        cv.text((center[0], center[1] - 40 - 60 * age), text, s, color)


def label(cv, text, pal, y=380, size=64, x=W / 2):
    cv.text((x, y), text, size, pal.at(0.15, 1.1))


class Timeline:
    """Back-to-back beats. Each beat is (duration, fn) with fn(u, t_local, dur)."""

    def __init__(self):
        self.beats = []
        self.total = 0.0

    def add(self, duration, fn, **info):
        self.beats.append((self.total, duration, fn, info))
        self.total += duration

    def at(self, t):
        for start, dur, fn, info in self.beats:
            if t < start + dur:
                return start, dur, fn, info
        return self.beats[-1]

    def play(self, cv, t):
        start, dur, fn, info = self.at(t)
        local = clamp(t - start, 0, dur)
        return fn(cv, local / dur if dur else 1.0, local, dur, **info)
