#!/usr/bin/env python3
# Motor de carrossel — foto real de fundo + texto branco com destaque verde musgo.
# Formato 4:5 (1080x1350). Estilo inspirado em carrossel "roadmap" de tech.
# Recursos: cover-crop, escurecimento com gradiente, texto com sombra, auto-fit do título,
#           recortes "colados" (borda branca + rotação + sombra), slide de CTA.
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

def load(path):
    """Abre a foto já aplicando a orientação EXIF (corrige fotos 'deitadas')."""
    return ImageOps.exif_transpose(Image.open(path))

W, H = 1080, 1350
WORK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WORK, "..", "output", "conciliar-vida-v3")
os.makedirs(OUT, exist_ok=True)

WHITE = (255, 255, 255)
GREEN = (61, 169, 79)        # verde musgo (brilho ajustado p/ legibilidade sobre foto escura)

FONT_DIR = "/System/Library/Fonts/Supplemental"
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

BLACK = "Arial Black.ttf"
BOLD = "Arial Bold.ttf"
REG = "Arial.ttf"

def cover_crop(img, w, h):
    img = img.convert("RGB")
    ar_t, ar_i = w / h, img.width / img.height
    if ar_i > ar_t:
        nh = h; nw = int(h * ar_i)
    else:
        nw = w; nh = int(w / ar_i)
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))

def darken(img, top=0.45, bottom=0.80, base=0.30):
    """Escurece a foto: overlay base + gradiente mais forte em cima e embaixo (onde fica texto)."""
    ov = Image.new("L", (1, H))
    for y in range(H):
        t = y / H
        a = base
        if t < 0.40: a = base + (0.40 - t) / 0.40 * top
        if t > 0.62: a = base + (t - 0.62) / 0.38 * bottom
        ov.putpixel((0, y), int(min(a, 0.92) * 255))
    ov = ov.resize((W, H))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(black, img, ov)

def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines

def text_shadow(draw, xy, text, fnt, fill, anchor=None, off=3):
    x, y = xy
    draw.text((x + off, y + off), text, font=fnt, fill=(0, 0, 0), anchor=anchor)
    draw.text((x, y), text, font=fnt, fill=fill, anchor=anchor)

def paste_cutout(base, path, center, width, angle, ratio=(4, 3), border=14):
    """Cola uma foto recortada com borda branca, rotação e sombra (estilo adesivo)."""
    h = int(width * ratio[1] / ratio[0])
    img = cover_crop(load(path), width, h)
    framed = Image.new("RGB", (width + 2 * border, h + 2 * border), (248, 248, 248))
    framed.paste(img, (border, border))
    rot = framed.convert("RGBA").rotate(angle, expand=True, resample=Image.BICUBIC)
    alpha = rot.split()[3]
    # sombra
    shadow = Image.new("RGBA", rot.size, (0, 0, 0, 0))
    shadow.putalpha(alpha.filter(ImageFilter.GaussianBlur(11)).point(lambda a: int(a * 0.55)))
    cx, cy = center
    ox, oy = int(cx - rot.width / 2), int(cy - rot.height / 2)
    base.paste(shadow, (ox + 8, oy + 12), shadow)
    base.paste(rot, (ox, oy), rot)
    return base

# ---------- SLIDES ----------
def build_cover(photo):
    img = darken(cover_crop(load(photo), W, H), top=0.55, bottom=0.55, base=0.38)
    d = ImageDraw.Draw(img)
    M = 80
    text_shadow(d, (M, 150), "A ROTINA DE QUEM FAZ TUDO AO MESMO TEMPO", font(BOLD, 34), GREEN)
    title = "COMO EU CONCILIO MEDICINA, EMPREENDEDORISMO, TREINO E VIDA SOCIAL"
    size = 86
    while size > 40:
        tf = font(BLACK, size)
        if max(d.textlength(w, font=tf) for w in title.split()) <= W - 2 * M:
            break
        size -= 2
    tf = font(BLACK, size)
    lines = wrap(d, title, tf, W - 2 * M)
    y, line_h = 210, int(size * 1.12)
    highlight = {"MEDICINA", "TREINO", "SOCIAL"}
    for ln in lines:
        cx = M
        for wd in ln.split():
            col = GREEN if wd.strip(",.") in highlight else WHITE
            text_shadow(d, (cx, y), wd, tf, col)
            cx += d.textlength(wd + " ", font=tf)
        y += line_h
    text_shadow(d, (M, H - 150), "arraste  →", font(BOLD, 36), WHITE)
    return img

