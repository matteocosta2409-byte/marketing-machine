"""Mix a short sound effect into a video at given timestamps.

Used to add a subtle "pop" each time a motion graphic appears. The SFX is
delayed to each cue time and summed with the original audio (no auto-normalize,
so the original stays at its loudnorm level); a final limiter guards against
clipping. Video is stream-copied — only the audio is re-encoded.

Usage:
    python helpers/add_sfx.py --video final.mp4 --sfx assets/pop.wav \
        --times 6.6,51.0,134.1 --out final_sfx.mp4
"""
from __future__ import annotations
import argparse
import subprocess
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", type=Path, required=True)
    ap.add_argument("--sfx", type=Path, required=True)
    ap.add_argument("--times", required=True, help="comma-separated seconds")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    times = [float(t) for t in args.times.split(",") if t.strip()]
    n = len(times)
    if n == 0:
        raise SystemExit("no times given")

    # asplit the SFX into N copies, delay each to its cue, then sum with original.
    labels = "".join(f"[s{i}]" for i in range(n))
    parts = [f"[1:a]asplit={n}{labels}"]
    for i, t in enumerate(times):
        ms = int(round(t * 1000))
        parts.append(f"[s{i}]adelay={ms}|{ms}[d{i}]")
    mix_in = "[0:a]" + "".join(f"[d{i}]" for i in range(n))
    parts.append(f"{mix_in}amix=inputs={n + 1}:normalize=0:dropout_transition=0[mx]")
    parts.append("[mx]alimiter=limit=0.97[aout]")
    filt = ";".join(parts)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(args.video),
        "-i", str(args.sfx),
        "-filter_complex", filt,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        str(args.out),
    ]
    print(f"mixing {n} SFX hits into {args.video.name} → {args.out.name}")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print("done")


if __name__ == "__main__":
    main()
