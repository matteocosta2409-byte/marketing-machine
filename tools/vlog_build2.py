"""Builder VLOG v2 (YouTube 16:9): abertura (teaser mudo + card VLOG verde c/ pop)
+ vlog completo em ordem, blur-fill 1080p, legenda. Competicao cortada, series
de exercicio com label verde. SEM corte de silencio. Uso: python vlog_build2.py
"""
import json, subprocess, os, sys
from pathlib import Path

PROJ = Path("/Users/mac-matteo/marketing machine/vlog_yt1")
RAW = Path("/Users/mac-matteo/Library/CloudStorage/GoogleDrive-matteocosta2409@gmail.com/"
           "Meu Drive/2026/Personal Branding/YouTube/Raw/Vlog 1 ")
EDIT = PROJ / "edit"
SEG = PROJ / "seg"; SEG.mkdir(parents=True, exist_ok=True)
TR = EDIT / "transcripts"
CARD = PROJ / "vlog_card.mov"
POP = PROJ / "pop.wav"

STYLE = ("FontName=Helvetica,FontSize=15,Bold=0,Italic=1,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&HC8000000,BorderStyle=1,Outline=1,Shadow=1,Alignment=2,MarginV=60")
# override verde (AABBGGRR: #3DA35D -> BB=5D GG=A3 RR=3D) top-center, bold, nao-italico
GREEN_TAG = r"{\an8\b1\i0\fs22\c&H005DA33D&\3c&H00000000&\bord3}"

# ----- TEASER (snippets mudos, ~1.0s) -----
TEASER = [
    ("IMG_9968", 3.8, 4.9),    # soco
    ("IMG_9974", 27.5, 28.6),  # supino
    ("IMG_0002", 7.0, 8.1),    # comida babar
    ("IMG_0007", 9.0, 10.1),   # restaurante
    ("IMG_0004", 5.0, 6.1),    # fusca
]
BEAT = ("IMG_9966", 11.0, 12.7)   # hero do card VLOG (1.7s)

# ----- MAIN (stem, start, end|None, kind) -----
# kind: talk | broll | exec:Label
MAIN = [
    ("IMG_9955", 0.0, None, "talk"),
    ("IMG_9956", 0.0, None, "talk"),
    ("IMG_9958", 0.0, None, "talk"),
    ("IMG_9961", 0.0, None, "talk"),
    ("IMG_9962", 0.0, None, "talk"),
    ("IMG_9963", 0.0, None, "broll"),
    ("IMG_9965", 0.0, None, "talk"),
    ("IMG_9966", 0.0, None, "talk"),
    ("IMG_9967", 0.0, None, "talk"),
    ("IMG_9968", 0.0, None, "talk"),
    ("IMG_9969", 0.0, None, "talk"),
    ("IMG_9970", 0.0, 14.40, "talk"),
    ("IMG_9972", 0.0, None, "talk"),
    ("IMG_9974", 26.0, 33.0, "exec:Supino"),
    ("IMG_9976", 6.0, 13.0, "exec:Desenvolvimento"),
    ("IMG_9977", 15.0, 22.0, "exec:Elevação lateral"),
    ("IMG_9978", 6.0, 13.0, "exec:Bíceps"),
    ("IMG_9979", 0.0, None, "talk"),
    ("IMG_9981", 0.0, None, "talk"),
    ("IMG_9985", 0.0, None, "talk"),
    ("IMG_9986", 0.0, None, "talk"),
    ("IMG_9988", 0.0, None, "talk"),
    ("IMG_9990", 0.0, 10.0, "broll"),
    ("IMG_9993", 0.0, 10.0, "broll"),
    ("IMG_9999", 0.0, None, "talk"),
    ("IMG_0001", 0.0, None, "talk"),
    ("IMG_0002", 0.0, None, "talk"),
    ("IMG_0004", 0.0, None, "talk"),
    ("IMG_0005", 0.0, None, "talk"),
    ("IMG_0006", 0.0, None, "talk"),
    ("IMG_0007", 0.0, None, "talk"),
    ("IMG_0021", 0.0, None, "talk"),
]

VF = ("[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,fps=30,split=2[a][b];"
      "[a]scale=1920:1080:force_original_aspect_ratio=decrease[fg];"
      "[b]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=18:4[bg];"
      "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]")


def probe_dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "default=nk=1:nw=1", str(f)], capture_output=True, text=True).stdout.strip() or 0)


def has_audio(f):
    return bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                "stream=index", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip())