def build_slide(photo, num, heading, body, focus_top=True, body_size=40, cutouts=None):
    img = darken(cover_crop(load(photo), W, H), top=0.60, bottom=0.55, base=0.42)
    d = ImageDraw.Draw(img)
    M = 80
    y = 150 if focus_top else 720
    text_shadow(d, (M, y), num, font(BLACK, 150), GREEN)
    hf = font(BLACK, 56)
    hy = y + 170
    for ln in wrap(d, heading, hf, W - 2 * M):
        text_shadow(d, (M, hy), ln, hf, WHITE)
        hy += 64
    bf = font(REG, body_size)
    by = hy + 24
    for ln in wrap(d, body, bf, W - 2 * M):
        text_shadow(d, (M, by), ln, bf, WHITE, off=2)
        by += int(body_size * 1.28)
    for c in (cutouts or []):
        paste_cutout(img, c["path"], c["center"], c["width"], c["angle"],
                     c.get("ratio", (4, 3)), c.get("border", 14))
    return img

def build_cta(photo):
    img = darken(cover_crop(load(photo), W, H), top=0.62, bottom=0.62, base=0.52)
    d = ImageDraw.Draw(img)
    cx = W // 2
    text_shadow(d, (cx, H // 2 - 150), "CURTIU A DICA?", font(BLACK, 84), WHITE, anchor="mm")
    sf = font(BOLD, 46)
    y = H // 2 - 30
    for ln in wrap(d, "Me segue pra acompanhar mais dessa rotina corrida!", sf, W - 200):
        text_shadow(d, (cx, y), ln, sf, WHITE, anchor="mm")
        y += 62
    text_shadow(d, (cx, y + 60), "ME SEGUE  →", font(BLACK, 46), GREEN, anchor="mm")
    return img

WK = lambda n: os.path.join(WORK, n)

slides = []
slides.append(("01_capa.jpg", build_cover(WK("treino-academia-halter.jpg"))))
slides.append(("02_empreendedorismo.jpg", build_slide(
    WK("calendario-madrugada.jpg"), "1",
    "O ALMOÇO VIRA REUNIÃO",
    "Me reúno com meus 2 sócios no almoço, segunda e quarta, das 12h às 14h — na própria faculdade, já que eles são da minha turma. Aquele tempo morto vira 4h por semana 100% na empresa. Fora o fim de semana.", focus_top=False)))
slides.append(("03_treino.jpg", build_slide(
    WK("equipe-jogos.jpg"), "2",
    "SEMPRE TENTO FAZER ATIVIDADE FÍSICA 5X NA SEMANA",
    "Handebol 2x por semana à noite e academia mais 3x — sexta, sábado e domingo. O fim de semana, quando a galera para, é exatamente quando eu treino. Uso o tempo que está disponível.", focus_top=False)))
slides.append(("04_social.jpg", build_slide(
    WK("casal-selfie.jpg"), "3",
    "PRESENÇA É ESCOLHA",
    "Não dá pra ir em toda festa — então eu escolho. Priorizo minha namorada, minha família e os amigos que importam de verdade. Tempo de qualidade com quem gosta de você é inegociável.", focus_top=False)))
slides.append(("05_medicina.jpg", build_slide(
    WK("biblioteca-estantes.jpg"), "4",
    "NÃO É QUANTIDADE, É EFICIÊNCIA",
    "Sendo sincero: não consigo estudar o tanto que eu gostaria — então tenho todas as minhas provas mapeadas no calendário e destino horários específicos de estudo, pra não me comprometer com nada antes deles. Algo que ajuda muito é estudar na biblioteca pós-aula com a minha namorada: tenho um tempo com ela e estudo ao mesmo tempo. Outra dica é otimizar ao máximo — peço pra IA gerar os flashcards e ganho material de revisão sem gastar o tempo de fazer os cards, que demora muito.",
    body_size=33,
    cutouts=[
        {"path": WK("calendario-madrugada.jpg"), "center": (310, 1175), "width": 380, "angle": 0, "ratio": (4, 3), "border": 0},
        {"path": WK("estudo-biblioteca-grupo.jpg"), "center": (740, 1090), "width": 330, "angle": 0, "ratio": (3, 4), "border": 0},
    ])))
slides.append(("06_cta.jpg", build_cta(WK("por-do-sol-cidade.jpg"))))

for name, im in slides:
    p = os.path.join(OUT, name)
    im.save(p, quality=92)
    print("salvo", name)
print("OK", len(slides), "slides")
