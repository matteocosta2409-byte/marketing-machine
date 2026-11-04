"""Tempo da fonte -> tempo na timeline CORTADA (onde entram overlays, SFX e zooms).
Uso: python timeline.py <proj> <palavra> [<palavra> ...]   -> imprime cada ocorrencia: src_t -> out_t
Import: from timeline import out_time, word_times"""
import glob, json, sys
from pathlib import Path

ROOT = Path("/Users/mac-matteo/marketing machine")


def load(proj):
    edit = ROOT / proj / "edit"
    ranges = [(float(r["start"]), float(r["end"])) for r in json.loads((edit / "edl.json").read_text())["ranges"]]
    words = [w for w in json.loads(Path(glob.glob(str(edit / "transcripts/*.json"))[0]).read_text())["words"]
             if w.get("type") == "word" and w.get("start") is not None]
    return ranges, words


def out_time(ranges, t):
    """None se o instante caiu num trecho cortado."""
    acc = 0.0
    for s, e in ranges:
        if s <= t <= e:
            return round(acc + t - s, 3)
        acc += e - s
    return None


def word_times(proj, needle):
    ranges, words = load(proj)
    needle = needle.lower().strip(".,!?")
    return [(w["start"], out_time(ranges, w["start"] + 0.02)) for w in words
            if w["text"].lower().strip(".,!?:;") == needle]


if __name__ == "__main__":
    for n in sys.argv[2:]:
        for src_t, out_t in word_times(sys.argv[1], n):
            print(f"{n}: src {src_t:.2f} -> out {out_t}")
