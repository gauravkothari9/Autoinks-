"""Speed-drawing engine: a picture is drawn on screen stroke by stroke, then colored in.

A picture is a list of items added back to front:
    sk.shape(pts, fill)        a closed shape: inked outline + colored fill, hides what is behind it
    sk.line(pts)               an ink line (whiskers, grass, details)
    sk.shade(pts, color)       a translucent shading or highlight fill on the shape just added
    sk.dot / sk.detail(...)    final touches drawn last (eye shine, sparkles)

Outlines hidden behind a front shape are clipped away up front, and every fill is masked by the
shapes in front of it, so the reveal order never breaks the layering.

The video plays four passes: ink outlines, color, shading, details. A pen, marker or brush
follows the stroke being drawn. The finished picture then gets a slow zoom and a few sparkles.

Every picture also gets a Variant (a mirrored layout, a hand-drawn warp, a color mood, a different
pen and paper), so the same style never comes out the same twice.
"""

import bisect
import colorsys
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from .art import (H, SHEET, W, Canvas, area, bbox, clamp, densify, ease_out, hex_rgb, length, lerp, paper, rgba,
                  rng_child, shade, smooth, twinkle)

INK = "#24212b"
PHASES = ("ink", "color", "shade", "detail")
LAYER = {"color": 0, "shade": 1, "ink": 2, "detail": 3}
# Relative speed of each pass (logical px of stroke per unit of time budget).
SPEED = {"ink": 1.0, "color": 1.0, "shade": 1.3, "detail": 1.0}


class Item:
    def __init__(self, kind, phase, depth, color, width=0.0, polys=None, poly=None, occludes=False,
                 together=False, tool="pen", clip=True):
        self.kind = kind          # "stroke" or "fill"
        self.phase = phase
        self.depth = depth
        self.color = color        # RGBA tuple
        self.width = width
        self.polys = polys or []  # stroke: list of polylines
        self.poly = poly          # fill: polygon
        self.occludes = occludes
        self.together = together  # stroke: draw all polylines at once (e.g. a growing tree level)
        self.tool = tool
        self.clip = clip


class Sketch:
    """Builder for one picture."""

    def __init__(self, rng, pal, desk=None, sheet=None, ink=None, ink_width=None):
        self.rng = rng
        self.pal = pal
        self.variant = Variant(rng_child(rng))
        self.desk = desk or rng.choice(["#c9a27c", "#b98b62", "#9fb4c7", "#c7b9a6", "#8fa98f", "#d8c3a5"])
        self.sheet = sheet or self.variant.sheet
        self.ink = ink or self.variant.ink
        self.ink_width = ink_width or self.variant.ink_width
        self.items = []
        self.depth = 0
        self.zoom = 1.06
        self.bounds = None  # (x0, y0, x1, y1): nothing is drawn outside this box (a picture frame)

    # -- building ------------------------------------------------------------------

    def shape(self, pts, fill=None, ink=True, width=None, occludes=True, outline=None):
        """Closed shape. fill=None leaves it uncolored (outline only, still hides what is behind)."""
        self.depth += 1
        pts = list(pts)
        if fill is not None:
            self.items.append(Item("fill", "color", self.depth, rgba(fill) if isinstance(fill, str) else fill,
                                   poly=pts, occludes=occludes, tool="marker"))
        elif occludes:
            self.items.append(Item("fill", "color", self.depth, (0, 0, 0, 0), poly=pts, occludes=True, tool=None))
        if ink:
            col = outline or self.ink
            self.items.append(Item("stroke", "ink", self.depth, rgba(col) if isinstance(col, str) else col,
                                   width or self.ink_width, polys=[pts + pts[:1]]))
        return pts

    def line(self, pts, color=None, width=None, phase="ink", together=False, tool="pen", new_depth=True):
        """An open ink line. Lines can be lists of polylines (drawn one after another, or all together)."""
        if new_depth:
            self.depth += 1
        polys = pts if pts and isinstance(pts[0][0], (tuple, list)) else [pts]
        col = color or self.ink
        self.items.append(Item("stroke", phase, self.depth, rgba(col) if isinstance(col, str) else col,
                               width or self.ink_width, polys=[list(p) for p in polys], together=together, tool=tool))

    def shade(self, pts, color, alpha=90, phase="shade"):
        """Translucent fill on top of the last shape (shadows, blush, highlights). Doesn't hide anything."""
        col = rgba(color, alpha) if isinstance(color, str) else color
        self.items.append(Item("fill", phase, self.depth, col, poly=list(pts), tool="brush"))

    def detail(self, pts, color, alpha=255):
        """Opaque final-touch fill drawn last (eye shine, stars)."""
        self.depth += 1
        self.items.append(Item("fill", "detail", self.depth, rgba(color, alpha) if isinstance(color, str) else color,
                               poly=list(pts), tool="brush"))

    def detail_line(self, pts, color, width=4):
        self.line(pts, color, width, phase="detail", tool="brush")

    # -- scene -----------------------------------------------------------------------

    def scene(self, duration, hold=3.0):
        self.variant.apply(self)
        return SketchScene(self, duration, hold)


