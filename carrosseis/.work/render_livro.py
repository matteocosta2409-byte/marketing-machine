#!/usr/bin/env python3
# Motor de carrossel — 5º formato: "página de livro" (ref: post do @matthgray).
# Fundo sintetizado: papel com grão + texto vazado da outra página (desfocado) + borrões de marca-texto.
# Texto serifado de livro (Hoefler Text) cor de tinta, com marca-texto laranja desenhado à mão nos destaques.
# Markup: **trecho** = marca-texto. Formato 4:5 (1080x1350).
import os, random, unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1350
WORK = os.path.dirname(os.path.abspath(__file__))

INK = (56, 50, 44)
MARKER = (164, 208, 128)     # verde de marca-texto (aplicado em multiply)
MARKER2 = (140, 192, 104)    # passada dupla, um pouco mais saturada
PAPER = (198, 203, 196)      # papel cinza-esverdeado frio

TTC = "/System/Library/Fonts/Supplemental/Hoefler Text.ttc"
def F(size, style="reg"):
    idx = {"reg": 0, "black": 1, "it": 2, "blackit": 3}[style]
    return ImageFont.truetype(TTC, size, index=idx)


# ---------------------------------------------------------------- fundo: papel
FAKE = ("a fim de que a memoria se consolide durante a noite o cerebro repete "
        "os padroes vistos no dia e descarta o que julga irrelevante por isso "
        "quem estuda sem dormir apaga parte do proprio esforco e o rendimento "
        "cai de forma silenciosa ate o dia da prova quando tudo se decide").split()

