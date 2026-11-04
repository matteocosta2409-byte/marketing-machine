"""Apps video — ícone do app dá POP toda vez que ele cita o app.

Só o ícone (sem barra branca, sem texto), com cantos arredondados uniformes
e sombra suave, no peito. Full-frame 1080x1920 RGBA -> qtrle MOV alpha.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import subprocess, shutil, json

W, H = 1080, 1920
FPS = 30
ICON = 300                  # lado do ícone
CENTER_Y = 1380             # peito, abaixo do queixo
CORNER = 0.22               # raio dos cantos (fração do lado) — visual de app icon
POP_T = 0.14
SHADOW_BLUR = 26
SHADOW_ALPHA = 140
SHADOW_DY = 14

HERE = Path(__file__).parent
PICK = HERE.parent.parent / "assets" / "icons"

CARDS = json.load(open(HERE / "cards_spec.json"))


def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3*(x-1)**3 + c1*(x-1)**2


def make_icon(fn, size, round_corners=True):
    """Ícone quadrado size x size, RGBA, cantos arredondados se pedido."""
    im = Image.open(PICK / fn).convert("RGBA")
    # encaixa preservando proporção (ícone inteiro, nunca cortado)
    im.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((size-im.width)//2, (size-im.height)//2))
    if round_corners:
        r = int(size*CORNER)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size-1, size-1], radius=r, fill=255)
        # só recorta onde o ícone já é opaco (preserva logos circulares/transparentes)
        a = canvas.getchannel("A")
        canvas.putalpha(Image.composite(a, Image.new("L", (size, size), 0), mask))
    return canvas


def render_icon(fn, dur, outdir, round_corners=True):
    base = make_icon(fn, ICON, round_corners)
    # sombra = silhueta do próprio ícone, borrada
    pad = SHADOW_BLUR*3
    sh_src = Image.new("RGBA", (ICON+2*pad, ICON+2*pad), (0, 0, 0, 0))
    silhouette = Image.new("RGBA", (ICON, ICON), (0, 0, 0, SHADOW_ALPHA))
    silhouette.putalpha(base.getchannel("A").point(lambda v: v*SHADOW_ALPHA//255))
    sh_src.alpha_composite(silhouette, (pad, pad))
    sh_src = sh_src.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))

    n = round(dur*FPS)
    frames = outdir / "frames"
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir(parents=True)
    for fi in range(n):
        t = fi/FPS
        prog = min(1.0, t/POP_T)
        scale = 0.72 + (1.0-0.72)*ease_out_back(prog) if prog < 1 else 1.0
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        s = round(ICON*scale)
        cx, cy = W//2, CENTER_Y
        sh = sh_src.resize((round(sh_src.width*scale), round(sh_src.height*scale)), Image.LANCZOS)
        img.alpha_composite(sh, (cx - sh.width//2, cy - sh.height//2 + round(SHADOW_DY*scale)))
        ic = base.resize((s, s), Image.LANCZOS)
        img.alpha_composite(ic, (cx - s//2, cy - s//2))
        img.save(frames / f"f_{fi:03d}.png")
    mov = outdir / (Path(fn).stem + ".mov")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(frames/"f_%03d.png"),
        "-c:v", "qtrle", "-pix_fmt", "argb", str(mov)
    ], check=True, capture_output=True)
    shutil.rmtree(frames)
    return mov.name


if __name__ == "__main__":
    for c in CARDS:
        name = render_icon(c["file"], c["duration"], HERE, c.get("round", True))
        print(f"  {name}  @ {c['start']}s  dur {c['duration']}s")
    print("ícones prontos")
