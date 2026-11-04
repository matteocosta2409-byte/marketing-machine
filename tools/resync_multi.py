"""Render MULTI-fonte: trim+concat (sync travado) de N fontes + legenda queimada. Uso: python resync_multi.py <proj>"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdr import sdr_chain, OUT_TAGS

proj = Path("/Users/mac-matteo/marketing machine") / sys.argv[1]
edit = proj / "edit"
edl = json.loads((edit / "edl.json").read_text())
srcs = edl["sources"]
ranges = edl["ranges"]
style = edl.get("subtitle_style", "")
srt = edit / "master.srt"

names = list(srcs.keys())
idx = {n: i for i, n in enumerate(names)}
inputs = []
for n in names:
    inputs += ["-i", srcs[n]]

parts, labels = [], []
for i, r in enumerate(ranges):
    s, e = float(r["start"]), float(r["end"])
    k = idx[r["source"]]
    parts.append(f"[{k}:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]")
    parts.append(f"[{k}:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
    labels.append(f"[v{i}][a{i}]")
n = len(ranges)
parts.append("".join(labels) + f"concat=n={n}:v=1:a=1[cv0][cca]")
parts.append(f"[cv0]{sdr_chain(srcs[names[0]])}[cv]")  # HDR do iPhone -> SDR BT.709
parts.append("[cca]loudnorm=I=-14:TP=-1:LRA=11[aout]")
srt_esc = str(srt.resolve()).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
parts.append(f"[cv]subtitles='{srt_esc}':force_style='{style}'[outv]")

(edit / "_fc_multi.txt").write_text(";".join(parts))
out = edit / "final_sync.mp4"
cmd = ["ffmpeg", "-y", *inputs, "-filter_complex_script", str(edit / "_fc_multi.txt"),
       "-map", "[outv]", "-map", "[aout]",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", *OUT_TAGS, "-r", "30",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ERRO:\n", r.stderr[-2000:]); raise SystemExit(1)
print("OK ->", out)