def normalize(stem, s, e, out, mute=False):
    src = RAW / f"{stem}.MOV"
    dur = probe_dur(src)
    if e is None or e > dur:
        e = dur
    fc = VF.format(s=f"{s:.3f}", e=f"{e:.3f}")
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if mute or not has_audio(src):
        cmd += ["-f", "lavfi", "-t", f"{e-s:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex", fc, "-map", "[v]", "-map", "1:a"]
    else:
        cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "0:a:0",
                "-af", f"atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO normalize", stem, "\n", r.stderr[-1200:]); sys.exit(1)
    return e - s


def make_beat(out):
    """hero normalizado mudo + overlay card VLOG + pop SFX."""
    bg = SEG / "_beatbg.mp4"
    d = normalize(BEAT[0], BEAT[1], BEAT[2], bg, mute=True)
    cmd = ["ffmpeg", "-y", "-i", str(bg), "-i", str(CARD), "-i", str(POP),
           "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto[v];[2:a]apad=whole_dur=%.3f[a]" % d,
           "-map", "[v]", "-map", "[a]", "-t", f"{d:.3f}",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO beat\n", r.stderr[-1200:]); sys.exit(1)
    return d


def load_words(stem):
    p = TR / f"{stem}.json"
    if not p.exists():
        return []
    return [w for w in json.loads(p.read_text())["words"]
            if w.get("type") == "word" and w.get("start") is not None]


def fix(t):
    return t.replace("Matheus", "Matteo").replace("matheus", "Matteo")


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.', ',')


def main():
    manifest = []
    cues = []
    offset = 0.0

    # 1) teaser snippets (mudos)
    for i, (stem, s, e) in enumerate(TEASER):
        out = SEG / f"t{i:02d}_{stem}.mp4"
        d = normalize(stem, s, e, out, mute=True)
        manifest.append(out); offset += d
        print(f"[teaser {i}] {stem} {d:.1f}s")
    # 2) beat VLOG
    beat = SEG / "beat_vlog.mp4"
    d = make_beat(beat); manifest.append(beat); offset += d
    print(f"[beat VLOG] {d:.1f}s  (offset pos-abertura={offset:.1f}s)")

    # 3) main
    for i, (stem, s, e, kind) in enumerate(MAIN):
        out = SEG / f"m{i:02d}_{stem}.mp4"
        mute = False
        d = normalize(stem, s, e, out, mute=mute)
        se = s + d
        manifest.append(out)
        print(f"[m{i:02d}] {stem} {s:.1f}-{se:.1f} ({d:.1f}s) {kind}")
        if kind == "talk":
            words = [w for w in load_words(stem) if w["start"] < se and w["end"] > s]
            group = []
            def flush():
                if not group: return
                a = offset + max(0.0, group[0]["start"] - s)
                b = offset + max(0.0, min(group[-1]["end"], se) - s) + 0.30
                txt = fix(" ".join(x["text"] for x in group).strip())
                cues.append([a, b, txt]); group.clear()
            for w in words:
                group.append(w)
                if w["text"].rstrip().endswith(('.', '!', '?', ',', ':', ';')) or len(group) >= 2:
                    flush()
            flush()
        elif kind.startswith("exec:"):
            label = kind.split(":", 1)[1]
            cues.append([offset + 0.15, offset + d - 0.15, GREEN_TAG + label])
        offset += d

    # ordena + evita overlap
    cues.sort()
    for j in range(len(cues)):
        if j + 1 < len(cues):
            cues[j][1] = min(cues[j][1], cues[j + 1][0] - 0.001)
        if cues[j][1] <= cues[j][0]:
            cues[j][1] = cues[j][0] + 0.05
    srt = "\n".join(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n" for k, (a, b, txt) in enumerate(cues, 1))
    (EDIT / "master2.srt").write_text(srt)
    print(f"TOTAL {offset:.1f}s | {len(cues)} cues")

    # concat
    lst = EDIT / "concat2.txt"
    lst.write_text("\n".join(f"file '{p.resolve()}'" for p in manifest))
    joined = EDIT / "joined2.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", "-movflags", "+faststart", str(joined)], capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO concat\n", r.stderr[-1200:]); sys.exit(1)

    # burn
    srt_esc = str((EDIT / "master2.srt").resolve()).replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")
    final = EDIT / "final_v2.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-i", str(joined),
                        "-vf", f"subtitles='{srt_esc}':force_style='{STYLE}'",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                        "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-movflags", "+faststart", str(final)], capture_output=True, text=True)
    if r.returncode != 0:
        print("ERRO burn\n", r.stderr[-1200:]); sys.exit(1)
    print("OK ->", final, f"({probe_dur(final):.1f}s)")


if __name__ == "__main__":
    main()
