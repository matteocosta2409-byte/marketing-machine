"""Colagem de fotos que vai acumulando por palavra-chave (estilo ref DercufHR25s, presets/reels-colagem.md).
Cada palavra -> mais 1 foto entra (corte seco, sem borda, sem pop) do lado das anteriores; o grupo some quando
o proximo grupo da mesma zona entra (ou no "fim"). Gera PNGs tela cheia e grava em edl["overlays"].
Uso: python colagem.py <proj> colagem.json
colagem.json: {"grupos": [
  {"zona": "topo"|"peito", "fim": 3.4 | "palavra" (opcional),
   "itens": [{"img": "/abs/foto.jpg", "palavra": "atleta", "n": 1}, {"img": "...", "t": 1.5}]}]}
Tempos "t" e "fim" numericos = timeline CORTADA. Rodar depois do edl final (ranges) e antes do resync."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageOps
sys.path.insert(0, str(Path(__file__).resolve().parent))
from timeline import word_times, ROOT

ZONAS = {"topo": (0.10, 0.24), "peito": (0.66, 0.22)}   # (y inicial, altura) em fracao de H
VAR = [(1.0, 0.0), (0.86, 0.07), (1.0, 0.02)]            # altura relativa e desce um pouco: colagem nao fica certinha
GAP, MARGEM, LARG_MAX = 0.0, 0.05, 0.46                  # fotos encostadas, como na ref


def frame_size(src):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data=rotation", "-of", "json", src],
                       capture_output=True, text=True).stdout
    st = json.loads(o)["streams"][0]
    w, h = st["width"], st["height"]
    rot = abs(int(next((d.get("rotation", 0) for d in st.get("side_data_list", [])), 0)))
    return (h, w) if rot in (90, 270) else (w, h)


def tempo(proj, it):
    if "t" in it:
        return float(it["t"])
    occ = [o for _, o in word_times(proj, it["palavra"]) if o is not None]
    n = it.get("n", 1)
    if len(occ) < n:
        sys.exit(f"palavra '{it['palavra']}' (ocorrencia {n}) nao esta na timeline cortada")
    return occ[n - 1]


def layout(imgs, W, H, zona):
    y0, hz = ZONAS[zona]
    boxes = []
    for i, im in enumerate(imgs):
        rel, dy = VAR[i % len(VAR)]
        h = hz * H * rel
        w = min(h * im.width / im.height, LARG_MAX * W)
        h = w * im.height / im.width
        boxes.append([w, h, (y0 + dy * hz) * H])
    total = sum(b[0] for b in boxes) + GAP * W * (len(boxes) - 1)
    k = min(1.0, (1 - 2 * MARGEM) * W / total)
    x = (W - total * k) / 2
    out = []
    for w, h, y in boxes:
        out.append((round(x), round(y), round(w * k), round(h * k)))
        x += w * k + GAP * W * k
    return out


proj = sys.argv[1]
edit = ROOT / proj / "edit"
edl = json.loads((edit / "edl.json").read_text())
spec = json.loads(Path(sys.argv[2]).read_text())
W, H = frame_size(list(edl["sources"].values())[0])
total = edl.get("total_duration_s") or sum(float(r["end"]) - float(r["start"]) for r in edl["ranges"])
pasta = edit / "colagem"
pasta.mkdir(exist_ok=True)
for f in pasta.glob("*.png"):
    f.unlink()

grupos = spec["grupos"]
for g in grupos:
    g["_t"] = [tempo(proj, it) for it in g["itens"]]
novos = []
for gi, g in enumerate(grupos):
    if "fim" in g:
        fim = float(g["fim"]) if isinstance(g["fim"], (int, float)) else tempo(proj, {"palavra": g["fim"]})
    else:
        prox = [h["_t"][0] for h in grupos if h["zona"] == g["zona"] and h["_t"][0] > g["_t"][0]]
        fim = min(prox) if prox else g["_t"][-1] + 2.5
    fim = min(fim, total)
    imgs = [ImageOps.exif_transpose(Image.open(it["img"])).convert("RGB") for it in g["itens"]]
    boxes = layout(imgs, W, H, g["zona"])
    for k in range(len(imgs)):
        t0 = g["_t"][k]
        t1 = g["_t"][k + 1] if k + 1 < len(imgs) else fim
        if t1 <= t0:
            continue
        tela = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for im, (x, y, w, h) in zip(imgs[:k + 1], boxes[:k + 1]):
            tela.paste(im.resize((w, h), Image.LANCZOS), (x, y))
        f = pasta / f"g{gi:02d}_{k}.png"
        tela.save(f)
        novos.append({"file": f"edit/colagem/{f.name}", "start_in_output": round(t0, 3), "duration": round(t1 - t0, 3)})

edl["overlays"] = [o for o in edl.get("overlays", []) if "edit/colagem/" not in o["file"]] + novos
(edit / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
print(f"{len(novos)} estados de colagem ({W}x{H}) -> edl.overlays")
