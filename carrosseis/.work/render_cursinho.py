#!/usr/bin/env python3
# Carrossel "notas do iCloud / iMessage" — título bold com contorno + balão verde com horário.
# Tema: como um aluno mediano passou em medicina em 1o lugar (2x). Formato 4:5.
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1080, 1350
WORK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WORK, "..", "output", "cursinho-medicina")
os.makedirs(OUT, exist_ok=True)

WHITE = (255, 255, 255)
GREEN = (52, 168, 83)        # verde iMessage / marca
BLUE = (10, 132, 255)        # azul iMessage
GRAYTS = (235, 235, 235)
FONT_DIR = "/System/Library/Fonts/Supplemental"
def font(name, size): return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
ROUND = "Arial Rounded Bold.ttf"
REG = "Arial.ttf"
BOLD = "Arial Bold.ttf"

def load(path): return ImageOps.exif_transpose(Image.open(path))

def cover_crop(img, w, h, vt=0.5, ht=0.5, zoom=1.0):
    img = img.convert("RGB")
    ar_t, ar_i = w / h, img.width / img.height
    if ar_i > ar_t: nh, nw = h, int(h * ar_i)
    else: nw, nh = w, int(w / ar_i)
    nw, nh = int(nw * zoom), int(nh * zoom)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = max(0, min(nw - w, int((nw - w) * ht)))
    top = max(0, min(nh - h, int((nh - h) * vt)))
    return img.crop((left, top, left + w, top + h))

def darken(img, top=0.55, bottom=0.35, base=0.32):
    ov = Image.new("L", (1, H))
    for y in range(H):
        t = y / H; a = base
        if t < 0.45: a = base + (0.45 - t) / 0.45 * top
        if t > 0.7: a = base + (t - 0.7) / 0.3 * bottom
        ov.putpixel((0, y), int(min(a, 0.92) * 255))
    ov = ov.resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, ov)

def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for wd in text.split():
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=fnt) <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines

def title(d, xy, text, size, fill=WHITE, anchor=None, stroke=5):
    d.text(xy, text, font=font(ROUND, size), fill=fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=(0, 0, 0))

def draw_title_block(img, text, size=78, top=110, M=70):
    d = ImageDraw.Draw(img)
    lines = wrap(d, text, font(ROUND, size), W - 2 * M)
    y = top
    lh = int(size * 1.12)
    for ln in lines:
        title(d, (M, y), ln, size)
        y += lh
    return y + 18

def pill(img, xy, text, size, bg, fg=WHITE, padx=22, pady=12, radius=18):
    d = ImageDraw.Draw(img)
    f = font(BOLD, size)
    tw = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + tw + 2 * padx, y + size + 2 * pady], radius=radius, fill=bg)
    d.text((x + padx, y + pady - 2), text, font=f, fill=fg)
    return y + size + 2 * pady

def bubble(img, x, y, w, text, size=37, fill=GREEN, fg=WHITE, pad=30, radius=38,
           timestamp=None, align="left"):
    d = ImageDraw.Draw(img)
    bf = font(REG, size)
    lines = wrap(d, text, bf, w - 2 * pad)
    lh = int(size * 1.34)
    ts_h = 40 if timestamp else 0
    h = pad * 2 + len(lines) * lh + ts_h
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill)
    ty = y + pad
    for ln in lines:
        d.text((x + pad, ty), ln, font=bf, fill=fg)
        ty += lh
    if timestamp:
        tf = font(BOLD, 26)
        tw = d.textlength(timestamp, font=tf)
        d.text((x + w - pad - tw, y + h - pad - 24), timestamp, font=tf, fill=GRAYTS)
    return y + h

def selection_text(img, text, top, size=46, max_w=W - 150, hl=(40, 120, 70), hl_a=180):
    """Texto centralizado com realce translúcido por linha + alças de seleção (estilo Notes)."""
    d0 = ImageDraw.Draw(img)
    f = font(BOLD, size)
    lines = wrap(d0, text, f, max_w)
    lh = int(size * 1.46)
    cx = W // 2
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    boxes, y = [], top
    for ln in lines:
        tw = d0.textlength(ln, font=f)
        x0 = cx - tw / 2
        od.rounded_rectangle([x0 - 16, y - 6, x0 + tw + 16, y + size + 12], radius=11,
                             fill=hl + (hl_a,))
        boxes.append((x0, tw, y))
        y += lh
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)
    for ln, (x0, tw, yy) in zip(lines, boxes):
        d.text((x0, yy), ln, font=f, fill=WHITE)
    r = 11
    fx, _, fy = boxes[0]
    lx, ltw, ly = boxes[-1]
    d.ellipse([fx - 16 - r, fy - 6 - r, fx - 16 + r, fy - 6 + r], fill=(52, 199, 89))      # alça verde início
    ex, ey = lx + ltw + 16, ly + size + 12
    d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(52, 199, 89))                         # alça verde fim
    return img, y

