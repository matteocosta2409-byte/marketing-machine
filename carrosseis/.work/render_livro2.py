#!/usr/bin/env python3
# Motor "página de livro" v2 (refs @matthgray de 04/11/2026): papel limpo, sem texto vazado,
# Hoefler Text (a dos posts), poucos grifos e diagramas de linha. 1080x1440.
# Markup: **trecho** = grifo; a pontuação fica dentro do grifo (**assim,**).
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1440
WORK = os.path.dirname(os.path.abspath(__file__))
INK = (40, 38, 36)
PAPER = (205, 208, 203)
SS = 3  # superamostragem dos diagramas

GREEN = (176, 222, 120)
BLUE = (168, 208, 240)
ROSE = (240, 178, 196)
YELLOW = (240, 224, 130)

BASK = "/System/Library/Fonts/Supplemental/Hoefler Text.ttc"  # mesma fonte dos carrosséis já postados
HELV = "/System/Library/Fonts/HelveticaNeue.ttc"


def F(size, style="reg"):
    return ImageFont.truetype(BASK, size, index={"reg": 0, "bold": 1, "it": 2, "semi": 1}[style])


def S(size):
    return ImageFont.truetype(HELV, size, index=1)  # rótulos dos diagramas


def paper(seed=7):
    """Papel limpo: grão em 3 escalas e luz irregular; nada vaza da outra página."""
    random.seed(seed)
    img = Image.new("RGB", (W, H), PAPER)
    def over(noise):
        return Image.merge("RGB", (noise, noise, noise))
    fine = Image.effect_noise((W, H), 18).filter(ImageFilter.GaussianBlur(0.5))
    img = ImageChops.overlay(img, over(fine))
    mid = Image.effect_noise((W // 3, H // 3), 24).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.0))
    img = ImageChops.overlay(img, over(mid))
    coarse = Image.effect_noise((W // 30, H // 30), 34).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
    coarse = coarse.point(lambda p: 128 + int((p - 128) * 0.55))
    img = ImageChops.overlay(img, over(coarse))
    shade = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade).ellipse([-W * 0.4, -H * 0.3, W * 1.4, H * 1.25], fill=20)
    shade = shade.filter(ImageFilter.GaussianBlur(240))
    return ImageChops.add(img, over(shade))


def parse(text):
    out, on = [], False
    for tok in text.split():
        if tok.startswith("**"):
            on, tok = True, tok[2:]
        if tok.endswith("**"):
            out.append((tok[:-2], on))
            on = False
        else:
            out.append((tok, on))
    return out


def wrap(words, fnt, maxw, d):
    lines, cur = [], []
    for w, h in words:
        trial = " ".join(x for x, _ in cur + [(w, h)])
        if cur and d.textlength(trial, font=fnt) > maxw:
            lines.append(cur)
            cur = [(w, h)]
        else:
            cur.append((w, h))
    if cur:
        lines.append(cur)
    return lines


def marker(md, x0, x1, ymid, hh, color):
    """Traço reto com pontas em diagonal (pedido do Matteo: sem ponta arredondada)."""
    x0 -= 7
    x1 += 7
    yt, yb = ymid - hh / 2, ymid + hh / 2
    skew = hh * 0.30
    md.polygon([(x0 + skew, yt), (x1 + skew, yt), (x1, yb), (x0, yb)], fill=color)


def text(img, paras, fnt, x, y, maxw, lh, gap, color=GREEN, align="left"):
    """Desenha parágrafos. Cada parágrafo pode ser str ou (str, cor_do_grifo). Retorna (img, y)."""
    mk = Image.new("RGB", (W, H), (255, 255, 255))
    md = ImageDraw.Draw(mk)
    tx = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tx)
    asc, _ = fnt.getmetrics()
    for p in paras:
        col = color
        if isinstance(p, tuple):
            p, col = p
        for line in wrap(parse(p), fnt, maxw, td):
            full = " ".join(w for w, _ in line)
            lx = x if align == "left" else x + (maxw - td.textlength(full, font=fnt)) / 2
            cx, start, end = lx, None, None
            for i, (w, hl) in enumerate(line):
                ww = td.textlength(w, font=fnt)
                if hl:
                    start = cx if start is None else start
                    end = cx + ww
                if start is not None and (not hl or i == len(line) - 1):
                    marker(md, start, end, y + asc * 0.60, asc * 0.98, col)
                    start = None
                cx += td.textlength(w + " ", font=fnt)
            td.text((lx, y), full, font=fnt, fill=INK + (245,))
            y += lh
        y += gap
    out = ImageChops.multiply(img, mk.filter(ImageFilter.GaussianBlur(1.6)))
    out.paste(tx, (0, 0), tx)
    return out, y - gap


class Canvas:
    """Camada de linhas em 3x; composta sobre o papel com leve textura de impressão."""

    def __init__(self):
        self.im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _s(self, *v):
        return [a * SS for a in v]

    def circle(self, x, y, r, fill=None, width=3):
        self.d.ellipse(self._s(x - r, y - r, x + r, y + r), fill=(fill + (255,)) if fill else None,
                       outline=INK + (255,), width=width * SS)

    def ellipse(self, x, y, rx, ry, width=3, fill=None):
        self.d.ellipse(self._s(x - rx, y - ry, x + rx, y + ry), fill=(fill + (255,)) if fill else None,
                       outline=INK + (255,), width=width * SS)

    def rect(self, x0, y0, x1, y1, width=3, fill=None):
        self.d.rectangle(self._s(x0, y0, x1, y1), fill=(fill + (255,)) if fill else None,
                         outline=INK + (255,), width=width * SS)

    def line(self, x0, y0, x1, y1, width=3):
        self.d.line(self._s(x0, y0, x1, y1), fill=INK + (255,), width=width * SS)

    def arrow(self, x0, y0, x1, y1, head=16, width=3):
        import math
        self.line(x0, y0, x1, y1, width)
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.55, -2.55):
            self.line(x1, y1, x1 + head * math.cos(a + da), y1 + head * math.sin(a + da), width)

    def label(self, x, y, s, size=26, font=None, anchor="mm"):
        fnt = font(size * SS) if font else S(size * SS)
        self.d.text((x * SS, y * SS), s, font=fnt, fill=INK + (255,), anchor=anchor)

    def compose(self, img):
        small = self.im.resize((W, H), Image.LANCZOS)
        img = img.copy()
        img.paste(small, (0, 0), small)
        return img