class Variant:
    """Per-video changes applied on top of any finished picture.

    The warp is a smooth displacement field, so shapes that touch keep touching and the layering
    stays intact. It fades to nothing at the picture frame, so frames stay straight.
    """

    # name: (weight, how a color changes); h, s, v in 0..1
    MOODS = {
        "natural": (4, lambda h, s, v: (h, s, v)),
        "pastel": (2, lambda h, s, v: (h, s * 0.72, v + (1 - v) * 0.3)),
        "vivid": (2, lambda h, s, v: (h, s + (1 - s) * 0.25, v * 1.03)),
        "warm": (2, lambda h, s, v: (_toward(h, 0.08, 0.06), s * 1.05, v)),
        "cool": (2, lambda h, s, v: (_toward(h, 0.58, 0.06), s, v * 0.98)),
        "dusk": (1, lambda h, s, v: (_toward(h, 0.78, 0.07), s * 0.92, v * 0.86)),
        "dreamy": (1, None),  # whole picture hue-rotated; set up in __init__
    }

    def __init__(self, rng):
        self.mirror = rng.random() < 0.5
        self.waves = []
        for axis in (0, 1):
            for amp, lam in (((5, 12), (650, 1300)), ((5, 12), (650, 1300)), ((1.0, 2.2), (90, 180))):
                a, k = rng.uniform(*amp), 2 * math.pi / rng.uniform(*lam)
                th = rng.uniform(0, 2 * math.pi)
                self.waves.append((axis, a, k * math.cos(th), k * math.sin(th), rng.uniform(0, 2 * math.pi)))
        names = list(self.MOODS)
        self.mood = rng.choices(names, [self.MOODS[n][0] for n in names])[0]
        if self.mood == "dreamy":
            turn = rng.choice((-1, 1)) * rng.uniform(0.07, 0.16)
            self.recolor = lambda h, s, v: (h + turn, s, v)
        else:
            self.recolor = self.MOODS[self.mood][1]
        self.ink = rng.choice((INK, INK, "#2e2219", "#1d2740", "#2b2b2b"))
        self.ink_width = rng.uniform(4.6, 6.4)
        self.sheet = rng.choice(("#fbf8f1", "#ffffff", "#f7f0e1", "#f4f2ee", "#fdf5e6"))

    def apply(self, sk):
        bounds = sk.bounds
        if bounds and self.mirror:
            bounds = sk.bounds = (W - bounds[2], bounds[1], W - bounds[0], bounds[3])
        ink = rgba(sk.ink)
        for it in sk.items:
            if it.poly is not None:
                it.poly = self._points(densify(it.poly + it.poly[:1], 14)[:-1], bounds)
            it.polys = [self._points(densify(p, 14), bounds) for p in it.polys]
            if it.color[3] and it.color != ink:
                it.color = self._color(it.color)

    def _points(self, pts, bounds):
        out = []
        for x, y in pts:
            if self.mirror:
                x = W - x
            dx = dy = 0.0
            for axis, a, kx, ky, ph in self.waves:
                d = a * math.sin(kx * x + ky * y + ph)
                if axis:
                    dy += d
                else:
                    dx += d
            if bounds:
                f = smooth(min(x - bounds[0], bounds[2] - x, y - bounds[1], bounds[3] - y) / 90)
                dx, dy = dx * f, dy * f
            out.append((x + dx, y + dy))
        return out

    def _color(self, c):
        h, s, v = colorsys.rgb_to_hsv(*(x / 255 for x in c[:3]))
        h, s, v = self.recolor(h, s, v)
        r, g, b = colorsys.hsv_to_rgb(h % 1.0, clamp(s), clamp(v))
        return (round(r * 255), round(g * 255), round(b * 255), c[3])


