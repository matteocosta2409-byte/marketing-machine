#!/usr/bin/env python3
# Carrossel acadêmico — ação de extensão sobre Doença de Chagas num colégio público (Ceilândia-DF).
# Estilo editorial limpo: foto escurecida + kicker verde no topo + frase branca embaixo. 4:5.
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1080, 1350
WORK = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(WORK, "..", "chagas")
OUT = os.path.join(WORK, "..", "output", "chagas-extensao")
os.makedirs(OUT, exist_ok=True)

WHITE = (255, 255, 255)
GREEN = (60, 178, 100)        # verde marca (saúde/biologia, legível sobre foto)
GREEND = (38, 120, 70)        # verde escuro p/ barra
GRAY = (210, 210, 210)
FONT_DIR = "/System/Library/Fonts/Supplemental"
def font(name, size): return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
BLACK, BOLD, REG = "Arial Black.ttf", "Arial Bold.ttf", "Arial.ttf"

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

def darken(img, top=0.45, bottom=0.7, base=0.4):
    ov = Image.new("L", (1, H))
    for y in range(H):
        t = y / H; a = base
        if t < 0.34: a = base + (0.34 - t) / 0.34 * top
        if t > 0.55: a = base + (t - 0.55) / 0.45 * bottom
        ov.putpixel((0, y), int(min(a, 0.94) * 255))
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

def shadow(d, xy, text, fnt, fill, anchor=None, off=3):
    x, y = xy
    d.text((x + off, y + off), text, font=fnt, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), text, font=fnt, fill=fill, anchor=anchor)

