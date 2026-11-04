"""Carrossel "desculpa, tenho planos" — cópia do @alizada.r_54 (DbQSaAZABBh).
Capa com 2 textinhos brancos estilo texto nativo do IG; resto só fotos ORIGINAIS (sem grade: o Matteo não quer cor alterada)."""
import glob, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(ROOT, "fotos")
DRIVE = os.path.expanduser("~/Library/CloudStorage/GoogleDrive-matteocosta2409@gmail.com/Meu Drive/2026/Personal Branding/Fotos")
OUT = os.path.join(ROOT, "output", "desculpa-tenho-planos")
W, H = 1080, 1440  # 3:4, igual à ref
TMP = tempfile.mkdtemp()

def src(name):
    hits = glob.glob(os.path.join(FOTOS, name + ".*")) or glob.glob(os.path.join(DRIVE, name + "*"))
    assert hits, name
    p = hits[0]
    if p.lower().endswith((".heic", ".png")):
        j = os.path.join(TMP, os.path.basename(p) + ".jpg")
        subprocess.run(["sips", "-s", "format", "jpeg", p, "--out", j], capture_output=True)
        p = j
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    return im.rotate(-ROTATE.get(name, 0), expand=True)

def fit(im, focus=(0.5, 0.5)):
    return ImageOps.fit(im, (W, H), Image.LANCZOS, centering=focus)

def font(size):
    f = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", size)
    f.set_variation_by_name("Medium")
    return f

def caption(img, text, cy, size=50):
    f = font(size)
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=f)
    x, y = (W - w) / 2, cy - size * 0.6
    sh = Image.new("L", img.size, 0)
    ImageDraw.Draw(sh).text((x, y + 2), text, font=f, fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), mask=sh)
    d.text((x, y), text, font=f, fill="white")

# fotos que vieram deitadas (graus no sentido horário)
ROTATE = {"IMG_9293": 90}

# (foto, alvo de luminância, foco do crop)
COVER = ("setup-estudo-quarto", 52, (0.5, 0.6))
SLIDES = [
    ("138BD1CB", 62, (0.5, 0.5)),         # kindle na mão
    ("900D8803", 62, (0.5, 0.5)),         # bola de handebol + garrafa
    ("A02C6974", 66, (0.5, 0.5)),         # livro aberto
    ("tocando-piano", 55, (0.5, 0.5)),    # piano
    ("IMG_8379", 50, (0.5, 0.5)),         # laptop na mesa de sinuca
    ("IMG_9457", 55, (0.5, 0.5)),         # 2 livros na mesa (Tolstói)
    ("E98472FB", 66, (0.5, 0.5)),         # bolo + café
    ("calendario-madrugada", 30, (0.5, 0.5)),  # 01:36
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    name, l, foc = COVER
    cov = fit(src(name), foc)
    caption(cov, "“desculpa, tenho planos”", int(H * 0.262))
    caption(cov, "planos:", int(H * 0.555))
    cov.save(os.path.join(OUT, "01.jpg"), quality=95)
    for i, (name, l, foc) in enumerate(SLIDES, 2):
        fit(src(name), foc).save(os.path.join(OUT, f"{i:02d}.jpg"), quality=95)
    print("ok", OUT)