def _toward(h, target, amount):
    """Hue h nudged toward target by up to amount, the short way around the color wheel."""
    d = (target - h + 0.5) % 1.0 - 0.5
    return h + max(-amount, min(amount, d))


def _visible_runs(poly, arr, step=2.5):
    """Split a polyline into the runs not covered by the mask (front shapes)."""
    pts = densify(poly, step)
    h, w = arr.shape
    runs, cur = [], []
    for p in pts:
        x, y = int(p[0]), int(p[1])
        hidden = 0 <= x < w and 0 <= y < h and arr[y, x] > 0
        if hidden:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        runs.append(cur)
    return runs


def _hatch(poly, angle, gap):
    """Zig-zag coloring path that covers a polygon, like filling it in with a marker."""
    ca, sa = math.cos(angle), math.sin(angle)
    us = [x * ca + y * sa for x, y in poly]
    vs = [-x * sa + y * ca for x, y in poly]
    u0, u1, v0, v1 = min(us) - gap * 0.3, max(us) + gap * 0.3, min(vs), max(vs)
    rows = max(1, int((v1 - v0) / gap) + 1)
    out = []
    for i in range(rows + 1):
        v = v0 + (v1 - v0) * i / rows
        a, b = (u0, u1) if i % 2 == 0 else (u1, u0)
        out += [(a, v), (b, v)]
    return [(u * ca - v * sa, u * sa + v * ca) for u, v in out]


class _Path:
    """A polyline with cumulative lengths, for partial drawing and pen positions."""

    def __init__(self, pts):
        self.pts = pts
        self.cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            self.cum.append(self.cum[-1] + math.dist(a, b))
        self.len = self.cum[-1]

    def upto(self, d):
        if d >= self.len:
            return self.pts
        i = bisect.bisect_right(self.cum, d)
        a, b = self.pts[i - 1], self.pts[i]
        seg_len = self.cum[i] - self.cum[i - 1]
        f = (d - self.cum[i - 1]) / seg_len if seg_len else 0
        return self.pts[:i] + [(lerp(a[0], b[0], f), lerp(a[1], b[1], f))]


