"""v3 do arco: v2 (congela viradas de cabeca) + imagens aura ao longo do video todo (estilo ref
instagram.com/reels/DcRdRF3JtH-): uma foto por frase no peito, legenda logo acima; par med+ent no
gancho e no "medico ou empreendedor"; CTA limpo.
Uso: video-use/.venv/bin/python build_v3.py"""
import json, subprocess, re
from pathlib import Path
from PIL import Image

EDIT = Path(__file__).resolve().parent
PROJ = EDIT.parent
IMGS = EDIT / "imgs"
W, H, FPS = 1080, 1920, 30
SRCS = {"main": PROJ / "main.mov", "cta": PROJ / "cta.mov"}

# fim do VIDEO (tempo fonte) em takes onde a cabeca comeca a virar antes do corte
VEND = {1: 28.75, 2: 45.00, 9: 121.86, 19: 274.75, 21: 308.98}

Y0 = 1310            # topo das fotos
RY = Y0 - 50         # topo da faixa de overlay (folga pra sombra/pop)
RH = 520             # altura da faixa
PAIR, GAP = 380, 24  # par lado a lado
SW, SH = 440, 400    # foto unica

# (palavra-gatilho, tempo minimo na saida, imagens) — troca quando ele fala a palavra
BEATS = [
    ("escuta", 0.0, ["med", "ent"]),
    ("senta", 4.0, ["00"]), ("nota", 10.9, ["01"]), ("viciado", 12.2, ["02"]),
    ("revisão", 17.0, ["03"]), ("questões", 19.0, ["04"]), ("disciplina", 23.9, ["05"]),
    ("lista", 27.0, ["06"]), ("difícil", 30.0, ["07"]), ("ninguém", 33.0, ["08"]),
    ("curso", 38.5, ["09"]), ("motor", 41.6, ["10"]), ("seis", 47.0, ["11"]),
    ("construir", 53.0, ["12"]), ("habilidade", 56.7, ["13"]), ("método", 61.0, ["14"]),
    ("ensinar", 67.6, ["15"]), ("muito", 72.2, ["16"]), ("jeito", 74.7, ["17"]),
    ("senta", 77.6, ["18"]), ("constrói", 81.4, ["19"]), ("escolher", 86.3, ["med", "ent"]),
]
SDR = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
       "zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
END_IMAGES = "Oi"  # imagens somem quando comeca o CTA

edl = json.loads((EDIT / "edl.json").read_text())
ranges = edl["ranges"]


def srt_cues():
    out = []
    for b in (EDIT / "master.srt").read_text().strip().split("\n\n"):
        ls = b.split("\n")
        m = re.findall(r"(\d+):(\d+):(\d+),(\d+)", ls[1])
        st, en = [int(h) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000 for h, mi, s, ms in m]
        out.append((st, en, " ".join(ls[2:])))
    return out


def find(cues, word, tmin):
    for st, en, txt in cues:
        if st >= tmin - 0.01 and re.search(rf"(?<!\w){re.escape(word.lower())}(?!\w)", txt.lower()):
            return st
    raise SystemExit(f"nao achei '{word}' depois de {tmin}")


# ponto horizontal do recorte (0=esquerda, 0.5=centro) pra imagens que nao centram bem
FOCUS_X = {"ent": 0.62}


