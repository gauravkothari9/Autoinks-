"""Drawing toolkit: palettes, a canvas, easing, vector shapes and backgrounds.

Coordinates are logical pixels on a 1080x1920 canvas, (0, 0) top-left, y pointing down.
Every scene redraws the whole frame at time t, so animation is a pure function of time and the seed.
"""

import colorsys
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920

# name: (accent colors, (background top, background bottom))
PALETTES = {
    "Pastel Dream": (["#ffadad", "#ffd6a5", "#fdffb6", "#caffbf", "#9bf6ff", "#bdb2ff"], ("#1b1726", "#0b0910")),
    "Sunset Glow": (["#ff7b54", "#ffb26b", "#ffd56b", "#e84a5f", "#a8336a"], ("#2a1124", "#0d0509")),
    "Ocean Breeze": (["#00a8e8", "#48cae4", "#90e0ef", "#0077b6", "#00f5d4"], ("#04142a", "#01070f")),
    "Forest Walk": (["#2d6a4f", "#52b788", "#95d5b2", "#d8f3dc", "#e9c46a"], ("#0b1a12", "#030806")),
    "Candy Shop": (["#ff70a6", "#ff9770", "#ffd670", "#e9ff70", "#70d6ff"], ("#1d0d1f", "#08040a")),
    "Autumn Leaves": (["#9c2c2c", "#d1495b", "#edae49", "#f4a259", "#5b8e7d"], ("#1f120b", "#080403")),
    "Neon Night": (["#ff00c8", "#7b2cff", "#00e5ff", "#00ff95", "#ffe600"], ("#0b0420", "#02010a")),
    "Royal Gold": (["#ffd166", "#ffb703", "#fb8500", "#ffe8a3", "#c77dff"], ("#140c02", "#030201")),
    "Rainbow": ([
        "#%02x%02x%02x" % tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h / 7, 0.75, 1))
        for h in range(7)
    ], ("#0d0d14", "#020203")),
}


def hex_rgb(color):
    if isinstance(color, tuple):
        return color[:3]
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def rgba(color, alpha=255):
    return (*hex_rgb(color), int(alpha))


def shade(color, k):
    """Scale a hex color's brightness (k < 1 darker, k > 1 lighter)."""
    return rgb_hex(c * k for c in hex_rgb(color))


def blend(a, b, u):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex(x + (y - x) * u for x, y in zip(ra, rb))


def hsv(h, s, v):
    return rgb_hex(c * 255 for c in colorsys.hsv_to_rgb(h % 1.0, clamp(s), clamp(v)))


def jitter(color, rng, amount=0.06):
    """The same color nudged in hue and brightness, so each video differs slightly."""
    r, g, b = (c / 255 for c in hex_rgb(color))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return hsv(h + rng.uniform(-amount, amount) * 0.5, s * rng.uniform(0.9, 1.08), v * rng.uniform(0.93, 1.05))


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
        """A palette color pushed toward the background."""
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


def wave(t, period, phase=0.0):
    return math.sin(2 * math.pi * (t / period + phase))


# -- fonts and canvas -----------------------------------------------------------

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
    """ImageDraw wrapper in logical coordinates. Colors may be hex strings or RGBA tuples (alpha blends)."""

    def __init__(self, img, scale):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.s = scale

    def P(self, p):
        return (p[0] * self.s, p[1] * self.s)

    def line(self, pts, color, width, caps=True):
        pts = [self.P(p) for p in pts]
        w = max(1, round(width * self.s))
        self.d.line(pts, fill=color, width=w, joint="curve")
        if caps and w >= 3:
            r = w / 2
            for x, y in (pts[0], pts[-1]):
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def circle(self, c, r, fill=None, outline=None, width=0):
        x, y = self.P(c)
        r *= self.s
        if r <= 0:
            return
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline,
                       width=max(1, round(width * self.s)) if outline else 0)

    def ellipse(self, c, rx, ry, fill):
        x, y = self.P(c)
        self.d.ellipse((x - rx * self.s, y - ry * self.s, x + rx * self.s, y + ry * self.s), fill=fill)

    def poly(self, pts, fill, outline=None, width=0):
        self.d.polygon([self.P(p) for p in pts], fill=fill)
        if outline:
            self.line(list(pts) + [pts[0]], outline, width)

    def rect(self, box, fill=None, outline=None, width=0, radius=0):
        (x0, y0), (x1, y1) = self.P(box[:2]), self.P(box[2:])
        if x1 <= x0 or y1 <= y0:
            return
        self.d.rounded_rectangle((x0, y0, x1, y1), radius=radius * self.s, fill=fill, outline=outline,
                                 width=max(1, round(width * self.s)) if outline else 0)

    def text(self, c, text, size, color, anchor="mm"):
        self.d.text(self.P(c), text, font=font(size * self.s), fill=color, anchor=anchor)


