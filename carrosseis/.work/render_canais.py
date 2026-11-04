"""Carrossel "canais do youtube que eu usei" — estilo @isaaccutrimm (DbZFUhukfvG).
Foto escura de fundo + card escuro do canal (avatar redondo, nome, @, inscritos · vídeos)
+ frase branca centralizada com **sublinhado** nas palavras-chave. Contador n/N no canto.
Markup: **trecho** = sublinhado, ~trecho~ = itálico (não usa _ por causa de @handles)."""
import os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1350  # 4:5, igual à ref
WORK = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(WORK)
AVATARES = os.path.join(ROOT, "canais", "avatares")
SF, SFI = "/System/Library/Fonts/SFNS.ttf", "/System/Library/Fonts/SFNSItalic.ttf"
EMOJI = "/System/Library/Fonts/Apple Color Emoji.ttc"

def font(size, weight="Semibold", italic=False):
    f = ImageFont.truetype(SFI if italic else SF, size)
    f.set_variation_by_name(weight + (" Italic" if italic else ""))
    return f

def photo(name, focus=(0.5, 0.5)):
    """Foto de .work/ ou fotos/, só recortada 4:5."""
    p = os.path.join(WORK, name + ".jpg")
    if not os.path.exists(p):
        p = os.path.join(ROOT, "fotos", name + ".jpg")
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    im = ImageOps.fit(im, (W, H), Image.LANCZOS, centering=focus)
    return im  # foto original, sem tratamento nenhum (pedido do Matteo: as tratadas ficavam cinza)

# ---------- texto ----------

def tokens(text):
    """'a **b c** _d_' -> [(palavra, sublinhado, itálico)]"""
    out, ul, it = [], False, False
    for part in re.split(r"(\*\*|~)", text):
        if part == "**": ul = not ul; continue
        if part == "~": it = not it; continue
        for w in part.split(" "):
            if w: out.append((w, ul, it))
    return out

def layout(text, size, weight, maxw):
    """Quebra em linhas. Cada linha = lista de (palavra, ul, font, x relativo, largura); retorna (linhas, larguras)."""
    sp = font(size, weight).getlength(" ")
    lines, cur, x = [], [], 0
    for w, ul, it in tokens(text):
        f = font(size, weight, it)
        wl = f.getlength(w)
        if cur and x + sp + wl > maxw and w[0] not in ",.;:!?)":
            lines.append(cur); cur, x = [], 0
        if cur and w[0] not in ",.;:!?)": x += sp
        cur.append((w, ul, f, x, wl)); x += wl
    if cur: lines.append(cur)
    return lines, [ln[-1][3] + ln[-1][4] for ln in lines]

def text(img, txt, y, size=40, weight="Semibold", maxw=900, lead=1.28, align="center", x0=None, shadow=True):
    """Desenha bloco de texto branco; retorna y final."""
    lines, widths = layout(txt, size, weight, maxw)
    lh = size * lead
    mask = Image.new("L", img.size, 0); dm = ImageDraw.Draw(mask)
    for k, (ln, lw) in enumerate(zip(lines, widths)):
        bx = (W - lw) / 2 if align == "center" else x0
        by = y + k * lh
        for i, (w, ul, f, x, wl) in enumerate(ln):
            dm.text((bx + x, by), w, font=f, fill=255)
            if ul:  # sublinhado contínuo até a próxima palavra sublinhada
                end = bx + x + wl
                if i + 1 < len(ln) and ln[i + 1][1]: end = bx + ln[i + 1][3]
                uy = by + size * 1.08
                dm.rectangle([bx + x, uy, end, uy + max(2, size * 0.07)], fill=255)
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 1.6)))
        img.paste((0, 0, 0), mask=sh)
    img.paste((255, 255, 255), mask=mask)
    return y + lh * len(lines)

def counter(img, n, total):
    text(img, f"{n}/{total}", 52, size=32, align="left", x0=W - 70 - font(32).getlength(f"{n}/{total}"), maxw=300)

# ---------- card do canal ----------

def card(img, avatar, name, handle, stats, top=430):
    av_d, pad, gap = 190, 38, 34
    fn, fh, fs = font(52, "Bold"), font(34, "Medium"), font(30, "Medium")
    tw = max(fn.getlength(name), fh.getlength(handle), fs.getlength(stats))
    cw, ch = pad + av_d + gap + tw + 52, 270
    x0 = (W - cw) / 2
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle([x0, top, x0 + cw, top + ch], radius=30, fill=(22, 22, 22, 228))
    img.paste(layer, (0, 0), layer)
    av = ImageOps.fit(Image.open(os.path.join(AVATARES, avatar)).convert("RGB"), (av_d * 2, av_d * 2), Image.LANCZOS)
    m = Image.new("L", av.size, 0); ImageDraw.Draw(m).ellipse([0, 0, av.width - 1, av.height - 1], fill=255)
    av, m = av.resize((av_d, av_d), Image.LANCZOS), m.resize((av_d, av_d), Image.LANCZOS)
    img.paste(av, (int(x0 + pad), int(top + (ch - av_d) / 2)), m)
    d = ImageDraw.Draw(img)
    tx = x0 + pad + av_d + gap
    d.text((tx, top + 52), name, font=fn, fill="white")
    d.text((tx, top + 124), handle, font=fh, fill=(215, 215, 215))
    d.text((tx, top + 176), stats, font=fs, fill=(215, 215, 215))
    return top + ch

# ---------- slides ----------

def channel_slide(bg, n, total, avatar, name, handle, stats, caption, subject=None):
    img = photo(*bg)
    if total:
        counter(img, n, total)
    if subject:
        text(img, subject, 340, size=44, weight="Bold")
    bottom = card(img, avatar, name, handle, stats)
    text(img, caption, bottom + 48, size=40)
    return img

def cover_slide(bg, title, footnote, title_y=150, title_size=64):
    img = photo(*bg)
    text(img, title, title_y, size=title_size, weight="Bold", maxw=960, lead=1.18)
    y = text(img, footnote, 1010, size=36, align="left", x0=56, maxw=520, lead=1.2)
    # ➡️ emoji (fonte de emoji só renderiza em 160px; desenha e reduz)
    e = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((10, 10), "➡️", font=ImageFont.truetype(EMOJI, 160), embedded_color=True)
    e = e.crop(e.getbbox()).resize((96, 96), Image.LANCZOS)
    img.paste(e, (110, int(y + 30)), e)
    return img

def cta_slide(bg, title, body):
    img = photo(*bg)
    y = text(img, title, 560, size=64, weight="Bold", maxw=960)
    for para in body:
        y = text(img, para, y + 40, size=40, maxw=880)
    return img
