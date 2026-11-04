"""Carrossel "10 livros que mudaram minha vida" — estilo @matthgray (DcuUQ25DTXH).
Capa = foto do Matteo + título grande embaixo à esquerda.
Slide de livro = fundo preto, (Título) no topo, frase de contexto, seta à mão,
capa do livro no centro, frase de resultado embaixo com trechos **em verde**."""
import math, os, random, re
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1440  # 3:4, igual à ref
HN = "/System/Library/Fonts/HelveticaNeue.ttc"
BOLD, MEDIUM = 1, 10
WHITE = (255, 255, 255)
GREEN = (219, 252, 106)  # verde-limão medido na ref

def font(idx, size):
    return ImageFont.truetype(HN, size, index=idx)

# ---------- texto com tracking apertado + destaque **...** ----------

def runs(text):
    """'a **b** c' -> [('a ', False), ('b', True), (' c', False)]"""
    out = []
    for i, part in enumerate(re.split(r"\*\*", text)):
        if part:
            out.append((part, i % 2 == 1))
    return out

def run_width(s, f, track):
    return f.getlength(s) + track * max(len(s) - 1, 0)

def line_width(line_runs, f, track):
    return sum(run_width(s, f, track) for s, _ in line_runs) + track * max(len(line_runs) - 1, 0)

def wrap(text, f, track, maxw):
    """Quebra por palavras preservando o destaque. Retorna lista de linhas (cada uma = lista de runs)."""
    words = []  # (palavra, destaque)
    for s, hl in runs(text):
        for k, w in enumerate(s.split(" ")):
            if w:
                words.append((w, hl))
    lines, cur = [], []
    for w in words:
        test = cur + [w]
        if cur and line_width(_join(test), f, track) > maxw:
            lines.append(_join(cur)); cur = [w]
        else:
            cur = test
    if cur:
        lines.append(_join(cur))
    return lines

def _join(words):
    """Junta palavras em runs contíguos da mesma cor."""
    out = []
    for i, (w, hl) in enumerate(words):
        s = w if i == 0 or w[0] in ",.;:!?" else " " + w
        if out and out[-1][1] == hl:
            out[-1] = (out[-1][0] + s, hl)
        else:
            out.append((s, hl))
    return out

def draw_run(d, x, y, s, f, track, fill):
    for i, ch in enumerate(s):
        # avanço cumulativo preserva o kerning
        cx = x + f.getlength(s[:i]) + track * i
        d.text((cx, y), ch, font=f, fill=fill)
    return x + run_width(s, f, track) + track

def text_block(img, text, cy, size, idx=MEDIUM, track=-0.035, lead=1.08, maxw=860, anchor="top"):
    """Bloco centralizado. anchor='top' -> cy é o topo; 'bottom' -> cy é a base. Retorna (topo, base)."""
    f = font(idx, size)
    tr = track * size
    lines = []
    for para in text.split("\n"):
        lines += wrap(para, f, tr, maxw)
    lh = size * lead
    total = lh * len(lines)
    y0 = cy if anchor == "top" else cy - total
    d = ImageDraw.Draw(img)
    for k, ln in enumerate(lines):
        x = (W - line_width(ln, f, tr)) / 2
        for s, hl in ln:
            x = draw_run(d, x, y0 + k * lh, s, f, tr, GREEN if hl else WHITE)
    return y0, y0 + total

# ---------- seta desenhada à mão ----------

