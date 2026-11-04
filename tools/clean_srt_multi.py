"""master.srt limpo p/ EDL multi-fonte. Cada palavra -> range da SUA fonte (maior sobreposicao),
uma vez; ordena por tempo de saida; cues sem overlap. Uso: python clean_srt_multi.py <proj>"""
import json, sys
from pathlib import Path

proj = Path("/Users/mac-matteo/marketing machine") / sys.argv[1]
edit = proj / "edit"
edl = json.loads((edit / "edl.json").read_text())
ranges = edl["ranges"]
tr = {}
for name in edl["sources"]:
    p = edit / "transcripts" / (name + ".json")
    tr[name] = [w for w in json.loads(p.read_text())["words"]
                if w.get("type") == "word" and w.get("start") is not None]

offs, acc = [], 0.0
for r in ranges:
    offs.append(acc); acc += float(r["end"]) - float(r["start"])


def assign(w, src):
    if w["end"] - w["start"] < 0.05:
        for i, r in enumerate(ranges):
            if r["source"] == src and float(r["start"]) <= w["start"] <= float(r["end"]):
                return i, offs[i] + (w["start"] - float(r["start"]))
        return None
    best_i, best_ov = None, 0.0
    for i, r in enumerate(ranges):
        if r["source"] != src:
            continue
        s, e = float(r["start"]), float(r["end"])
        ov = min(w["end"], e) - max(w["start"], s)
        if ov > best_ov:
            best_ov, best_i = ov, i
    wdur = max(0.01, w["end"] - w["start"])
    if best_i is None or (best_ov < 0.06 and best_ov < 0.40 * wdur):
        return None
    r = ranges[best_i]; s = float(r["start"])
    return best_i, offs[best_i] + (min(max(w["start"], s), float(r["end"])) - s)


items = []
for src, words in tr.items():
    for w in words:
        a = assign(w, src)
        if a is not None:
            items.append((a[1], a[0], w["text"]))
items.sort()

cues, cur, prev = [], [], None
for o, ri, text in items:
    if prev is not None and ri != prev and cur:
        cues.append(cur); cur = []
    prev = ri
    cur.append((o, text))
    if text.rstrip().endswith(('.', '!', '?', ',', ':', ';')) or len(cur) >= 2:
        cues.append(cur); cur = []
if cur:
    cues.append(cur)

raw = []
for c in cues:
    raw.append([c[0][0], max(x[0] for x in c) + 0.30, " ".join(x[1] for x in c).strip()])
for i in range(len(raw)):
    if i + 1 < len(raw):
        raw[i][1] = min(raw[i][1], raw[i+1][0] - 0.001)
    if raw[i][1] <= raw[i][0]:
        raw[i][1] = raw[i][0] + 0.05


def ts(t):
    h = int(t//3600); m = int((t % 3600)//60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')


out = [f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(raw, 1)]
(edit / "master.srt").write_text("\n".join(out))
print(f"{len(raw)} cues -> master.srt")
