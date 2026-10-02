"""Frame compositing: gradient background, 2x supersampling, glow, quote and watermark overlays."""

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

from .art import W, Canvas, font, make_background


class Compositor:
    """Turns a scene's draw(cv, t) into finished video frames."""

    def __init__(self, out_size, background, supersample=2, glow=0.55, hook_text=None, watermark=None):
        self.out_w, self.out_h = out_size
        self.ss = supersample
        self.scale = self.out_w / W * supersample
        self.base = make_background((self.out_w * supersample, self.out_h * supersample), *background)
        self.glow = glow
        self.overlay = self._make_overlay(hook_text) if hook_text else None
        if watermark:
            wm = self._make_watermark(watermark)
            self.overlay = wm if self.overlay is None else Image.alpha_composite(self.overlay, wm)

    def frame(self, draw, t):
        hi = self.base.copy()
        draw(Canvas(hi, self.scale), t)
        img = hi.reduce(self.ss) if self.ss > 1 else hi
        glow = self.glow * getattr(draw, "glow", 1.0)  # paper drawings turn the glow off
        if glow > 0:
            small = img.reduce(4).filter(ImageFilter.GaussianBlur(radius=max(2, self.out_w // 160)))
            bloom = ImageEnhance.Brightness(small.resize(img.size, Image.BILINEAR)).enhance(glow * 2)
            img = ImageChops.screen(img, bloom)
        if self.overlay is not None:
            img.paste(self.overlay, (0, 0), self.overlay)
        return img

    def _make_watermark(self, text):
        """Purple banner below the action, burned into free trial Shorts."""
        layer = Image.new("RGBA", (self.out_w, self.out_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        f = font(self.out_w * 0.05)
        w = d.textlength(text, font=f)
        y = self.out_h * 0.8
        pad = self.out_w * 0.03
        d.rounded_rectangle(((self.out_w - w) / 2 - pad, y - pad * 0.6, (self.out_w + w) / 2 + pad, y + self.out_w * 0.07),
                            radius=pad, fill=(139, 92, 246, 150))
        d.text(((self.out_w - w) / 2, y), text, font=f, fill=(255, 255, 255, 235))
        return layer

    def _make_overlay(self, text):
        """Short one-line quote in a soft rounded box near the top; font shrinks to fit the width."""
        layer = Image.new("RGBA", (self.out_w, self.out_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        text = f"“{text.strip().strip(chr(34))}”"
        max_w = self.out_w * 0.84
        size = int(self.out_w * 0.056)
        f = font(size)
        while d.textlength(text, font=f) > max_w and size > 12:
            size -= 1
            f = font(size)
        ascent, descent = f.getmetrics()
        w, h = d.textlength(text, font=f), ascent + descent
        top = self.out_h * 0.1
        pad = size * 0.6
        d.rounded_rectangle(((self.out_w - w) / 2 - pad, top - pad * 0.7, (self.out_w + w) / 2 + pad, top + h + pad * 0.5),
                            radius=pad, fill=(0, 0, 0, 115))
        d.text(((self.out_w - w) / 2, top), text, font=f, fill=(255, 255, 255, 245))
        return layer