# -- vector shapes (lists of points) -------------------------------------------------

def circle(c, r, n=None, a0=0.0):
    n = n or max(28, int(r * 0.45))
    return [(c[0] + r * math.cos(a0 + 2 * math.pi * i / n), c[1] + r * math.sin(a0 + 2 * math.pi * i / n))
            for i in range(n)]


def ellipse(c, rx, ry, rot=0.0, n=None, a0=0.0, a1=2 * math.pi):
    """Closed ellipse (or an open arc from a0 to a1, radians), rotated by rot degrees."""
    n = n or max(28, int((rx + ry) * 0.25))
    full = abs(a1 - a0 - 2 * math.pi) < 1e-9
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n if full else n + 1):
        a = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((c[0] + x * cr - y * sr, c[1] + x * sr + y * cr))
    return out


def cubic(p0, p1, p2, p3, n=20):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def quad(p0, c, p1, n=16):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p1[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p1[1]) for u in (i / n for i in range(n + 1))]


def spline(points, closed=True, per=10):
    """Catmull-Rom curve through the points: a smooth outline from a few control points."""
    pts = list(points)
    n = len(pts)
    out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed else pts[max(0, i - 1)]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed else pts[min(n - 1, i + 2)]
        for k in range(per):
            u = k / per
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in (0, 1)))
    if not closed:
        out.append(pts[-1])
    return out


def blob(rng, c, r, n=7, wobble=0.18, per=8):
    """Organic closed shape (bushes, clouds, rocks)."""
    a0 = rng.uniform(0, 2 * math.pi)
    pts = [(c[0] + r * (1 + rng.uniform(-wobble, wobble)) * math.cos(a0 + 2 * math.pi * i / n),
            c[1] + r * (1 + rng.uniform(-wobble, wobble)) * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]
    return spline(pts, True, per)


def cloud(c, w, h, bumps=4):
    """Flat-bottomed cartoon cloud: the top edge of a row of overlapping circles."""
    x0, x1, base = c[0] - w / 2, c[0] + w / 2, c[1] + h / 2
    circles = []
    for i in range(bumps):
        u = (i + 0.5) / bumps
        r = w / bumps * 0.62 * (0.7 + 0.6 * math.sin(math.pi * u))
        circles.append((lerp(x0 + r * 0.9, x1 - r * 0.9, u), base - r * 0.15, r))
    out = []
    for k in range(61):
        x = lerp(x0, x1, k / 60)
        tops = [cy - math.sqrt(r * r - (x - cx) ** 2) for cx, cy, r in circles if abs(x - cx) < r]
        out.append((x, min(min(tops, default=base), base)))
    return out


def move(pts, dx=0.0, dy=0.0):
    return [(x + dx, y + dy) for x, y in pts]


def transform(pts, origin=(0, 0), scale=1.0, rot=0.0, dx=0.0, dy=0.0, sx=None, sy=None):
    """Scale and rotate (degrees) around origin, then move."""
    sx = scale if sx is None else sx
    sy = scale if sy is None else sy
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    ox, oy = origin
    out = []
    for x, y in pts:
        x, y = (x - ox) * sx, (y - oy) * sy
        out.append((ox + x * c - y * s + dx, oy + x * s + y * c + dy))
    return out


def mirror(pts, x):
    return [(2 * x - px, py) for px, py in pts]


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def area(pts):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))) / 2


def densify(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        k = max(1, int(d / step))
        out += [(lerp(a[0], b[0], i / k), lerp(a[1], b[1], i / k)) for i in range(1, k + 1)]
    return out


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def star(c, r_out, r_in, n=5, rot=-90):
    out = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + 180 * i / n)
        out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return out


# -- backgrounds -------------------------------------------------------------------

