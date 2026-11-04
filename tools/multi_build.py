"""Builder MULTI-parte: junta N partes (cada uma silence-cut + KILLS proprios) -> edl.json ordenado.
Uso: python multi_build.py <proj> '<parts_json>'
  parts_json = [{"name":"IMG_9282","kills":[]}, {"name":"IMG_9283","kills":[[14.8,15.1]]}, ...]
Cada parte tem src em <proj>/<name>.mov e transcript em <proj>/edit/transcripts/<name>.json"""
import json, re, subprocess, sys
from pathlib import Path

proj = Path("/Users/mac-matteo/marketing machine") / sys.argv[1]
EDIT = proj / "edit"
parts = json.loads(sys.argv[2])
GAP, PAD, KEEP = 0.30, 0.04, 0.06
STYLE = ("FontName=Helvetica,FontSize=15,Bold=0,Italic=1,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&HC8000000,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV=60")


def cut_ranges(src, kills):
    err = subprocess.run(["ffmpeg", "-i", str(src), "-af", "silencedetect=noise=-32dB:d=0.18",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    sils, cur = [], None
    for m in re.finditer(r"silence_(start|end):\s*([0-9.]+)", err):
        if m.group(1) == "start":
            cur = float(m.group(2))
        elif cur is not None:
            sils.append((cur, float(m.group(2)))); cur = None
    tr = EDIT / "transcripts" / (src.stem + ".json")
    words = [w for w in json.loads(tr.read_text())["words"]
             if w.get("type") == "word" and w.get("start") is not None]

    def killed(t):
        return any(a <= t < b for a, b in kills)
    kept = []
    for w in words:
        if killed(w["start"]):
            continue
        end = w["end"]
        for a, b in kills:
            if w["start"] < a < end:
                end = a
        kept.append({"start": w["start"], "end": end})
    segs = []
    s = kept[0]["start"] - PAD
    prev = kept[0]["end"]
    for w in kept[1:]:
        if w["start"] - prev >= GAP:
            segs.append([s, prev + PAD]); s = w["start"] - PAD
        prev = max(prev, w["end"])
    segs.append([s, prev + PAD])
    res = []
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
                    res.append([round(cur2, 3), round(a + KEEP, 3)])
                cur2 = b - KEEP
        if b0 - cur2 >= 0.12:
            res.append([round(max(0.0, cur2), 3), round(b0, 3)])
    return res


sources, ranges = {}, []
for p in parts:
    name = p["name"]
    src = proj / (name + ".mov")
    sources[name] = str(src)
    for s, e in cut_ranges(src, p.get("kills", [])):
        ranges.append({"source": name, "start": s, "end": e})

total = round(sum(r["end"] - r["start"] for r in ranges), 3)
edl = {"version": 1, "sources": sources, "ranges": ranges, "grade": "none", "overlays": [],
       "subtitle_case": "natural", "subtitle_style": STYLE, "total_duration_s": total}
(EDIT / "edl.json").write_text(json.dumps(edl, indent=2, ensure_ascii=False))
print(f"{len(parts)} partes, {len(ranges)} ranges | total {total}s")
