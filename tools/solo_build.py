"""Builder single-source: corta KILLS + silencio -> edl.json (legenda italica padrao).
Uso: python solo_build.py <proj> <kills_json>   ex: solo_build.py solo_frac '[[22.0,28.8]]'"""
import json, re, subprocess, sys, glob
from pathlib import Path

proj = Path("/Users/mac-matteo/marketing machine") / sys.argv[1]
EDIT = proj / "edit"
SRC = proj / "src.mov"
KILLS = json.loads(sys.argv[2]) if len(sys.argv) > 2 else []
GAP, PAD, KEEP = 0.30, 0.04, 0.06

# ESTILO PADRAO (igual YouTube do Matteo): branca, italica, rodape, sem caixa
STYLE = ("FontName=Helvetica,FontSize=15,Bold=0,Italic=1,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&HC8000000,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV=60")


def is_vertical(path):
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                      "stream=width,height:stream_side_data=rotation", "-of", "json", str(path)],
                                     capture_output=True, text=True).stdout)["streams"][0]
    w, h = info["width"], info["height"]
    if any(abs(sd.get("rotation", 0)) == 90 for sd in info.get("side_data_list", [])):
        w, h = h, w
    return h > w


# vertical (Reels 2160x3840): libass escala pela altura -> 10/45 e o tamanho aprovado
if is_vertical(SRC):
    STYLE = STYLE.replace("FontSize=15", "FontSize=10").replace("MarginV=60", "MarginV=45")


def killed(t):
    return any(a <= t < b for a, b in KILLS)


err = subprocess.run(["ffmpeg", "-i", str(SRC), "-af", "silencedetect=noise=-32dB:d=0.18",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
sils, cur = [], None
for m in re.finditer(r"silence_(start|end):\s*([0-9.]+)", err):
    if m.group(1) == "start":
        cur = float(m.group(2))
    elif cur is not None:
        sils.append((cur, float(m.group(2)))); cur = None

words = [w for w in json.loads(Path(glob.glob(str(EDIT / "transcripts/*.json"))[0]).read_text())["words"]
         if w.get("type") == "word" and w.get("start") is not None]
kept = []
for w in words:
    if killed(w["start"]):
        continue
    end = w["end"]
    for a, b in KILLS:
        if w["start"] < a < end:
            end = a
    kept.append({"start": w["start"], "end": end})

def gap_killed(a0, b0):
    # True se existe um KILL sobrepondo a lacuna (a0,b0) entre duas palavras mantidas
    return any(a < b0 and b > a0 for a, b in KILLS)


segs = []
s = kept[0]["start"] - PAD
prev = kept[0]["end"]
for w in kept[1:]:
    if w["start"] - prev >= GAP or gap_killed(prev, w["start"]):
        segs.append([s, prev + PAD]); s = w["start"] - PAD
    prev = max(prev, w["end"])
segs.append([s, prev + PAD])

ranges = []
for a0, b0 in segs:
    for a, b in sils:
        if a - 0.01 <= a0 < b:
            a0 = max(a0, b - KEEP)
        if a < b0 <= b + 0.01:
            b0 = min(b0, a + KEEP)
    cur2 = a0
    for a, b in sorted(sils):
        if a0 < a and b < b0 and (b - a) >= GAP:
            if a + KEEP - cur2 >= 0.12:
                ranges.append([round(cur2, 3), round(a + KEEP, 3)])
            cur2 = b - KEEP
    if b0 - cur2 >= 0.12:
        ranges.append([round(max(0.0, cur2), 3), round(b0, 3)])

total = round(sum(e - s for s, e in ranges), 3)
edl = {
    "version": 1, "sources": {"src": str(SRC)},
    "ranges": [{"source": "src", "start": s, "end": e} for s, e in ranges],
    "grade": "none", "overlays": [], "subtitle_case": "natural",
    "subtitle_style": STYLE, "total_duration_s": total,
}
(EDIT / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
orig = words[-1]["end"]
print(f"{len(ranges)} ranges | {total}s de {orig:.1f}s (cortou {orig-total:.1f}s)")