def notes_bar(img, label="‹ All iCloud"):
    d = ImageDraw.Draw(img)
    d.text((40, 38), label, font=font(BOLD, 34), fill=GREEN)
    # ••• num círculo (extrema direita)
    cx, cy = W - 70, 58
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=WHITE, width=3)
    for dx in (-9, 0, 9):
        d.ellipse([cx + dx - 3, cy - 3, cx + dx + 3, cy + 3], fill=WHITE)
    # ícone de compartilhar (à esquerda do •••)
    sx, sy = W - 150, 60
    d.rounded_rectangle([sx - 16, sy - 4, sx + 16, sy + 24], radius=6, outline=WHITE, width=3)
    d.line([sx, sy - 24, sx, sy + 6], fill=WHITE, width=3)
    d.line([sx - 9, sy - 14, sx, sy - 25], fill=WHITE, width=3)
    d.line([sx + 9, sy - 14, sx, sy - 25], fill=WHITE, width=3)

# ---------- SLIDES ----------
def build_cover(photo, ttl, caption=None, vt=0.0, ht=0.5, zoom=1.0):
    img = darken(cover_crop(load(photo), W, H, vt=vt, ht=ht, zoom=zoom),
                 top=0.5, bottom=0.32, base=0.3)
    notes_bar(img, "‹ All iCloud")
    d = ImageDraw.Draw(img)
    size = 64
    f = font(BOLD, size)
    lines = wrap(d, ttl, f, W - 2 * 70)
    y = 120
    lh = int(size * 1.18)
    for ln in lines:                      # branco limpo + sombra suave (sem contorno grosso)
        d.text((73, y + 3), ln, font=f, fill=(0, 0, 0))
        d.text((70, y), ln, font=f, fill=WHITE)
        y += lh
    d.text((70, H - 100), "arraste  →", font=font(BOLD, 36), fill=WHITE,
           stroke_width=4, stroke_fill=(0, 0, 0))
    return img

def build_slide(photo, ttl, body, timestamp=None, tag=None, tag_bg=(230, 57, 70)):
    img = darken(cover_crop(load(photo), W, H), top=0.6, bottom=0.34, base=0.36)
    y = draw_title_block(img, ttl, size=76, top=110)
    if tag:
        y = pill(img, (70, y), tag, 30, tag_bg) + 26
    else:
        y += 18
    img, _ = selection_text(img, body, y)
    return img

def build_cta(photo, ttl, lines):
    img = darken(cover_crop(load(photo), W, H), top=0.5, bottom=0.6, base=0.42)
    draw_title_block(img, ttl, size=86, top=110)
    # balões azuis alinhados à direita
    d = ImageDraw.Draw(img)
    y = 560
    for ln in lines:
        bf = font(BOLD, 40)
        tw = d.textlength(ln, font=bf)
        bw = tw + 56
        x = W - 70 - bw
        d.rounded_rectangle([x, y, x + bw, y + 78], radius=39, fill=GREEN)
        d.text((x + 28, y + 18), ln, font=bf, fill=WHITE)
        y += 96
    d.text((70, H - 150), "me segue  →", font=font(BOLD, 40), fill=WHITE,
           stroke_width=4, stroke_fill=(0, 0, 0))
    return img

WK = lambda n: os.path.join(WORK, n)

slides = [
    ("00_capa.jpg", build_cover(WK("selfie-elevador-vermelho.jpg"),
        "Como um aluno medíocre passou em MEDICINA em 1º lugar (2x)",
        vt=0.0, ht=0.16, zoom=1.16)),
    ("01_planejamento.jpg", build_slide(WK("calendario-estudos-tablet.jpg"),
        "Eu planejei cada dia",
        "Mapeei todas as provas e revisões num calendário. Eu nunca sentava pra estudar sem saber exatamente o que fazer — isso mata a procrastinação de ficar decidindo.",
        timestamp="revisado todo domingo")),
    ("02_recall.jpg", build_slide(WK("cadernos-escritos.jpg"),
        "Escrevi até gravar",
        "Esqueci o 'ler e grifar'. Eu fechava o material e reescrevia de cabeça. Se eu não conseguia explicar no papel, era porque eu não sabia de verdade.")),
    ("03_questoes.jpg", build_slide(WK("questoes-monitor.jpg"),
        "Questão é o jogo real",
        "Teoria é só o aquecimento. Eu resolvia questão atrás de questão e revisava TODO erro num caderno separado. A prova premia quem treinou o formato dela.",
        timestamp="2h por dia, no mínimo")),
    ("04_constancia.jpg", build_slide(WK("biblioteca-cursinho.jpg"),
        "Constância > surto",
        "Não era maratona de 12h uma vez por semana. Era todo dia, no mesmo lugar, sem depender de motivação. A biblioteca virou meu segundo quarto.",
        timestamp="07:00 - 22:00")),
    ("05_revisao.jpg", build_slide(WK("material-do-not-touch.jpg"),
        "Revisão espaçada",
        "Revisei cada conteúdo em 24h, 7 dias e 30 dias. É o que tira a matéria da memória de curto prazo e fixa de vez. Sem isso, você estuda pra esquecer.",
        timestamp="24h · 7d · 30d")),
    ("06_aprovado.jpg", build_cta(WK("aprovado-trote-farinha.jpg"),
        "1º lugar. Duas vezes.",
        ["Comenta \"MÉTODO\"", "que eu te mando o passo a passo", "e me segue!"])),
]

for name, im in slides:
    im.save(os.path.join(OUT, name), quality=92)
    print("salvo", name)
print("OK", len(slides), "slides")