def paper(seed=7):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), PAPER)

    # leve variação de iluminação (mais claro no centro, canto sup. um pouco mais escuro)
    shade = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shade)
    sd.ellipse([-W * 0.5, -H * 0.4, W * 1.5, H * 1.3], fill=26)
    shade = shade.filter(ImageFilter.GaussianBlur(220))
    img = ImageChops.add(img, Image.merge("RGB", (shade, shade, shade)))

    # texto vazado da outra página (espelhado + bem desfocado) com trechos "grifados"
    bleed = Image.new("RGB", (W, H), (255, 255, 255))
    bd = ImageDraw.Draw(bleed)
    fb = F(38)
    y = -rnd.randint(0, 60)
    while y < H + 40:
        n = rnd.randint(6, 9)
        line = " ".join(rnd.choice(FAKE) for _ in range(n))
        x = rnd.randint(-60, 40)
        if rnd.random() < 0.25:  # linha grifada na outra página
            wln = bd.textlength(line, font=fb)
            bd.rounded_rectangle([x - 6, y + 4, x + wln + 10, y + 46], 20,
                                 fill=(224, 238, 210))
        bd.text((x, y), line, font=fb, fill=(176, 178, 174))
        y += rnd.randint(88, 150)
    bleed = bleed.transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(6))
    bleed = Image.blend(Image.new("RGB", (W, H), (255, 255, 255)), bleed, 0.55)
    img = ImageChops.multiply(img, bleed)

    # textura da folha, em 3 escalas (bem carregada, como na ref):
    # 1) grão fino (fibra do papel) — 2 passadas pra ficar bem presente
    fine = Image.effect_noise((W, H), 34).filter(ImageFilter.GaussianBlur(0.4))
    img = ImageChops.overlay(img, Image.merge("RGB", (fine, fine, fine)))
    fine2 = Image.effect_noise((W, H), 22)
    img = ImageChops.overlay(img, Image.merge("RGB", (fine2, fine2, fine2)))
    # 2) granulado médio — caroços/relevo do papel
    mid = Image.effect_noise((W // 3, H // 3), 30).resize((W, H), Image.LANCZOS)
    mid = mid.filter(ImageFilter.GaussianBlur(1.0))
    img = ImageChops.overlay(img, Image.merge("RGB", (mid, mid, mid)))
    # 3) manchas largas de tom (papel não uniforme)
    coarse = Image.effect_noise((W // 24, H // 24), 40).resize((W, H), Image.BICUBIC)
    coarse = coarse.filter(ImageFilter.GaussianBlur(26))
    coarse = coarse.point(lambda p: 128 + int((p - 128) * 0.7))
    img = ImageChops.overlay(img, Image.merge("RGB", (coarse, coarse, coarse)))
    return img


# ------------------------------------------------------- marca-texto (à mão)
def marker_stroke(layer_draw, x0, x1, ymid, hh, rnd):
    """Traço reto de marca-texto com pontas em DIAGONAL (paralelogramo)."""
    x0 -= rnd.randint(4, 10); x1 += rnd.randint(4, 10)
    yt, yb = ymid - hh / 2, ymid + hh / 2
    skew = hh * 0.38  # inclinação da ponta (topo deslocado à direita)
    layer_draw.polygon([(x0 + skew, yt), (x1 + skew, yt), (x1, yb), (x0, yb)],
                       fill=MARKER)
    # passada dupla parcial (trecho mais saturado), mesmo formato
    if rnd.random() < 0.8 and (x1 - x0) > 160:
        a = x0 + rnd.randint(0, int((x1 - x0) * 0.3))
        b = min(a + rnd.randint(120, max(140, int((x1 - x0) * 0.6))), x1)
        layer_draw.polygon([(a + skew, yt + 5), (b + skew, yt + 5), (b, yb - 3), (a, yb - 3)],
                           fill=MARKER2)


# --------------------------------------------------------------- texto marcado
def parse_marked(text):
    """Divide em palavras com flag de destaque a partir de **...**."""
    words, hl = [], False
    for tok in text.split():
        w = tok
        starts = w.startswith("**"); ends = w.endswith("**") and len(w.replace("**", "")) > 0
        if starts: hl = True; w = w[2:]
        if w.endswith("**"): w = w[:-2]; words.append((w, hl)); hl = False; continue
        words.append((w, hl))
    return words

def wrap_words(words, fnt, maxw, d):
    lines, cur = [], []
    for w, h in words:
        trial = " ".join(x for x, _ in cur + [(w, h)])
        if cur and d.textlength(trial, font=fnt) > maxw:
            lines.append(cur); cur = [(w, h)]
        else:
            cur.append((w, h))
    if cur: lines.append(cur)
    return lines

def block_height(paragraphs, fnt, maxw, d, lh, gap):
    total = 0
    for p in paragraphs:
        lines = wrap_words(parse_marked(p), fnt, maxw, d)
        total += len(lines) * lh + gap
    return total - gap

def draw_paragraphs(img, paragraphs, fnt, x, y, maxw, lh, gap, seed=1, align="left"):
    """Desenha parágrafos com marca-texto nos trechos **...**. Retorna y final."""
    rnd = random.Random(seed)
    mk = Image.new("RGB", (W, H), (255, 255, 255))
    mkd = ImageDraw.Draw(mk)
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    asc, desc = fnt.getmetrics()
    for p in paragraphs:
        lines = wrap_words(parse_marked(p), fnt, maxw, td)
        for line in lines:
            full = " ".join(w for w, _ in line)
            lw = td.textlength(full, font=fnt)
            lx = x if align == "left" else x + (maxw - lw) / 2
            # spans contíguos destacados
            cx = lx
            span = None
            for i, (w, hl) in enumerate(line):
                ww = td.textlength(w, font=fnt)
                sw = td.textlength(w + " ", font=fnt)
                if hl and span is None: span = cx
                if hl: span_end = cx + ww
                if (not hl or i == len(line) - 1) and span is not None:
                    ymid = y + asc * 0.62
                    marker_stroke(mkd, span, span_end, ymid, asc * 1.02, rnd)
                    span = None
                cx += sw
            td.text((lx, y), full, font=fnt, fill=INK + (242,))
            y += lh
        y += gap
    mk = mk.filter(ImageFilter.GaussianBlur(2.5))
    out = ImageChops.multiply(img, mk)
    txt = txt.filter(ImageFilter.GaussianBlur(0.4))
    out.paste(txt, (0, 0), txt)
    return out, y


# ------------------------------------------------------------------- builders
def body_slide(paragraphs, seed, size=47, y0=None):
    img = paper(seed)
    d = ImageDraw.Draw(img)
    x, maxw = 88, W - 2 * 88
    # texto longo: diminui a fonte até caber na página (mín. 36)
    while True:
        fnt = F(size)
        lh, gap = int(size * 1.32), int(size * 0.92)
        total = block_height(paragraphs, fnt, maxw, d, lh, gap)
        if total <= H - 300 or size <= 36:
            break
        size -= 1
    if y0 is None:
        y0 = max(215, int(H * 0.44 - total / 2))
    img, _ = draw_paragraphs(img, paragraphs, fnt, x, y0, maxw, lh, gap, seed=seed)
    return img

def cover_slide(line1, line2, seed=3, size=62, hl1=True, hl2=False, sub=None, note=None):
    """Capa centralizada. Use '|' para quebras manuais; hl1/hl2 = onde vai o grifo.
    sub = linha menor abaixo do título; note = rodapé pequeno (ex.: asterisco)."""
    img = paper(seed)
    d = ImageDraw.Draw(img)
    fit = F(size, "it"); freg = F(size)
    maxw = W - 2 * 70
    def mark(s, on): return "**" + s + "**" if on else s
    l1 = [mark(s.strip(), hl1) for s in line1.split("|")]
    l2 = [mark(s.strip(), hl2) for s in line2.split("|")]
    lh = int(size * 1.28)
    n1 = sum(len(wrap_words(parse_marked(p), fit, maxw, d)) for p in l1)
    n2 = sum(len(wrap_words(parse_marked(p), freg, maxw, d)) for p in l2)
    fsub = F(int(size * 0.66)); lhs = int(size * 0.66 * 1.3)
    subs = [x.strip() for x in sub.split("|")] if sub else []
    ns = sum(len(wrap_words(parse_marked(x), fsub, maxw, d)) for x in subs)
    y = int(H * 0.52 - ((n1 + n2) * lh + (ns * lhs + 40 if sub else 0)) / 2)
    for p in l1:
        img, y = draw_paragraphs(img, [p], fit, 70, y, maxw, lh, 0, seed=seed, align="center")
    y += 6
    for p in l2:
        img, y = draw_paragraphs(img, [p], freg, 70, y, maxw, lh, 0, seed=seed + 1, align="center")
    if sub:
        img, y = draw_paragraphs(img, subs, fsub, 70, y + 40, maxw, lhs, 0, seed=seed + 2, align="center")
    if note:
        fn = F(30, "it")
        img, _ = draw_paragraphs(img, [note], fn, 70, H - 130, maxw, 40, 0, seed=seed + 3, align="center")
    return img