def fit(path, bw, bh):
    """Crop-fill na caixa, cantos RETOS (o Matteo nao quer borda arredondada, nunca)."""
    im = Image.open(path).convert("RGB")
    s = max(bw / im.width, bh / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l = int((im.width - bw) * FOCUS_X.get(Path(path).stem, 0.5))
    t = (im.height - bh) // 2
    return im.crop((l, t, l + bw, t + bh)).convert("RGBA")


def beat_clip(idx, names):
    """1 quadro estatico da faixa RHxW (sem pop: entra em corte seco); o ffmpeg segura o quadro."""
    if len(names) == 2:
        cards = [fit(IMGS / f"{n}.png", PAIR, PAIR) for n in names]
        x0 = (W - (2 * PAIR + GAP)) // 2
        pos = [(x0, Y0 - RY), (x0 + PAIR + GAP, Y0 - RY)]
    else:
        cards = [fit(IMGS / f"{names[0]}.png", SW, SH)]
        pos = [((W - SW) // 2, Y0 - RY)]
    frame = Image.new("RGBA", (W, RH), (0, 0, 0, 0))
    for c, xy in zip(cards, pos):
        frame.alpha_composite(c, xy)
    fdir = EDIT / "beat_frames"
    fdir.mkdir(exist_ok=True)
    out = fdir / f"{idx:02d}.png"
    frame.save(out)
    return out, 0.0


def captions_ass(cues):
    """Legenda inteira em ASS, logo acima das fotos. Estilo PADRAO do Matteo (estilo-legenda-italica):
    Helvetica italica branca, sem caixa, contorno fino + sombra; vertical = FontSize 10@288 -> 67@1920."""
    ts = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Helvetica,67,&H00FFFFFF,&H00FFFFFF,&HC8000000,&H96000000,0,1,0,0,100,100,0,0,1,2.5,2.5,2,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\pos({W // 2},{Y0 - 30})}}{t}"
                for s, e, t in cues) + "\n"
    p = EDIT / "caps_v8.ass"
    p.write_text(ass)
    return p


def render():
    cues = srt_cues()
    starts = [find(cues, w, tmin) for w, tmin, _ in BEATS]
    starts[0] = 0.0
    end_all = find(cues, END_IMAGES, starts[-1])
    names = list(SRCS)
    inputs = []
    for n in names:
        inputs += ["-i", str(SRCS[n])]
    parts, labels = [], []
    for i, r in enumerate(ranges):
        s, e = float(r["start"]), float(r["end"])
        k = names.index(r["source"])
        ve = VEND.get(i, e) if r["source"] == "main" else e
        hold = f",tpad=stop_mode=clone:stop_duration={e - ve:.3f}" if ve < e else ""
        parts.append(f"[{k}:v]trim=start={s:.3f}:end={ve:.3f},setpts=PTS-STARTPTS{hold}[v{i}]")
        parts.append(f"[{k}:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
        labels.append(f"[v{i}][a{i}]")
    parts.append("".join(labels) + f"concat=n={len(ranges)}:v=1:a=1[hdr][cca]")
    # iPhone grava HDR (HLG/BT.2020). Foto da internet e sRGB: colada em video marcado HDR ela
    # satura/avermelha. Converte o video pra SDR BT.709 e cola as fotos na MESMA matriz.
    parts.append(f"[hdr]{SDR}[cv]")
    parts.append("[cca]loudnorm=I=-14:TP=-1:LRA=11[aout]")
    cur = "cv"
    for bi, (w, _, imgs) in enumerate(BEATS):
        a = starts[bi]
        b = starts[bi + 1] if bi + 1 < len(BEATS) else end_all
        mov, plen = beat_clip(bi, imgs)
        k = inputs.count("-i")
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{b - a:.3f}", "-i", str(mov)]
        parts.append(f"[{k}:v]format=rgba,scale=out_color_matrix=bt709:out_range=tv,format=yuva420p,"
                     f"setpts=PTS+{a:.3f}/TB[b{bi}]")
        parts.append(f"[{cur}][b{bi}]overlay=0:{RY}:eof_action=pass[o{bi}]")
        cur = f"o{bi}"
        print(f"  {a:6.2f}-{b:6.2f}  {w:<11} {'+'.join(imgs)}")
    ass = str(captions_ass(cues)).replace(":", r"\:").replace("'", r"\'")
    parts.append(f"[{cur}]ass='{ass}'[outv]")
    (EDIT / "_fc_v8.txt").write_text(";\n".join(parts))
    out = EDIT / "final_v8.mp4"
    r = subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex_script", str(EDIT / "_fc_v8.txt"),
                        "-map", "[outv]", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", "-color_range", "tv", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-movflags", "+faststart", str(out)], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2500:]); raise SystemExit(1)
    print("OK ->", out)


if __name__ == "__main__":
    render()
