#!/usr/bin/env python3
# Carrossel "stack de apps" — capa com foto da pessoa + slides com logo (tile) sobre foto real.
# Pouco texto. Formato 4:5. Logos REAIS entram depois (jogar PNG em carrosseis/logos/<slug>.png).
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

W, H = 1080, 1350
WORK = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(WORK, "..", "output", "apps-saas")
LOGOS = os.path.join(WORK, "..", "logos")
os.makedirs(OUT, exist_ok=True)

WHITE = (255, 255, 255)
GREEN = (61, 169, 79)
GRAY = (205, 205, 205)
FONT_DIR = "/System/Library/Fonts/Supplemental"
def font(name, size): return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
BLACK, BOLD, REG = "Arial Black.ttf", "Arial Bold.ttf", "Arial.ttf"

def load(path): return ImageOps.exif_transpose(Image.open(path))

def cover_crop(img, w, h):
    img = img.convert("RGB")
    ar_t, ar_i = w / h, img.width / img.height
    if ar_i > ar_t: nh, nw = h, int(h * ar_i)
    else: nw, nh = w, int(w / ar_i)
    img = img.resize((nw, nh), Image.LANCZOS)
    return img.crop(((nw - w) // 2, (nh - h) // 2, (nw - w) // 2 + w, (nh - h) // 2 + h))

def darken(img, top=0.45, bottom=0.6, base=0.4):
    ov = Image.new("L", (1, H))
    for y in range(H):
        t = y / H; a = base
        if t < 0.34: a = base + (0.34 - t) / 0.34 * top
        if t > 0.62: a = base + (t - 0.62) / 0.38 * bottom
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

def text_shadow(draw, xy, text, fnt, fill, anchor=None, off=3):
    x, y = xy
    draw.text((x + off, y + off), text, font=fnt, fill=(0, 0, 0), anchor=anchor)
    draw.text((x, y), text, font=fnt, fill=fill, anchor=anchor)

def logo_tile(slug, tile_bg, mark, mark_color, triangle=False, on_tile=False, size=300, radius=58):
    """Usa logo real em logos/<slug>.png se existir; senão monta um tile placeholder."""
    real = os.path.join(LOGOS, slug + ".png")
    if os.path.exists(real):
        lg = load(real).convert("RGBA")
        if on_tile:  # logo (ex: estrela transparente) sobre base arredondada escura
            inner = int(size * 0.64)
            lg.thumbnail((inner, inner), Image.LANCZOS)
            tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            ImageDraw.Draw(tile).rounded_rectangle(
                [0, 0, size - 1, size - 1], radius=radius, fill=tile_bg + (255,))
            tile.alpha_composite(lg, ((size - lg.width) // 2, (size - lg.height) // 2))
            return tile
        lg.thumbnail((size, size), Image.LANCZOS)
        if lg.split()[3].getextrema()[0] == 255:  # logo opaco (quadrado) -> arredonda cantos
            mask = Image.new("L", lg.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                [0, 0, lg.width - 1, lg.height - 1], radius=int(min(lg.size) * 0.22), fill=255)
            lg.putalpha(mask)
        tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        tile.alpha_composite(lg, ((size - lg.width) // 2, (size - lg.height) // 2))
        return tile
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=tile_bg + (255,))
    if triangle:
        cx, cy, s = size // 2, size // 2 + size * 0.04, size * 0.32
        td.polygon([(cx, cy - s), (cx - s * 1.08, cy + s * 0.78), (cx + s * 1.08, cy + s * 0.78)],
                   fill=(255, 255, 255, 255))
    else:
        td.text((size // 2, size // 2 - 6), mark, font=font(BLACK, int(size * 0.58)),
                fill=mark_color + (255,), anchor="mm")
    return tile

def paste_with_shadow(base, tile, xy, radius=58):
    """Sombra que segue o formato real (alpha) do tile/logo."""
    x, y = xy
    alpha = tile.split()[3]
    sh = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(16)).point(lambda a: int(a * 0.5)))
    base.paste(sh, (x + 6, y + 14), sh)
    base.paste(tile, (x, y), tile)

def build_cover(photo, title):
    img = darken(cover_crop(load(photo), W, H), top=0.42, bottom=0.66, base=0.3)
    d = ImageDraw.Draw(img)
    M = 80
    # legendinha no topo explicando a sigla
    text_shadow(d, (M, 110), "SaaS = software as a service", font(BOLD, 30), GREEN, off=2)
    tf = font(BLACK, 64)
    lines = wrap(d, title, tf, W - 2 * M)
    y = H - 250 - len(lines) * 76
    for ln in lines:
        cx = M
        for wd in ln.split():
            col = GREEN if wd.strip(",.").upper() in {"SAAS", "7", "EDUCAÇÃO"} else WHITE
            text_shadow(d, (cx, y), wd, tf, col)
            cx += d.textlength(wd + " ", font=tf)
        y += 76
    sf = font(BOLD, 30)
    cx = M
    for wd in "(a plataforma já tem +360 usuários)".split():
        col = GREEN if "+360" in wd else WHITE
        text_shadow(d, (cx, y + 14), wd, sf, col, off=2)
        cx += d.textlength(wd + " ", font=sf)
    text_shadow(d, (M, y + 64), "arraste  →", font(BOLD, 36), WHITE)
    return img

def build_app(photo, num, name, desc, note, slug, tile_bg, mark, mark_color, triangle=False, on_tile=False):
    img = darken(cover_crop(load(photo), W, H), top=0.5, bottom=0.62, base=0.46)
    d = ImageDraw.Draw(img)
    M = 80
    text_shadow(d, (M, 140), f"{num}. {name}", font(BLACK, 62), WHITE)
    tile = logo_tile(slug, tile_bg, mark, mark_color, triangle, on_tile)
    tx, ty = M, 360
    paste_with_shadow(img, tile, (tx, ty), radius=58)
    by = ty + tile.height + 60
    for ln in wrap(d, desc, font(REG, 42), W - 2 * M):
        text_shadow(d, (M, by), ln, font(REG, 42), WHITE, off=2); by += 54
    if note:
        by += 14
        for ln in wrap(d, note, font(REG, 31), W - 2 * M):
            text_shadow(d, (M, by), ln, font(REG, 31), GRAY, off=2); by += 41
    return img

def build_cta(photo):
    img = darken(cover_crop(load(photo), W, H), top=0.62, bottom=0.62, base=0.52)
    d = ImageDraw.Draw(img)
    cx = W // 2
    text_shadow(d, (cx, H // 2 - 150), "CURTIU?", font(BLACK, 96), WHITE, anchor="mm")
    sf = font(BOLD, 46)
    y = H // 2 - 30
    for ln in wrap(d, "Me segue pra acompanhar os bastidores de quem tá construindo um SaaS de educação!", sf, W - 200):
        text_shadow(d, (cx, y), ln, sf, WHITE, anchor="mm")
        y += 62
    text_shadow(d, (cx, y + 60), "ME SEGUE  →", font(BLACK, 46), GREEN, anchor="mm")
    return img

WK = lambda n: os.path.join(WORK, n)

APPS = [
    dict(photo="setup-estudo-quarto.jpg", num=1, name="antigravity", slug="antigravity",
         desc="atualmente é minha IDE principal pra escrever e organizar o projeto.",
         note="(usei o Cursor um tempo, mas como tenho o plano Pro do Google pra estudantes, dá pra usar o Antigravity de graça)",
         tile_bg=(32, 33, 36), mark="A", mark_color=(138, 180, 248)),
    dict(photo="fastfood-trabalho.jpg", num=2, name="claude code", slug="claude-code",
         desc="o Claude é praticamente um dev sênior, faz tudo: monta o código, organiza o banco de dados, corrige bugs e me ajuda a planejar novas features.",
         note=None, tile_bg=(26, 26, 26), mark="C", mark_color=(217, 119, 87)),
    dict(photo="estudo-noturno-mesa.jpg", num=3, name="supabase", slug="supabase",
         desc="como o SaaS é de educação, uso o Supabase como banco de dados (banco de questões, flashcards...).",
         note=None, tile_bg=(15, 15, 15), mark="S", mark_color=(62, 207, 142)),
    dict(photo="escritorio-trabalho.jpg", num=4, name="vercel", slug="vercel",
         desc="hospedagem da plataforma — deploy rápido e sem dor de cabeça.",
         note=None, tile_bg=(0, 0, 0), mark="", mark_color=(255, 255, 255), triangle=True),
    dict(photo="estudo-cafe-tablet.jpg", num=5, name="posthog", slug="posthog",
         desc="onde eu acompanho as estatísticas e métricas do SaaS em tempo real.",
         note=None, tile_bg=(17, 24, 39), mark="P", mark_color=(52, 211, 153)),
    dict(photo="estudo-matematica-mesa.jpg", num=6, name="gemini", slug="gemini", on_tile=True,
         desc="uso o Deep Research pra pesquisa de mercado e o modo Pro pra ideias no geral — e imagens também.",
         note=None, tile_bg=(26, 28, 46), mark="G", mark_color=(94, 114, 235)),
    dict(photo="calendario-madrugada.jpg", num=7, name="spotify", slug="spotify",
         desc="e por último, uma playlist pra fingir que tô construindo o Facebook 2.",
         note=None, tile_bg=(18, 18, 18), mark="♪", mark_color=(29, 185, 84)),
]

slides = [("00_capa.jpg", build_cover(WK("mirror-selfie-elevador.jpg"),
           "7 apps que eu uso pra construir meu SaaS de educação"))]
for a in APPS:
    slides.append((f"{a['num']:02d}_{a['slug']}.jpg", build_app(
        WK(a["photo"]), a["num"], a["name"], a["desc"], a["note"], a["slug"],
        a["tile_bg"], a["mark"], a["mark_color"], a.get("triangle", False), a.get("on_tile", False))))

slides.append(("08_cta.jpg", build_cta(WK("por-do-sol-cidade.jpg"))))

for name, im in slides:
    im.save(os.path.join(OUT, name), quality=92)
    print("salvo", name)
print("OK", len(slides), "slides")
