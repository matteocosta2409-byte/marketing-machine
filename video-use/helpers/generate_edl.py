"""Auto-generate EDL ranges from a transcript by tightening silence gaps.

For long videos, hand-authoring dozens of cut ranges is impractical. This walks
the word-level transcript, splits the timeline at every silence gap >= threshold,
and emits one range per kept span (with word-boundary padding). Pauses below the
threshold are left intact (natural speech rhythm).

Usage:
    python helpers/generate_edl.py <transcript.json> --source NAME --path /abs/file.mov \
        --threshold 0.5 --out edl.json [--start 0 --end 210]
"""
from __future__ import annotations
import argparse, json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript", type=Path)
    ap.add_argument("--source", required=True, help="EDL source key")
    ap.add_argument("--path", required=True, help="absolute path to source video")
    ap.add_argument("--threshold", type=float, default=0.5, help="min gap (s) to cut")
    ap.add_argument("--pad", type=float, default=0.075, help="padding into silence at each cut edge")
    ap.add_argument("--head-pad", type=float, default=0.05)
    ap.add_argument("--tail-pad", type=float, default=0.08)
    ap.add_argument("--start", type=float, default=0.0, help="window start (s)")
    ap.add_argument("--end", type=float, default=None, help="window end (s); default = whole video")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    tr = json.loads(args.transcript.read_text())
    words = [w for w in tr["words"] if w.get("type") == "word" and w.get("start") is not None]
    lo, hi = args.start, (args.end if args.end is not None else 1e9)
    words = [w for w in words if w["end"] > lo and w["start"] < hi]
    if not words:
        raise SystemExit("no words in window")

    segments = []
    seg_start = max(lo, words[0]["start"] - args.head_pad)
    prev_end = words[0]["end"]
    for w in words[1:]:
        gap = w["start"] - prev_end
        if gap >= args.threshold:
            segments.append((seg_start, prev_end + args.pad))
            seg_start = w["start"] - args.pad
        prev_end = w["end"]
    segments.append((seg_start, min(hi, prev_end + args.tail_pad)))

    ranges = [{"source": args.source, "start": round(s, 3), "end": round(e, 3)}
              for s, e in segments if e - s > 0.15]
    total = round(sum(r["end"] - r["start"] for r in ranges), 2)
    edl = {
        "version": 1,
        "sources": {args.source: args.path},
        "ranges": ranges,
        "grade": "none",
        "total_duration_s": total,
    }
    args.out.write_text(json.dumps(edl, indent=2, ensure_ascii=False))
    orig = words[-1]["end"] - words[0]["start"]
    print(f"{len(ranges)} ranges | kept {total:.1f}s of {orig:.1f}s "
          f"(cut {orig - total:.1f}s) → {args.out.name}")


if __name__ == "__main__":
    main()
