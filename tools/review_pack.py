"""Pacote de revisao de um final: checagens automaticas + quadros pro revisor (subagente) olhar.
Uso: python review_pack.py <video.mp4> [--edl edit/edl.json] [--srt edit/master.srt] [--src fonte.mov]
Saida: <pasta do video>/review/  -> review.md (checagens) + hook.jpg, timeline.jpg, ev_*.jpg"""
import json, re, subprocess, sys
from pathlib import Path

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
video = Path(sys.argv[1]).resolve()
arg = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
edl_p = Path(arg("--edl")) if arg("--edl") else video.parent / "edl.json"
srt_p = Path(arg("--srt")) if arg("--srt") else video.parent / "master.srt"
src = arg("--src")
out = video.parent / "review"
out.mkdir(exist_ok=True)


def probe(path, entries):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", entries,
                        "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(r.stdout)["streams"][0]


def ff(*a):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *a], capture_output=True, text=True).stderr


def sheet(name, vf, ss=None, t=None):
    pre = (["-ss", str(ss)] if ss is not None else []) + (["-t", str(t)] if t else [])
    stamp = f"drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=10:y=10:fontsize=44:fontcolor=yellow:box=1:boxcolor=black@0.6"
    ff("-y", *pre, "-i", str(video), "-vf", f"{vf},{stamp},scale=360:-2,tile=6x2", "-frames:v", "1", str(out / name))


checks, warn = [], []
v = probe(video, "stream=width,height,r_frame_rate,color_space,color_primaries,color_transfer")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                           capture_output=True, text=True).stdout)
checks.append(f"- Formato: {v['width']}x{v['height']} @ {v['r_frame_rate']} | {dur:.1f}s")
tags = (v.get("color_space"), v.get("color_primaries"), v.get("color_transfer"))
(checks if tags == ("bt709",) * 3 else warn).append(f"- Cor: {tags} (esperado bt709 x3, senao foto fica vermelha)")
if src:
    sfps = probe(src, "stream=r_frame_rate")["r_frame_rate"]
    (checks if sfps == v["r_frame_rate"] else warn).append(f"- FPS fonte {sfps} vs final {v['r_frame_rate']}")

e = ff("-i", str(video), "-af", "ebur128=peak=true", "-f", "null", "-")
lufs = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", e)[-1])
tp = float(re.findall(r"Peak:\s+(-?[0-9.]+) dBFS", e)[-1])
(checks if abs(lufs + 14) <= 1.0 else warn).append(f"- Loudness: {lufs} LUFS (alvo -14 +-1)")
(checks if tp <= -1.0 else warn).append(f"- True peak: {tp} dBTP (alvo <= -1)")

e = ff("-i", str(video), "-af", "silencedetect=noise=-32dB:d=0.3", "-f", "null", "-")
sil = re.findall(r"silence_start: ([0-9.]+)[\s\S]*?silence_duration: ([0-9.]+)", e)
sil = [(float(a), float(b)) for a, b in sil if float(a) < dur - 1.0]
(checks if not sil else warn).append(f"- Pausas >0.3s (fora do fim): {[(round(a,2), round(b,2)) for a,b in sil] or 'nenhuma'}")

if srt_p.exists():
    cues = re.findall(r"(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)\n(.+)", srt_p.read_text())
    sec = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + float(s[6:].replace(",", "."))
    over = [c[2] for a, b in zip(cues, cues[1:]) if sec(a[1]) > sec(b[0]) for c in [b]]
    txt = " ".join(c[2] for c in cues)
    dup = re.findall(r"\b(\w+) \1\b", txt, re.I)
    (checks if not over else warn).append(f"- Legenda sobreposta (empilha 2 linhas): {over or 'nenhuma'}")
    (checks if not dup else warn).append(f"- Palavra repetida na legenda: {dup or 'nenhuma'}")
    (checks if "Matheus" not in txt else warn).append("- Nome: " + ("'Matheus' na legenda -> trocar por Matteo" if "Matheus" in txt else "ok"))

# quadros: gancho (0-3s a 4fps), video todo, e cada evento (overlay/zoom) do EDL
sheet("hook.jpg", "fps=4", 0, 3)
sheet("timeline.jpg", f"fps=12/{dur:.2f}")
events = []
if edl_p.exists():
    edl = json.loads(edl_p.read_text())
    events = [("ov", o["start_in_output"], Path(o["file"]).stem) for o in edl.get("overlays", [])]
    events += [("zoom", z["start_in_output"], f"x{z['scale']}") for z in edl.get("zooms", [])]
for i, (kind, t, label) in enumerate(events):
    ff("-y", "-ss", f"{max(0, t - 0.2):.2f}", "-i", str(video), "-vf", "fps=6,scale=360:-2,tile=6x1", "-frames:v", "1",
       str(out / f"ev_{i:02d}_{kind}_{label}.jpg"))

md = [f"# Revisao automatica: {video.name}", "", "## OK", *checks, "", "## ATENCAO", *(warn or ["- nada"]), "",
      "## Imagens pro revisor", "- hook.jpg: 0-3s a 4fps (o gancho tem que estar na tela no quadro 0)",
      "- timeline.jpg: 12 quadros do video inteiro",
      *[f"- ev_{i:02d}_*.jpg: {k} '{l}' em {t:.2f}s (6 quadros a partir de t-0.2s)" for i, (k, t, l) in enumerate(events)]]
(out / "review.md").write_text("\n".join(md))
print("\n".join(md))
