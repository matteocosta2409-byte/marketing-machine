"""Acha os "quadrados pretos" gravados de proposito (tecnica do Altari): cartao/placa preta fosca no quadro
= espaco reservado pro grafico. Eu preencho esse retangulo com motion (Remotion Impacto com "box").
Uso: python find_slots.py <video> [--fps 2] [--min-area 0.03] [--min-dur 2]  -> JSON [{start,end,x,y,w,h}] em px 1080x1920
Criterio: celulas PRETAS (luma<26, faixa TV: preto=16) e LISISSIMAS (desvio<2) -> maior retangulo continuo. Camiseta preta
nao passa (tem dobra/estampa = desvio alto). Precisa durar >= 2s (sombra da camiseta pisca <1.5s;
quadrado de verdade segura a frase toda). Gravar: cartao preto FOSCO, parado, longe da camiseta."""
import json, subprocess, sys
import numpy as np

video = sys.argv[1]
arg = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
fps, min_area, min_dur = arg("--fps", 2.0), arg("--min-area", 0.03), arg("--min-dur", 2.0)
W, H, C = 270, 480, 6          # analise em 270x480, celula 6px
SX = 1080 / W

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale={W}:{H},format=gray",
                      "-f", "rawvideo", "-"], capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)


def largest_rect(mask):
    """Maior retangulo de 1s numa matriz binaria (histograma por linha)."""
    best, hist = (0, 0, 0, 0, 0), np.zeros(mask.shape[1], int)
    for r in range(mask.shape[0]):
        hist = np.where(mask[r], hist + 1, 0)
        stack = []
        for c in range(len(hist) + 1):
            hgt = hist[c] if c < len(hist) else 0
            start = c
            while stack and stack[-1][1] >= hgt:
                start, sh = stack.pop()
                area = sh * (c - start)
                if area > best[0]:
                    best = (area, start, r - sh + 1, c - start, sh)
            stack.append((start, hgt))
    return best


hits = []
for i, f in enumerate(frames):
    g = f[: H // C * C, : W // C * C].reshape(H // C, C, W // C, C)
    mean, std = g.mean(axis=(1, 3)), g.std(axis=(1, 3))
    area, cx, cy, cw, ch = largest_rect((mean < 26) & (std < 2))
    if area * C * C >= min_area * W * H:
        hits.append((i / fps, [round(v * C * SX) for v in (cx, cy, cw, ch)]))

slots = []
for t, box in hits:
    if slots and t - slots[-1]["end"] <= 1.01 / fps and \
            all(abs(a - b) < 60 for a, b in zip(box, [slots[-1][k] for k in "xywh"])):
        slots[-1]["end"] = round(t + 1 / fps, 2)
    else:
        slots.append({"start": round(t, 2), "end": round(t + 1 / fps, 2), **dict(zip("xywh", box))})
slots = [s for s in slots if s["end"] - s["start"] >= min_dur]
print(json.dumps(slots, indent=1))