def kicker(img, text, M=80, y=96):
    """Etiqueta verde no topo: barrinha + texto em caixa alta."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([M, y + 6, M + 46, y + 16], radius=5, fill=GREEN)
    shadow(d, (M + 64, y - 4), text.upper(), font(BOLD, 30), GREEN, off=2)

def page_dot(img, idx, total, M=80, y=104):
    d = ImageDraw.Draw(img)
    shadow(d, (W - M, y - 6), f"{idx:02d} / {total:02d}", font(BOLD, 28), WHITE,
           anchor="ra", off=2)

# logo UnB carimbado no rodapé de toda página (procura unb.png em chagas/ ou logos/)
_UNB = None
for _p in (os.path.join(FOTOS, "unb.png"), os.path.join(WORK, "..", "logos", "unb.png")):
    if os.path.exists(_p): _UNB = _p; break

def stamp_unb(img, h=78, M=72, yt=82):
    if not _UNB: return
    lg = load(_UNB).convert("RGBA")
    lg.thumbnail((h * 4, h), Image.LANCZOS)
    x, y = W - M - lg.width, yt
    # sombra leve seguindo o alpha pra logo aparecer sobre foto clara/escura
    sh = Image.new("RGBA", lg.size, (0, 0, 0, 0))
    sh.putalpha(lg.split()[3].filter(ImageFilter.GaussianBlur(7)).point(lambda a: int(a * 0.55)))
    img.paste(sh, (x + 2, y + 4), sh)
    img.paste(lg, (x, y), lg)

# ---------- SLIDES ----------
def build_cover(photo, line1, line2, sub, vt=0.5, ht=0.5, zoom=1.0):
    img = darken(cover_crop(load(photo), W, H, vt, ht, zoom), top=0.4, bottom=0.78, base=0.4)
    d = ImageDraw.Draw(img)
    M = 80
    kicker(img, "Projeto de extensão", y=96)
    stamp_unb(img)
    # título grande embaixo
    f = font(BLACK, 78)
    lines = wrap(d, line1 + " " + line2, f, W - 2 * M)
    lh = 90
    y = H - 300 - len(lines) * lh
    for ln in lines:
        cx = M
        for wd in ln.split():
            col = GREEN if wd.strip(",.").upper() in {"CHAGAS"} else WHITE
            shadow(d, (cx, y), wd, f, col)
            cx += d.textlength(wd + " ", font=f)
        y += lh
    for ln in wrap(d, sub, font(BOLD, 34), W - 2 * M):
        shadow(d, (M, y + 18), ln, font(BOLD, 34), GRAY, off=2); y += 44
    shadow(d, (M, H - 96), "arraste  →", font(BOLD, 34), WHITE, off=2)
    return img

def build_slide(photo, tag, text, idx, total, vt=0.5, ht=0.5, zoom=1.0):
    img = darken(cover_crop(load(photo), W, H, vt, ht, zoom), top=0.4, bottom=0.74, base=0.42)
    d = ImageDraw.Draw(img)
    M = 80
    kicker(img, tag, y=96)
    stamp_unb(img)
    f = font(BOLD, 52)
    lines = wrap(d, text, f, W - 2 * M)
    lh = 66
    y = H - 150 - len(lines) * lh
    # barrinha verde à esquerda do bloco de texto
    d.rounded_rectangle([M, y + 4, M + 8, y + len(lines) * lh - 14], radius=4, fill=GREEN)
    for ln in lines:
        shadow(d, (M + 34, y), ln, f, WHITE, off=2)
        y += lh
    return img

def build_end(photo, title, text, vt=0.5, ht=0.5, zoom=1.0):
    img = darken(cover_crop(load(photo), W, H, vt, ht, zoom), top=0.55, bottom=0.7, base=0.5)
    d = ImageDraw.Draw(img)
    M = 80
    kicker(img, "Extensão universitária", y=96)
    stamp_unb(img)
    f = font(BLACK, 60)
    lines = wrap(d, title, f, W - 2 * M)
    lh = 72
    y = H - 360 - len(lines) * lh
    for ln in lines:
        cx = M
        for wd in ln.split():
            col = GREEN if wd.strip(",.").upper() in {"SAÚDE"} else WHITE
            shadow(d, (cx, y), wd, f, col)
            cx += d.textlength(wd + " ", font=f)
        y += lh
    for ln in wrap(d, text, font(BOLD, 36), W - 2 * M):
        shadow(d, (M, y + 14), ln, font(BOLD, 36), GRAY, off=2); y += 48
    return img

WK = lambda n: os.path.join(FOTOS, n)
TOTAL = 7

slides = [
    ("00_capa.jpg", build_cover(WK("apresentacao-ciclo.jpeg"),
        "Levamos a doença de", "Chagas pra sala de aula",
        "Colégio em Ceilândia-DF • 2º ano do ensino médio",
        vt=0.45, ht=0.5, zoom=1.05)),
    ("01_contexto.jpg", build_slide(WK("plateia-colegio.jpeg"), "A ação",
        "Fomos a um colégio em Ceilândia conversar com alunos do 2º ano do ensino médio.",
        2, TOTAL, vt=0.4)),
    ("02_apresentacao.jpg", build_slide(WK("apresentacao-ciclo-2.jpeg"), "A doença",
        "Apresentamos a doença de Chagas: uma realidade ainda presente no Brasil, mas pouco falada.",
        3, TOTAL, vt=0.45)),
    ("03_encenacao.jpg", build_slide(WK("encenacao-mesa.jpeg"), "A encenação",
        "Encenamos o ciclo biológico do protozoário, mostrando o papel do barbeiro na transmissão.",
        4, TOTAL, vt=0.4)),
    ("04_social.jpg", build_slide(WK("interacao-aluno-mesa.jpeg"), "O contexto social",
        "Explicamos como moradia precária e saneamento tornam algumas comunidades mais vulneráveis.",
        5, TOTAL, vt=0.4)),
    ("05_dialogo.jpg", build_slide(WK("interacao-turma.jpeg"), "De perto",
        "Tiramos dúvidas e transformamos conteúdo de faculdade em conversa real com os estudantes.",
        6, TOTAL, vt=0.35, ht=0.45)),
    ("06_equipe.jpg", build_end(WK("equipe-roda.jpeg"),
        "Levar ciência pra fora da universidade também é cuidar da saúde da população.",
        "Obrigado à escola e a todos os alunos que participaram.",
        vt=0.45, zoom=1.02)),
]

for name, im in slides:
    im.save(os.path.join(OUT, name), quality=92)
    print("salvo", name)
print("OK", len(slides), "slides")
