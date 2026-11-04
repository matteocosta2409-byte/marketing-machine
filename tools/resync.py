"""Render single-source: trim+concat (sync travado) + overlays + SFX + legenda queimada. Uso: python resync.py <proj>
Opcional no edl.json (tempos na timeline CORTADA):
  "overlays": [{"file": "edit/motion/x70.mov", "start_in_output": 9.1}]   # MOV com alpha, tela cheia
              {"file": "edit/motion/titulo.png", "start_in_output": 0, "duration": 23.8}  # PNG parado (titulo)
  "sfx":      [{"file": "/.../assets/sfx/pop.wav", "time": 9.1, "db": -6}]
Ordem do grafo: corte -> SDR -> overlays -> legenda (legenda sempre por cima)."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdr import sdr_chain, OUT_TAGS, RGBA_709

proj = Path("/Users/mac-matteo/marketing machine") / sys.argv[1]
edit = proj / "edit"
edl = json.loads((edit / "edl.json").read_text())
src = list(edl["sources"].values())[0]
ranges = edl["ranges"]
style = edl.get("subtitle_style", "")
srt = edit / "master.srt"

parts, labels = [], []
for i, r in enumerate(ranges):
    s, e = float(r["start"]), float(r["end"])
    parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]")
    parts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
    labels.append(f"[v{i}][a{i}]")
n = len(ranges)
parts.append("".join(labels) + f"concat=n={n}:v=1:a=1[cv0][cca]")
parts.append(f"[cv0]{sdr_chain(src)}[cv]")  # HDR do iPhone -> SDR BT.709

inputs, n_in = ["-i", src], 1
overlays, sfx = edl.get("overlays", []), edl.get("sfx", [])
vlast = "cv"
for j, ov in enumerate(overlays):
    k, n_in = n_in, n_in + 1
    f = str(proj / ov["file"]) if not ov["file"].startswith("/") else ov["file"]
    if f.endswith(".png"):
        inputs += ["-loop", "1", "-t", str(ov.get("duration", edl.get("total_duration_s", 60))), "-i", f]
    else:
        inputs += ["-i", f]
    t = float(ov["start_in_output"])
    conv = RGBA_709 if f.endswith(".png") else "format=yuva420p"  # PNG e sRGB: matriz BT.709 (senao avermelha)
    parts.append(f"[{k}:v]{conv},setpts=PTS-STARTPTS+{t:.3f}/TB[ov{j}]")
    parts.append(f"[{vlast}][ov{j}]overlay=0:0:eof_action=pass:format=auto[vo{j}]")
    vlast = f"vo{j}"

alast = "cca"
if sfx:
    mix = ["[cca]"]
    for j, fx in enumerate(sfx):
        k, n_in = n_in, n_in + 1
        inputs += ["-i", fx["file"]]
        ms = int(float(fx["time"]) * 1000)
        parts.append(f"[{k}:a]aresample=48000,volume={fx.get('db', -6)}dB,adelay={ms}|{ms}[fx{j}]")
        mix.append(f"[fx{j}]")
    parts.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0[amx]")
    alast = "amx"
parts.append(f"[{alast}]loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
srt_esc = str(srt.resolve()).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
parts.append(f"[{vlast}]subtitles='{srt_esc}':force_style='{style}'[outv]")

(edit / "_fc.txt").write_text(";".join(parts))
out = edit / "final_sync.mp4"
cmd = ["ffmpeg", "-y", *inputs, "-filter_complex_script", str(edit / "_fc.txt"),
       "-map", "[outv]", "-map", "[aout]",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", *OUT_TAGS, "-r", "30",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ERRO:\n", r.stderr[-2000:]); raise SystemExit(1)
print("OK ->", out)