def _bezier(p0, p1, p2, p3, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c, e = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return pts

def arrow(img, p0, c1, c2, p3, width=3, head=22, seed=0):
    """Curva cúbica com tremidinha leve + ponta em 'V' aberta, desenhada em 2x e reduzida (antialias)."""
    rnd = random.Random(seed)
    S = 2
    layer = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(layer)
    pts = _bezier(p0, c1, c2, p3)
    pts = [(x + rnd.uniform(-0.6, 0.6), y + rnd.uniform(-0.6, 0.6)) for x, y in pts]
    d.line([(x * S, y * S) for x, y in pts], fill=255, width=width * S, joint="curve")
    (x1, y1), (x2, y2) = pts[-4], pts[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    for s in (+1, -1):
        a = ang + math.pi + s * math.radians(38)
        d.line([(x2 * S, y2 * S), ((x2 + head * math.cos(a)) * S, (y2 + head * math.sin(a)) * S)],
               fill=255, width=width * S)
    layer = layer.resize((W, H), Image.LANCZOS)
    img.paste(Image.new("RGB", (W, H), WHITE), mask=layer)

# ---------- slides ----------

COVER_BOX = (415, 635)   # tamanho máx da capa do livro (medido na ref)
COVER_CY = 770

def book_slide(title, top, cover_path, bottom, arrow_style="down", seed=0):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    # título longo: encolhe até caber numa linha (mín. 56); se nem assim, quebra e empurra o texto
    size = 84
    while size > 56 and run_width(f"({title})", font(BOLD, size), -0.045 * size) > 980:
        size -= 2
    _, t_end = text_block(img, f"({title})", 78, size, idx=BOLD, track=-0.045, maxw=980)
    _, top_end = text_block(img, top, max(215, t_end + 40), 40, maxw=820)

    cov = Image.open(cover_path).convert("RGB")
    k = min(COVER_BOX[0] / cov.width, COVER_BOX[1] / cov.height)  # amplia também (capa pequena)
    cov = cov.resize((round(cov.width * k), round(cov.height * k)), Image.LANCZOS)
    cx0 = (W - cov.width) // 2
    cy0 = COVER_CY - cov.height // 2
    img.paste(cov, (cx0, cy0))
    # contorno sutil: some em capa clara, separa capa escura do fundo preto
    ImageDraw.Draw(img).rectangle([cx0, cy0, cx0 + cov.width - 1, cy0 + cov.height - 1], outline=(48, 48, 48), width=2)
    cx1, cy1 = cx0 + cov.width, cy0 + cov.height

    b_top, _ = text_block(img, bottom, 1300, 40, maxw=840, anchor="bottom")

    # setas: posições derivadas do layout, como nas variações da ref
    if arrow_style == "down":          # reta pra baixo, do texto até a capa
        x = W / 2
        arrow(img, (x, top_end + 25), (x + 6, top_end + 55), (x - 4, top_end + 85), (x - 2, top_end + 115), seed=seed)
    elif arrow_style == "left":        # sai da esquerda do texto e curva até a lateral da capa
        x = cx0 - 70
        arrow(img, (x, top_end + 20), (x - 30, top_end + 110), (x - 10, cy0 + 40), (cx0 - 14, cy0 + 30), seed=seed)
    elif arrow_style == "right":       # sai da direita do texto, onda, até o canto da capa
        x = cx1 + 60
        arrow(img, (x, top_end + 15), (x + 40, top_end + 70), (x - 30, top_end + 90), (cx1 - 10, cy0 - 18), seed=seed)
    elif arrow_style == "bottom_right":  # sai do canto inferior da capa e desce até o texto de baixo
        arrow(img, (cx1 + 25, cy1 - 30), (cx1 + 45, cy1 + 20), (cx1 + 40, b_top - 50), (cx1 + 20, b_top - 22), seed=seed)
    elif arrow_style == "bottom_left":
        arrow(img, (cx0 - 25, cy1 - 30), (cx0 - 45, cy1 + 20), (cx0 - 40, b_top - 50), (cx0 - 20, b_top - 22), seed=seed)
    return img

def cover_slide(photo, title, rotate=0, focus=(0.5, 0.5), size=112, cy=0.80):
    im = ImageOps.exif_transpose(Image.open(photo)).convert("RGB").rotate(-rotate, expand=True)
    im = ImageOps.fit(im, (W, H), Image.LANCZOS, centering=focus)
    # escurece só a parte de baixo pra ler o título
    grad = Image.linear_gradient("L").resize((W, H))
    grad = grad.point(lambda v: int(max(0, v - 90) * 1.15))
    im.paste(Image.new("RGB", (W, H), (0, 0, 0)), mask=grad)
    f = font(BOLD, size)
    tr = -0.05 * size
    lines = title.split("\n")
    lh = size * 0.98
    y0 = H * cy - lh * len(lines) / 2
    sh = Image.new("L", (W, H), 0)
    ds, d = ImageDraw.Draw(sh), ImageDraw.Draw(im)
    for k, ln in enumerate(lines):
        draw_run(ds, 52, y0 + k * lh + 3, ln, f, tr, 140)
    im.paste(Image.new("RGB", (W, H), (0, 0, 0)), mask=sh.filter(ImageFilter.GaussianBlur(8)))
    for k, ln in enumerate(lines):
        draw_run(d, 52, y0 + k * lh, ln, f, tr, WHITE)
    return im