class SketchScene:
    """Callable draw(cv, t) for a Sketch, with incremental caching of the finished strokes."""

    def __init__(self, sk, duration, hold):
        self.sk = sk
        self.duration = duration
        self.draw_end = max(1.0, duration - max(hold, 0.6))
        self.glow = 0.0  # paper drawings get no bloom
        self.thumb_at = duration
        self.items = self._order(self._clip(sk.items))
        self._plan()
        self.state = None

    # -- preparation (logical coordinates) ------------------------------------------------

    def _clip(self, items):
        """Remove the parts of strokes hidden behind shapes in front, back to front ordering kept."""
        union = Image.new("L", (W, H), 0)
        ud = ImageDraw.Draw(union)
        b = self.sk.bounds
        if b:
            union.paste(255, (0, 0, W, H))
            ud.rectangle((b[0] - 4, b[1] - 4, b[2] + 4, b[3] + 4), fill=0)
        arr = None
        for it in reversed(items):
            if it.kind == "stroke" and it.clip:
                if arr is None:
                    arr = np.asarray(union)
                polys = []
                for p in it.polys:
                    polys += _visible_runs(p, arr)
                it.polys = polys
            if it.occludes and it.poly is not None:
                ud.polygon(it.poly, fill=255)
                arr = None
        self.occluders = [it for it in items if it.occludes and it.poly is not None]
        return [it for it in items if (it.kind == "fill" and it.color[3] > 0) or (it.kind == "stroke" and it.polys)]

    def _order(self, items):
        return [it for ph in PHASES for it in items if it.phase == ph]

    def _plan(self):
        """Give every item a time slot, proportional to how much drawing it takes."""
        rng = self.sk.rng
        prev = None
        costs = []
        for it in self.items:
            if it.kind == "stroke":
                it.paths = [_Path(p) for p in it.polys]
                it.total = max(p.len for p in it.paths) if it.together else sum(p.len for p in it.paths)
                cost = it.total / SPEED[it.phase] + 25 * (len(it.paths) - 1) * (not it.together)
                start = it.paths[0].pts[0]
            else:
                a = area(it.poly)
                gap = clamp(math.sqrt(a) / 9, 9, 34)
                it.hatch = _Path(_hatch(it.poly, rng.uniform(-0.6, 0.6) + math.pi / 5, gap))
                it.hatch_width = gap * 1.7
                it.total = it.hatch.len
                cost = (it.total * 0.32 + 60) / SPEED[it.phase]
                start = it.hatch.pts[0]
            travel = math.dist(prev, start) * 0.25 if prev else 0
            costs.append((travel, cost))
            prev = (it.paths[-1].pts[-1] if it.kind == "stroke" else it.hatch.pts[-1])
        total = sum(a + b for a, b in costs) or 1
        lead = 0.5  # pen settles in before the first stroke
        k = (self.draw_end - lead) / total
        t = lead
        for it, (travel, cost) in zip(self.items, costs):
            it.t0 = t + travel * k
            it.t1 = it.t0 + cost * k
            t = it.t1

    # -- rendering (output pixels) ---------------------------------------------------------

    def _setup(self, cv):
        size, s = cv.img.size, cv.s
        base = paper(size, s, self.sk.desk, self.sk.sheet, seed=7)
        self.state = dict(size=size, s=s, base=base, comp=base.copy(), done=0,
                          layers={z: Image.new("RGBA", size, (0, 0, 0, 0)) for z in set(LAYER.values())},
                          masks={})

    def _box(self, it):
        s = self.state["s"]
        if it.kind == "stroke":
            pts = [p for path in it.paths for p in path.pts]
            pad = it.width
        else:
            pts = it.poly
            pad = 2
        x0, y0, x1, y1 = bbox(pts)
        w, h = self.state["size"]
        box = (max(0, int((x0 - pad) * s) - 2), max(0, int((y0 - pad) * s) - 2),
               min(w, int((x1 + pad) * s) + 3), min(h, int((y1 + pad) * s) + 3))
        return box if box[2] > box[0] and box[3] > box[1] else None

    def _fill_mask(self, it, box):
        """Polygon mask minus every shape in front of it, cropped to box."""
        key = id(it)
        if key not in self.state["masks"]:
            s = self.state["s"]
            ox, oy = box[0], box[1]
            m = Image.new("L", (box[2] - box[0], box[3] - box[1]), 0)
            d = ImageDraw.Draw(m)
            tr = lambda pts: [(x * s - ox, y * s - oy) for x, y in pts]  # noqa: E731
            d.polygon(tr(it.poly), fill=255)
            b = self.sk.bounds
            if b:
                keep = Image.new("L", m.size, 0)
                ImageDraw.Draw(keep).rectangle((b[0] * s - ox, b[1] * s - oy, b[2] * s - ox, b[3] * s - oy), fill=255)
                m = ImageChops.multiply(m, keep)
                d = ImageDraw.Draw(m)
            for oc in self.occluders:
                if oc.depth > it.depth:
                    d.polygon(tr(oc.poly), fill=0)
            self.state["masks"] = {key: m}  # only the active fill needs its mask kept
        return self.state["masks"][key]

    def _render_item(self, it, u, box):
        """The item drawn up to progress u, as an RGBA image the size of box. Returns (image, tip)."""
        s = self.state["s"]
        ox, oy = box[0], box[1]
        size = (box[2] - box[0], box[3] - box[1])
        tr = lambda pts: [(x * s - ox, y * s - oy) for x, y in pts]  # noqa: E731
        tip = None
        if it.kind == "stroke":
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            w = max(1, round(it.width * s))
            r = w / 2

            def draw(pts):
                pts = tr(pts)
                if len(pts) > 1:
                    d.line(pts, fill=it.color, width=w, joint="curve")
                for x, y in (pts[0], pts[-1]):
                    d.ellipse((x - r, y - r, x + r, y + r), fill=it.color)

            if it.together:
                for p in it.paths:
                    pts = p.upto(u * it.total)
                    draw(pts)
                    if tip is None:
                        tip = pts[-1]
            else:
                left = u * it.total
                for p in it.paths:
                    pts = p.upto(left)
                    draw(pts)
                    tip = pts[-1]
                    left -= p.len
                    if left <= 0:
                        break
            return img, tip
        mask = self._fill_mask(it, box)
        if u < 1:
            hm = Image.new("L", size, 0)
            pts = it.hatch.upto(u * it.total)
            ImageDraw.Draw(hm).line(tr(pts), fill=255, width=max(1, round(it.hatch_width * s)), joint="curve")
            mask = ImageChops.multiply(mask, hm)
            tip = pts[-1]
        alpha = mask if it.color[3] == 255 else mask.point(lambda v, a=it.color[3]: v * a // 255)
        img = Image.new("RGBA", size, it.color[:3] + (0,))
        img.putalpha(alpha)
        return img, tip

    def _region(self, box, extra=None):
        """Base + all layers (plus an in-progress item at its layer) inside box."""
        st = self.state
        region = st["base"].crop(box).convert("RGBA")
        for z in sorted(st["layers"]):
            region.alpha_composite(st["layers"][z].crop(box))
            if extra and extra[0] == z:
                region.alpha_composite(extra[1])
        return region.convert("RGB")

    def _commit(self, it):
        box = self._box(it)
        if box:
            img, _ = self._render_item(it, 1.0, box)
            self.state["layers"][LAYER[it.phase]].alpha_composite(img, dest=box[:2])
            self.state["comp"].paste(self._region(box), box[:2])
        self.state["masks"] = {}

    def __call__(self, cv, t):
        if self.state is None or self.state["size"] != cv.img.size:
            self._setup(cv)
        st = self.state
        n_done = bisect.bisect_right([it.t1 for it in self.items], t)
        if n_done < st["done"]:
            self._setup(cv)
            st = self.state
        while st["done"] < n_done:
            self._commit(self.items[st["done"]])
            st["done"] += 1
        frame = st["comp"].copy()
        tip, tool, color = None, "pen", self.sk.ink
        active = self.items[st["done"]] if st["done"] < len(self.items) else None
        if active and t >= active.t0:
            u = clamp((t - active.t0) / (active.t1 - active.t0))
            box = self._box(active)
            if box:
                img, tip = self._render_item(active, u, box)
                frame.paste(self._region(box, (LAYER[active.phase], img)), box[:2])
            tool, color = active.tool, active.color
        elif active:
            # Travelling to the next item: glide from the previous end point to the next start.
            prev = self.items[st["done"] - 1] if st["done"] else None
            a = self._end(prev) if prev else (W * 0.85, H * 0.95)
            b = self._start(active)
            t0 = prev.t1 if prev else 0
            u = smooth(clamp((t - t0) / max(1e-6, active.t0 - t0)))
            tip = (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
            tool, color = active.tool, active.color
        img = frame
        if t > self.draw_end:
            img = self._finale(frame, t - self.draw_end, cv.s)
        cv.img.paste(img)
        if t <= self.draw_end + 0.8 and tool:
            if tip is None and self.items:
                last = self.items[-1]
                tip = self._end(last)
                tool, color = last.tool, last.color
            if tip is not None:
                lift = ease_out(clamp((t - self.draw_end) / 0.8)) if t > self.draw_end else 0
                if active and t < active.t0:
                    lift = max(lift, 0.08)
                tip = (tip[0] + 900 * lift, tip[1] - 700 * lift)
                _tool(Canvas(cv.img, cv.s), tip, tool, color, t)

    def _start(self, it):
        return it.paths[0].pts[0] if it.kind == "stroke" else it.hatch.pts[0]

    def _end(self, it):
        return it.paths[-1].pts[-1] if it.kind == "stroke" else it.hatch.pts[-1]

    def _finale(self, frame, age, s):
        z = 1 + (self.sk.zoom - 1) * smooth(age / 3.0)
        w, h = frame.size
        cx, cy = w / 2, (SHEET[1] + SHEET[3]) / 2 * s
        cw, ch = w / z, h / z
        cy = min(max(cy, ch / 2), h - ch / 2)
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        img = frame.resize(frame.size, Image.BILINEAR, box=box) if z > 1.0005 else frame
        cv = Canvas(img, s)
        rng = __import__("random").Random(11)
        for i in range(14):
            x = rng.uniform(SHEET[0] + 40, SHEET[2] - 40)
            y = rng.uniform(SHEET[1] + 40, SHEET[3] - 40)
            ph = age * 1.6 - i * 0.17
            if 0 < ph < 1:
                r = 26 * math.sin(math.pi * ph) * rng.uniform(0.6, 1.2)
                twinkle(cv, (x, y), r, (255, 214, 92, 235))
        return img


def _tool(cv, tip, tool, color, t):
    """A pen, marker or paintbrush held at the tip point, leaning to the upper right."""
    a = math.radians(-38 + 2.5 * math.sin(t * 7))
    d = (math.sin(-a), -math.cos(-a))   # from the tip toward the back of the tool
    n = (-d[1], d[0])

    def P(along, side):
        return (tip[0] + d[0] * along + n[0] * side, tip[1] + d[1] * along + n[1] * side)

    def quad_(a0, a1, w0, w1, col):
        cv.poly([P(a0, -w0), P(a1, -w1), P(a1, w1), P(a0, w0)], col)

    # Soft shadow on the paper.
    sh = (24, 30)
    cv.poly([(x + sh[0], y + sh[1]) for x, y in [P(30, -14), P(460, -22), P(460, 22), P(30, 14)]], (0, 0, 0, 45))
    body = color[:3] if color[3] > 0 else (120, 120, 120)
    if tool == "marker":
        quad_(0, 18, 7, 12, body)
        quad_(18, 46, 12, 22, (235, 235, 235))
        quad_(46, 420, 22, 22, (250, 250, 248))
        quad_(330, 440, 24, 24, body)
        quad_(60, 300, 4, 4, (255, 255, 255, 120))
        cv.line([P(46, -22), P(46, 22)], (200, 200, 200), 2)
    elif tool == "brush":
        quad_(0, 40, 3, 12, body)
        quad_(40, 70, 12, 13, (190, 196, 205))
        quad_(70, 430, 13, 9, (205, 60, 50))
        quad_(80, 380, 3, 3, (255, 255, 255, 90))
    else:  # fineliner pen
        quad_(0, 14, 2, 4, (30, 30, 34))
        quad_(14, 50, 6, 16, (60, 62, 70))
        quad_(50, 400, 17, 17, (44, 46, 54))
        quad_(260, 410, 19, 19, (25, 26, 30))
        quad_(70, 250, 4, 4, (255, 255, 255, 70))
        cv.line([P(300, 19), P(380, 24)], (190, 190, 200), 5)
