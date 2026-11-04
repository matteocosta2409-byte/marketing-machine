"""master.srt limpo: cada palavra -> range de maior sobreposicao (uma vez); cues sem overlap. Uso: python clean_srt.py <proj> [--palavra]
--palavra: 1 palavra por cue, minuscula, sem pontuacao (estilo ref DercufHR25s / presets/reels-colagem.md)"""
import json, sys, glob
from pathlib import Path

proj = Path("/Users/mac-matteo/marketing machine") / sys.argv[1]
edit = proj / "edit"
edl = json.loads((edit / "edl.json").read_text())
ranges = [(float(r["start"]), float(r["end"])) for r in edl["ranges"]]
tr_path = glob.glob(str(edit / "transcripts/*.json"))[0]
words = [w for w in json.loads(Path(tr_path).read_text())["words"]
         if w.get("type") == "word" and w.get("start") is not None]

offsets, acc = [], 0.0
for s, e in ranges:
    offsets.append(acc); acc += e - s


def assign(w):
    if w["end"] - w["start"] < 0.05:                # palavra ponto
        for i, (s, e) in enumerate(ranges):
            if s <= w["start"] <= e:
                return i, offsets[i] + (w["start"] - s)
        return None
    best_i, best_ov = None, 0.0
    for i, (s, e) in enumerate(ranges):
        ov = min(w["end"], e) - max(w["start"], s)
        if ov > best_ov:
            best_ov, best_i = ov, i
    wdur = max(0.01, w["end"] - w["start"])
    if best_i is None or (best_ov < 0.06 and best_ov < 0.40 * wdur):
        return None
    s, e = ranges[best_i]
    return best_i, offsets[best_i] + (min(max(w["start"], s), e) - s)


# calcula (out_time, range_idx, texto) de cada palavra e ORDENA por tempo de saida
# (essencial quando os ranges sao reordenados no EDL)
items = []
for w in words:
    a = assign(w)
    if a is not None:
        ri, o = a
        items.append((o, ri, w["text"]))
items.sort()
PALAVRA = "--palavra" in sys.argv
if PALAVRA:
    items = [(o, ri, t.lower().strip(".,!?:;\"'")) for o, ri, t in items]

cues, cur, prev = [], [], None
for o, ri, text in items:
    if prev is not None and ri != prev and cur:
        cues.append(cur); cur = []
    prev = ri
    cur.append((o, text))
    if text.rstrip().endswith(('.', '!', '?', ',', ':', ';')) or len(cur) >= (1 if PALAVRA else 2):
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