def make_background(size, top, bottom):
    """Vertical gradient with a soft radial vignette."""
    w, h = size
    top, bottom = np.array(hex_rgb(top), float), np.array(hex_rgb(bottom), float)
    ys = np.linspace(0, 1, h)[:, None, None]
    grad = np.broadcast_to(top * (1 - ys) + bottom * ys, (h, w, 3)).copy()
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    vignette = np.clip(1.15 - 0.45 * dist, 0.55, 1.0)[..., None]
    return Image.fromarray(np.clip(grad * vignette, 0, 255).astype(np.uint8), "RGB")


def gradient(size, stops):
    """Vertical multi-stop gradient: stops = [(0.0, "#hex"), ..., (1.0, "#hex")]."""
    w, h = size
    ys = np.linspace(0, 1, h)
    pos = [p for p, _ in stops]
    cols = np.array([hex_rgb(c) for _, c in stops], float)
    rows = np.stack([np.interp(ys, pos, cols[:, j]) for j in range(3)], axis=1)
    return Image.fromarray(np.broadcast_to(rows[:, None, :], (h, w, 3)).astype(np.uint8), "RGB")


SHEET = (70, 330, 1010, 1650)  # the paper sheet on the desk, logical coordinates


def paper(size, scale, desk="#c9a27c", sheet="#fbf8f1", seed=0):
    """A sheet of textured paper with a soft shadow, lying on a plain desk."""
    w, h = size
    rnd = np.random.default_rng(seed)
    base = np.empty((h, w, 3), float)
    base[:] = hex_rgb(desk)
    # Gentle light falloff toward the corners of the desk.
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h * 0.48) / (h / 2)) ** 2)
    base *= np.clip(1.1 - 0.35 * dist, 0.6, 1.05)[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    x0, y0, x1, y1 = (v * scale for v in SHEET)
    shadow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 10 * scale, y0 + 18 * scale, x1 + 10 * scale, y1 + 18 * scale),
                                             radius=14 * scale, fill=120)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18 * scale))
    img.paste(Image.new("RGB", (w, h), (20, 12, 6)), (0, 0), shadow)
    sheet_rgb = np.empty((int(y1 - y0), int(x1 - x0), 3), float)
    sheet_rgb[:] = hex_rgb(sheet)
    grain = rnd.normal(0, 3.2, sheet_rgb.shape[:2])[..., None]
    sheet_rgb += grain
    sheet_img = Image.fromarray(np.clip(sheet_rgb, 0, 255).astype(np.uint8), "RGB")
    mask = Image.new("L", sheet_img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sheet_img.size[0] - 1, sheet_img.size[1] - 1), radius=12 * scale, fill=255)
    img.paste(sheet_img, (int(x0), int(y0)), mask)
    return img


def twinkle(cv, c, r, color, width=4):
    """Four-point sparkle."""
    if r <= 1:
        return
    cv.poly([(c[0], c[1] - r), (c[0] + r * 0.2, c[1] - r * 0.2), (c[0] + r, c[1]), (c[0] + r * 0.2, c[1] + r * 0.2),
             (c[0], c[1] + r), (c[0] - r * 0.2, c[1] + r * 0.2), (c[0] - r, c[1]), (c[0] - r * 0.2, c[1] - r * 0.2)], color)


class Cache:
    """Remembers images rendered once per output size (static scenery behind the animation)."""

    def __init__(self):
        self.store = {}

    def get(self, key, cv, build, opaque=False):
        """build(canvas) draws the layer once; opaque layers come back as RGB for a fast paste."""
        k = (key, cv.img.size)
        if k not in self.store:
            img = Image.new("RGBA", cv.img.size, (0, 0, 0, 0))
            build(Canvas(img, cv.s))
            self.store[k] = img.convert("RGB") if opaque else img
        return self.store[k]

    def paste(self, key, cv, build, opaque=False):
        img = self.get(key, cv, build, opaque)
        if opaque:
            cv.img.paste(img)
        else:
            cv.img.paste(img, (0, 0), img)


def soft(cv, draw, blur):
    """Draw onto a separate layer, blur it and blend it in (glows, mist, nebulas)."""
    layer = Image.new("RGBA", cv.img.size, (0, 0, 0, 0))
    draw(Canvas(layer, cv.s))
    layer = layer.filter(ImageFilter.GaussianBlur(blur * cv.s))
    if cv.img.mode == "RGBA":
        cv.img.alpha_composite(layer)
    else:
        cv.img.paste(layer, (0, 0), layer)


def rng_child(rng):
    return random.Random(rng.randrange(1 << 30))
