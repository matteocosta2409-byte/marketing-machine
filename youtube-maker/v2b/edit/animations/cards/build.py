"""Maker video — 'imagem na palavra-chave' cards (estilo @pathofseb).
Cada card = foto landscape com cantos arredondados + sombra suave, aparece
na parte de baixo do peito (longe do rosto) com um POP de entrada.
Full-frame 1080x1920 RGBA -> qtrle MOV alpha, um por card.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import subprocess, shutil, json

W, H = 1080, 1920
FPS = 30
CW, CH = 390, 277           # tamanho do card (landscape ~3:2) — cabe acima da cabeça
RADIUS = 0                  # retangular (sem cantos arredondados)
CENTER_Y = 1270           # peito (abaixado um pouquinho)
POP_T = 0.14                # duracao do pop-in
SHADOW_BLUR = 34
SHADOW_ALPHA = 150
SHADOW_DY = 16

HERE = Path(__file__).parent
PICK = HERE.parent.parent / "assets" / "cards_pick"

# cards lidos do spec (arquivo, start_in_output, duration) — gerado por map_cards.py
CARDS = [(c["file"], c["start"], c["duration"])
         for c in json.load(open(HERE / "cards_spec.json"))]

def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, w-1, h-1], radius=r, fill=255)
    return m

def make_card_img(fn):
    """Crop-fill foto para CWxCH com cantos arredondados (RGBA)."""
    im = Image.open(PICK / fn).convert("RGB")
    iw, ih = im.size
    s = max(CW/iw, CH/ih)
    im = im.resize((round(iw*s), round(ih*s)), Image.LANCZOS)
    nw, nh = im.size
    im = im.crop(((nw-CW)//2, (nh-CH)//2, (nw-CW)//2+CW, (nh-CH)//2+CH))
    card = Image.new("RGBA", (CW, CH), (0,0,0,0))
    card.paste(im, (0,0))
    card.putalpha(rounded_mask(CW, CH, RADIUS))
    return card

def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3*(x-1)**3 + c1*(x-1)**2

def render_card(fn, dur, outdir):
    base_card = make_card_img(fn)
    # sombra pre-render (rounded rect preto borrado) no tamanho full do card
    shadow_src = Image.new("RGBA", (CW+2*SHADOW_BLUR*2, CH+2*SHADOW_BLUR*2), (0,0,0,0))
    sd = ImageDraw.Draw(shadow_src)
    off = SHADOW_BLUR*2
    sd.rounded_rectangle([off, off, off+CW-1, off+CH-1], radius=RADIUS, fill=(0,0,0,SHADOW_ALPHA))
    shadow_src = shadow_src.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))

    n = round(dur*FPS)
    frames = outdir / "frames"
    if frames.exists(): shutil.rmtree(frames)
    frames.mkdir(parents=True)
    for fi in range(n):
        t = fi/FPS
        prog = min(1.0, t/POP_T)
        scale = 0.72 + (1.0-0.72)*ease_out_back(prog) if prog < 1 else 1.0
        img = Image.new("RGBA", (W, H), (0,0,0,0))
        cw, ch = round(CW*scale), round(CH*scale)
        cx = W//2
        cy = CENTER_Y
        # sombra
        sh = shadow_src.resize((round(shadow_src.width*scale), round(shadow_src.height*scale)), Image.LANCZOS)
        img.alpha_composite(sh, (cx - sh.width//2, cy - sh.height//2 + round(SHADOW_DY*scale)))
        # card
        c = base_card.resize((cw, ch), Image.LANCZOS)
        img.alpha_composite(c, (cx - cw//2, cy - ch//2))
        img.save(frames / f"f_{fi:03d}.png")
    mov = outdir / (Path(fn).stem + ".mov")
    subprocess.run([
        "ffmpeg","-y","-framerate",str(FPS),"-i",str(frames/"f_%03d.png"),
        "-c:v","qtrle","-pix_fmt","argb",str(mov)
    ], check=True, capture_output=True)
    shutil.rmtree(frames)
    return mov.name

if __name__ == "__main__":
    for fn, st, dur in CARDS:
        name = render_card(fn, dur, HERE)
        print(f"  {name}  @ {st}s  dur {dur}s")
    print("cards prontos")
